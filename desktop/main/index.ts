import { app, BrowserWindow, Menu, Tray, nativeImage, ipcMain, globalShortcut, screen, session, clipboard } from 'electron';
import * as path from 'path';
import { Channels, IpcResponse, loadDesktopEnv } from 'dictapilot-desktop-shared';
import { audioService, transcriptionService, settingsService, historyService, editingService, GroqProvider, SmartEditResult } from 'dictapilot-desktop-backend';
import { keyboard, Key } from '@nut-tree-fork/nut-js';
import Store from 'electron-store';
import { GlobalKeyboardListener } from 'node-global-key-listener';

loadDesktopEnv();
app.disableHardwareAcceleration();

const store = new Store() as any;
let mainWindow: BrowserWindow | null = null;
let widgetWindow: BrowserWindow | null = null;
let tray: Tray | null = null;

let keyListener: GlobalKeyboardListener | null = null;
let currentHotkey = 'F9';
let isRecording = false;
let isQuitting = false;
let appliedTranscript = '';

function configureRuntimeSettings() {
    const settings = settingsService.getSettings();
    currentHotkey = (settings.HOTKEY || 'F9').toUpperCase();

    const groqApiKey = settings.GROQ_API_KEY || process.env.GROQ_API_KEY || '';
    if (groqApiKey) {
        const groqProvider = new GroqProvider(groqApiKey);
        transcriptionService.setProvider(groqProvider);
    } else {
        transcriptionService.clearProvider();
        console.warn('GROQ_API_KEY not found. Dictation will fall back until a key is available.');
    }
}

configureRuntimeSettings();

// Ensure single instance
const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) {
    app.quit();
}

function safeSend(window: BrowserWindow | null, channel: string, ...args: any[]) {
    if (window && !window.isDestroyed() && window.webContents) {
        window.webContents.send(channel, ...args);
    }
}

function broadcastMainWindowState() {
    safeSend(mainWindow, Channels.OnMainWindowStateChange, {
        isMaximized: mainWindow?.isMaximized() ?? false
    });
}

function normalizeWindowBounds(bounds: { width: number; height: number; x?: number; y?: number }) {
    const displays = screen.getAllDisplays();
    const hasSavedPosition = typeof bounds.x === 'number' && typeof bounds.y === 'number';

    if (hasSavedPosition) {
        const visibleOnAnyDisplay = displays.some(({ workArea }) => {
            const x = bounds.x as number;
            const y = bounds.y as number;
            return (
                x < workArea.x + workArea.width &&
                x + bounds.width > workArea.x &&
                y < workArea.y + workArea.height &&
                y + bounds.height > workArea.y
            );
        });

        if (visibleOnAnyDisplay) {
            return bounds;
        }
    }

    const primaryWorkArea = screen.getPrimaryDisplay().workArea;
    return {
        width: Math.min(bounds.width, primaryWorkArea.width),
        height: Math.min(bounds.height, primaryWorkArea.height),
        x: Math.round(primaryWorkArea.x + (primaryWorkArea.width - bounds.width) / 2),
        y: Math.round(primaryWorkArea.y + Math.max(24, (primaryWorkArea.height - bounds.height) / 2)),
    };
}

function longestCommonPrefix(a: string, b: string) {
    const limit = Math.min(a.length, b.length);
    let index = 0;

    while (index < limit && a[index] === b[index]) {
        index += 1;
    }

    return index;
}

function computeDelta(previousText: string, updatedText: string) {
    const prefixLength = longestCommonPrefix(previousText || '', updatedText || '');
    return {
        deleteCount: Math.max(0, (previousText || '').length - prefixLength),
        insertText: (updatedText || '').slice(prefixLength),
    };
}

function sleep(ms: number) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

async function pasteInsert(text: string) {
    if (!text) {
        return;
    }

    clipboard.writeText(text);
    await sleep(50);
    await keyboard.pressKey(Key.LeftControl, Key.V);
    await keyboard.releaseKey(Key.LeftControl, Key.V);
}

