import {
    type DictionaryRecord,
    type SessionPayload,
    type SettingsRecord,
    type SnippetRecord,
    type SyncPreferences,
    type SyncQueueItem,
    type SyncRecordMetadata,
} from 'dictapilot-desktop-shared';
import { cloudStoreService } from './cloudStoreService';
import { dictionaryRepository, settingsRepository, snippetRepository } from './localRepositoryService';
import { accountProfileService, syncQueueStoreService } from './storageService';

function toMillis(value?: string | null): number {
    return value ? new Date(value).getTime() : 0;
}

function nextBackoff(attempts: number): string {
    const delay = Math.min(300_000, Math.max(5_000, 5_000 * 2 ** attempts));
    return new Date(Date.now() + delay).toISOString();
}

export function chooseWinningMetadata(local: SyncRecordMetadata, remote: SyncRecordMetadata): SyncRecordMetadata {
    const localTime = toMillis(local.updatedAt);
    const remoteTime = toMillis(remote.updatedAt);
    if (remoteTime > localTime) {
        return remote;
    }
    if (localTime > remoteTime) {
        return local;
    }
    return remote.version >= local.version ? remote : local;
}

function chooseWinningRecord<T extends { metadata: SyncRecordMetadata }>(local: T | null, remote: T | null): T | null {
    if (!local) {
        return remote;
    }
    if (!remote) {
        return local;
    }
    return chooseWinningMetadata(local.metadata, remote.metadata) === remote.metadata ? remote : local;
}

export class SyncQueueService {
    private processing = false;

    getStatus(enabled: boolean, errorMessage?: string | null, statusOverride?: SyncPreferences['status']): SyncPreferences {
        const profile = accountProfileService.getProfile();
        return {
            enabled,
            status: statusOverride || (enabled ? 'idle' : 'disabled'),
            pendingOperations: syncQueueStoreService.getPendingCount(),
            lastSyncedAt: profile?.lastSyncedAt ?? null,
            errorMessage: errorMessage ?? null,
        };
    }

    private async applyItem(session: SessionPayload, item: SyncQueueItem): Promise<void> {
        switch (item.domain) {
            case 'settings':
                if (item.operation === 'upsert' && item.payload) {
                    await cloudStoreService.upsertSettings(session, item.payload as SettingsRecord);
                }
                break;
            case 'snippets':
                if (item.operation === 'delete') {
                    await cloudStoreService.tombstoneSnippet(session, item.recordId, item.metadata);
                } else if (item.payload) {
                    await cloudStoreService.upsertSnippet(session, item.payload as SnippetRecord);
                }
                break;
            case 'dictionary':
                if (item.operation === 'delete') {
                    await cloudStoreService.tombstoneDictionary(session, item.recordId, item.metadata);
                } else if (item.payload) {
                    await cloudStoreService.upsertDictionary(session, item.payload as DictionaryRecord);
                }
                break;
            default:
                break;
        }
    }

    async syncNow(session: SessionPayload): Promise<SyncPreferences> {
        if (this.processing) {
            return this.getStatus(true, null, 'syncing');
        }

        this.processing = true;
        let status: SyncPreferences['status'] = 'syncing';
        let errorMessage: string | null = null;

        try {
            const queue = syncQueueStoreService.getItems().filter((item) => !item.nextAttemptAt || toMillis(item.nextAttemptAt) <= Date.now());
            for (const item of queue) {
                try {
                    await this.applyItem(session, item);
                    syncQueueStoreService.remove(item.id);
                } catch (error) {
                    syncQueueStoreService.upsert({
                        ...item,
                        attempts: item.attempts + 1,
                        nextAttemptAt: nextBackoff(item.attempts + 1),
                        errorMessage: error instanceof Error ? error.message : 'sync_failed',
                    });
                    status = 'error';
                    errorMessage = error instanceof Error ? error.message : 'Sync failed.';
                }
            }
        } finally {
            this.processing = false;
        }

        return this.getStatus(true, errorMessage, status === 'syncing' ? 'idle' : status);
    }

    async hydrateFromCloud(session: SessionPayload): Promise<void> {
        const remoteSettings = await cloudStoreService.getSettings(session);
        const localSettings = settingsRepository.getLocal();
        const winningSettings = chooseWinningRecord(localSettings, remoteSettings);
        if (winningSettings && winningSettings === remoteSettings) {
            settingsRepository.applyRemote({ ...winningSettings, metadata: { ...winningSettings.metadata, dirty: false } });
        }

        const remoteSnippets = await cloudStoreService.listSnippets(session);
        const localSnippets = snippetRepository.listLocal(true);
        const snippetMap = new Map<string, SnippetRecord>();
        for (const record of [...localSnippets, ...remoteSnippets]) {
            const existing = snippetMap.get(record.id) || null;
            const winner = chooseWinningRecord(existing, record);
            if (winner) {
                snippetMap.set(record.id, { ...winner, metadata: { ...winner.metadata, dirty: false } });
            }
        }
        snippetRepository.replaceAll([...snippetMap.values()]);

        const remoteDictionary = await cloudStoreService.listDictionary(session);
        const localDictionary = dictionaryRepository.listLocal(true);
        const dictionaryMap = new Map<string, DictionaryRecord>();
        for (const record of [...localDictionary, ...remoteDictionary]) {
            const existing = dictionaryMap.get(record.id) || null;
            const winner = chooseWinningRecord(existing, record);
            if (winner) {
                dictionaryMap.set(record.id, { ...winner, metadata: { ...winner.metadata, dirty: false } });
            }
        }
        dictionaryRepository.replaceAll([...dictionaryMap.values()]);
    }
}

export const syncQueueService = new SyncQueueService();
