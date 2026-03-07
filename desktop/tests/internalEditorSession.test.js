const {
  applyInternalEditorSessionTranscript,
  captureInternalEditorSession,
} = require('../shared/dist/internalEditorSession');

describe('internalEditorSession', () => {
  test('replaces only the captured selection across repeated transcript updates', () => {
    const snapshot = captureInternalEditorSession('session-a', 'alpha beta gamma', 6, 10);

    expect(applyInternalEditorSessionTranscript(snapshot, 'one')).toEqual({
      value: 'alpha one gamma',
      selectionStart: 9,
      selectionEnd: 9,
    });

    expect(applyInternalEditorSessionTranscript(snapshot, 'two words')).toEqual({
      value: 'alpha two words gamma',
      selectionStart: 15,
      selectionEnd: 15,
    });
  });

  test('clamps invalid selections before applying transcript text', () => {
    const snapshot = captureInternalEditorSession('session-b', 'hello', -4, 999);

    expect(applyInternalEditorSessionTranscript(snapshot, 'world')).toEqual({
      value: 'world',
      selectionStart: 5,
      selectionEnd: 5,
    });
  });
});
