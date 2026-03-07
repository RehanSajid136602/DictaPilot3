import type { DictionaryRecord, SettingsRecord, SnippetRecord } from 'dictapilot-desktop-shared';
import {
    accountProfileService,
    createQueueItem,
    dictionaryService,
    settingsService,
    snippetService,
    syncQueueStoreService,
} from './storageService';
import { authService } from './authService';

function shouldQueueSync(): boolean {
    const profile = accountProfileService.getProfile();
    return Boolean(authService.getCurrentSession() && profile?.syncEnabled);
}

function queueIfNeeded(item: ReturnType<typeof createQueueItem>): void {
    if (!shouldQueueSync()) {
        return;
    }
    syncQueueStoreService.upsert(item);
}

export const settingsRepository = {
    getLocal(): SettingsRecord {
        return settingsService.getSettingsRecord();
    },
    updateLocal(values: Partial<Record<string, string>>): SettingsRecord {
        const record = settingsService.updateSettings(values);
        queueIfNeeded(createQueueItem('settings', 'upsert', record.id, record, record.metadata));
        return record;
    },
    applyRemote(record: SettingsRecord): SettingsRecord {
        return settingsService.replaceSettingsRecord({
            ...record,
            metadata: { ...record.metadata, dirty: false },
        });
    },
};

export const snippetRepository = {
    listLocal(includeDeleted = false): SnippetRecord[] {
        return snippetService.getSnippets(includeDeleted);
    },
    upsertLocal(record: Omit<SnippetRecord, 'metadata'> & { metadata?: Partial<SnippetRecord['metadata']> }): SnippetRecord {
        const next = snippetService.upsert(record);
        queueIfNeeded(createQueueItem('snippets', 'upsert', next.id, next, next.metadata));
        return next;
    },
    deleteLocal(id: string): SnippetRecord | null {
        const next = snippetService.tombstone(id);
        if (next) {
            queueIfNeeded(createQueueItem('snippets', 'delete', id, null, next.metadata));
        }
        return next;
    },
    replaceAll(records: SnippetRecord[]): void {
        snippetService.replaceAll(records);
    },
};

export const dictionaryRepository = {
    listLocal(includeDeleted = false): DictionaryRecord[] {
        return dictionaryService.getEntries(includeDeleted);
    },
    upsertLocal(record: Omit<DictionaryRecord, 'metadata'> & { metadata?: Partial<DictionaryRecord['metadata']> }): DictionaryRecord {
        const next = dictionaryService.upsert(record);
        queueIfNeeded(createQueueItem('dictionary', 'upsert', next.id, next, next.metadata));
        return next;
    },
    deleteLocal(id: string): DictionaryRecord | null {
        const next = dictionaryService.tombstone(id);
        if (next) {
            queueIfNeeded(createQueueItem('dictionary', 'delete', id, null, next.metadata));
        }
        return next;
    },
    replaceAll(records: DictionaryRecord[]): void {
        dictionaryService.replaceAll(records);
    },
};
