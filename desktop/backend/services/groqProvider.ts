import { EventEmitter } from 'events';
import Groq from 'groq-sdk';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import { TranscriptionProvider } from './transcriptionService';

export class GroqProvider extends EventEmitter implements TranscriptionProvider {
    private groq: Groq;
    private audioBuffer: Buffer[] = [];
    private isRecording = false;
    private processInterval: NodeJS.Timeout | null = null;
    private tempFileCount = 0;
    private isProcessing = false;
    private currentSessionId: string | null = null;

    constructor(apiKey: string) {
        super();
        this.groq = new Groq({ apiKey });
    }

    startSession(sessionId: string) {
        this.abortSession(this.currentSessionId || sessionId);
        this.currentSessionId = sessionId;
        this.isRecording = true;
        this.audioBuffer = [];
        this.isProcessing = false;
        
        // Transcribe every 2 seconds to create a streaming effect
        this.processInterval = setInterval(() => {
            if (!this.isProcessing && this.currentSessionId === sessionId) {
                void this.transcribeCurrentBuffer(sessionId, false);
            }
        }, 2000); 
    }

    processAudioChunk(sessionId: string, chunk: Buffer) {
        if (!this.isRecording || sessionId !== this.currentSessionId) return;
        this.audioBuffer.push(chunk);
    }

    async stopSession(sessionId: string): Promise<string> {
        if (sessionId !== this.currentSessionId) {
            return '';
        }
        this.isRecording = false;
        if (this.processInterval) {
            clearInterval(this.processInterval);
            this.processInterval = null;
        }
        
        // Wait a tiny bit for the last chunk
        await new Promise(resolve => setTimeout(resolve, 300));

        const result = await this.transcribeCurrentBuffer(sessionId, true);
        if (this.currentSessionId === sessionId) {
            this.currentSessionId = null;
            this.audioBuffer = [];
        }
        return result;
    }

    abortSession(sessionId: string) {
        if (!this.currentSessionId || sessionId !== this.currentSessionId) {
            return;
        }
        this.isRecording = false;
        if (this.processInterval) {
            clearInterval(this.processInterval);
            this.processInterval = null;
        }
        this.audioBuffer = [];
        this.isProcessing = false;
        this.currentSessionId = null;
    }

    private createWavHeader(dataLength: number, sampleRate: number = 16000, channels: number = 1, bitDepth: number = 16): Buffer {
        const header = Buffer.alloc(44);
        header.write('RIFF', 0);
        header.writeUInt32LE(36 + dataLength, 4);
        header.write('WAVE', 8);
        header.write('fmt ', 12);
        header.writeUInt32LE(16, 16);
        header.writeUInt16LE(1, 20);
        header.writeUInt16LE(channels, 22);
        header.writeUInt32LE(sampleRate, 24);
        header.writeUInt32LE(sampleRate * channels * (bitDepth / 8), 28);
        header.writeUInt16LE(channels * (bitDepth / 8), 32);
        header.writeUInt16LE(bitDepth, 34);
        header.write('data', 36);
        header.writeUInt32LE(dataLength, 40);
        return header;
    }

    private async transcribeCurrentBuffer(sessionId: string, isFinal: boolean): Promise<string> {
        if (sessionId !== this.currentSessionId || this.audioBuffer.length === 0) return "";
        if (this.audioBuffer.length === 0) return "";

        this.isProcessing = true;
        
        // Combine all chunks recorded so far
        const pcmData = Buffer.concat(this.audioBuffer);
        
        // Skip if buffer is too small (< 0.5s of audio)
        if (!isFinal && pcmData.length < 16000) {
            this.isProcessing = false;
            return "";
        }

        const wavHeader = this.createWavHeader(pcmData.length);
        const wavData = Buffer.concat([wavHeader, pcmData]);

        const tempPath = path.join(os.tmpdir(), `dictapilot_chunk_${Date.now()}_${this.tempFileCount++}.wav`);
        fs.writeFileSync(tempPath, wavData);

        try {
            const transcription = await this.groq.audio.transcriptions.create({
                file: fs.createReadStream(tempPath),
                model: 'whisper-large-v3',
                language: 'en',
            });

            if (this.currentSessionId !== sessionId) {
                return "";
            }

            this.emit('transcription-update', { sessionId, text: transcription.text, isFinal });
            return transcription.text;
        } catch (error) {
            console.error('Groq transcription error:', error);
            this.emit('error', error);
            return "";
        } finally {
            try {
                fs.unlinkSync(tempPath);
            } catch (e) {
                // Ignore cleanup errors
            }
            this.isProcessing = false;
        }
    }
}
