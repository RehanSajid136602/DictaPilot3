import type {
    AccountProfile,
    DeviceMetadata,
    DictionaryRecord,
    SessionPayload,
    SettingsRecord,
    SnippetRecord,
    SyncRecordMetadata,
} from 'dictapilot-desktop-shared';
import { validateFirebaseProviderConfig } from './firebaseConfigService';

type FirestoreDocument = {
    name?: string;
    fields?: Record<string, FirestoreValue>;
};

type FirestoreValue =
    | { stringValue: string }
    | { integerValue: string }
    | { doubleValue: number }
    | { booleanValue: boolean }
    | { nullValue: null }
    | { mapValue: { fields: Record<string, FirestoreValue> } }
    | { arrayValue: { values: FirestoreValue[] } };

export class CloudStoreServiceError extends Error {
    constructor(public readonly code: string, message: string) {
        super(message);
        this.name = 'CloudStoreServiceError';
    }
}

function buildBaseUrl(): string {
    const validation = validateFirebaseProviderConfig();
    if (!validation.valid || !validation.config) {
        throw new Error(`Firebase configuration is incomplete. Missing: ${validation.missing.join(', ')}`);
    }
    return `https://firestore.googleapis.com/v1/projects/${validation.config.projectId}/databases/(default)/documents`;
}

