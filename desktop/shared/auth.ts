export type AuthProvider = 'password' | 'google';

export type AuthStatus = 'signed_out' | 'authenticated' | 'loading' | 'error';

export type SyncStatus = 'disabled' | 'idle' | 'syncing' | 'offline' | 'error';

export type SyncDomain = 'settings' | 'snippets' | 'dictionary';

export interface UserIdentity {
    uid: string;
    email: string;
    displayName?: string;
    photoURL?: string;
    provider: AuthProvider;
    emailVerified: boolean;
}

export interface SyncPreferences {
    enabled: boolean;
    status: SyncStatus;
    pendingOperations: number;
    lastSyncedAt?: string | null;
    errorMessage?: string | null;
}

export interface AuthState {
    status: AuthStatus;
    user: UserIdentity | null;
    sync: SyncPreferences;
    errorMessage?: string | null;
}

export interface SignUpPayload {
    email: string;
    password: string;
    confirmPassword: string;
    displayName?: string;
}

export interface SignInPayload {
    email: string;
    password: string;
}

export interface AccountProfile extends UserIdentity {
    syncEnabled: boolean;
    createdAt: string;
    updatedAt: string;
    lastSyncedAt?: string | null;
}

export interface SessionPayload {
    idToken: string;
    refreshToken: string;
    expiresAt: string;
    issuedAt: string;
    user: UserIdentity;
}

export interface DeviceMetadata {
    deviceId: string;
    platform: string;
    appVersion: string;
    lastSeenAt: string;
}

export interface SyncRecordMetadata {
    id: string;
    updatedAt: string;
    deviceId: string;
    deletedAt?: string | null;
    version: number;
    dirty?: boolean;
}

export interface SettingsRecord {
    id: 'default';
    values: Record<string, string>;
    metadata: SyncRecordMetadata;
}

export interface SnippetRecord {
    id: string;
    trigger: string;
    content: string;
    category?: string;
    metadata: SyncRecordMetadata;
}

export interface DictionaryRecord {
    id: string;
    phrase: string;
    frequency: number;
    source: 'manual' | 'auto';
    metadata: SyncRecordMetadata;
}

export interface SyncQueueItem {
    id: string;
    domain: SyncDomain;
    operation: 'upsert' | 'delete';
    recordId: string;
    payload?: unknown;
    attempts: number;
    nextAttemptAt?: string | null;
    errorMessage?: string | null;
    metadata: SyncRecordMetadata;
}

export interface SyncStatusEvent extends SyncPreferences {}

export const DEFAULT_SYNC_PREFERENCES: SyncPreferences = {
    enabled: false,
    status: 'disabled',
    pendingOperations: 0,
    lastSyncedAt: null,
    errorMessage: null,
};

export const SIGNED_OUT_AUTH_STATE: AuthState = {
    status: 'signed_out',
    user: null,
    sync: DEFAULT_SYNC_PREFERENCES,
    errorMessage: null,
};
