import { app, BrowserWindow, Menu, Tray, nativeImage, ipcMain, screen, session, clipboard } from 'electron';
import { randomUUID } from 'crypto';
import * as path from 'path';
import {
    DEFAULT_SYNC_PREFERENCES,
    type DictationState,
    type DictationSessionResponse,
    Channels,
    type AuthState,
    type IpcResponse,
    LOADING_AUTH_STATE,
    type MainWindowStateEvent,
    SIGNED_OUT_AUTH_STATE,
    type SignInRequest,
    type SignUpRequest,
    type SyncPreferences,
    type SyncPreferencesUpdateRequest,
    loadDesktopEnv,
} from 'dictapilot-desktop-shared';
import {
    accountProfileService,
    authService,
    AuthServiceError,
    audioService,
    cloudStoreService,
    CloudStoreServiceError,
    createQueueItem,
    deviceService,
    dictionaryRepository,
    editingService,
    historyService,
    sessionService,
    settingsRepository,
    settingsService,
    snippetRepository,
    syncQueueService,
    syncQueueStoreService,
    textInsertionService,
    transcriptionService,
    validateFirebaseProviderConfig,
} from 'dictapilot-desktop-backend';
import { keyboard, Key } from '@nut-tree-fork/nut-js';
import Store from 'electron-store';
import { GlobalKeyboardListener } from 'node-global-key-listener';
import { startGoogleOAuthPkce } from './googleOAuthService';

loadDesktopEnv();
app.disableHardwareAcceleration();

const store = new Store() as Store<Record<string, unknown>>;

let mainWindow: BrowserWindow | null = null;
let widgetWindow: BrowserWindow | null = null;
let tray: Tray | null = null;
let keyListener: GlobalKeyboardListener | null = null;
let currentHotkey = 'F9';
let dictationLifecycleState: DictationState = 'idle';
let isQuitting = false;
let currentAuthState: AuthState = { ...LOADING_AUTH_STATE };
let activeDictationSessionId: string | null = null;

function getErrorCode(error: unknown, fallbackCode: string): string {
    if (error instanceof AuthServiceError || error instanceof CloudStoreServiceError) {
        return error.code;
    }
    if (error instanceof Error && error.name) {
        return error.name;
    }
    return fallbackCode;
}

function getErrorMessage(error: unknown, fallbackMessage: string): string {
    return error instanceof Error && error.message ? error.message : fallbackMessage;
}

function isSessionInvalidError(error: unknown): boolean {
    const code = getErrorCode(error, '');
    return [
        'session_invalid',
        'invalid_refresh_token',
        'INVALID_REFRESH_TOKEN',
        'TOKEN_EXPIRED',
        'INVALID_ID_TOKEN',
        'USER_NOT_FOUND',
    ].includes(code);
}

function isOfflineError(error: unknown): boolean {
    if (!(error instanceof Error)) {
        return false;
    }
    return /fetch failed|network|offline|timed out|enotfound|econnrefused/i.test(error.message);
}

function safeSend(window: BrowserWindow | null, channel: string, ...args: unknown[]): void {
    if (window && !window.isDestroyed() && window.webContents) {
        window.webContents.send(channel, ...args);
    }
}

function publishDictationState(state: DictationState, sessionId: string | null): void {
    dictationLifecycleState = state;
    safeSend(mainWindow, Channels.OnStateChange, { state, sessionId });
    safeSend(widgetWindow, Channels.OnStateChange, { state, sessionId });
}

function syncStatusFromCurrentState(overrides?: Partial<SyncPreferences>): SyncPreferences {
    return {
        enabled: currentAuthState.sync.enabled,
        status: currentAuthState.sync.status,
        pendingOperations: syncQueueStoreService.getPendingCount(),
        lastSyncedAt: currentAuthState.sync.lastSyncedAt ?? null,
        errorMessage: currentAuthState.sync.errorMessage ?? null,
        ...overrides,
    };
}

function buildSignedOutState(errorMessage?: string | null): AuthState {
    return {
        ...SIGNED_OUT_AUTH_STATE,
        sync: {
            ...DEFAULT_SYNC_PREFERENCES,
            pendingOperations: 0,
        },
        errorMessage: errorMessage ?? null,
    };
}

function revealMainWindow(): void {
    if (!mainWindow) {
        return;
    }
    mainWindow.show();
    mainWindow.focus();
    mainWindow.moveTop();
}

