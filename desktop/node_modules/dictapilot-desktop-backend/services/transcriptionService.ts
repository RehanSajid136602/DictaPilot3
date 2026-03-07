import { EventEmitter } from 'events';
import { audioService } from './audioService';

export interface TranscriptionProvider extends EventEmitter {
    start(): void;
    processAudioChunk(buffer: Buffer): void;
    stop(): Promise<string>;
}

export class TranscriptionService extends EventEmitter {
    private provider: TranscriptionProvider | null = null;
    private isRecording = false;

    constructor() {
        super();
        audioService.on('audio-data', (data: Buffer) => {
            if (this.isRecording && this.provider) {
                this.provider.processAudioChunk(data);
            }
        });
    }

    setProvider(provider: TranscriptionProvider) {
        if (this.provider) {
            this.provider.removeAllListeners('transcription-update');
            this.provider.removeAllListeners('error');
        }
        
        this.provider = provider;
        this.provider.on('transcription-update', (data) => {
            this.emit('transcription-update', data);
        });
        this.provider.on('error', (err) => {
            this.emit('error', err);
        });
    }

    clearProvider() {
        if (this.provider) {
            this.provider.removeAllListeners('transcription-update');
            this.provider.removeAllListeners('error');
        }
        this.provider = null;
    }

    start() {
        if (!this.provider) {
            console.error('TranscriptionService: No provider set');
            return;
        }
        this.isRecording = true;
        this.provider.start();
    }

    async stop() {
        this.isRecording = false;
        if (!this.provider) return;
        const finalText = await this.provider.stop();
        return finalText;
    }
}

export const transcriptionService = new TranscriptionService();
