import { useEffect, useRef, useState } from 'react';
import {
  Cloud,
  CloudOff,
  Copy,
  Eye,
  EyeOff,
  History,
  LogOut,
  Maximize2,
  Menu,
  Mic,
  Minimize2,
  Minus,
  RefreshCw,
  Settings,
  ShieldCheck,
  Square,
  Trash2,
  Wand2,
  X,
} from 'lucide-react';
import {
  DEFAULT_SYNC_PREFERENCES,
  LOADING_AUTH_STATE,
  type AuthState,
  type SignInPayload,
  type SignUpPayload,
} from '@shared/auth';
import {
  isAuthenticatedState,
  resolveDesktopAuthGateView,
  type AuthMode,
} from '@shared/authFlow';
import {
  applyInternalEditorSessionTranscript,
  captureInternalEditorSession,
  type InternalEditorSessionSnapshot,
} from '@shared/internalEditorSession';
import type { AudioInputDeviceInfo } from '@shared/ipc';
import {
  DESKTOP_SETTING_DEFINITIONS,
  type DesktopSettingDefinition,
  type DesktopSettings,
} from '@shared/settings';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { AuthOnboarding } from './AuthOnboarding';
import { MicrophoneController } from './microphoneController';
import './App.css';

type DictationStatus = 'idle' | 'recording' | 'processing' | 'error';
type SidebarTab = 'history' | 'settings';
type FeedbackTone = 'error' | 'success' | 'info';

interface HistoryItem {
  id: string;
  text: string;
  timestamp: string;
}

interface AuthFormState {
  displayName: string;
  email: string;
  password: string;
  confirmPassword: string;
}

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const SETTING_GROUPS = DESKTOP_SETTING_DEFINITIONS.reduce<Array<{
  group: string;
  definitions: DesktopSettingDefinition[];
}>>((groups, definition) => {
  const existing = groups.find((group) => group.group === definition.group);
  if (existing) {
    existing.definitions.push(definition);
    return groups;
  }

  groups.push({ group: definition.group, definitions: [definition] });
  return groups;
}, []);

const EMPTY_AUTH_FORM: AuthFormState = {
  displayName: '',
  email: '',
  password: '',
  confirmPassword: '',
};

function getSyncLabel(state: AuthState['sync']['status']): string {
  switch (state) {
    case 'syncing':
      return 'Syncing';
    case 'offline':
      return 'Offline';
    case 'error':
      return 'Attention needed';
    case 'disabled':
      return 'Sync off';
    default:
      return 'Connected';
  }
}

function formatLastSyncedAt(value?: string | null): string {
  if (!value) {
    return 'Not yet';
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return 'Not yet';
  }

  return parsed.toLocaleString();
}

