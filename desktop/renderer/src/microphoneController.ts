import type { AudioInputDeviceInfo } from 'dictapilot-desktop-shared';

export interface MicrophoneControllerEvents {
    onAudioData: (sessionId: string, buffer: ArrayBuffer) => void;
    onDevicesChanged?: (devices: AudioInputDeviceInfo[]) => void;
    onNotice?: (message: string | null) => void;
    onError?: (message: string) => void;
}

function normalizePreferredDeviceId(deviceId?: string | null): string {
    return deviceId && deviceId.trim() ? deviceId : 'default';
}

export class MicrophoneController {
    private readonly onAudioData: MicrophoneControllerEvents['onAudioData'];
    private readonly onDevicesChanged?: MicrophoneControllerEvents['onDevicesChanged'];
    private readonly onNotice?: MicrophoneControllerEvents['onNotice'];
    private readonly onError?: MicrophoneControllerEvents['onError'];
    private readonly AudioContextCtor: typeof AudioContext;

    private currentSessionId: string | null = null;
    private preferredDeviceId = 'default';
    private resolvedDeviceId = 'default';
    private stream: MediaStream | null = null;
    private audioContext: AudioContext | null = null;
    private processor: ScriptProcessorNode | null = null;
    private source: MediaStreamAudioSourceNode | null = null;
    private devices: AudioInputDeviceInfo[] = [];
    private pendingDeviceRefresh = false;
    private disposed = false;
    private readonly deviceChangeCleanup: () => void;

    constructor(events: MicrophoneControllerEvents) {
        this.onAudioData = events.onAudioData;
        this.onDevicesChanged = events.onDevicesChanged;
        this.onNotice = events.onNotice;
        this.onError = events.onError;

        const AudioCtor = window.AudioContext || (window as typeof window & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
        if (!AudioCtor) {
            throw new Error('This browser does not support Web Audio input capture.');
        }
        this.AudioContextCtor = AudioCtor;

        this.deviceChangeCleanup = window.dictationAPI.onAudioDevicesChanged(() => {
            if (this.disposed) {
                return;
            }
            if (this.currentSessionId) {
                this.pendingDeviceRefresh = true;
                this.onNotice?.('Microphone change detected. The new device will be used on the next recording.');
                return;
            }
            void this.refreshDevices();
        });
    }

    async initialize(preferredDeviceId?: string): Promise<AudioInputDeviceInfo[]> {
        this.preferredDeviceId = normalizePreferredDeviceId(preferredDeviceId);
        return this.refreshDevices();
    }

    getDevices(): AudioInputDeviceInfo[] {
        return [...this.devices];
    }

    getPreferredDeviceId(): string {
        return this.preferredDeviceId;
    }

    getResolvedDeviceId(): string {
        return this.resolvedDeviceId;
    }

    async setPreferredDeviceId(deviceId: string): Promise<AudioInputDeviceInfo[]> {
        this.preferredDeviceId = normalizePreferredDeviceId(deviceId);
        return this.refreshDevices();
    }

    async refreshDevices(requestPermission = false): Promise<AudioInputDeviceInfo[]> {
        const response = await window.dictationAPI.getAudioInputDevices(requestPermission);
        const discoveredDevices = response.success && response.data ? response.data : [];

        const preferred = normalizePreferredDeviceId(this.preferredDeviceId);
        const explicitMatch = discoveredDevices.find((device) => !device.isDefault && device.deviceId === preferred);
        const nextDevices = [...discoveredDevices];

        if (preferred !== 'default' && !explicitMatch) {
            nextDevices.push({
                deviceId: preferred,
                label: 'Previously selected microphone (unavailable)',
                isDefault: false,
                unavailable: true,
            });
        }
        this.devices = nextDevices;

        if (preferred !== 'default' && !explicitMatch) {
            this.resolvedDeviceId = 'default';
            if (discoveredDevices.length > 0) {
                this.onNotice?.('Selected microphone is unavailable. Using the system default microphone.');
            }
        } else {
            this.resolvedDeviceId = explicitMatch?.deviceId || 'default';
            if (!this.currentSessionId) {
                this.onNotice?.(null);
            }
        }

        this.onDevicesChanged?.([...nextDevices]);
        return [...nextDevices];
    }

    async startSession(sessionId: string): Promise<void> {
        this.pendingDeviceRefresh = false;
        this.currentSessionId = sessionId;
        await this.teardown();
        await this.refreshDevices(true);

        const preferred = normalizePreferredDeviceId(this.preferredDeviceId);
        const resolved = this.resolvedDeviceId || preferred;
        const constraints: MediaStreamConstraints = resolved === 'default'
            ? { audio: true }
            : { audio: { deviceId: { exact: resolved } } };

        try {
            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            if (this.currentSessionId !== sessionId) {
                stream.getTracks().forEach((track) => track.stop());
                return;
            }

            this.stream = stream;
            this.audioContext = new this.AudioContextCtor({ sampleRate: 16000 });
            this.source = this.audioContext.createMediaStreamSource(stream);
            this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);

            this.processor.onaudioprocess = (event) => {
                if (this.currentSessionId !== sessionId) {
                    return;
                }

                const inputData = event.inputBuffer.getChannelData(0);
                const pcm16 = new Int16Array(inputData.length);
                for (let index = 0; index < inputData.length; index += 1) {
                    const sample = Math.max(-1, Math.min(1, inputData[index]));
                    pcm16[index] = sample * 0x7fff;
                }

                this.onAudioData(sessionId, pcm16.buffer);
            };

            this.source.connect(this.processor);
            this.processor.connect(this.audioContext.destination);
            this.onNotice?.(preferred === 'default' && resolved === 'default' ? null : `Using ${this.getResolvedDeviceLabel()}.`);
        } catch (error) {
            this.currentSessionId = null;
            await this.teardown();
            this.onError?.(error instanceof Error ? error.message : 'Microphone access failed.');
            throw error;
        }
    }

    async stopSession(sessionId: string): Promise<void> {
        if (this.currentSessionId !== sessionId) {
            return;
        }
        this.currentSessionId = null;
        await this.teardown();
        if (this.pendingDeviceRefresh) {
            this.pendingDeviceRefresh = false;
            await this.refreshDevices();
        }
    }

    async abortSession(sessionId: string): Promise<void> {
        if (this.currentSessionId !== sessionId) {
            return;
        }
        this.currentSessionId = null;
        await this.teardown();
    }

    async dispose(): Promise<void> {
        this.disposed = true;
        this.deviceChangeCleanup();
        const sessionId = this.currentSessionId;
        this.currentSessionId = null;
        if (sessionId) {
            await this.teardown();
        }
    }

    private getResolvedDeviceLabel(): string {
        if (this.resolvedDeviceId === 'default') {
            return 'system default microphone';
        }
        return this.devices.find((device) => device.deviceId === this.resolvedDeviceId)?.label || 'selected microphone';
    }

    private async teardown(): Promise<void> {
        if (this.processor) {
            this.processor.onaudioprocess = null;
            this.processor.disconnect();
            this.processor = null;
        }
        if (this.source) {
            this.source.disconnect();
            this.source = null;
        }
        if (this.stream) {
            this.stream.getTracks().forEach((track) => track.stop());
            this.stream = null;
        }
        if (this.audioContext) {
            await this.audioContext.close();
            this.audioContext = null;
        }
    }
}
