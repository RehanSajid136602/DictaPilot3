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
export interface TranscriptionUpdateEvent {
    text: string;
    isFinal: boolean;
}

export interface StateChangeEvent {
    state: DictationState;
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
    OnMainWindowStateChange: 'window:main:on-state-change'
} as const;
