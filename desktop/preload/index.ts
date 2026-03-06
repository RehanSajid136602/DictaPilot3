import { contextBridge, ipcRenderer } from 'electron';
import { Channels, IpcResponse, TranscriptionUpdateEvent, StateChangeEvent } from 'dictapilot-desktop-shared';

const dictationAPI = {
    startDictation: (): Promise<IpcResponse> => ipcRenderer.invoke(Channels.StartDictation),
    stopDictation: (): Promise<IpcResponse> => ipcRenderer.invoke(Channels.StopDictation),
    updateSettings: (settings: any): Promise<IpcResponse> => ipcRenderer.invoke(Channels.UpdateSettings, settings),
    getSettings: (): Promise<IpcResponse> => ipcRenderer.invoke(Channels.GetSettings),
    getHistory: (): Promise<IpcResponse> => ipcRenderer.invoke(Channels.GetHistory),
    
    sendAudioData: (buffer: ArrayBuffer) => ipcRenderer.send(Channels.SendAudioData, buffer),

    onAmplitudeUpdate: (callback: (amp: number) => void) => {
        const sub = (_: any, amp: number) => callback(amp);
        ipcRenderer.on(Channels.OnAmplitudeUpdate, sub);
        return () => ipcRenderer.removeListener(Channels.OnAmplitudeUpdate, sub);
    },

    onTranscriptionUpdate: (callback: (data: TranscriptionUpdateEvent) => void) => {
        const sub = (_: any, data: TranscriptionUpdateEvent) => callback(data);
        ipcRenderer.on(Channels.OnTranscriptionUpdate, sub);
        return () => ipcRenderer.removeListener(Channels.OnTranscriptionUpdate, sub);
    },

    onStateChange: (callback: (data: StateChangeEvent) => void) => {
        const sub = (_: any, data: StateChangeEvent) => callback(data);
        ipcRenderer.on(Channels.OnStateChange, sub);
        return () => ipcRenderer.removeListener(Channels.OnStateChange, sub);
    },

    onHotkeyPress: (callback: () => void) => {
        const sub = () => callback();
        ipcRenderer.on(Channels.OnHotkeyPress, sub);
        return () => ipcRenderer.removeListener(Channels.OnHotkeyPress, sub);
    }
};

contextBridge.exposeInMainWorld('dictationAPI', dictationAPI);

declare global {
    interface Window {
        dictationAPI: typeof dictationAPI;
    }
}
