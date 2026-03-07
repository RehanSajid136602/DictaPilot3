export interface InternalEditorSessionSnapshot {
    sessionId: string;
    baseValue: string;
    selectionStart: number;
    selectionEnd: number;
}

export interface InternalEditorSessionResult {
    value: string;
    selectionStart: number;
    selectionEnd: number;
}

function clampSelection(value: string, position?: number | null): number {
    if (typeof position !== 'number' || Number.isNaN(position)) {
        return value.length;
    }

    return Math.min(Math.max(position, 0), value.length);
}

export function captureInternalEditorSession(
    sessionId: string,
    value: string,
    selectionStart?: number | null,
    selectionEnd?: number | null,
): InternalEditorSessionSnapshot {
    const normalizedStart = clampSelection(value, selectionStart);
    const normalizedEnd = clampSelection(value, selectionEnd);
    const start = Math.min(normalizedStart, normalizedEnd);
    const end = Math.max(normalizedStart, normalizedEnd);

    return {
        sessionId,
        baseValue: value,
        selectionStart: start,
        selectionEnd: end,
    };
}

export function applyInternalEditorSessionTranscript(
    snapshot: InternalEditorSessionSnapshot,
    transcript: string,
): InternalEditorSessionResult {
    const before = snapshot.baseValue.slice(0, snapshot.selectionStart);
    const after = snapshot.baseValue.slice(snapshot.selectionEnd);
    const value = `${before}${transcript}${after}`;
    const caret = snapshot.selectionStart + transcript.length;

    return {
        value,
        selectionStart: caret,
        selectionEnd: caret,
    };
}
