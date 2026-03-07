const { TextInsertionService } = require('../backend/dist/services/textInsertionService');

describe('TextInsertionService', () => {
  test('commits text only once for an active session', () => {
    const service = new TextInsertionService();

    service.beginSession('session-a');

    expect(service.canCommit('session-a')).toBe(true);
    expect(service.commit('session-a', 'hello world')).toEqual({
      sessionId: 'session-a',
      text: 'hello world',
    });
    expect(service.canCommit('session-a')).toBe(false);
    expect(service.commit('session-a', 'hello again')).toBeNull();
  });

  test('ignores commits from stale sessions', () => {
    const service = new TextInsertionService();

    service.beginSession('session-a');
    service.beginSession('session-b');

    expect(service.canCommit('session-a')).toBe(false);
    expect(service.commit('session-a', 'stale text')).toBeNull();
    expect(service.commit('session-b', 'fresh text')).toEqual({
      sessionId: 'session-b',
      text: 'fresh text',
    });
  });

  test('resetting the session clears the insertion baseline', () => {
    const service = new TextInsertionService();

    service.beginSession('session-a');
    service.commit('session-a', 'hello world');
    expect(service.getCommittedText()).toBe('hello world');

    service.resetSession();

    expect(service.getCommittedText()).toBe('');
    expect(service.canCommit('session-a')).toBe(false);
  });
});