function syncAuthWindowAccess(): void {
    if (currentAuthState.status === 'authenticated') {
        if (widgetWindow && !widgetWindow.isDestroyed() && !widgetWindow.isVisible()) {
            widgetWindow.showInactive();
        }
        return;
    }

    if (widgetWindow && !widgetWindow.isDestroyed() && widgetWindow.isVisible()) {
        widgetWindow.hide();
    }
}

function resetActiveDictationSession(): void {
    const sessionId = activeDictationSessionId;
    if (!sessionId && dictationLifecycleState === 'idle') {
        return;
    }

    audioService.stop();

    if (sessionId) {
        transcriptionService.abortSession(sessionId);
        textInsertionService.resetSession(sessionId);
    }

    activeDictationSessionId = null;
    publishDictationState('idle', null);
}

function requireAuthenticatedAccess(message: string): boolean {
    if (currentAuthState.status === 'authenticated') {
        return true;
    }

    if (currentAuthState.status !== 'loading') {
        setAuthState(buildSignedOutState(message));
    }
    revealMainWindow();
    return false;
}

function publishAuthState(): void {
    safeSend(mainWindow, Channels.OnAuthStateChange, currentAuthState);
}

function publishSyncStatus(): void {
    safeSend(mainWindow, Channels.OnSyncStatusChange, currentAuthState.sync);
}

function setSyncStatus(overrides?: Partial<SyncPreferences>): void {
    currentAuthState = {
        ...currentAuthState,
        sync: syncStatusFromCurrentState(overrides),
    };
    syncAuthWindowAccess();
    publishSyncStatus();
    publishAuthState();
}

function setAuthState(next: AuthState): void {
    const wasAuthenticated = currentAuthState.status === 'authenticated';
    currentAuthState = {
        ...next,
        sync: {
            ...next.sync,
            pendingOperations: syncQueueStoreService.getPendingCount(),
        },
    };
    if (wasAuthenticated && currentAuthState.status !== 'authenticated') {
        resetActiveDictationSession();
    }
    syncAuthWindowAccess();
    publishAuthState();
    publishSyncStatus();
}

function configureRuntimeSettings(): void {
    const settings = settingsService.getSettings();
    currentHotkey = (settings.HOTKEY || 'F9').toUpperCase();

    // NVIDIA NIM provider is used automatically by transcriptionService
    // No need to manually set provider - it uses NVIDIA_API_KEY from environment
}

async function pasteCommittedText(text: string): Promise<void> {
    clipboard.writeText(text);

    if (mainWindow?.isFocused() || widgetWindow?.isFocused()) {
        textInsertionService.clearCommittedBaseline();
        return;
    }

    await keyboard.pressKey(Key.LeftControl, Key.V);
    await keyboard.releaseKey(Key.LeftControl, Key.V);
}

function queueLocalSnapshotForSync(): void {
    const settingsRecord = settingsRepository.getLocal();
    syncQueueStoreService.upsert(createQueueItem('settings', 'upsert', settingsRecord.id, settingsRecord, settingsRecord.metadata));

    for (const record of snippetRepository.listLocal(true)) {
        syncQueueStoreService.upsert(
            createQueueItem(
                'snippets',
                record.metadata.deletedAt ? 'delete' : 'upsert',
                record.id,
                record.metadata.deletedAt ? null : record,
                record.metadata,
            )
        );
    }

    for (const record of dictionaryRepository.listLocal(true)) {
        syncQueueStoreService.upsert(
            createQueueItem(
                'dictionary',
                record.metadata.deletedAt ? 'delete' : 'upsert',
                record.id,
                record.metadata.deletedAt ? null : record,
                record.metadata,
            )
        );
    }
}

async function forceSignedOutRecovery(message: string): Promise<AuthState> {
    sessionService.clear();
    syncQueueStoreService.clear();
    accountProfileService.clearProfile();
    authService.signOut();
    const nextState = buildSignedOutState(message);
    setAuthState(nextState);
    revealMainWindow();
    return nextState;
}

configureRuntimeSettings();