function buildHeaders(session: SessionPayload): Record<string, string> {
    return {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${session.idToken}`,
    };
}

function toFirestoreValue(value: unknown): FirestoreValue {
    if (value === null || value === undefined) {
        return { nullValue: null };
    }
    if (typeof value === 'string') {
        return { stringValue: value };
    }
    if (typeof value === 'boolean') {
        return { booleanValue: value };
    }
    if (typeof value === 'number') {
        if (Number.isInteger(value)) {
            return { integerValue: String(value) };
        }
        return { doubleValue: value };
    }
    if (Array.isArray(value)) {
        return {
            arrayValue: {
                values: value.map((entry) => toFirestoreValue(entry)),
            },
        };
    }
    if (typeof value === 'object') {
        const fields: Record<string, FirestoreValue> = {};
        for (const [key, entry] of Object.entries(value as Record<string, unknown>)) {
            fields[key] = toFirestoreValue(entry);
        }
        return { mapValue: { fields } };
    }
    return { stringValue: String(value) };
}

function fromFirestoreValue(value: FirestoreValue | undefined): unknown {
    if (!value) {
        return null;
    }
    if ('stringValue' in value) {
        return value.stringValue;
    }
    if ('booleanValue' in value) {
        return value.booleanValue;
    }
    if ('integerValue' in value) {
        return Number.parseInt(value.integerValue, 10);
    }
    if ('doubleValue' in value) {
        return value.doubleValue;
    }
    if ('nullValue' in value) {
        return null;
    }
    if ('arrayValue' in value) {
        return (value.arrayValue.values || []).map((entry) => fromFirestoreValue(entry));
    }
    if ('mapValue' in value) {
        const result: Record<string, unknown> = {};
        for (const [key, entry] of Object.entries(value.mapValue.fields || {})) {
            result[key] = fromFirestoreValue(entry);
        }
        return result;
    }
    return null;
}

function documentToObject<T>(document: FirestoreDocument | null): T | null {
    if (!document?.fields) {
        return null;
    }
    const result: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(document.fields)) {
        result[key] = fromFirestoreValue(value);
    }
    return result as T;
}

function buildDocument<T extends object>(fields: T): { fields: Record<string, FirestoreValue> } {
    const mapped: Record<string, FirestoreValue> = {};
    for (const [key, value] of Object.entries(fields as Record<string, unknown>)) {
        mapped[key] = toFirestoreValue(value);
    }
    return { fields: mapped };
}

async function request<T>(session: SessionPayload, path: string, init?: RequestInit): Promise<T> {
    const response = await fetch(`${buildBaseUrl()}/${path}`, {
        ...init,
        headers: {
            ...buildHeaders(session),
            ...(init?.headers || {}),
        },
    });

    if (response.status === 404) {
        return null as T;
    }

    if (response.status === 401 || response.status === 403) {
        const payload = await response.text();
        throw new CloudStoreServiceError(
            'session_invalid',
            payload || 'The authenticated session is no longer valid.'
        );
    }

    if (!response.ok) {
        const payload = await response.text();
        throw new Error(payload || `Firestore request failed with ${response.status}`);
    }

    return await response.json() as T;
}

export class CloudStoreService {
    async getProfile(session: SessionPayload): Promise<AccountProfile | null> {
        const document = await request<FirestoreDocument | null>(session, `users/${session.user.uid}`);
        return documentToObject<AccountProfile>(document);
    }

    async upsertProfile(session: SessionPayload, syncEnabled: boolean): Promise<AccountProfile> {
        const existing = await this.getProfile(session);
        const timestamp = new Date().toISOString();
        const profile: AccountProfile = {
            uid: session.user.uid,
            email: session.user.email,
            displayName: session.user.displayName,
            photoURL: session.user.photoURL,
            provider: session.user.provider,
            emailVerified: session.user.emailVerified,
            syncEnabled: existing?.syncEnabled ?? syncEnabled,
            createdAt: existing?.createdAt || timestamp,
            updatedAt: timestamp,
            lastSyncedAt: existing?.lastSyncedAt ?? null,
        };

        const document = await request<FirestoreDocument>(session, `users/${session.user.uid}`, {
            method: 'PATCH',
            body: JSON.stringify(buildDocument(profile)),
        });
        return documentToObject<AccountProfile>(document) as AccountProfile;
    }

    async updateSyncEnabled(session: SessionPayload, enabled: boolean): Promise<AccountProfile> {
        const existing = await this.upsertProfile(session, enabled);
        const document = await request<FirestoreDocument>(session, `users/${session.user.uid}`, {
            method: 'PATCH',
            body: JSON.stringify(buildDocument({
                ...existing,
                syncEnabled: enabled,
                updatedAt: new Date().toISOString(),
            })),
        });
        return documentToObject<AccountProfile>(document) as AccountProfile;
    }

    async registerDevice(session: SessionPayload, metadata: DeviceMetadata): Promise<void> {
        await request<FirestoreDocument>(session, `users/${session.user.uid}/devices/${metadata.deviceId}`, {
            method: 'PATCH',
            body: JSON.stringify(buildDocument(metadata)),
        });
    }

    async getSettings(session: SessionPayload): Promise<SettingsRecord | null> {
        const document = await request<FirestoreDocument | null>(session, `users/${session.user.uid}/settings/default`);
        return documentToObject<SettingsRecord>(document);
    }

    async upsertSettings(session: SessionPayload, record: SettingsRecord): Promise<void> {
        await request<FirestoreDocument>(session, `users/${session.user.uid}/settings/default`, {
            method: 'PATCH',
            body: JSON.stringify(buildDocument(record)),
        });
    }

    async listSnippets(session: SessionPayload): Promise<SnippetRecord[]> {
        const documents = await request<{ documents?: FirestoreDocument[] } | null>(session, `users/${session.user.uid}/snippets`);
        return (documents?.documents || [])
            .map((document) => documentToObject<SnippetRecord>(document))
            .filter((record): record is SnippetRecord => Boolean(record));
    }

    async upsertSnippet(session: SessionPayload, record: SnippetRecord): Promise<void> {
        await request<FirestoreDocument>(session, `users/${session.user.uid}/snippets/${record.id}`, {
            method: 'PATCH',
            body: JSON.stringify(buildDocument(record)),
        });
    }

    async tombstoneSnippet(session: SessionPayload, id: string, metadata: SyncRecordMetadata): Promise<void> {
        await request<FirestoreDocument>(session, `users/${session.user.uid}/snippets/${id}`, {
            method: 'PATCH',
            body: JSON.stringify(buildDocument({
                id,
                trigger: '',
                content: '',
                category: '',
                metadata: {
                    ...metadata,
                    deletedAt: metadata.deletedAt || new Date().toISOString(),
                },
            })),
        });
    }

    async listDictionary(session: SessionPayload): Promise<DictionaryRecord[]> {
        const documents = await request<{ documents?: FirestoreDocument[] } | null>(session, `users/${session.user.uid}/dictionary`);
        return (documents?.documents || [])
            .map((document) => documentToObject<DictionaryRecord>(document))
            .filter((record): record is DictionaryRecord => Boolean(record));
    }

    async upsertDictionary(session: SessionPayload, record: DictionaryRecord): Promise<void> {
        await request<FirestoreDocument>(session, `users/${session.user.uid}/dictionary/${record.id}`, {
            method: 'PATCH',
            body: JSON.stringify(buildDocument(record)),
        });
    }

    async tombstoneDictionary(session: SessionPayload, id: string, metadata: SyncRecordMetadata): Promise<void> {
        await request<FirestoreDocument>(session, `users/${session.user.uid}/dictionary/${id}`, {
            method: 'PATCH',
            body: JSON.stringify(buildDocument({
                id,
                phrase: '',
                frequency: 0,
                source: 'manual',
                metadata: {
                    ...metadata,
                    deletedAt: metadata.deletedAt || new Date().toISOString(),
                },
            })),
        });
    }
}

export const cloudStoreService = new CloudStoreService();