async function sendBackspaces(count: number) {
    for (let index = 0; index < count; index += 1) {
        await keyboard.pressKey(Key.Backspace);
        await keyboard.releaseKey(Key.Backspace);
    }
}

async function applySmartEditResult(result: SmartEditResult) {
    if (mainWindow?.isFocused() || widgetWindow?.isFocused()) {
        console.log('DictaPilot is focused, skipping external text injection.');
        return;
    }

    if (result.action === 'ignore') {
        return;
    }

    const { deleteCount, insertText } = computeDelta(appliedTranscript, result.updatedText);
    if (deleteCount > 0) {
        await sendBackspaces(deleteCount);
    }

    if (insertText) {
        await pasteInsert(insertText);
    }

    appliedTranscript = result.updatedText;
}

async function handleStartDictation() {
    if (isRecording) return;
    isRecording = true;
    console.log('Main IPC: Start dictation requested');
    audioService.start();
    transcriptionService.start();
    safeSend(mainWindow, Channels.OnStateChange, { state: 'recording' });
    safeSend(widgetWindow, Channels.OnStateChange, { state: 'recording' });
}

async function handleStopDictation() {
    if (!isRecording) return;
    isRecording = false;
    console.log('Main IPC: Stop dictation requested');
    audioService.stop();

    safeSend(mainWindow, Channels.OnStateChange, { state: 'processing' });
    safeSend(widgetWindow, Channels.OnStateChange, { state: 'processing' });

    try {
        const finalRawText = await transcriptionService.stop();
        if (finalRawText) {
            console.log('Final transcription received, applying smart edit...');
            const smartEditResult = await editingService.processSmart(finalRawText);

            safeSend(mainWindow, Channels.OnTranscriptionUpdate, {
                text: smartEditResult.displayText,
                isFinal: true
            });
            safeSend(widgetWindow, Channels.OnTranscriptionUpdate, {
                text: smartEditResult.displayText,
                isFinal: true
            });
            if ((smartEditResult.action === 'append' || smartEditResult.action === 'undo_append') && smartEditResult.updatedText) {
                historyService.saveResult(smartEditResult.updatedText);
            }

            try {
                await sleep(100);
                await applySmartEditResult(smartEditResult);
            } catch (err) {
                console.error('Auto-paste failed:', err);
            }
        }
    } catch (e) {
        console.error(e);
    }

    safeSend(mainWindow, Channels.OnStateChange, { state: 'idle' });
    safeSend(widgetWindow, Channels.OnStateChange, { state: 'idle' });
}

function createWindow() {
    const savedBounds = store.get('windowBounds', { width: 600, height: 800 }) as { width: number, height: number, x?: number, y?: number };
    const bounds = normalizeWindowBounds(savedBounds);

    mainWindow = new BrowserWindow({
        ...bounds,
        show: false,
        frame: false,
        backgroundColor: '#050505',
        webPreferences: {
            preload: path.join(__dirname, '../../preload/dist/index.js'),
            nodeIntegration: false,
            contextIsolation: true,
            sandbox: false  // Must be explicit: Electron 20+ defaults sandbox to true, which breaks ipcRenderer in preload
        }
    });

    // Load the Vite dev server URL or the local index.html
    if (!app.isPackaged) {
        mainWindow.loadURL((process.env.VITE_DEV_SERVER_URL || 'http://localhost:5174'));
    } else {
        mainWindow.loadFile(path.join(__dirname, '../../renderer/dist/index.html'));
    }

    mainWindow.once('ready-to-show', () => {
        mainWindow?.show();
        mainWindow?.focus();
        mainWindow?.moveTop();
        broadcastMainWindowState();
        // mainWindow?.webContents.openDevTools({ mode: 'detach' });
    });

    mainWindow.on('close', (event) => {
        // Hide to tray instead of quitting if we arent explicitly quitting
        if (!isQuitting) {
            event.preventDefault();
            mainWindow?.hide();
        }
    });

    const saveBounds = () => {
        if (mainWindow) {
            store.set('windowBounds', mainWindow.getBounds());
        }
    };

    mainWindow.on('resize', saveBounds);
    mainWindow.on('moved', saveBounds);
    mainWindow.on('maximize', broadcastMainWindowState);
    mainWindow.on('unmaximize', broadcastMainWindowState);
    mainWindow.on('enter-full-screen', broadcastMainWindowState);
    mainWindow.on('leave-full-screen', broadcastMainWindowState);
}

