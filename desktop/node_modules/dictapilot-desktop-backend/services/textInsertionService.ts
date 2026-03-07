export interface InsertionCommit {
    sessionId: string;
    text: string;
}

export class TextInsertionService {
    private activeSessionId: string | null = null;
    private finalizedSessions = new Set<string>();
    private lastCommittedText = '';

    beginSession(sessionId: string): void {
        this.activeSessionId = sessionId;
        this.lastCommittedText = '';
    }

    resetSession(sessionId?: string | null): void {
        if (!sessionId || this.activeSessionId === sessionId) {
            this.activeSessionId = null;
        }
        this.lastCommittedText = '';
    }

    abandonSession(sessionId?: string | null): void {
        this.resetSession(sessionId);
    }

    canCommit(sessionId: string): boolean {
        return this.activeSessionId === sessionId && !this.finalizedSessions.has(sessionId);
    }

    commit(sessionId: string, text: string): InsertionCommit | null {
        if (!this.canCommit(sessionId)) {
            return null;
        }

        const normalized = text.trim();
        this.finalizedSessions.add(sessionId);
        this.activeSessionId = null;
        this.lastCommittedText = normalized;

        if (!normalized) {
            return null;
        }

        return {
            sessionId,
            text: normalized,
        };
    }

    clearCommittedBaseline(): void {
        this.lastCommittedText = '';
    }

    getCommittedText(): string {
        return this.lastCommittedText;
    }
}

export const textInsertionService = new TextInsertionService();
