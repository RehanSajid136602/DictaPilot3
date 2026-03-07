import { contextBridge, ipcRenderer } from 'electron';
import type {
    AudioInputDeviceInfo,
    AuthState,
    DictationSessionEvent,
    SignInPayload,
    SignUpPayload,
    SyncStatusEvent,
} from 'dictapilot-desktop-shared';
import {
    Channels,
    type IpcResponse,
    type MainWindowStateEvent,
    type StateChangeEvent,
    type TranscriptionUpdateEvent,
} from 'dictapilot-desktop-shared';

async function enumerateAudioInputDevices(requestPermission = false): Promise<AudioInputDeviceInfo[]> {
    if (!navigator.mediaDevices?.enumerateDevices) {
        return [];
    }

    if (requestPermission && navigator.mediaDevices.getUserMedia) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            stream.getTracks().forEach((track) => track.stop());
        } catch {
            // Ignore permission failures here; the caller will handle missing labels/devices.
        }
    }

    const devices = await navigator.mediaDevices.enumerateDevices();
    const audioInputs = devices.filter((device) => device.kind === 'audioinput');
    return [
        {
            deviceId: 'default',
            label: 'System default microphone',
            isDefault: true,
        },
        ...audioInputs.map((device, index) => ({
            deviceId: device.deviceId,
            label: device.label || `Microphone ${index + 1}`,
            isDefault: false,
        })),
    ];
}

const dictationAPI = {
    startDictation: (): Promise<IpcResponse<DictationSessionEvent>> => ipcRenderer.invoke(Channels.StartDictation),
    stopDictation: (): Promise<IpcResponse> => ipcRenderer.invoke(Channels.StopDictation),
    updateSettings: (settings: Record<string, string>): Promise<IpcResponse<Record<string, string>>> => ipcRenderer.invoke(Channels.UpdateSettings, settings),
    getSettings: (): Promise<IpcResponse<Record<string, string>>> => ipcRenderer.invoke(Channels.GetSettings),
    getHistory: (): Promise<IpcResponse<Array<{ id: string; text: string; timestamp: string }>>> => ipcRenderer.invoke(Channels.GetHistory),
    getAudioInputDevices: async (requestPermission = false): Promise<IpcResponse<AudioInputDeviceInfo[]>> => ({
        success: true,
        data: await enumerateAudioInputDevices(requestPermission),
    }),
    getSelectedAudioInput: (): Promise<IpcResponse<string>> => ipcRenderer.invoke(Channels.GetSelectedAudioInput),
    setSelectedAudioInput: (deviceId: string): Promise<IpcResponse<string>> => ipcRenderer.invoke(Channels.SetSelectedAudioInput, deviceId),
    signUp: (payload: SignUpPayload): Promise<IpcResponse<AuthState>> => ipcRenderer.invoke(Channels.SignUp, payload),
    signIn: (payload: SignInPayload): Promise<IpcResponse<AuthState>> => ipcRenderer.invoke(Channels.SignIn, payload),
    signInWithGoogle: (): Promise<IpcResponse<AuthState>> => ipcRenderer.invoke(Channels.SignInWithGoogle),
    signOut: (): Promise<IpcResponse<AuthState>> => ipcRenderer.invoke(Channels.SignOut),
    getAuthState: (): Promise<IpcResponse<AuthState>> => ipcRenderer.invoke(Channels.GetAuthState),
    updateSyncPreferences: (payload: { enabled: boolean }): Promise<IpcResponse<AuthState>> => ipcRenderer.invoke(Channels.UpdateSyncPreferences, payload),
    getMainWindowState: (): Promise<IpcResponse<MainWindowStateEvent>> => ipcRenderer.invoke(Channels.GetMainWindowState),
    minimizeMainWindow: (): Promise<IpcResponse> => ipcRenderer.invoke(Channels.MinimizeMainWindow),
    toggleMainWindowMaximize: (): Promise<IpcResponse> => ipcRenderer.invoke(Channels.ToggleMainWindowMaximize),
    closeMainWindow: (): Promise<IpcResponse> => ipcRenderer.invoke(Channels.CloseMainWindow),
    closeWidgetWindow: (): Promise<IpcResponse> => ipcRenderer.invoke(Channels.CloseWidgetWindow),
    sendAudioData: (sessionId: string, buffer: ArrayBuffer) => ipcRenderer.send(Channels.SendAudioData, { sessionId, buffer }),

    onAmplitudeUpdate: (callback: (amp: number) => void) => {
        const sub = (_event: Electron.IpcRendererEvent, amp: number) => callback(amp);
        ipcRenderer.on(Channels.OnAmplitudeUpdate, sub);
        return () => ipcRenderer.removeListener(Channels.OnAmplitudeUpdate, sub);
    },

    onTranscriptionUpdate: (callback: (data: TranscriptionUpdateEvent) => void) => {
        const sub = (_event: Electron.IpcRendererEvent, data: TranscriptionUpdateEvent) => callback(data);
        ipcRenderer.on(Channels.OnTranscriptionUpdate, sub);
        return () => ipcRenderer.removeListener(Channels.OnTranscriptionUpdate, sub);
    },

    onStateChange: (callback: (data: StateChangeEvent) => void) => {
        const sub = (_event: Electron.IpcRendererEvent, data: StateChangeEvent) => callback(data);
        ipcRenderer.on(Channels.OnStateChange, sub);
        return () => ipcRenderer.removeListener(Channels.OnStateChange, sub);
    },

    onHotkeyPress: (callback: () => void) => {
        const sub = () => callback();
        ipcRenderer.on(Channels.OnHotkeyPress, sub);
        return () => ipcRenderer.removeListener(Channels.OnHotkeyPress, sub);
    },

    onAuthStateChange: (callback: (state: AuthState) => void) => {
        const sub = (_event: Electron.IpcRendererEvent, state: AuthState) => callback(state);
        ipcRenderer.on(Channels.OnAuthStateChange, sub);
        return () => ipcRenderer.removeListener(Channels.OnAuthStateChange, sub);
    },

    onSyncStatusChange: (callback: (status: SyncStatusEvent) => void) => {
        const sub = (_event: Electron.IpcRendererEvent, status: SyncStatusEvent) => callback(status);
        ipcRenderer.on(Channels.OnSyncStatusChange, sub);
        return () => ipcRenderer.removeListener(Channels.OnSyncStatusChange, sub);
    },

    onMainWindowStateChange: (callback: (data: MainWindowStateEvent) => void) => {
        const sub = (_event: Electron.IpcRendererEvent, data: MainWindowStateEvent) => callback(data);
        ipcRenderer.on(Channels.OnMainWindowStateChange, sub);
        return () => ipcRenderer.removeListener(Channels.OnMainWindowStateChange, sub);
    },

    onAudioDevicesChanged: (callback: () => void) => {
        if (!navigator.mediaDevices?.addEventListener) {
            return () => {};
        }
        const handler = () => callback();
        navigator.mediaDevices.addEventListener('devicechange', handler);
        return () => navigator.mediaDevices.removeEventListener('devicechange', handler);
    },
};

contextBridge.exposeInMainWorld('dictationAPI', dictationAPI);