function createWidgetWindow() {
    const primaryDisplay = screen.getPrimaryDisplay();
    const { x, y, width } = primaryDisplay.workArea;

    const widgetWidth = 180;
    const widgetHeight = 44;
    const widgetX = Math.round(x + (width - widgetWidth) / 2);
    const widgetY = y + 24;

    widgetWindow = new BrowserWindow({
        width: widgetWidth,
        height: widgetHeight,
        x: widgetX,
        y: widgetY,
        show: false,
        frame: false,
        backgroundColor: '#101214',
        alwaysOnTop: true,
        skipTaskbar: true,
        resizable: false,
        webPreferences: {
            preload: path.join(__dirname, '../../preload/dist/index.js'),
            nodeIntegration: false,
            contextIsolation: true,
            sandbox: false  // Must be explicit: Electron 20+ defaults sandbox to true, which breaks ipcRenderer in preload
        }
    });

    if (!app.isPackaged) {
        widgetWindow.loadURL((process.env.VITE_DEV_SERVER_URL || 'http://localhost:5174') + '#widget');
    } else {
        widgetWindow.loadFile(path.join(__dirname, '../../renderer/dist/index.html'), { hash: 'widget' });
    }

    widgetWindow.once('ready-to-show', () => {
        widgetWindow?.setAlwaysOnTop(true, 'screen-saver');
        widgetWindow?.showInactive();
    });
}

function registerHotkeys() {
    currentHotkey = (settingsService.getSettings().HOTKEY || 'F9').toUpperCase();

    if (!keyListener) {
        keyListener = new GlobalKeyboardListener();
        keyListener.addListener((e) => {
            if (e.name === currentHotkey.toUpperCase()) {
                if (e.state === 'DOWN' && !isRecording) {
                    handleStartDictation();
                } else if (e.state === 'UP' && isRecording) {
                    handleStopDictation();
                }
            }
        });
    }
}

function createTray() {
    // Use a blank icon for now, ideally read from assets
    const icon = nativeImage.createEmpty();
    tray = new Tray(icon);

    const contextMenu = Menu.buildFromTemplate([
        { label: 'DictaPilot', enabled: false },
        { type: 'separator' },
        {
            label: 'Show Dashboard', click: () => {
                mainWindow?.show();
                mainWindow?.focus();
                mainWindow?.moveTop();
            }
        },
        {
            label: 'Show Widget', click: () => {
                widgetWindow?.setAlwaysOnTop(true, 'screen-saver');
                widgetWindow?.showInactive();
            }
        },
        { type: 'separator' },
        {
            label: 'Quit DictaPilot', click: () => {
                isQuitting = true;
                app.quit();
            }
        }
    ]);

    tray.setToolTip('DictaPilot Dictation Engine');
    tray.setContextMenu(contextMenu);
    tray.on('click', () => {
        if (!mainWindow) return;
        if (mainWindow.isVisible()) {
            mainWindow.hide();
            return;
        }

        mainWindow.show();
        mainWindow.focus();
        mainWindow.moveTop();
    });
}

function registerAutoUpdateHandlers() {
    // Stub for future auto-update logic with electron-updater
    console.log('Main: Auto-update handlers registered');
}

