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

    constructor(apiKey: string) {
        super();
        this.groq = new Groq({ apiKey });
    }

    start() {
        this.isRecording = true;
        this.audioBuffer = [];
        this.isProcessing = false;
        
        // Transcribe every 2 seconds to create a streaming effect
        this.processInterval = setInterval(() => {
            if (!this.isProcessing) {
                this.transcribeCurrentBuffer(false);
            }
        }, 2000); 
    }

    processAudioChunk(chunk: Buffer) {
        if (!this.isRecording) return;
        this.audioBuffer.push(chunk);
    }

    async stop(): Promise<string> {
        this.isRecording = false;
        if (this.processInterval) {
            clearInterval(this.processInterval);
            this.processInterval = null;
        }
        
        // Wait a tiny bit for the last chunk
        await new Promise(resolve => setTimeout(resolve, 300));
        
        return await this.transcribeCurrentBuffer(true);
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

    private async transcribeCurrentBuffer(isFinal: boolean): Promise<string> {
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

            this.emit('transcription-update', { text: transcription.text, isFinal });
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
