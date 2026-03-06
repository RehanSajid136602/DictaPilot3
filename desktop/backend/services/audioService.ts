import { EventEmitter } from 'events';

export class AudioService extends EventEmitter {
    start() {
        console.log('AudioService: Waiting for renderer audio stream...');
    }

    stop() {
        console.log('AudioService: Stopping renderer audio stream...');
    }

    finalize() {
        this.stop();
    }
}

export const audioService = new AudioService();