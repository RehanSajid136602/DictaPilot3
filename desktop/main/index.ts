import { app, BrowserWindow, Menu, Tray, nativeImage, ipcMain, globalShortcut, screen, session, clipboard } from 'electron';
import * as path from 'path';
import * as dotenv from 'dotenv';
import { Channels, IpcResponse } from 'dictapilot-desktop-shared';
import { audioService, transcriptionService, settingsService, historyService, editingService, GroqProvider } from 'dictapilot-desktop-backend';
import { keyboard, Key } from '@nut-tree-fork/nut-js';
import Store from 'electron-store';
import { GlobalKeyboardListener } from 'node-global-key-listener';

dotenv.config({ path: path.join(__dirname, '../../.env') });

const store = new Store() as any;
let mainWindow: BrowserWindow | null = null;
let widgetWindow: BrowserWindow | null = null;
let tray: Tray | null = null;

let keyListener: GlobalKeyboardListener | null = null;
let currentHotkey = 'F9';
let isRecording = false;

// Initialize GroqProvider
const groqApiKey = process.env.GROQ_API_KEY || '';
if (groqApiKey) {
    const groqProvider = new GroqProvider(groqApiKey);
    transcriptionService.setProvider(groqProvider);
} else {
    console.warn('GROQ_API_KEY not found in .env');
}

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
                // Return focus to the active window before pasting
                if (mainWindow && Reflect.has(mainWindow, 'restoreFocus')) {
                    // Try some electron trick if possible, usually windows manages this if we don't steal focus.
                }
                setTimeout(async () => {
                    await keyboard.type(Key.LeftControl, Key.V);
                }, 100); // small delay to ensure clipboard is ready
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
    const bounds = store.get('windowBounds', { width: 600, height: 800 }) as { width: number, height: number, x?: number, y?: number };

    mainWindow = new BrowserWindow({
        ...bounds,
        show: false,
        frame: false,
        transparent: true,
        webPreferences: {
            preload: path.join(__dirname, '../../preload/dist/index.js'),
            nodeIntegration: false,
            contextIsolation: true,
            sandbox: true
        }
    });

    // Load the Vite dev server URL or the local index.html
    if (!app.isPackaged) {
        mainWindow.loadURL((process.env.VITE_DEV_SERVER_URL || 'http://localhost:5174'));
    } else {
        mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));
    }

    mainWindow.once('ready-to-show', () => {
        mainWindow?.show();
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
        transparent: true,
        alwaysOnTop: true,
        skipTaskbar: true,
        resizable: false,
        webPreferences: {
            preload: path.join(__dirname, '../../preload/dist/index.js'),
            nodeIntegration: false,
            contextIsolation: true,
            sandbox: true
        }
    });

    if (!app.isPackaged) {
        widgetWindow.loadURL((process.env.VITE_DEV_SERVER_URL || 'http://localhost:5174') + '#widget');
    } else {
        widgetWindow.loadFile(path.join(__dirname, '../renderer/index.html'), { hash: 'widget' });
    }

    widgetWindow.once('ready-to-show', () => {
        widgetWindow?.show();
    });
}

function registerHotkeys() {
    currentHotkey = (store.get('settings.hotkey') as string) || 'F9';

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
        { label: 'Show Dashboard', click: () => mainWindow?.show() },
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
        mainWindow?.isVisible() ? mainWindow.hide() : mainWindow?.show();
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
        if (settings.hotkey) {
            store.set('settings.hotkey', settings.hotkey);
            currentHotkey = settings.hotkey;
        }
        return { success: true };
    });

    ipcMain.handle(Channels.GetSettings, async (): Promise<IpcResponse> => {
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
