import { useEffect, useRef, useState } from 'react';
import {
  Cloud,
  CloudOff,
  Copy,
  Eye,
  EyeOff,
  History,
  LogOut,
  Mail,
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
  UserRound,
  Wand2,
  X,
} from 'lucide-react';
import {
  DEFAULT_SYNC_PREFERENCES,
  SIGNED_OUT_AUTH_STATE,
  type AuthState,
  type SignInPayload,
  type SignUpPayload,
} from '@shared/auth';
import type { AudioInputDeviceInfo } from '@shared/ipc';
import {
  DESKTOP_SETTING_DEFINITIONS,
  type DesktopSettingDefinition,
  type DesktopSettings,
} from '@shared/settings';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { MicrophoneController } from './microphoneController';
import './App.css';

type DictationStatus = 'idle' | 'recording' | 'processing' | 'error';
type SidebarTab = 'history' | 'settings';
type AuthMode = 'sign-in' | 'sign-up';
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
      return 'Local only';
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
  const [authState, setAuthState] = useState<AuthState>({ ...SIGNED_OUT_AUTH_STATE });
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
  const activeSessionIdRef = useRef<string | null>(null);
  const microphoneControllerRef = useRef<MicrophoneController | null>(null);

  stateRef.current = dictationState;

  const setFeedback = (message: string | null, tone: FeedbackTone = 'error') => {
    setAuthFeedback(message);
    setAuthFeedbackTone(tone);
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
    if (stateRef.current === 'idle') {
      setTranscription('');
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
        setTranscription('');
      }

      if (data.state === 'idle') {
        activeSessionIdRef.current = null;
      }

      if (data.state === 'idle') {
        void hydrateAppState();
      }
    });

    const unsubTranscription = window.dictationAPI.onTranscriptionUpdate((data) => {
      if (data.sessionId && activeSessionIdRef.current && data.sessionId !== activeSessionIdRef.current) {
        return;
      }
      setTranscription(data.text);
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
    setFeedback(
      authMode === 'sign-up' ? 'Account created. Sync is ready when you enable it.' : 'Signed in successfully.',
      'success',
    );
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
    setFeedback('Google account connected.', 'success');
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
    setFeedback('Signed out. Local-only mode remains available on this device.', 'info');
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
        ? 'Sync enabled. DictaPilot will reconcile local data with your account.'
        : 'Sync disabled. DictaPilot will stay local-only until you turn it back on.',
      'success',
    );
  };

  const combinedFeedback = authFeedback
    ?? authState.errorMessage
    ?? authState.sync.errorMessage
    ?? null;
  const combinedFeedbackTone = authFeedback
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

      <main className={cn('main-stage', isSidebarOpen && 'sidebar-open')}>
        <header className="stage-header">
          <div className="stage-status-row">
            <div className="status-indicator">
              <span className={cn('status-dot', dictationState)}></span>
              <span className="status-text">{dictationState}</span>
            </div>
            <div className={cn('sync-pill', authState.sync.status)}>
              {authState.sync.status === 'disabled' ? <CloudOff size={14} /> : <Cloud size={14} />}
              <span>{authState.status === 'authenticated' ? syncStatusLabel : 'Local only'}</span>
            </div>
          </div>
          <button className="icon-btn" type="button" onClick={() => setIsSidebarOpen(true)} aria-label="Open sidebar">
            <Menu size={24} />
          </button>
        </header>

        <div className="center-stage">
          <div className="input-container glass">
            <textarea
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
      </main>

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
                    <p className="account-kicker">Account &amp; Sync</p>
                    <h2>Bring DictaPilot with you</h2>
                  </div>
                  <div className={cn('account-status-chip', authState.status === 'authenticated' ? 'connected' : 'local-only')}>
                    {authState.status === 'authenticated' ? <ShieldCheck size={14} /> : <CloudOff size={14} />}
                    <span>{authState.status === 'authenticated' ? 'Authenticated' : 'Local only'}</span>
                  </div>
                </div>

                {combinedFeedback && (
                  <div className={cn('feedback-banner', combinedFeedbackTone)}>
                    {combinedFeedbackTone === 'info' ? <Mail size={15} /> : <RefreshCw size={15} />}
                    <span>{combinedFeedback}</span>
                  </div>
                )}

                {authState.status === 'authenticated' && authState.user ? (
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
                          Keep settings, snippets, and dictionary data in sync. Signed-out mode still stays local.
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
                ) : (
                  <div className="auth-panel">
                    <div className="auth-mode-switch">
                      <button
                        className={cn('auth-mode-btn', authMode === 'sign-in' && 'active')}
                        type="button"
                        onClick={() => {
                          setAuthMode('sign-in');
                          setFeedback(null);
                        }}
                      >
                        Sign in
                      </button>
                      <button
                        className={cn('auth-mode-btn', authMode === 'sign-up' && 'active')}
                        type="button"
                        onClick={() => {
                          setAuthMode('sign-up');
                          setFeedback(null);
                        }}
                      >
                        Create account
                      </button>
                    </div>

                    <div className="auth-grid">
                      {authMode === 'sign-up' && (
                        <div className="setting-group">
                          <label htmlFor="auth-display-name">Display name</label>
                          <input
                            id="auth-display-name"
                            className="glass-input"
                            type="text"
                            value={authForm.displayName}
                            placeholder="How should DictaPilot label this account?"
                            onChange={(event) => handleAuthFieldChange('displayName', event.target.value)}
                          />
                        </div>
                      )}

                      <div className="setting-group">
                        <label htmlFor="auth-email">Email</label>
                        <input
                          id="auth-email"
                          className="glass-input"
                          type="email"
                          value={authForm.email}
                          placeholder="name@example.com"
                          onChange={(event) => handleAuthFieldChange('email', event.target.value)}
                        />
                      </div>

                      <div className="setting-group">
                        <label htmlFor="auth-password">Password</label>
                        {renderSecretInput('auth-password', authForm.password, 'Enter password', (value) => {
                          handleAuthFieldChange('password', value);
                        })}
                      </div>

                      {authMode === 'sign-up' && (
                        <div className="setting-group">
                          <label htmlFor="auth-confirm-password">Confirm password</label>
                          {renderSecretInput('auth-confirm-password', authForm.confirmPassword, 'Confirm password', (value) => {
                            handleAuthFieldChange('confirmPassword', value);
                          })}
                        </div>
                      )}
                    </div>

                    <button
                      className="account-action primary"
                      type="button"
                      onClick={() => {
                        void handleEmailAuthSubmit();
                      }}
                      disabled={isAuthSubmitting}
                    >
                      <UserRound size={16} />
                      {isAuthSubmitting
                        ? 'Working...'
                        : authMode === 'sign-up'
                          ? 'Create account'
                          : 'Sign in'}
                    </button>

                    <div className="auth-divider">
                      <span></span>
                      <p>or</p>
                      <span></span>
                    </div>

                    <button
                      className="account-action google"
                      type="button"
                      onClick={() => {
                        void handleGoogleSignIn();
                      }}
                      disabled={isAuthSubmitting}
                    >
                      <Mail size={16} />
                      Continue with Google
                    </button>

                    <p className="account-footnote">
                      Staying signed out keeps DictaPilot fully local. Sign in only if you want cloud-backed continuity.
                    </p>
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
    </div>
  );
}

export default App;
