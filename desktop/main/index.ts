import { app, BrowserWindow, Menu, Tray, nativeImage, ipcMain, globalShortcut, screen, session, clipboard } from 'electron';
import * as path from 'path';
import { Channels, IpcResponse, loadDesktopEnv } from 'dictapilot-desktop-shared';
import { audioService, transcriptionService, settingsService, historyService, editingService, GroqProvider } from 'dictapilot-desktop-backend';
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

async function handleStartDictation() {
    if (isRecording) return;
    isRecording = true;
    console.log('Main IPC: Start dictation requested');
    audioService.start();
    transcriptionService.start();
    widgetWindow?.showInactive();
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
            const finalCleanText = await editingService.processSmart(finalRawText);

            safeSend(mainWindow, Channels.OnTranscriptionUpdate, {
                text: finalCleanText,
                isFinal: true
            });
            safeSend(widgetWindow, Channels.OnTranscriptionUpdate, {
                text: finalCleanText,
                isFinal: true
            });
            historyService.saveResult(finalCleanText);

            // Auto paste
            clipboard.writeText(finalCleanText);
            try {
                // If DictaPilot itself is focused, the UI already displays the text, do not paste it.
                if (mainWindow?.isFocused() || widgetWindow?.isFocused()) {
                    console.log("DictaPilot is focused, skipping auto-paste to avoid double typing in our own UI.");
                } else {
                    // Return focus to the active window before pasting
                    if (mainWindow && Reflect.has(mainWindow, 'restoreFocus')) {
                        // Try some electron trick if possible, usually windows manages this if we don't steal focus.
                    }
                    setTimeout(async () => {
                        await keyboard.pressKey(Key.LeftControl, Key.V);
                        await keyboard.releaseKey(Key.LeftControl, Key.V);
                    }, 100); // small delay to ensure clipboard is ready
                }
            } catch (err) {
                console.error('Auto-paste failed:', err);
            }
        }
    } catch (e) {
        console.error(e);
    }

    safeSend(mainWindow, Channels.OnStateChange, { state: 'idle' });
    safeSend(widgetWindow, Channels.OnStateChange, { state: 'idle' });
    widgetWindow?.hide();
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
}

function createWidgetWindow() {
    const primaryDisplay = screen.getPrimaryDisplay();
    const { width, height } = primaryDisplay.workAreaSize;

    const widgetWidth = 180;
    const widgetHeight = 44;

    widgetWindow = new BrowserWindow({
        width: widgetWidth,
        height: widgetHeight,
        x: (width - widgetWidth) / 2,
        y: height - widgetHeight - 40,
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
        if (isRecording) {
            widgetWindow?.showInactive();
        }
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

let isQuitting = false;


