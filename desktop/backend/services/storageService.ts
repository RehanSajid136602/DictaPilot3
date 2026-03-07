import { randomUUID } from 'crypto';
import Store from 'electron-store';
import {
    type AccountProfile,
    type DeviceMetadata,
    type DictionaryRecord,
    type SettingsRecord,
    type SnippetRecord,
    type SyncQueueItem,
    type SyncRecordMetadata,
    type SyncStatus,
    type UserIdentity,
    type DesktopSettings,
    loadDesktopEnv,
} from 'dictapilot-desktop-shared';

loadDesktopEnv();

const STORAGE_VERSION = '2.0.0';
const APP_VERSION = process.env.npm_package_version || '1.0.0';
const store = new Store({ name: 'dictapilot-data' }) as Store<Record<string, unknown>>;

type PersistedSessionEnvelope = {
    encrypted: boolean;
    payload: string;
};

function nowIso(): string {
    return new Date().toISOString();
}

function toNonEmptyString(value: unknown, fallback = ''): string {
    return typeof value === 'string' && value.trim() ? value : fallback;
}

function isObject(value: unknown): value is Record<string, unknown> {
    return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function getDefaultSettings(): DesktopSettings {
    return {
        HOTKEY: 'F9',
        SMART_EDIT: '1',
        SMART_MODE: 'llm',
        LLM_ALWAYS_CLEAN: '1',
        DICTATION_MODE: 'accurate',
        GROQ_WHISPER_MODEL: 'whisper-large-v3-turbo',
        GROQ_CHAT_MODEL: 'openai/gpt-oss-120b',
        AUDIO_INPUT_DEVICE_ID: 'default',
    };
}

function normalizeSettings(settings: Record<string, unknown>): DesktopSettings {
    const normalized: DesktopSettings = {};
    for (const [key, value] of Object.entries(settings)) {
        normalized[key] = value == null ? '' : String(value);
    }
    return normalized;
}

function applySettingsToEnv(settings: DesktopSettings): void {
    for (const [key, value] of Object.entries(settings)) {
        if (value === '') {
            delete process.env[key];
            continue;
        }
        process.env[key] = value;
    }
}

function migrateLegacySettings(raw: unknown): DesktopSettings {
    const defaults = getDefaultSettings();
    if (!isObject(raw)) {
        return defaults;
    }

    const migrated = normalizeSettings(raw);
    if (migrated.hotkey && !migrated.HOTKEY) {
        migrated.HOTKEY = migrated.hotkey;
    }

    delete (migrated as Record<string, string>).hotkey;
    delete (migrated as Record<string, string>).model;
    return { ...defaults, ...migrated };
}

function getDeviceId(): string {
    const existing = toNonEmptyString(store.get('device_id', ''));
    if (existing) {
        return existing;
    }
    const next = randomUUID();
    store.set('device_id', next);
    return next;
}

function createMetadata(id: string, partial: Partial<SyncRecordMetadata> | undefined, deviceId: string): SyncRecordMetadata {
    const updatedAt = toNonEmptyString(partial?.updatedAt, nowIso());
    return {
        id: toNonEmptyString(partial?.id, id),
        updatedAt,
        deviceId: toNonEmptyString(partial?.deviceId, deviceId),
        deletedAt: partial?.deletedAt ?? null,
        version: typeof partial?.version === 'number' && Number.isFinite(partial.version) ? partial.version : 1,
        dirty: partial?.dirty ?? false,
    };
}

function ensureSettingsRecord(raw: unknown, deviceId: string): SettingsRecord {
    if (isObject(raw) && isObject(raw.values) && isObject(raw.metadata)) {
        return {
            id: 'default',
            values: normalizeSettings(raw.values),
            metadata: createMetadata('default', raw.metadata as Partial<SyncRecordMetadata>, deviceId),
        };
    }

    return {
        id: 'default',
        values: migrateLegacySettings(raw),
        metadata: createMetadata('default', undefined, deviceId),
    };
}

function ensureSnippetRecord(raw: unknown, deviceId: string): SnippetRecord | null {
    if (!isObject(raw)) {
        return null;
    }

    const id = toNonEmptyString(raw.id, randomUUID());
    const trigger = toNonEmptyString(raw.trigger);
    const content = toNonEmptyString(raw.content);
    if (!trigger || !content) {
        return null;
    }

    return {
        id,
        trigger,
        content,
        category: toNonEmptyString(raw.category, ''),
        metadata: createMetadata(id, isObject(raw.metadata) ? raw.metadata as Partial<SyncRecordMetadata> : undefined, deviceId),
    };
}

function ensureDictionaryRecord(raw: unknown, deviceId: string): DictionaryRecord | null {
    if (!isObject(raw)) {
        return null;
    }

    const id = toNonEmptyString(raw.id, randomUUID());
    const phrase = toNonEmptyString(raw.phrase || raw.word);
    if (!phrase) {
        return null;
    }

    return {
        id,
        phrase,
        frequency: typeof raw.frequency === 'number' && Number.isFinite(raw.frequency) ? raw.frequency : 1,
        source: raw.source === 'auto' ? 'auto' : 'manual',
        metadata: createMetadata(id, isObject(raw.metadata) ? raw.metadata as Partial<SyncRecordMetadata> : undefined, deviceId),
    };
}

function ensureSyncQueueItem(raw: unknown, deviceId: string): SyncQueueItem | null {
    if (!isObject(raw)) {
        return null;
    }

    const id = toNonEmptyString(raw.id, randomUUID());
    const domain = raw.domain === 'dictionary' || raw.domain === 'snippets' ? raw.domain : 'settings';
    const operation = raw.operation === 'delete' ? 'delete' : 'upsert';
    const recordId = toNonEmptyString(raw.recordId, id);

    return {
        id,
        domain,
        operation,
        recordId,
        payload: raw.payload,
        attempts: typeof raw.attempts === 'number' && Number.isFinite(raw.attempts) ? raw.attempts : 0,
        nextAttemptAt: toNonEmptyString(raw.nextAttemptAt, '') || null,
        errorMessage: toNonEmptyString(raw.errorMessage, '') || null,
        metadata: createMetadata(recordId, isObject(raw.metadata) ? raw.metadata as Partial<SyncRecordMetadata> : undefined, deviceId),
    };
}

function migrateStore(): void {
    const currentVersion = toNonEmptyString(store.get('schema_version', '0.0.0'));
    const deviceId = getDeviceId();

    const settingsRecord = ensureSettingsRecord(store.get('settings'), deviceId);
    store.set('settings', settingsRecord);
    applySettingsToEnv(settingsRecord.values);

    const snippets = (store.get('snippets', []) as unknown[])
        .map((item) => ensureSnippetRecord(item, deviceId))
        .filter((item): item is SnippetRecord => Boolean(item));
    store.set('snippets', snippets);

    const dictionary = (store.get('dictionary', []) as unknown[])
        .map((item) => ensureDictionaryRecord(item, deviceId))
        .filter((item): item is DictionaryRecord => Boolean(item));
    store.set('dictionary', dictionary);

    const syncQueue = (store.get('sync_queue', []) as unknown[])
        .map((item) => ensureSyncQueueItem(item, deviceId))
        .filter((item): item is SyncQueueItem => Boolean(item));
    store.set('sync_queue', syncQueue);

    if (currentVersion !== STORAGE_VERSION) {
        console.log(`Migrating storage from ${currentVersion} to ${STORAGE_VERSION}`);
        store.set('schema_version', STORAGE_VERSION);
    }
}

migrateStore();

export class HistoryService {
    saveResult(text: string): void {
        const history = store.get('history', []) as Array<{ id: string; text: string; timestamp: string }>;
        history.unshift({
            id: randomUUID(),
            text,
            timestamp: nowIso(),
        });
        store.set('history', history.slice(0, 100));
    }

    getHistory(): Array<{ id: string; text: string; timestamp: string }> {
        return (store.get('history', []) as Array<{ id: string; text: string; timestamp: string }>).slice();
    }
}

export class DeviceService {
    getDeviceId(): string {
        return getDeviceId();
    }

    getDeviceMetadata(): DeviceMetadata {
        return {
            deviceId: getDeviceId(),
            platform: process.platform,
            appVersion: APP_VERSION,
            lastSeenAt: nowIso(),
        };
    }
}

export class SettingsService {
    getSettingsRecord(): SettingsRecord {
        return ensureSettingsRecord(store.get('settings'), getDeviceId());
    }

    getSettings(): DesktopSettings {
        const record = this.getSettingsRecord();
        applySettingsToEnv(record.values);
        return { ...record.values };
    }

    replaceSettingsRecord(record: SettingsRecord): SettingsRecord {
        const next: SettingsRecord = {
            id: 'default',
            values: normalizeSettings(record.values),
            metadata: createMetadata('default', {
                ...record.metadata,
                dirty: record.metadata?.dirty ?? false,
            }, getDeviceId()),
        };
        store.set('settings', next);
        applySettingsToEnv(next.values);
        return next;
    }

    updateSettings(settings: Partial<DesktopSettings>): SettingsRecord {
        const current = this.getSettingsRecord();
        const nextValues = normalizeSettings({ ...current.values, ...settings });
        const next: SettingsRecord = {
            id: 'default',
            values: nextValues,
            metadata: createMetadata('default', {
                ...current.metadata,
                updatedAt: nowIso(),
                version: current.metadata.version + 1,
                dirty: true,
            }, getDeviceId()),
        };
        store.set('settings', next);
        applySettingsToEnv(next.values);
        return next;
    }
}

export class AccountProfileService {
    getProfile(): AccountProfile | null {
        const raw = store.get('account_profile', null);
        return isObject(raw) ? raw as unknown as AccountProfile : null;
    }

    setProfile(profile: AccountProfile | null): void {
        if (!profile) {
            store.delete('account_profile');
            return;
        }
        store.set('account_profile', profile);
    }

    clearProfile(): void {
        store.delete('account_profile');
    }

    updateSync(enabled: boolean, status: SyncStatus, lastSyncedAt?: string | null): AccountProfile | null {
        const current = this.getProfile();
        if (!current) {
            return null;
        }

        const next: AccountProfile = {
            ...current,
            syncEnabled: enabled,
            updatedAt: nowIso(),
            lastSyncedAt: lastSyncedAt ?? current.lastSyncedAt ?? null,
        };
        this.setProfile(next);
        store.set('account_sync_status', status);
        return next;
    }
}

export class SnippetService {
    getSnippets(includeDeleted = false): SnippetRecord[] {
        const records = (store.get('snippets', []) as unknown[])
            .map((item) => ensureSnippetRecord(item, getDeviceId()))
            .filter((item): item is SnippetRecord => Boolean(item));
        return includeDeleted ? records : records.filter((item) => !item.metadata.deletedAt);
    }

    replaceAll(records: SnippetRecord[]): void {
        store.set('snippets', records.map((record) => ({
            ...record,
            metadata: { ...record.metadata, dirty: false },
        })));
    }

    upsert(record: Omit<SnippetRecord, 'metadata'> & { metadata?: Partial<SyncRecordMetadata> }): SnippetRecord {
        const current = this.getSnippets(true);
        const existing = current.find((item) => item.id === record.id);
        const next: SnippetRecord = {
            id: record.id,
            trigger: record.trigger,
            content: record.content,
            category: record.category,
            metadata: createMetadata(record.id, {
                ...existing?.metadata,
                ...record.metadata,
                deletedAt: null,
                updatedAt: nowIso(),
                version: (existing?.metadata.version || 0) + 1,
                dirty: true,
            }, getDeviceId()),
        };
        const remaining = current.filter((item) => item.id !== record.id);
        remaining.unshift(next);
        store.set('snippets', remaining);
        return next;
    }

    tombstone(id: string): SnippetRecord | null {
        const current = this.getSnippets(true);
        const existing = current.find((item) => item.id === id);
        if (!existing) {
            return null;
        }
        const next: SnippetRecord = {
            ...existing,
            metadata: {
                ...existing.metadata,
                deletedAt: nowIso(),
                updatedAt: nowIso(),
                version: existing.metadata.version + 1,
                dirty: true,
            },
        };
        const remaining = current.filter((item) => item.id !== id);
        remaining.unshift(next);
        store.set('snippets', remaining);
        return next;
    }
}

export class DictionaryService {
    getEntries(includeDeleted = false): DictionaryRecord[] {
        const records = (store.get('dictionary', []) as unknown[])
            .map((item) => ensureDictionaryRecord(item, getDeviceId()))
            .filter((item): item is DictionaryRecord => Boolean(item));
        return includeDeleted ? records : records.filter((item) => !item.metadata.deletedAt);
    }

    replaceAll(records: DictionaryRecord[]): void {
        store.set('dictionary', records.map((record) => ({
            ...record,
            metadata: { ...record.metadata, dirty: false },
        })));
    }

    upsert(record: Omit<DictionaryRecord, 'metadata'> & { metadata?: Partial<SyncRecordMetadata> }): DictionaryRecord {
        const current = this.getEntries(true);
        const existing = current.find((item) => item.id === record.id);
        const next: DictionaryRecord = {
            id: record.id,
            phrase: record.phrase,
            frequency: record.frequency,
            source: record.source,
            metadata: createMetadata(record.id, {
                ...existing?.metadata,
                ...record.metadata,
                deletedAt: null,
                updatedAt: nowIso(),
                version: (existing?.metadata.version || 0) + 1,
                dirty: true,
            }, getDeviceId()),
        };
        const remaining = current.filter((item) => item.id !== record.id);
        remaining.unshift(next);
        store.set('dictionary', remaining);
        return next;
    }

    tombstone(id: string): DictionaryRecord | null {
        const current = this.getEntries(true);
        const existing = current.find((item) => item.id === id);
        if (!existing) {
            return null;
        }
        const next: DictionaryRecord = {
            ...existing,
            metadata: {
                ...existing.metadata,
                deletedAt: nowIso(),
                updatedAt: nowIso(),
                version: existing.metadata.version + 1,
                dirty: true,
            },
        };
        const remaining = current.filter((item) => item.id !== id);
        remaining.unshift(next);
        store.set('dictionary', remaining);
        return next;
    }
}

export class SyncQueueStoreService {
    getItems(): SyncQueueItem[] {
        return (store.get('sync_queue', []) as unknown[])
            .map((item) => ensureSyncQueueItem(item, getDeviceId()))
            .filter((item): item is SyncQueueItem => Boolean(item));
    }

    getPendingCount(): number {
        return this.getItems().length;
    }

    upsert(item: SyncQueueItem): void {
        const current = this.getItems().filter((entry) => (
            entry.id !== item.id &&
            !(entry.domain === item.domain && entry.recordId === item.recordId)
        ));
        current.push(item);
        store.set('sync_queue', current);
    }

    remove(id: string): void {
        store.set('sync_queue', this.getItems().filter((item) => item.id !== id));
    }

    clear(): void {
        store.set('sync_queue', []);
    }
}

export class SessionStoreService {
    getEnvelope(): PersistedSessionEnvelope | null {
        const raw = store.get('auth_session', null);
        return isObject(raw) ? raw as PersistedSessionEnvelope : null;
    }

    setEnvelope(envelope: PersistedSessionEnvelope | null): void {
        if (!envelope) {
            store.delete('auth_session');
            return;
        }
        store.set('auth_session', envelope);
    }
}

export function createQueueItem(
    domain: SyncQueueItem['domain'],
    operation: SyncQueueItem['operation'],
    recordId: string,
    payload: unknown,
    metadata?: Partial<SyncRecordMetadata>,
): SyncQueueItem {
    const deviceId = getDeviceId();
    const id = randomUUID();
    return {
        id,
        domain,
        operation,
        recordId,
        payload,
        attempts: 0,
        nextAttemptAt: null,
        errorMessage: null,
        metadata: createMetadata(recordId, {
            ...metadata,
            dirty: true,
        }, deviceId),
    };
}

export const historyService = new HistoryService();
export const deviceService = new DeviceService();
export const settingsService = new SettingsService();
export const accountProfileService = new AccountProfileService();
export const snippetService = new SnippetService();
export const dictionaryService = new DictionaryService();
export const syncQueueStoreService = new SyncQueueStoreService();
export const sessionStoreService = new SessionStoreService();