function App() {
  const [dictationState, setDictationState] = useState<DictationStatus>('idle');
  const [transcription, setTranscription] = useState('');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<SidebarTab>('history');
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [settings, setSettings] = useState<DesktopSettings>({} as DesktopSettings);
  const [revealedKeys, setRevealedKeys] = useState<Record<string, boolean>>({});
  const [isWindowMaximized, setIsWindowMaximized] = useState(false);
  const [authState, setAuthState] = useState<AuthState>({ ...LOADING_AUTH_STATE });
  const [authMode, setAuthMode] = useState<AuthMode>('sign-in');
  const [authForm, setAuthForm] = useState<AuthFormState>(EMPTY_AUTH_FORM);
  const [authFeedback, setAuthFeedback] = useState<string | null>(null);
  const [authFeedbackTone, setAuthFeedbackTone] = useState<FeedbackTone>('error');
  const [isAuthSubmitting, setIsAuthSubmitting] = useState(false);
  const [isSyncSubmitting, setIsSyncSubmitting] = useState(false);
  const [audioDevices, setAudioDevices] = useState<AudioInputDeviceInfo[]>([]);
  const [selectedAudioInputId, setSelectedAudioInputId] = useState('default');
  const [resolvedAudioInputId, setResolvedAudioInputId] = useState('default');
  const [microphoneNotice, setMicrophoneNotice] = useState<string | null>(null);
  const stateRef = useRef<DictationStatus>('idle');
  const transcriptionRef = useRef('');
  const authStateRef = useRef<AuthState>({ ...LOADING_AUTH_STATE });
  const isAuthenticatedRef = useRef(false);
  const activeSessionIdRef = useRef<string | null>(null);
  const microphoneControllerRef = useRef<MicrophoneController | null>(null);
  const transcriptionInputRef = useRef<HTMLTextAreaElement | null>(null);
  const internalEditorSessionRef = useRef<InternalEditorSessionSnapshot | null>(null);

  stateRef.current = dictationState;
  transcriptionRef.current = transcription;

  const isAuthenticated = isAuthenticatedState(authState);
  const authGateView = resolveDesktopAuthGateView(authState);
  authStateRef.current = authState;
  isAuthenticatedRef.current = isAuthenticated;

  const setFeedback = (message: string | null, tone: FeedbackTone = 'error') => {
    setAuthFeedback(message);
    setAuthFeedbackTone(tone);
  };

  const resetInternalEditorSession = () => {
    internalEditorSessionRef.current = null;
  };

  const captureInternalEditorSelection = (sessionId: string) => {
    const textarea = transcriptionInputRef.current;
    const currentValue = transcriptionRef.current;
    const textareaFocused = Boolean(textarea && document.activeElement === textarea);

    internalEditorSessionRef.current = captureInternalEditorSession(
      sessionId,
      currentValue,
      textareaFocused ? textarea?.selectionStart : 0,
      textareaFocused ? textarea?.selectionEnd : currentValue.length,
    );

    if (!textareaFocused) {
      setTranscription('');
    }
  };

  const applyInternalEditorTranscript = (sessionId: string | null | undefined, text: string) => {
    if (!sessionId) {
      setTranscription(text);
      return;
    }

    const session = internalEditorSessionRef.current;
    if (!session || session.sessionId !== sessionId) {
      setTranscription(text);
      return;
    }

    const next = applyInternalEditorSessionTranscript(session, text);
    setTranscription(next.value);

    requestAnimationFrame(() => {
      const textarea = transcriptionInputRef.current;
      if (!textarea || document.activeElement !== textarea) {
        return;
      }
      textarea.selectionStart = next.selectionStart;
      textarea.selectionEnd = next.selectionEnd;
    });
  };

  const hydrateAppState = async () => {
    const [settingsRes, historyRes, authRes, mainWindowStateRes] = await Promise.all([
      window.dictationAPI.getSettings(),
      window.dictationAPI.getHistory(),
      window.dictationAPI.getAuthState(),
      window.dictationAPI.getMainWindowState(),
    ]);

    if (settingsRes.success && settingsRes.data) {
      setSettings(settingsRes.data);
    }

    if (historyRes.success && historyRes.data) {
      setHistory(historyRes.data);
    }

    if (authRes.success && authRes.data) {
      setAuthState(authRes.data);
    }

    if (mainWindowStateRes.success) {
      setIsWindowMaximized(Boolean(mainWindowStateRes.data?.isMaximized));
    }
  };

  const refreshAudioDevices = async (requestPermission = false) => {
    if (!microphoneControllerRef.current) {
      return;
    }
    const devices = await microphoneControllerRef.current.refreshDevices(requestPermission);
    setAudioDevices(devices);
    setResolvedAudioInputId(microphoneControllerRef.current.getResolvedDeviceId());
  };

  const toggleDictation = async () => {
    if (!isAuthenticatedRef.current) {
      const currentAuth = authStateRef.current;
      setFeedback(
        currentAuth.status === 'loading'
          ? 'DictaPilot is still restoring your session.'
          : 'Sign in or create an account to start desktop dictation.',
        'info',
      );
      return;
    }

    if (stateRef.current === 'idle') {
      setMicrophoneNotice(null);
      const response = await window.dictationAPI.startDictation();
      if (!response.success || !response.data?.sessionId) {
        setFeedback(response.error?.message ?? 'Failed to start dictation.');
        return;
      }

      activeSessionIdRef.current = response.data.sessionId;
      try {
        await microphoneControllerRef.current?.startSession(response.data.sessionId);
      } catch {
        await window.dictationAPI.stopDictation();
      }
      return;
    }

    if (stateRef.current === 'recording') {
      const sessionId = activeSessionIdRef.current;
      if (sessionId) {
        await microphoneControllerRef.current?.stopSession(sessionId);
      }
      await window.dictationAPI.stopDictation();
    }
  };

  useEffect(() => {
    const controller = new MicrophoneController({
      onAudioData: (sessionId, buffer) => {
        window.dictationAPI.sendAudioData(sessionId, buffer);
      },
      onDevicesChanged: (devices) => {
        setAudioDevices(devices);
        setResolvedAudioInputId(controller.getResolvedDeviceId());
      },
      onNotice: (message) => setMicrophoneNotice(message),
      onError: (message) => {
        setMicrophoneNotice(message);
        setDictationState('error');
      },
    });
    microphoneControllerRef.current = controller;

    void hydrateAppState().then(async () => {
      const selectedResponse = await window.dictationAPI.getSelectedAudioInput();
      const selectedDeviceId = selectedResponse.success && selectedResponse.data ? selectedResponse.data : 'default';
      setSelectedAudioInputId(selectedDeviceId);
      await controller.initialize(selectedDeviceId);
      setAudioDevices(controller.getDevices());
      setResolvedAudioInputId(controller.getResolvedDeviceId());
    });

    const unsubState = window.dictationAPI.onStateChange((data) => {
      setDictationState(data.state);
      activeSessionIdRef.current = data.sessionId ?? activeSessionIdRef.current;

      if (data.state === 'recording') {
        if (data.sessionId) {
          // Anchor preview updates to the original selection so repeated transcript refreshes
          // replace only this session's text instead of compounding older desktop content.
          captureInternalEditorSelection(data.sessionId);
        }
      }

      if (data.state === 'idle') {
        activeSessionIdRef.current = null;
        resetInternalEditorSession();
        void hydrateAppState();
      }
    });

    const unsubTranscription = window.dictationAPI.onTranscriptionUpdate((data) => {
      if (
        data.sessionId &&
        data.sessionId !== activeSessionIdRef.current &&
        data.sessionId !== internalEditorSessionRef.current?.sessionId
      ) {
        return;
      }
      applyInternalEditorTranscript(data.sessionId, data.text);
      if (data.isFinal) {
        setTimeout(() => {
          void hydrateAppState();
        }, 500);
      }
    });

    const unsubHotkey = window.dictationAPI.onHotkeyPress(() => {
      void toggleDictation();
    });

    const unsubAuth = window.dictationAPI.onAuthStateChange((nextState) => {
      setAuthState(nextState);
      if (nextState.status === 'authenticated') {
        setFeedback(null);
      }
    });

    const unsubSync = window.dictationAPI.onSyncStatusChange((nextSync) => {
      setAuthState((current) => ({
        ...current,
        sync: {
          ...DEFAULT_SYNC_PREFERENCES,
          ...current.sync,
          ...nextSync,
        },
      }));
    });

    const unsubMainWindowState = window.dictationAPI.onMainWindowStateChange((data) => {
      setIsWindowMaximized(Boolean(data.isMaximized));
    });

    return () => {
      unsubState();
      unsubTranscription();
      unsubHotkey();
      unsubAuth();
      unsubSync();
      unsubMainWindowState();
      void microphoneControllerRef.current?.dispose();
      microphoneControllerRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!isAuthenticated) {
      setIsSidebarOpen(false);
    }
  }, [isAuthenticated]);

  const handleSettingChange = async (key: string, value: string) => {
    const optimisticSettings = { ...settings, [key]: value };
    setSettings(optimisticSettings);

    const response = await window.dictationAPI.updateSettings({ [key]: value });
    if (response.success && response.data) {
      setSettings(response.data);
      return;
    }

    setFeedback(response.error?.message ?? 'Failed to update the setting.');
  };

  const handleAuthFieldChange = (key: keyof AuthFormState, value: string) => {
    setAuthForm((current) => ({ ...current, [key]: value }));
  };

  const handleAuthModeChange = (mode: AuthMode) => {
    setAuthMode(mode);
    setFeedback(null);
  };

  const toggleSecretVisibility = (key: string) => {
    setRevealedKeys((current) => ({ ...current, [key]: !current[key] }));
  };

  const renderSecretInput = (
    key: string,
    value: string,
    placeholder: string,
    onChange: (value: string) => void,
  ) => (
    <div className="secret-input">
      <input
        className="glass-input"
        type={revealedKeys[key] ? 'text' : 'password'}
        value={value}
        placeholder={placeholder}
        onChange={(event) => onChange(event.target.value)}
      />
      <button
        className="secret-toggle"
        type="button"
        onClick={() => toggleSecretVisibility(key)}
        aria-label={revealedKeys[key] ? 'Hide secret' : 'Show secret'}
      >
        {revealedKeys[key] ? <EyeOff size={16} /> : <Eye size={16} />}
      </button>
    </div>
  );

  const renderSettingControl = (definition: DesktopSettingDefinition) => {
    const value = settings[definition.key] ?? '';

    if (definition.input === 'toggle') {
      return (
        <label className="toggle-control">
          <input
            type="checkbox"
            checked={value === '1'}
            onChange={(event) => {
              void handleSettingChange(definition.key, event.target.checked ? '1' : '0');
            }}
          />
          <span>{value === '1' ? 'Enabled' : 'Disabled'}</span>
        </label>
      );
    }

    if (definition.input === 'select') {
      return (
        <select
          className="glass-input"
          value={value}
          onChange={(event) => {
            void handleSettingChange(definition.key, event.target.value);
          }}
        >
          {definition.options?.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      );
    }

    if (definition.input === 'textarea') {
      return (
        <textarea
          className="glass-input glass-textarea"
          rows={4}
          value={value}
          placeholder={definition.placeholder}
          onChange={(event) => {
            void handleSettingChange(definition.key, event.target.value);
          }}
        />
      );
    }

    if (definition.input === 'password') {
      return renderSecretInput(
        `setting:${definition.key}`,
        value,
        definition.placeholder ?? '',
        (nextValue) => {
          void handleSettingChange(definition.key, nextValue);
        },
      );
    }

    return (
      <input
        className="glass-input"
        type={definition.input === 'number' ? 'number' : 'text'}
        value={value}
        placeholder={definition.placeholder}
        onChange={(event) => {
          void handleSettingChange(definition.key, event.target.value);
        }}
      />
    );
  };

  const handleEmailAuthSubmit = async () => {
    if (!authForm.email.trim() || !authForm.password) {
      setFeedback('Email and password are required.');
      return;
    }

    if (authMode === 'sign-up' && authForm.password !== authForm.confirmPassword) {
      setFeedback('Confirm password must match the password.');
      return;
    }

    setIsAuthSubmitting(true);
    setFeedback(null);

    const response = authMode === 'sign-up'
      ? await window.dictationAPI.signUp({
        email: authForm.email.trim(),
        password: authForm.password,
        confirmPassword: authForm.confirmPassword,
        displayName: authForm.displayName.trim() || undefined,
      } satisfies SignUpPayload)
      : await window.dictationAPI.signIn({
        email: authForm.email.trim(),
        password: authForm.password,
      } satisfies SignInPayload);

    setIsAuthSubmitting(false);

    if (!response.success || !response.data) {
      setFeedback(response.error?.message ?? 'Authentication failed.');
      return;
    }

    setAuthState(response.data);
    setAuthForm((current) => ({
      ...current,
      password: '',
      confirmPassword: '',
    }));
  };

  const handleGoogleSignIn = async () => {
    setIsAuthSubmitting(true);
    setFeedback(null);

    const response = await window.dictationAPI.signInWithGoogle();
    setIsAuthSubmitting(false);

    if (!response.success || !response.data) {
      setFeedback(response.error?.message ?? 'Google sign-in failed.');
      return;
    }

    setAuthState(response.data);
  };

  const handleSignOut = async () => {
    setIsAuthSubmitting(true);
    const response = await window.dictationAPI.signOut();
    setIsAuthSubmitting(false);

    if (!response.success || !response.data) {
      setFeedback(response.error?.message ?? 'Sign-out failed.');
      return;
    }

    setAuthState(response.data);
    setFeedback('Signed out. Sign in again to continue using DictaPilot.', 'info');
  };

  const handleSyncToggle = async (enabled: boolean) => {
    setIsSyncSubmitting(true);
    setFeedback(null);

    const response = await window.dictationAPI.updateSyncPreferences({ enabled });
    setIsSyncSubmitting(false);

    if (!response.success || !response.data) {
      setFeedback(response.error?.message ?? 'Failed to update sync preferences.');
      return;
    }

    setAuthState(response.data);
    setFeedback(
      enabled
        ? 'Sync enabled. DictaPilot will reconcile this device with your account.'
        : 'Sync disabled. DictaPilot stays signed in, but this device stops cloud replication until you enable it again.',
      'success',
    );
  };

  const combinedFeedback = authFeedback
    ?? authState.errorMessage
    ?? authState.sync.errorMessage
    ?? null;
  const combinedFeedbackTone: FeedbackTone = authFeedback
    ? authFeedbackTone
    : authState.errorMessage
      ? 'error'
      : authState.sync.status === 'offline'
        ? 'info'
        : 'error';

  const syncStatusLabel = getSyncLabel(authState.sync.status);
  const accountTitle = authState.user?.displayName?.trim() || authState.user?.email || 'Account';
  const resolvedAudioInputLabel = audioDevices.find((device) => device.deviceId === resolvedAudioInputId)?.label || 'System default microphone';

  const handleAudioInputChange = async (deviceId: string) => {
    const nextDeviceId = deviceId || 'default';
    setSelectedAudioInputId(nextDeviceId);
    await window.dictationAPI.setSelectedAudioInput(nextDeviceId);
    await microphoneControllerRef.current?.setPreferredDeviceId(nextDeviceId);
    setResolvedAudioInputId(microphoneControllerRef.current?.getResolvedDeviceId() || 'default');
    setMicrophoneNotice(nextDeviceId === 'default' ? 'Using the system default microphone.' : null);
  };

  return (
    <div className="app-shell">
      <div className="title-bar">
        <div className="title-drag-area">DictaPilot</div>
        <div className="window-controls">
          <button
            className="window-control-btn"
            type="button"
            onClick={() => {
              void window.dictationAPI.minimizeMainWindow();
            }}
            aria-label="Minimize window"
            title="Minimize"
          >
            <Minus size={16} />
          </button>
          <button
            className="window-control-btn"
            type="button"
            onClick={() => {
              void window.dictationAPI.toggleMainWindowMaximize();
            }}
            aria-label={isWindowMaximized ? 'Restore window' : 'Maximize window'}
            title={isWindowMaximized ? 'Restore' : 'Maximize'}
          >
            {isWindowMaximized ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
          </button>
          <button
            className="window-control-btn close"
            type="button"
            onClick={() => {
              void window.dictationAPI.closeMainWindow();
            }}
            aria-label="Close window"
            title="Close"
          >
            <X size={15} />
          </button>
        </div>
      </div>

      <main className={cn('main-stage', isSidebarOpen && 'sidebar-open', authGateView !== 'app' && 'auth-gated')}>
        {authGateView === 'bootstrapping' && (
          <section className="auth-bootstrap glass">
            <div className="auth-bootstrap-spinner">
              <RefreshCw size={20} />
            </div>
            <p className="account-kicker">Restoring session</p>
            <h1>Checking your desktop access</h1>
            <p>DictaPilot is validating your saved account session before unlocking the app.</p>
          </section>
        )}

        {authGateView === 'onboarding' && (
          <AuthOnboarding
            authMode={authMode}
            authForm={authForm}
            feedback={combinedFeedback}
            feedbackTone={combinedFeedbackTone}
            isSubmitting={isAuthSubmitting}
            onModeChange={handleAuthModeChange}
            onFieldChange={handleAuthFieldChange}
            onEmailSubmit={() => {
              void handleEmailAuthSubmit();
            }}
            onGoogleSignIn={() => {
              void handleGoogleSignIn();
            }}
            renderSecretInput={renderSecretInput}
          />
        )}

        {authGateView === 'app' && (
          <>
            <header className="stage-header">
              <div className="stage-status-row">
                <div className="status-indicator">
                  <span className={cn('status-dot', dictationState)}></span>
                  <span className="status-text">{dictationState}</span>
                </div>
                <div className={cn('sync-pill', authState.sync.status)}>
                  {authState.sync.status === 'disabled' ? <CloudOff size={14} /> : <Cloud size={14} />}
                  <span>{syncStatusLabel}</span>
                </div>
              </div>
              <button className="icon-btn" type="button" onClick={() => setIsSidebarOpen(true)} aria-label="Open sidebar">
                <Menu size={24} />
              </button>
            </header>

            <div className="center-stage">
              <div className="input-container glass">
                <textarea
                  ref={transcriptionInputRef}
                  className="transcription-input"
                  value={transcription}
                  onChange={(event) => setTranscription(event.target.value)}
                  placeholder={`Press ${(settings.HOTKEY || 'F9').toUpperCase()} or click the mic to start...`}
                />
                {transcription && (
                  <div className="action-bar fade-in">
                    <button
                      className="action-btn"
                      type="button"
                      onClick={() => {
                        void navigator.clipboard.writeText(transcription);
                      }}
                    >
                      <Copy size={16} /> Copy
                    </button>
                    <button className="action-btn" type="button">
                      <Wand2 size={16} /> Refine
                    </button>
                    <button className="action-btn text-danger" type="button" onClick={() => setTranscription('')}>
                      <Trash2 size={16} /> Clear
                    </button>
                  </div>
                )}
              </div>

              <div className="mic-wrapper">
                <button className={cn('mic-btn', dictationState)} type="button" onClick={() => { void toggleDictation(); }}>
                  {dictationState === 'recording' ? <Square size={32} /> : <Mic size={32} />}
                </button>
                {dictationState === 'recording' && <div className="mic-rings"></div>}
              </div>
            </div>
          </>
        )}
      </main>

      {isAuthenticated && (
        <>
          <div className={cn('sidebar-backdrop', isSidebarOpen && 'visible')} onClick={() => setIsSidebarOpen(false)}></div>

          <aside className={cn('sidebar glass', isSidebarOpen && 'open')}>
            <div className="sidebar-header">
              <div className="tab-switcher">
                <button
                  className={cn('tab-btn', activeTab === 'history' && 'active')}
                  type="button"
                  onClick={() => {
                    setActiveTab('history');
                    void hydrateAppState();
                  }}
                >
                  <History size={16} /> History
                </button>
                <button
                  className={cn('tab-btn', activeTab === 'settings' && 'active')}
                  type="button"
                  onClick={() => setActiveTab('settings')}
                >
                  <Settings size={16} /> Settings
                </button>
              </div>
              <button className="icon-btn" type="button" onClick={() => setIsSidebarOpen(false)} aria-label="Close sidebar">
                <X size={24} />
              </button>
            </div>

            <div className="sidebar-content">
              {activeTab === 'history' && (
                <div className="history-list fade-in">
                  {history.length === 0 ? (
                    <p className="empty-state">No history yet.</p>
                  ) : (
                    history.map((item) => (
                      <div
                        className="history-card"
                        key={item.id}
                        onClick={() => {
                          void navigator.clipboard.writeText(item.text);
                        }}
                      >
                        <p className="history-text">{item.text}</p>
                        <span className="history-time">{new Date(item.timestamp).toLocaleTimeString()}</span>
                      </div>
                    ))
                  )}
                </div>
              )}

              {activeTab === 'settings' && (
                <div className="settings-panel fade-in">
                  <section className="account-section">
                    <div className="account-hero">
                      <div>
                        <p className="account-kicker">Authenticated Workspace</p>
                        <h2>Your DictaPilot account</h2>
                      </div>
                      <div className="account-status-chip connected">
                        <ShieldCheck size={14} />
                        <span>Authenticated</span>
                      </div>
                    </div>

                    {combinedFeedback && (
                      <div className={cn('feedback-banner', combinedFeedbackTone)}>
                        {combinedFeedbackTone === 'info' ? <RefreshCw size={15} /> : <ShieldCheck size={15} />}
                        <span>{combinedFeedback}</span>
                      </div>
                    )}

                    {authState.user && (
                      <div className="account-card">
                        <div className="account-card-head">
                          <div className="account-avatar">
                            {accountTitle.charAt(0).toUpperCase()}
                          </div>
                          <div className="account-copy">
                            <h3>{accountTitle}</h3>
                            <p>{authState.user.email}</p>
                          </div>
                        </div>

                        <div className="account-meta-row">
                          <span className={cn('meta-badge', authState.sync.status)}>
                            {authState.sync.status === 'disabled' ? <CloudOff size={12} /> : <Cloud size={12} />}
                            {syncStatusLabel}
                          </span>
                          <span className="meta-badge">{authState.user.provider === 'google' ? 'Google' : 'Email'}</span>
                          {authState.user.emailVerified && (
                            <span className="meta-badge verified">
                              <ShieldCheck size={12} />
                              Verified
                            </span>
                          )}
                        </div>

                        <div className="sync-control-card">
                          <div>
                            <p className="sync-control-title">Cross-device sync</p>
                            <p className="sync-control-copy">
                              Keep settings, snippets, and dictionary data tied to this account. Turn sync off
                              if this device should stop cloud replication.
                            </p>
                          </div>
                          <label className="toggle-control sync-toggle">
                            <input
                              type="checkbox"
                              checked={authState.sync.enabled}
                              disabled={isSyncSubmitting}
                              onChange={(event) => {
                                void handleSyncToggle(event.target.checked);
                              }}
                            />
                            <span>{isSyncSubmitting ? 'Updating...' : authState.sync.enabled ? 'Enabled' : 'Disabled'}</span>
                          </label>
                        </div>

                        <div className="account-stats">
                          <div className="account-stat">
                            <span>Pending operations</span>
                            <strong>{authState.sync.pendingOperations}</strong>
                          </div>
                          <div className="account-stat">
                            <span>Last sync</span>
                            <strong>{formatLastSyncedAt(authState.sync.lastSyncedAt)}</strong>
                          </div>
                        </div>

                        <button
                          className="account-action secondary"
                          type="button"
                          onClick={() => {
                            void handleSignOut();
                          }}
                          disabled={isAuthSubmitting}
                        >
                          <LogOut size={16} />
                          Sign out
                        </button>
                      </div>
                    )}
                  </section>

                  <section className="settings-section">
                    <div className="settings-section-header">
                      <h3>Microphone</h3>
                    </div>
                    <div className="settings-section-body">
                      <div className="setting-group">
                        <div className="setting-label-row">
                          <label htmlFor="audio-input-select">Audio Input</label>
                          <span className="setting-key">AUDIO_INPUT_DEVICE_ID</span>
                        </div>
                        <p className="setting-description">
                          Choose the system default microphone or lock DictaPilot to a specific input device.
                        </p>
                        <select
                          id="audio-input-select"
                          className="glass-input"
                          value={selectedAudioInputId}
                          onChange={(event) => {
                            void handleAudioInputChange(event.target.value);
                          }}
                        >
                          {audioDevices.map((device) => (
                            <option key={device.deviceId} value={device.deviceId}>
                              {device.label}
                            </option>
                          ))}
                        </select>
                      </div>

                      <div className="audio-input-meta">
                        <span className="audio-input-pill">Resolved input: {resolvedAudioInputLabel}</span>
                        <button
                          className="action-btn"
                          type="button"
                          onClick={() => {
                            void refreshAudioDevices(true);
                          }}
                        >
                          <RefreshCw size={14} /> Refresh devices
                        </button>
                      </div>

                      {microphoneNotice && (
                        <div className="feedback-banner info">
                          <RefreshCw size={15} />
                          <span>{microphoneNotice}</span>
                        </div>
                      )}
                    </div>
                  </section>

                  {SETTING_GROUPS.map((group) => (
                    <section className="settings-section" key={group.group}>
                      <div className="settings-section-header">
                        <h3>{group.group}</h3>
                      </div>
                      <div className="settings-section-body">
                        {group.definitions.map((definition) => (
                          <div className="setting-group" key={definition.key}>
                            <div className="setting-label-row">
                              <label htmlFor={definition.key}>{definition.label}</label>
                              <span className="setting-key">{definition.key}</span>
                            </div>
                            <p className="setting-description">{definition.description}</p>
                            {renderSettingControl(definition)}
                          </div>
                        ))}
                      </div>
                    </section>
                  ))}
                </div>
              )}
            </div>
          </aside>
        </>
      )}
    </div>
  );
}

export default App;
