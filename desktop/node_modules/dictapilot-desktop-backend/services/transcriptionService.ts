import { EventEmitter } from 'events';
import { audioService } from './audioService';

export interface TranscriptionProvider extends EventEmitter {
    startSession(sessionId: string): void;
    processAudioChunk(sessionId: string, buffer: Buffer): void;
    stopSession(sessionId: string): Promise<string>;
    abortSession(sessionId: string): void;
}

export class TranscriptionService extends EventEmitter {
    private provider: TranscriptionProvider | null = null;
    private isRecording = false;
    private activeSessionId: string | null = null;
    private closingSessionId: string | null = null;

    constructor() {
        super();
    }

    setProvider(provider: TranscriptionProvider) {
        if (this.provider) {
            this.provider.removeAllListeners('transcription-update');
            this.provider.removeAllListeners('error');
        }
        
        this.provider = provider;
        this.provider.on('transcription-update', (data) => {
            if (data?.sessionId && (data.sessionId === this.activeSessionId || data.sessionId === this.closingSessionId)) {
                this.emit('transcription-update', data);
            }
        });
        this.provider.on('error', (err) => {
            this.emit('error', err);
        });
    }

    clearProvider() {
        if (this.provider && this.activeSessionId) {
            this.provider.abortSession(this.activeSessionId);
        }
        if (this.provider) {
            this.provider.removeAllListeners('transcription-update');
            this.provider.removeAllListeners('error');
        }
        this.provider = null;
        this.activeSessionId = null;
        this.closingSessionId = null;
        this.isRecording = false;
    }

    startSession(sessionId: string) {
        if (!this.provider) {
            console.error('TranscriptionService: No provider set');
            return;
        }
        if (this.activeSessionId) {
            this.provider.abortSession(this.activeSessionId);
        }
        this.closingSessionId = null;
        this.activeSessionId = sessionId;
        this.isRecording = true;
        this.provider.startSession(sessionId);
    }

    appendAudio(sessionId: string, buffer: Buffer) {
        if (!this.provider || !this.isRecording || sessionId !== this.activeSessionId) {
            return;
        }
        this.provider.processAudioChunk(sessionId, buffer);
    }

    abortSession(sessionId: string) {
        if (!this.provider) {
            return;
        }
        if (this.activeSessionId === sessionId) {
            this.provider.abortSession(sessionId);
            this.activeSessionId = null;
        }
        if (this.closingSessionId === sessionId) {
            this.closingSessionId = null;
        }
        this.isRecording = false;
    }

    resetSession() {
        if (this.activeSessionId) {
            this.abortSession(this.activeSessionId);
        }
        this.activeSessionId = null;
        this.closingSessionId = null;
        this.isRecording = false;
    }

    async stopSession(sessionId: string) {
        this.isRecording = false;
        if (!this.provider || sessionId !== this.activeSessionId) return '';
        this.closingSessionId = sessionId;
        this.activeSessionId = null;
        const finalText = await this.provider.stopSession(sessionId);
        if (this.closingSessionId === sessionId) {
            this.closingSessionId = null;
        }
        return finalText;
    }
}

export const transcriptionService = new TranscriptionService();