const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) {
    app.quit();
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

function broadcastMainWindowState(): void {
    const payload: MainWindowStateEvent = {
        isMaximized: mainWindow?.isMaximized() ?? false,
    };
    safeSend(mainWindow, Channels.OnMainWindowStateChange, payload);
}

async function maybeSyncAuthenticatedState(): Promise<void> {
    const session = authService.getCurrentSession();
    if (!session || currentAuthState.status !== 'authenticated' || !currentAuthState.sync.enabled) {
        return;
    }

    setSyncStatus({ status: 'syncing', errorMessage: null });

    try {
        await syncQueueService.hydrateFromCloud(session);
        queueLocalSnapshotForSync();
        const syncResult = await syncQueueService.syncNow(session);
        const lastSyncedAt = syncResult.status === 'error'
            ? currentAuthState.sync.lastSyncedAt ?? null
            : new Date().toISOString();
        const profile = accountProfileService.updateSync(true, syncResult.status, lastSyncedAt);

        setAuthState({
            status: 'authenticated',
            user: profile ?? currentAuthState.user,
            sync: syncStatusFromCurrentState({
                enabled: true,
                status: syncResult.status === 'error' ? 'error' : 'idle',
                errorMessage: syncResult.errorMessage ?? null,
                lastSyncedAt,
            }),
            errorMessage: null,
        });
    } catch (error) {
        if (isSessionInvalidError(error)) {
            await forceSignedOutRecovery('Your session expired. Sign in again to resume sync.');
            return;
        }

        const offline = isOfflineError(error);
        setSyncStatus({
            status: offline ? 'offline' : 'error',
            errorMessage: getErrorMessage(
                error,
                offline
                    ? 'You appear to be offline. DictaPilot will keep changes local until sync can resume.'
                    : 'Sync failed.',
            ),
        });
    }
}

async function hydrateAuthenticatedState(): Promise<AuthState> {
    const session = authService.getCurrentSession();
    if (!session) {
        const signedOut = { ...SIGNED_OUT_AUTH_STATE };
        setAuthState(signedOut);
        return signedOut;
    }

    try {
        const localProfile = accountProfileService.getProfile();
        const profile = await cloudStoreService.upsertProfile(session, localProfile?.syncEnabled ?? false);
        accountProfileService.setProfile(profile);
        await cloudStoreService.registerDevice(session, deviceService.getDeviceMetadata());

        const nextState: AuthState = {
            status: 'authenticated',
            user: profile,
            sync: {
                enabled: profile.syncEnabled,
                status: profile.syncEnabled ? 'idle' : 'disabled',
                pendingOperations: syncQueueStoreService.getPendingCount(),
                lastSyncedAt: profile.lastSyncedAt ?? null,
                errorMessage: null,
            },
            errorMessage: null,
        };

        setAuthState(nextState);
        if (profile.syncEnabled) {
            await maybeSyncAuthenticatedState();
        }
        return currentAuthState;
    } catch (error) {
        if (isSessionInvalidError(error)) {
            return forceSignedOutRecovery('Your session expired. Sign in again to resume sync.');
        }

        const fallbackProfile = accountProfileService.getProfile();
        const fallbackState: AuthState = {
            status: 'authenticated',
            user: fallbackProfile ?? session.user,
            sync: {
                enabled: fallbackProfile?.syncEnabled ?? false,
                status: 'error',
                pendingOperations: syncQueueStoreService.getPendingCount(),
                lastSyncedAt: fallbackProfile?.lastSyncedAt ?? null,
                errorMessage: error instanceof Error ? error.message : 'Failed to load sync state.',
            },
            errorMessage: null,
        };
        setAuthState(fallbackState);
        return fallbackState;
    }
}

async function bootstrapAuthState(): Promise<void> {
    const configValidation = validateFirebaseProviderConfig({ requireGoogle: true });
    if (!configValidation.valid) {
        accountProfileService.clearProfile();
        syncQueueStoreService.clear();
        setAuthState(
            buildSignedOutState(
                `Authentication is required, but Firebase is not configured. Missing: ${configValidation.missing.join(', ')}`
            )
        );
        return;
    }

    const persisted = sessionService.load();
    if (!persisted) {
        accountProfileService.clearProfile();
        syncQueueStoreService.clear();
        setAuthState(buildSignedOutState());
        return;
    }

    const restored = await sessionService.restore();
    if (!restored) {
        await forceSignedOutRecovery('Your saved session is no longer valid. Sign in again to resume sync.');
        return;
    }

    await hydrateAuthenticatedState();
}

async function handleStartDictation() {
    if (!requireAuthenticatedAccess(
        currentAuthState.status === 'loading'
            ? 'DictaPilot is still restoring your session.'
            : 'Sign in or create an account to start dictation.'
    )) {
        return null;
    }

    if (dictationLifecycleState === 'recording') {
        return activeDictationSessionId;
    }
    if (dictationLifecycleState === 'processing') {
        return null;
    }

    const sessionId = randomUUID();
    activeDictationSessionId = sessionId;
    audioService.start();
    transcriptionService.resetSession();
    editingService.resetSession();
    textInsertionService.beginSession(sessionId);
    transcriptionService.startSession(sessionId);
    publishDictationState('recording', sessionId);
    return sessionId;
}

async function handleStopDictation() {
    if (dictationLifecycleState !== 'recording' || !activeDictationSessionId) {
        return;
    }
    const sessionId = activeDictationSessionId;
    audioService.stop();
    publishDictationState('processing', sessionId);

    try {
        const finalRawText = sessionId ? await transcriptionService.stopSession(sessionId) : '';
        if (finalRawText && sessionId && textInsertionService.canCommit(sessionId)) {
            const finalCleanText = await editingService.processSmart(finalRawText);
            const commit = textInsertionService.commit(sessionId, finalCleanText);
            safeSend(mainWindow, Channels.OnTranscriptionUpdate, {
                text: finalCleanText,
                isFinal: true,
                sessionId,
            });
            safeSend(widgetWindow, Channels.OnTranscriptionUpdate, {
                text: finalCleanText,
                isFinal: true,
                sessionId,
            });
            historyService.saveResult(finalCleanText);
            if (commit) {
                setTimeout(() => {
                    void pasteCommittedText(commit.text);
                }, 100);
            }
        } else if (sessionId) {
            textInsertionService.abandonSession(sessionId);
        }
    } catch (error) {
        if (sessionId) {
            transcriptionService.abortSession(sessionId);
            textInsertionService.abandonSession(sessionId);
        }
        console.error(error);
    } finally {
        activeDictationSessionId = null;
        publishDictationState('idle', null);
    }
}

function createWindow(): void {
    const savedBounds = store.get('windowBounds', { width: 600, height: 800 }) as { width: number; height: number; x?: number; y?: number };
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
            sandbox: false,
        },
    });

    if (!app.isPackaged) {
        void mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL || 'http://localhost:5174');
    } else {
        void mainWindow.loadFile(path.join(__dirname, '../../renderer/dist/index.html'));
    }

    mainWindow.once('ready-to-show', () => {
        mainWindow?.show();
        mainWindow?.focus();
        mainWindow?.moveTop();
        broadcastMainWindowState();
        publishAuthState();
        publishSyncStatus();
    });

    mainWindow.on('close', (event) => {
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
}

function createWidgetWindow(): void {
    const primaryDisplay = screen.getPrimaryDisplay();
    const { x, y, width } = primaryDisplay.workArea;
    const widgetWidth = 180;
    const widgetHeight = 44;

    widgetWindow = new BrowserWindow({
        width: widgetWidth,
        height: widgetHeight,
        x: Math.round(x + (width - widgetWidth) / 2),
        y: y + 24,
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
            sandbox: false,
        },
    });

    if (!app.isPackaged) {
        void widgetWindow.loadURL(`${process.env.VITE_DEV_SERVER_URL || 'http://localhost:5174'}#widget`);
    } else {
        void widgetWindow.loadFile(path.join(__dirname, '../../renderer/dist/index.html'), { hash: 'widget' });
    }

    widgetWindow.once('ready-to-show', () => {
        syncAuthWindowAccess();
    });
}

