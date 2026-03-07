import { safeStorage } from 'electron';
import type { SessionPayload } from 'dictapilot-desktop-shared';
import { authService } from './authService';
import { sessionStoreService } from './storageService';

function encodeSession(session: SessionPayload): { encrypted: boolean; payload: string } {
    const raw = Buffer.from(JSON.stringify(session), 'utf8');
    if (safeStorage.isEncryptionAvailable()) {
        return {
            encrypted: true,
            payload: safeStorage.encryptString(raw.toString('utf8')).toString('base64'),
        };
    }

    return {
        encrypted: false,
        payload: raw.toString('base64'),
    };
}

function decodeSession(envelope: { encrypted: boolean; payload: string }): SessionPayload | null {
    try {
        if (envelope.encrypted) {
            const decrypted = safeStorage.decryptString(Buffer.from(envelope.payload, 'base64'));
            return JSON.parse(decrypted) as SessionPayload;
        }

        const raw = Buffer.from(envelope.payload, 'base64').toString('utf8');
        return JSON.parse(raw) as SessionPayload;
    } catch {
        return null;
    }
}

export class SessionService {
    persist(session: SessionPayload): void {
        sessionStoreService.setEnvelope(encodeSession(session));
    }

    clear(): void {
        sessionStoreService.setEnvelope(null);
    }

    load(): SessionPayload | null {
        const envelope = sessionStoreService.getEnvelope();
        if (!envelope) {
            return null;
        }
        return decodeSession(envelope);
    }

    async restore(): Promise<SessionPayload | null> {
        const persisted = this.load();
        if (!persisted) {
            return null;
        }

        try {
            const restored = await authService.restoreSession(persisted);
            this.persist(restored.session);
            return restored.session;
        } catch {
            this.clear();
            return null;
        }
    }
}

export const sessionService = new SessionService();