function registerIpcHandlers() {
    // Listen for backend updates
    transcriptionService.on('transcription-update', (data) => {
        const processed = editingService.process(data.text);
        safeSend(mainWindow, Channels.OnTranscriptionUpdate, {
            text: processed,
            isFinal: data.isFinal
        });
        safeSend(widgetWindow, Channels.OnTranscriptionUpdate, {
            text: processed,
            isFinal: data.isFinal
        });
        if (data.isFinal) {
            historyService.saveResult(processed);
        }
    });

    ipcMain.handle(Channels.StartDictation, async (): Promise<IpcResponse> => {
        await handleStartDictation();
        return { success: true };
    });

    ipcMain.handle(Channels.StopDictation, async (): Promise<IpcResponse> => {
        await handleStopDictation();
        return { success: true };
    });

    ipcMain.handle(Channels.UpdateSettings, async (_, settings: any): Promise<IpcResponse> => {
        console.log('Main IPC: Settings update', settings);
        settingsService.updateSettings(settings);
        configureRuntimeSettings();
        return { success: true };
    });

    ipcMain.handle(Channels.GetSettings, async (): Promise<IpcResponse<any>> => {
        return { success: true, data: settingsService.getSettings() };
    });

    ipcMain.handle(Channels.GetHistory, async (): Promise<IpcResponse> => {
        return { success: true, data: historyService.getHistory() };
    });

    ipcMain.handle(Channels.GetMainWindowState, async (): Promise<IpcResponse<{ isMaximized: boolean }>> => {
        return {
            success: true,
            data: {
                isMaximized: mainWindow?.isMaximized() ?? false
            }
        };
    });

    ipcMain.handle(Channels.MinimizeMainWindow, async (): Promise<IpcResponse> => {
        mainWindow?.minimize();
        broadcastMainWindowState();
        return { success: true };
    });

    ipcMain.handle(Channels.ToggleMainWindowMaximize, async (): Promise<IpcResponse> => {
        if (mainWindow) {
            if (mainWindow.isMaximized()) {
                mainWindow.unmaximize();
            } else {
                mainWindow.maximize();
            }
        }

        broadcastMainWindowState();
        return { success: true };
    });

    ipcMain.handle(Channels.CloseMainWindow, async (): Promise<IpcResponse> => {
        mainWindow?.close();
        return { success: true };
    });

    ipcMain.handle(Channels.CloseWidgetWindow, async (): Promise<IpcResponse> => {
        widgetWindow?.hide();
        return { success: true };
    });

    ipcMain.on(Channels.SendAudioData, (event, buffer: ArrayBuffer) => {
        const buf = Buffer.from(buffer);
        audioService.emit('audio-data', buf);

        // Calculate amplitude (RMS of Int16 PCM)
        let sumSq = 0;
        const count = buf.length / 2;
        for (let i = 0; i < buf.length; i += 2) {
            const val = buf.readInt16LE(i);
            const norm = val / 32768.0;
            sumSq += norm * norm;
        }
        const rms = count > 0 ? Math.sqrt(sumSq / count) : 0;

        safeSend(mainWindow, Channels.OnAmplitudeUpdate, rms);
        safeSend(widgetWindow, Channels.OnAmplitudeUpdate, rms);
    });
}

app.whenReady().then(() => {
    session.defaultSession.setPermissionCheckHandler((webContents, permission, requestingOrigin, details) => {
        if (permission === 'media') {
            return true;
        }
        return false;
    });
    session.defaultSession.setPermissionRequestHandler((webContents, permission, callback) => {
        if (permission === 'media') {
            callback(true);
        } else {
            callback(false);
        }
    });

    createWindow();
    createWidgetWindow();
    createTray();
    registerHotkeys();
    registerIpcHandlers();
    registerAutoUpdateHandlers();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
            createWidgetWindow();
        } else {
            mainWindow?.show();
        }
    });
});

app.on('will-quit', () => {
    if (keyListener) {
        keyListener.kill();
    }
});

app.on('second-instance', () => {
    if (mainWindow) {
        if (mainWindow.isMinimized()) mainWindow.restore();
        mainWindow.focus();
        mainWindow.show();
    }
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});