function registerHotkeys(): void {
    currentHotkey = (settingsService.getSettings().HOTKEY || 'F9').toUpperCase();

    if (!keyListener) {
        keyListener = new GlobalKeyboardListener();
        keyListener.addListener((event) => {
            if (event.name === currentHotkey.toUpperCase()) {
                if (event.state === 'DOWN' && dictationLifecycleState === 'idle') {
                    void handleStartDictation();
                } else if (event.state === 'UP' && dictationLifecycleState === 'recording') {
                    void handleStopDictation();
                }
            }
        });
    }
}

function createTray(): void {
    const icon = nativeImage.createEmpty();
    tray = new Tray(icon);

    const contextMenu = Menu.buildFromTemplate([
        { label: 'DictaPilot', enabled: false },
        { type: 'separator' },
        {
            label: 'Show Dashboard',
            click: () => {
                mainWindow?.show();
                mainWindow?.focus();
                mainWindow?.moveTop();
            },
        },
        {
            label: 'Show Widget',
            click: () => {
                if (currentAuthState.status === 'authenticated') {
                    widgetWindow?.showInactive();
                    return;
                }
                revealMainWindow();
            },
        },
        { type: 'separator' },
        {
            label: 'Quit DictaPilot',
            click: () => {
                isQuitting = true;
                app.quit();
            },
        },
    ]);

    tray.setToolTip('DictaPilot Dictation Engine');
    tray.setContextMenu(contextMenu);
    tray.on('click', () => {
        if (!mainWindow) {
            return;
        }
        if (mainWindow.isVisible()) {
            mainWindow.hide();
            return;
        }
        mainWindow.show();
        mainWindow.focus();
        mainWindow.moveTop();
    });
}

