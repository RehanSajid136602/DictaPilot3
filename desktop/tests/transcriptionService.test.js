const { EventEmitter } = require('events');
const mockAudioService = new EventEmitter();

jest.mock('../backend/dist/services/audioService', () => ({
  audioService: mockAudioService,
}));

const { TranscriptionService } = require('../backend/dist/services/transcriptionService');

class MockProvider extends EventEmitter {
  constructor() {
    super();
    this.sessions = [];
    this.received = [];
  }

  startSession(sessionId) {
    this.sessions.push(['start', sessionId]);
  }

  processAudioChunk(sessionId, buffer) {
    this.received.push({ sessionId, size: buffer.length });
  }

  async stopSession(sessionId) {
    this.sessions.push(['stop', sessionId]);
    this.emit('transcription-update', { sessionId, text: `final:${sessionId}`, isFinal: true });
    return `final:${sessionId}`;
  }

  abortSession(sessionId) {
    this.sessions.push(['abort', sessionId]);
  }
}

describe('TranscriptionService', () => {
  test('only forwards transcription updates for the active session', () => {
    const service = new TranscriptionService();
    const provider = new MockProvider();
    const updates = [];

    service.setProvider(provider);
    service.on('transcription-update', (event) => updates.push(event));

    service.startSession('session-a');
    provider.emit('transcription-update', { sessionId: 'session-a', text: 'hello', isFinal: false });
    provider.emit('transcription-update', { sessionId: 'session-b', text: 'stale', isFinal: false });

    expect(updates).toEqual([
      { sessionId: 'session-a', text: 'hello', isFinal: false },
    ]);
  });

  test('ignores audio chunks for inactive sessions', () => {
    const service = new TranscriptionService();
    const provider = new MockProvider();

    service.setProvider(provider);
    service.startSession('session-a');
    service.appendAudio('session-b', Buffer.from([1, 2, 3]));
    service.appendAudio('session-a', Buffer.from([1, 2, 3, 4]));

    expect(provider.received).toEqual([
      { sessionId: 'session-a', size: 4 },
    ]);
  });

  test('aborting a session prevents stale updates from leaking into the next one', async () => {
    const service = new TranscriptionService();
    const provider = new MockProvider();
    const updates = [];

    service.setProvider(provider);
    service.on('transcription-update', (event) => updates.push(event));

    service.startSession('session-a');
    service.abortSession('session-a');
    service.startSession('session-b');

    provider.emit('transcription-update', { sessionId: 'session-a', text: 'stale', isFinal: false });
    provider.emit('transcription-update', { sessionId: 'session-b', text: 'fresh', isFinal: false });
    await service.stopSession('session-b');

    expect(provider.sessions).toEqual([
      ['start', 'session-a'],
      ['abort', 'session-a'],
      ['start', 'session-b'],
      ['stop', 'session-b'],
    ]);
    expect(updates).toEqual([
      { sessionId: 'session-b', text: 'fresh', isFinal: false },
      { sessionId: 'session-b', text: 'final:session-b', isFinal: true },
    ]);
  });
});
