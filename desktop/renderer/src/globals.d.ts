import type {
  IpcResponse,
  MainWindowStateEvent,
  StateChangeEvent,
  TranscriptionUpdateEvent,
} from '@shared/ipc/index';
import type { DesktopSettings } from '@shared/settings';

interface DictationAPI {
  startDictation: () => Promise<IpcResponse>;
  stopDictation: () => Promise<IpcResponse>;
  updateSettings: (settings: any) => Promise<IpcResponse>;
  getSettings: () => Promise<IpcResponse<DesktopSettings>>;
  getHistory: () => Promise<IpcResponse<any[]>>;
  getMainWindowState: () => Promise<IpcResponse<MainWindowStateEvent>>;
  minimizeMainWindow: () => Promise<IpcResponse>;
  toggleMainWindowMaximize: () => Promise<IpcResponse>;
  closeMainWindow: () => Promise<IpcResponse>;
  closeWidgetWindow: () => Promise<IpcResponse>;
  sendAudioData: (buffer: ArrayBuffer) => void;
  onAmplitudeUpdate: (callback: (amp: number) => void) => () => void;
  onTranscriptionUpdate: (callback: (data: TranscriptionUpdateEvent) => void) => () => void;
  onStateChange: (callback: (data: StateChangeEvent) => void) => () => void;
  onHotkeyPress: (callback: () => void) => () => void;
  onMainWindowStateChange: (callback: (data: MainWindowStateEvent) => void) => () => void;
}

declare global {
  interface Window {
    dictationAPI: DictationAPI;
  }
}

export {};