function registerIpcHandlers(): void {
    transcriptionService.on('transcription-update', (data) => {
        if (data.sessionId !== activeDictationSessionId && !data.isFinal) {
            return;
        }
        const processed = editingService.process(data.text);
        safeSend(mainWindow, Channels.OnTranscriptionUpdate, {
            text: processed,
            isFinal: data.isFinal,
            sessionId: data.sessionId,
        });
        safeSend(widgetWindow, Channels.OnTranscriptionUpdate, {
            text: processed,
            isFinal: data.isFinal,
            sessionId: data.sessionId,
        });
        if (data.isFinal) {
            historyService.saveResult(processed);
        }
    });

    ipcMain.handle(Channels.StartDictation, async (): Promise<DictationSessionResponse> => {
        const sessionId = await handleStartDictation();
        if (!sessionId) {
            return {
                success: false,
                error: dictationLifecycleState === 'processing'
                    ? {
                        code: 'dictation_processing',
                        message: 'DictaPilot is still finalizing the previous dictation.',
                    }
                    : {
                        code: currentAuthState.status === 'loading' ? 'auth_bootstrapping' : 'not_authenticated',
                        message: currentAuthState.status === 'loading'
                            ? 'DictaPilot is still restoring your session.'
                            : 'Sign in or create an account to start dictation.',
                    },
            };
        }
        return { success: true, data: { sessionId } };
    });

    ipcMain.handle(Channels.StopDictation, async (): Promise<IpcResponse> => {
        await handleStopDictation();
        return { success: true };
    });

    ipcMain.handle(Channels.GetSettings, async (): Promise<IpcResponse<Record<string, string>>> => ({
        success: true,
        data: settingsService.getSettings(),
    }));

    ipcMain.handle(Channels.UpdateSettings, async (_, settings: Partial<Record<string, string>>): Promise<IpcResponse<Record<string, string>>> => {
        const record = settingsRepository.updateLocal(settings);
        configureRuntimeSettings();
        void maybeSyncAuthenticatedState();
        return { success: true, data: record.values };
    });

    ipcMain.handle(Channels.GetHistory, async (): Promise<IpcResponse<Array<{ id: string; text: string; timestamp: string }>>> => ({
        success: true,
        data: historyService.getHistory(),
    }));

    ipcMain.handle(Channels.GetSelectedAudioInput, async (): Promise<IpcResponse<string>> => ({
        success: true,
        data: settingsService.getSettings().AUDIO_INPUT_DEVICE_ID || 'default',
    }));

    ipcMain.handle(Channels.SetSelectedAudioInput, async (_, deviceId: string): Promise<IpcResponse<string>> => {
        const record = settingsRepository.updateLocal({ AUDIO_INPUT_DEVICE_ID: deviceId || 'default' });
        return {
            success: true,
            data: record.values.AUDIO_INPUT_DEVICE_ID || 'default',
        };
    });

    ipcMain.handle(Channels.GetAuthState, async (): Promise<IpcResponse<AuthState>> => ({
        success: true,
        data: currentAuthState,
    }));

    ipcMain.handle(Channels.SignUp, async (_, payload: SignUpRequest): Promise<IpcResponse<AuthState>> => {
        try {
            const result = await authService.signUp(payload);
            sessionService.persist(result.session);
            await hydrateAuthenticatedState();
            return { success: true, data: currentAuthState };
        } catch (error) {
            return {
                success: false,
                error: {
                    code: getErrorCode(error, 'auth_failed'),
                    message: getErrorMessage(error, 'Sign-up failed.'),
                },
            };
        }
    });

    ipcMain.handle(Channels.SignIn, async (_, payload: SignInRequest): Promise<IpcResponse<AuthState>> => {
        try {
            const result = await authService.signIn(payload);
            sessionService.persist(result.session);
            await hydrateAuthenticatedState();
            return { success: true, data: currentAuthState };
        } catch (error) {
            return {
                success: false,
                error: {
                    code: getErrorCode(error, 'auth_failed'),
                    message: getErrorMessage(error, 'Sign-in failed.'),
                },
            };
        }
    });

    ipcMain.handle(Channels.SignInWithGoogle, async (): Promise<IpcResponse<AuthState>> => {
        try {
            const tokens = await startGoogleOAuthPkce();
            const result = await authService.completeGoogleSignIn(tokens);
            sessionService.persist(result.session);
            await hydrateAuthenticatedState();
            return { success: true, data: currentAuthState };
        } catch (error) {
            return {
                success: false,
                error: {
                    code: getErrorCode(error, 'google_sign_in_failed'),
                    message: getErrorMessage(error, 'Google sign-in failed.'),
                },
            };
        }
    });

    ipcMain.handle(Channels.SignOut, async (): Promise<IpcResponse<AuthState>> => {
        sessionService.clear();
        syncQueueStoreService.clear();
        accountProfileService.clearProfile();
        authService.signOut();
        const state = buildSignedOutState();
        setAuthState(state);
        revealMainWindow();
        return { success: true, data: state };
    });

    ipcMain.handle(Channels.UpdateSyncPreferences, async (_, update: SyncPreferencesUpdateRequest): Promise<IpcResponse<AuthState>> => {
        const sessionPayload = authService.getCurrentSession();
        if (!sessionPayload || currentAuthState.status !== 'authenticated') {
            return {
                success: false,
                error: {
                    code: 'not_authenticated',
                    message: 'Sign in before updating sync preferences.',
                },
            };
        }

        try {
            const profile = await cloudStoreService.updateSyncEnabled(sessionPayload, update.enabled);
            accountProfileService.setProfile(profile);
            if (!update.enabled) {
                syncQueueStoreService.clear();
            }
            setAuthState({
                status: 'authenticated',
                user: profile,
                sync: syncStatusFromCurrentState({
                    enabled: update.enabled,
                    status: update.enabled ? 'idle' : 'disabled',
                    errorMessage: null,
                }),
                errorMessage: null,
            });
            if (update.enabled) {
                await maybeSyncAuthenticatedState();
            }
            return { success: true, data: currentAuthState };
        } catch (error) {
            if (isSessionInvalidError(error)) {
                const recovered = await forceSignedOutRecovery('Your session expired. Sign in again to resume sync.');
                return { success: false, error: { code: 'session_invalid', message: recovered.errorMessage || 'Session expired.' } };
            }

            setSyncStatus({
                status: isOfflineError(error) ? 'offline' : 'error',
                errorMessage: getErrorMessage(error, 'Failed to update sync preferences.'),
            });
            return {
                success: false,
                error: {
                    code: 'sync_preferences_failed',
                    message: getErrorMessage(error, 'Failed to update sync preferences.'),
                },
            };
        }
    });

    ipcMain.handle(Channels.GetMainWindowState, async (): Promise<IpcResponse<MainWindowStateEvent>> => ({
        success: true,
        data: {
            isMaximized: mainWindow?.isMaximized() ?? false,
        },
    }));

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

    ipcMain.on(Channels.SendAudioData, (_, payload: { sessionId?: string; buffer: ArrayBuffer }) => {
        if (
            dictationLifecycleState !== 'recording' ||
            !payload?.sessionId ||
            payload.sessionId !== activeDictationSessionId
        ) {
            return;
        }

        const buf = Buffer.from(payload.buffer);
        transcriptionService.appendAudio(payload.sessionId, buf);

        let sumSq = 0;
        const count = buf.length / 2;
        for (let index = 0; index < buf.length; index += 2) {
            const val = buf.readInt16LE(index);
            const norm = val / 32768.0;
            sumSq += norm * norm;
        }
        const rms = count > 0 ? Math.sqrt(sumSq / count) : 0;
        safeSend(mainWindow, Channels.OnAmplitudeUpdate, rms);
        safeSend(widgetWindow, Channels.OnAmplitudeUpdate, rms);
    });
}

app.whenReady().then(async () => {
    session.defaultSession.setPermissionCheckHandler((_, permission) => permission === 'media');
    session.defaultSession.setPermissionRequestHandler((_, permission, callback) => {
        callback(permission === 'media');
    });

    createWindow();
    createWidgetWindow();
    createTray();
    registerHotkeys();
    registerIpcHandlers();
    await bootstrapAuthState();

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
    textInsertionService.resetSession(activeDictationSessionId);
});

app.on('second-instance', () => {
    if (mainWindow) {
        if (mainWindow.isMinimized()) {
            mainWindow.restore();
        }
        mainWindow.focus();
        mainWindow.show();
    }
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});
