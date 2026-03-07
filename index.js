"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const electron_1 = require("electron");
const path = __importStar(require("path"));
const dictapilot_desktop_shared_1 = require("dictapilot-desktop-shared");
const dictapilot_desktop_backend_1 = require("dictapilot-desktop-backend");
const nut_js_1 = require("@nut-tree-fork/nut-js");
const electron_store_1 = __importDefault(require("electron-store"));
const node_global_key_listener_1 = require("node-global-key-listener");
(0, dictapilot_desktop_shared_1.loadDesktopEnv)();
const store = new electron_store_1.default();
let mainWindow = null;
let widgetWindow = null;
let tray = null;
let keyListener = null;
let currentHotkey = 'F9';
let isRecording = false;
// Initialize GroqProvider
const groqApiKey = process.env.GROQ_API_KEY || '';
if (groqApiKey) {
    const groqProvider = new dictapilot_desktop_backend_1.GroqProvider(groqApiKey);
    dictapilot_desktop_backend_1.transcriptionService.setProvider(groqProvider);
}
else {
    console.warn('GROQ_API_KEY not found. Dictation will fall back until a key is available.');
}
// Ensure single instance
const gotTheLock = electron_1.app.requestSingleInstanceLock();
if (!gotTheLock) {
    electron_1.app.quit();
}
function safeSend(window, channel, ...args) {
    if (window && !window.isDestroyed() && window.webContents) {
        window.webContents.send(channel, ...args);
    }
}
async function handleStartDictation() {
    if (isRecording)
        return;
    isRecording = true;
    console.log('Main IPC: Start dictation requested');
    dictapilot_desktop_backend_1.audioService.start();
    dictapilot_desktop_backend_1.transcriptionService.start();
    safeSend(mainWindow, dictapilot_desktop_shared_1.Channels.OnStateChange, { state: 'recording' });
    safeSend(widgetWindow, dictapilot_desktop_shared_1.Channels.OnStateChange, { state: 'recording' });
}
async function handleStopDictation() {
    if (!isRecording)
        return;
    isRecording = false;
    console.log('Main IPC: Stop dictation requested');
    dictapilot_desktop_backend_1.audioService.stop();
    safeSend(mainWindow, dictapilot_desktop_shared_1.Channels.OnStateChange, { state: 'processing' });
    safeSend(widgetWindow, dictapilot_desktop_shared_1.Channels.OnStateChange, { state: 'processing' });
    try {
        const finalRawText = await dictapilot_desktop_backend_1.transcriptionService.stop();
        if (finalRawText) {
            console.log('Final transcription received, applying smart edit...');
            const finalCleanText = await dictapilot_desktop_backend_1.editingService.processSmart(finalRawText);
            safeSend(mainWindow, dictapilot_desktop_shared_1.Channels.OnTranscriptionUpdate, {
                text: finalCleanText,
                isFinal: true
            });
            safeSend(widgetWindow, dictapilot_desktop_shared_1.Channels.OnTranscriptionUpdate, {
                text: finalCleanText,
                isFinal: true
            });
            dictapilot_desktop_backend_1.historyService.saveResult(finalCleanText);
            // Auto paste
            electron_1.clipboard.writeText(finalCleanText);
            try {
                // If DictaPilot itself is focused, the UI already displays the text, do not paste it.
                if (mainWindow?.isFocused() || widgetWindow?.isFocused()) {
                    console.log("DictaPilot is focused, skipping auto-paste to avoid double typing in our own UI.");
                }
                else {
                    // Return focus to the active window before pasting
                    if (mainWindow && Reflect.has(mainWindow, 'restoreFocus')) {
                        // Try some electron trick if possible, usually windows manages this if we don't steal focus.
                    }
                    setTimeout(async () => {
                        await nut_js_1.keyboard.pressKey(nut_js_1.Key.LeftControl, nut_js_1.Key.V);
                        await nut_js_1.keyboard.releaseKey(nut_js_1.Key.LeftControl, nut_js_1.Key.V);
                    }, 100); // small delay to ensure clipboard is ready
                }
            }
            catch (err) {
                console.error('Auto-paste failed:', err);
            }
        }
    }
    catch (e) {
        console.error(e);
    }
    safeSend(mainWindow, dictapilot_desktop_shared_1.Channels.OnStateChange, { state: 'idle' });
    safeSend(widgetWindow, dictapilot_desktop_shared_1.Channels.OnStateChange, { state: 'idle' });
}
function createWindow() {
    const bounds = store.get('windowBounds', { width: 600, height: 800 });
    mainWindow = new electron_1.BrowserWindow({
        ...bounds,
        show: false,
        frame: false,
        transparent: true,
        webPreferences: {
            preload: path.join(__dirname, '../../preload/dist/index.js'),
            nodeIntegration: false,
            contextIsolation: true,
            sandbox: false // Must be explicit: Electron 20+ defaults sandbox to true, which breaks ipcRenderer in preload
        }
    });
    // Load the Vite dev server URL or the local index.html
    if (!electron_1.app.isPackaged) {
        mainWindow.loadURL((process.env.VITE_DEV_SERVER_URL || 'http://localhost:5174'));
    }
    else {
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
    const primaryDisplay = electron_1.screen.getPrimaryDisplay();
    const { width, height } = primaryDisplay.workAreaSize;
    const widgetWidth = 180;
    const widgetHeight = 44;
    widgetWindow = new electron_1.BrowserWindow({
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
            sandbox: false // Must be explicit: Electron 20+ defaults sandbox to true, which breaks ipcRenderer in preload
        }
    });
    if (!electron_1.app.isPackaged) {
        widgetWindow.loadURL((process.env.VITE_DEV_SERVER_URL || 'http://localhost:5174') + '#widget');
    }
    else {
        widgetWindow.loadFile(path.join(__dirname, '../renderer/index.html'), { hash: 'widget' });
    }
    widgetWindow.once('ready-to-show', () => {
        widgetWindow?.show();
    });
}
function registerHotkeys() {
    currentHotkey = store.get('settings.hotkey') || 'F9';
    if (!keyListener) {
        keyListener = new node_global_key_listener_1.GlobalKeyboardListener();
        keyListener.addListener((e) => {
            if (e.name === currentHotkey.toUpperCase()) {
                if (e.state === 'DOWN' && !isRecording) {
                    handleStartDictation();
                }
                else if (e.state === 'UP' && isRecording) {
                    handleStopDictation();
                }
            }
        });
    }
}
function createTray() {
    // Use a blank icon for now, ideally read from assets
    const icon = electron_1.nativeImage.createEmpty();
    tray = new electron_1.Tray(icon);
    const contextMenu = electron_1.Menu.buildFromTemplate([
        { label: 'DictaPilot', enabled: false },
        { type: 'separator' },
        { label: 'Show Dashboard', click: () => mainWindow?.show() },
        { type: 'separator' },
        {
            label: 'Quit DictaPilot', click: () => {
                isQuitting = true;
                electron_1.app.quit();
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
    dictapilot_desktop_backend_1.transcriptionService.on('transcription-update', (data) => {
        const processed = dictapilot_desktop_backend_1.editingService.process(data.text);
        safeSend(mainWindow, dictapilot_desktop_shared_1.Channels.OnTranscriptionUpdate, {
            text: processed,
            isFinal: data.isFinal
        });
        safeSend(widgetWindow, dictapilot_desktop_shared_1.Channels.OnTranscriptionUpdate, {
            text: processed,
            isFinal: data.isFinal
        });
        if (data.isFinal) {
            dictapilot_desktop_backend_1.historyService.saveResult(processed);
        }
    });
    electron_1.ipcMain.handle(dictapilot_desktop_shared_1.Channels.StartDictation, async () => {
        await handleStartDictation();
        return { success: true };
    });
    electron_1.ipcMain.handle(dictapilot_desktop_shared_1.Channels.StopDictation, async () => {
        await handleStopDictation();
        return { success: true };
    });
    electron_1.ipcMain.handle(dictapilot_desktop_shared_1.Channels.UpdateSettings, async (_, settings) => {
        console.log('Main IPC: Settings update', settings);
        dictapilot_desktop_backend_1.settingsService.updateSettings(settings);
        if (settings.hotkey) {
            store.set('settings.hotkey', settings.hotkey);
            currentHotkey = settings.hotkey;
        }
        return { success: true };
    });
    electron_1.ipcMain.handle(dictapilot_desktop_shared_1.Channels.GetSettings, async () => {
        return { success: true, data: dictapilot_desktop_backend_1.settingsService.getSettings() };
    });
    electron_1.ipcMain.handle(dictapilot_desktop_shared_1.Channels.GetHistory, async () => {
        return { success: true, data: dictapilot_desktop_backend_1.historyService.getHistory() };
    });
    electron_1.ipcMain.on(dictapilot_desktop_shared_1.Channels.SendAudioData, (event, buffer) => {
        const buf = Buffer.from(buffer);
        dictapilot_desktop_backend_1.audioService.emit('audio-data', buf);
        // Calculate amplitude (RMS of Int16 PCM)
        let sumSq = 0;
        const count = buf.length / 2;
        for (let i = 0; i < buf.length; i += 2) {
            const val = buf.readInt16LE(i);
            const norm = val / 32768.0;
            sumSq += norm * norm;
        }
        const rms = count > 0 ? Math.sqrt(sumSq / count) : 0;
        safeSend(mainWindow, dictapilot_desktop_shared_1.Channels.OnAmplitudeUpdate, rms);
        safeSend(widgetWindow, dictapilot_desktop_shared_1.Channels.OnAmplitudeUpdate, rms);
    });
}
electron_1.app.whenReady().then(() => {
    electron_1.session.defaultSession.setPermissionCheckHandler((webContents, permission, requestingOrigin, details) => {
        if (permission === 'media') {
            return true;
        }
        return false;
    });
    electron_1.session.defaultSession.setPermissionRequestHandler((webContents, permission, callback) => {
        if (permission === 'media') {
            callback(true);
        }
        else {
            callback(false);
        }
    });
    createWindow();
    createWidgetWindow();
    createTray();
    registerHotkeys();
    registerIpcHandlers();
    registerAutoUpdateHandlers();
    electron_1.app.on('activate', () => {
        if (electron_1.BrowserWindow.getAllWindows().length === 0) {
            createWindow();
            createWidgetWindow();
        }
        else {
            mainWindow?.show();
        }
    });
});
electron_1.app.on('will-quit', () => {
    if (keyListener) {
        keyListener.kill();
    }
});
electron_1.app.on('second-instance', () => {
    if (mainWindow) {
        if (mainWindow.isMinimized())
            mainWindow.restore();
        mainWindow.focus();
        mainWindow.show();
    }
});
electron_1.app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        electron_1.app.quit();
    }
});
let isQuitting = false;
