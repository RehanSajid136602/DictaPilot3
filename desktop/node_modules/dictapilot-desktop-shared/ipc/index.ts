import type { AuthState, SignInPayload, SignUpPayload, SyncPreferences, SyncStatusEvent } from '../auth';

export type DictationState = 'idle' | 'recording' | 'processing' | 'error';

// Standardized IPC Response Wrapper
export interface IpcResponse<T = void> {
    success: boolean;
    data?: T;
    error?: IpcError;
}

// Structured error model
export interface IpcError {
    code: string;
    message: string;
    details?: Record<string, any>;
}

// Event payloads
export interface AudioInputDeviceInfo {
    deviceId: string;
    label: string;
    isDefault: boolean;
    unavailable?: boolean;
}

export interface TranscriptionUpdateEvent {
    text: string;
    isFinal: boolean;
    sessionId?: string | null;
}

export interface StateChangeEvent {
    state: DictationState;
    sessionId?: string | null;
}

export interface DictationSessionEvent {
    sessionId: string;
}

export interface MainWindowStateEvent {
    isMaximized: boolean;
}

// Channels
export const Channels = {
    StartDictation: 'dictation:start',
    StopDictation: 'dictation:stop',
    UpdateSettings: 'settings:update',
    GetSettings: 'settings:get',
    GetHistory: 'history:get',
    GetSelectedAudioInput: 'audio-input:get-selected',
    SetSelectedAudioInput: 'audio-input:set-selected',
    SignUp: 'auth:sign-up',
    SignIn: 'auth:sign-in',
    SignInWithGoogle: 'auth:sign-in-with-google',
    SignOut: 'auth:sign-out',
    GetAuthState: 'auth:get-state',
    UpdateSyncPreferences: 'sync:update-preferences',
    GetMainWindowState: 'window:main:get-state',
    MinimizeMainWindow: 'window:main:minimize',
    ToggleMainWindowMaximize: 'window:main:toggle-maximize',
    CloseMainWindow: 'window:main:close',
    CloseWidgetWindow: 'window:widget:close',
    SendAudioData: 'dictation:audio-data',

    // Events sent main -> renderer
    OnTranscriptionUpdate: 'dictation:on-transcription-update',
    OnStateChange: 'dictation:on-state-change',
    OnHotkeyPress: 'hotkey-pressed',
    OnAmplitudeUpdate: 'dictation:on-amplitude-update',
    OnAuthStateChange: 'auth:on-state-change',
    OnSyncStatusChange: 'sync:on-status-change',
    OnMainWindowStateChange: 'window:main:on-state-change',
    OnAudioDevicesChanged: 'audio-input:on-devices-changed'
} as const;

export type AuthStateResponse = IpcResponse<AuthState>;
export type DictationSessionResponse = IpcResponse<DictationSessionEvent>;
export type SignInRequest = SignInPayload;
export type SignUpRequest = SignUpPayload;
export type SyncPreferencesUpdateRequest = Pick<SyncPreferences, 'enabled'>;
export type SyncStatusResponse = IpcResponse<SyncStatusEvent>;
export type AudioInputPreferenceResponse = IpcResponse<string>;
