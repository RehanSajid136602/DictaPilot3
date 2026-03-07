import { memo, startTransition, useCallback, useDeferredValue, useEffect, useRef, useState } from 'react';
import {
  Copy,
  Eye,
  EyeOff,
  History,
  Maximize2,
  Menu,
  Mic,
  Minimize2,
  Minus,
  Settings,
  Square,
  Trash2,
  Wand2,
  X,
} from 'lucide-react';
import {
  DESKTOP_SETTING_DEFINITIONS,
  type DesktopSettingDefinition,
  type DesktopSettings,
} from '@shared/settings';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import './App.css';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

type SidebarTab = 'history' | 'settings';

interface HistoryItem {
  id: string;
  text: string;
  timestamp: string;
}

const HISTORY_CHUNK_SIZE = 12;
const SIDEBAR_CONTENT_DELAY_MS = 140;
const SIDEBAR_ANIMATION_MS = 240;

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

interface HistoryPanelProps {
  history: HistoryItem[];
  visibleCount: number;
  onShowMore: () => void;
}

const HistoryPanel = memo(function HistoryPanel({ history, visibleCount, onShowMore }: HistoryPanelProps) {
  const visibleHistory = history.slice(0, visibleCount);

  if (history.length === 0) {
    return (
      <div className="history-list fade-in">
        <p className="empty-state">No history yet.</p>
      </div>
    );
  }

  return (
    <div className="history-list fade-in">
      {visibleHistory.map((item) => (
        <div className="history-card" key={item.id} onClick={() => navigator.clipboard.writeText(item.text)}>
          <p className="history-text">{item.text}</p>
          <span className="history-time">{new Date(item.timestamp).toLocaleTimeString()}</span>
        </div>
      ))}
      {visibleCount < history.length && (
        <button className="show-more-btn" type="button" onClick={onShowMore}>
          Show more
        </button>
      )}
    </div>
  );
});

interface SettingsPanelProps {
  settings: DesktopSettings;
  draftSettings: DesktopSettings;
  revealedKeys: Record<string, boolean>;
  onDraftChange: (key: string, value: string) => void;
  onImmediateChange: (key: string, value: string) => void;
  onCommitDraft: (key: string, value?: string) => void;
  onToggleSecretVisibility: (key: string) => void;
}

const SettingsPanel = memo(function SettingsPanel({
  settings,
  draftSettings,
  revealedKeys,
  onDraftChange,
  onImmediateChange,
  onCommitDraft,
  onToggleSecretVisibility,
}: SettingsPanelProps) {
  return (
    <div className="settings-panel fade-in">
      {SETTING_GROUPS.map((group) => (
        <SettingsSection
          key={group.group}
          group={group.group}
          definitions={group.definitions}
          settings={settings}
          draftSettings={draftSettings}
          revealedKeys={revealedKeys}
          onDraftChange={onDraftChange}
          onImmediateChange={onImmediateChange}
          onCommitDraft={onCommitDraft}
          onToggleSecretVisibility={onToggleSecretVisibility}
        />
      ))}
    </div>
  );
});

interface SettingsSectionProps extends SettingsPanelProps {
  group: string;
  definitions: DesktopSettingDefinition[];
}

const SettingsSection = memo(function SettingsSection({
  group,
  definitions,
  settings,
  draftSettings,
  revealedKeys,
  onDraftChange,
  onImmediateChange,
  onCommitDraft,
  onToggleSecretVisibility,
}: SettingsSectionProps) {
  return (
    <section className="settings-section">
      <div className="settings-section-header">
        <h3>{group}</h3>
      </div>
      <div className="settings-section-body">
        {definitions.map((definition) => (
          <SettingField
            key={definition.key}
            definition={definition}
            committedValue={settings[definition.key] ?? ''}
            draftValue={draftSettings[definition.key] ?? settings[definition.key] ?? ''}
            isRevealed={Boolean(revealedKeys[definition.key])}
            onDraftChange={onDraftChange}
            onImmediateChange={onImmediateChange}
            onCommitDraft={onCommitDraft}
            onToggleSecretVisibility={onToggleSecretVisibility}
          />
        ))}
      </div>
    </section>
  );
});

interface SettingFieldProps {
  definition: DesktopSettingDefinition;
  committedValue: string;
  draftValue: string;
  isRevealed: boolean;
  onDraftChange: (key: string, value: string) => void;
  onImmediateChange: (key: string, value: string) => void;
  onCommitDraft: (key: string, value?: string) => void;
  onToggleSecretVisibility: (key: string) => void;
}

const SettingField = memo(function SettingField({
  definition,
  committedValue,
  draftValue,
  isRevealed,
  onDraftChange,
  onImmediateChange,
  onCommitDraft,
  onToggleSecretVisibility,
}: SettingFieldProps) {
  const hasPendingDraft = draftValue !== committedValue;

  const handleInputKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      onCommitDraft(definition.key, draftValue);
    }
  };

  const handleTextareaKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      onCommitDraft(definition.key, draftValue);
    }
  };

  let control: React.ReactNode;

  if (definition.input === 'toggle') {
    control = (
      <label className="toggle-control">
        <input
          type="checkbox"
          checked={draftValue === '1'}
          onChange={(event) => onImmediateChange(definition.key, event.target.checked ? '1' : '0')}
        />
        <span>{draftValue === '1' ? 'Enabled' : 'Disabled'}</span>
      </label>
    );
  } else if (definition.input === 'select') {
    control = (
      <select
        className="glass-input"
        value={draftValue}
        onChange={(event) => onImmediateChange(definition.key, event.target.value)}
      >
        {definition.options?.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    );
  } else if (definition.input === 'textarea') {
    control = (
      <textarea
        className="glass-input glass-textarea"
        rows={4}
        value={draftValue}
        placeholder={definition.placeholder}
        onChange={(event) => onDraftChange(definition.key, event.target.value)}
        onBlur={() => onCommitDraft(definition.key)}
        onKeyDown={handleTextareaKeyDown}
      />
    );
  } else {
    const inputType =
      definition.input === 'password'
        ? (isRevealed ? 'text' : 'password')
        : definition.input === 'number'
          ? 'number'
          : 'text';

    const input = (
      <input
        className="glass-input"
        type={inputType}
        value={draftValue}
        placeholder={definition.placeholder}
        onChange={(event) => onDraftChange(definition.key, event.target.value)}
        onBlur={() => onCommitDraft(definition.key)}
        onKeyDown={handleInputKeyDown}
      />
    );

    control = definition.input === 'password'
      ? (
        <div className="secret-input">
          {input}
          <button
            className="secret-toggle"
            type="button"
            onClick={() => onToggleSecretVisibility(definition.key)}
            aria-label={isRevealed ? 'Hide secret' : 'Show secret'}
          >
            {isRevealed ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        </div>
      )
      : input;
  }

  return (
    <div className="setting-group">
      <div className="setting-label-row">
        <label htmlFor={definition.key}>{definition.label}</label>
        <span className="setting-key">{definition.key}</span>
      </div>
      <p className="setting-description">{definition.description}</p>
      {control}
      {hasPendingDraft && <span className="setting-draft-indicator">Press Enter or blur to save</span>}
    </div>
  );
});

function App() {
  const [dictationState, setDictationState] = useState<'idle' | 'recording' | 'processing' | 'error'>('idle');
  const [transcription, setTranscription] = useState('');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isSidebarAnimating, setIsSidebarAnimating] = useState(false);
  const [isSidebarContentReady, setIsSidebarContentReady] = useState(false);
  const [activeTab, setActiveTab] = useState<SidebarTab>('history');
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [visibleHistoryCount, setVisibleHistoryCount] = useState(HISTORY_CHUNK_SIZE);
  const [settings, setSettings] = useState<DesktopSettings>({} as DesktopSettings);
  const [draftSettings, setDraftSettings] = useState<DesktopSettings>({} as DesktopSettings);
  const [revealedKeys, setRevealedKeys] = useState<Record<string, boolean>>({});
  const [isWindowMaximized, setIsWindowMaximized] = useState(false);

  const deferredHistory = useDeferredValue(history);
  const audioContextRef = useRef<AudioContext | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const stateRef = useRef(dictationState);
  const settingsRef = useRef(settings);
  const draftSettingsRef = useRef(draftSettings);
  const animationTimerRef = useRef<number | null>(null);
  const contentTimerRef = useRef<number | null>(null);

  stateRef.current = dictationState;
  settingsRef.current = settings;
  draftSettingsRef.current = draftSettings;

  const loadSettings = useCallback(async () => {
    const settingsRes = await window.dictationAPI.getSettings();
    if (settingsRes.success && settingsRes.data) {
      setSettings(settingsRes.data);
      setDraftSettings(settingsRes.data);
    }
  }, []);

  const loadHistory = useCallback(async () => {
    const historyRes = await window.dictationAPI.getHistory();
    if (historyRes.success) {
      const nextHistory = historyRes.data ?? [];
      setHistory(nextHistory);
      setVisibleHistoryCount((current) => Math.min(Math.max(current, HISTORY_CHUNK_SIZE), nextHistory.length || HISTORY_CHUNK_SIZE));
    }
  }, []);

  const commitSetting = useCallback(async (key: string, explicitValue?: string) => {
    const previousSettings = settingsRef.current;
    const nextValue = explicitValue ?? draftSettingsRef.current[key] ?? previousSettings[key] ?? '';
    if (previousSettings[key] === nextValue) {
      setDraftSettings((current) => ({ ...current, [key]: nextValue }));
      return;
    }

    const nextSettings = { ...previousSettings, [key]: nextValue };
    setSettings(nextSettings);
    setDraftSettings((current) => ({ ...current, [key]: nextValue }));

    const response = await window.dictationAPI.updateSettings({ [key]: nextValue });
    if (!response.success) {
      await loadSettings();
    }
  }, [loadSettings]);

  const handleImmediateSettingChange = useCallback(async (key: string, value: string) => {
    const previousSettings = settingsRef.current;
    if (previousSettings[key] === value) {
      setDraftSettings((current) => ({ ...current, [key]: value }));
      return;
    }

    const nextSettings = { ...previousSettings, [key]: value };
    setSettings(nextSettings);
    setDraftSettings((current) => ({ ...current, [key]: value }));

    const response = await window.dictationAPI.updateSettings({ [key]: value });
    if (!response.success) {
      await loadSettings();
    }
  }, [loadSettings]);

  const toggleDictation = async () => {
    if (stateRef.current === 'idle') {
      await window.dictationAPI.startDictation();
    } else if (stateRef.current === 'recording') {
      await window.dictationAPI.stopDictation();
    }
  };

  useEffect(() => {
    if (dictationState === 'recording') {
      navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
        streamRef.current = stream;
        const AudioCtx = window.AudioContext || (window as Window & typeof globalThis & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
        const ctx = new AudioCtx({ sampleRate: 16000 });
        audioContextRef.current = ctx;
        const source = ctx.createMediaStreamSource(stream);
        const processor = ctx.createScriptProcessor(4096, 1, 1);
        processorRef.current = processor;

        processor.onaudioprocess = (event) => {
          const inputData = event.inputBuffer.getChannelData(0);
          const pcm16 = new Int16Array(inputData.length);
          for (let index = 0; index < inputData.length; index += 1) {
            const sample = Math.max(-1, Math.min(1, inputData[index]));
            pcm16[index] = sample * 0x7fff;
          }

          window.dictationAPI.sendAudioData(pcm16.buffer);
        };

        source.connect(processor);
        processor.connect(ctx.destination);
      }).catch((error) => {
        console.error('Mic access error:', error);
        setDictationState('error');
      });
    } else {
      if (processorRef.current) {
        processorRef.current.disconnect();
        processorRef.current = null;
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
        audioContextRef.current = null;
      }
    }
  }, [dictationState]);

  useEffect(() => {
    loadSettings();
    loadHistory();

    const unsubState = window.dictationAPI.onStateChange((data) => {
      setDictationState(data.state);
      if (data.state === 'recording') {
        setTranscription('');
      }
      if (data.state === 'idle') {
        loadHistory();
      }
    });

    const unsubTranscription = window.dictationAPI.onTranscriptionUpdate((data) => {
      setTranscription(data.text);
    });

    const unsubHotkey = window.dictationAPI.onHotkeyPress(() => {
      void toggleDictation();
    });

    const unsubMainWindowState = window.dictationAPI.onMainWindowStateChange((data) => {
      setIsWindowMaximized(Boolean(data?.isMaximized));
    });

    void window.dictationAPI.getMainWindowState().then((response) => {
      if (response?.success) {
        setIsWindowMaximized(Boolean(response.data?.isMaximized));
      }
    });

    return () => {
      unsubState();
      unsubTranscription();
      unsubHotkey();
      unsubMainWindowState();
      if (animationTimerRef.current !== null) {
        window.clearTimeout(animationTimerRef.current);
      }
      if (contentTimerRef.current !== null) {
        window.clearTimeout(contentTimerRef.current);
      }
    };
  }, [loadHistory, loadSettings]);

  useEffect(() => {
    if (animationTimerRef.current !== null) {
      window.clearTimeout(animationTimerRef.current);
    }
    if (contentTimerRef.current !== null) {
      window.clearTimeout(contentTimerRef.current);
    }

    setIsSidebarAnimating(true);

    if (isSidebarOpen) {
      contentTimerRef.current = window.setTimeout(() => {
        setIsSidebarContentReady(true);
      }, SIDEBAR_CONTENT_DELAY_MS);
    } else {
      setIsSidebarContentReady(false);
    }

    animationTimerRef.current = window.setTimeout(() => {
      setIsSidebarAnimating(false);
    }, SIDEBAR_ANIMATION_MS);
  }, [isSidebarOpen]);

  const openSidebar = useCallback(() => {
    setIsSidebarOpen(true);
  }, []);

  const closeSidebar = useCallback(() => {
    setIsSidebarOpen(false);
  }, []);

  const switchTab = useCallback((tab: SidebarTab) => {
    startTransition(() => {
      setActiveTab(tab);
      if (tab === 'history') {
        setVisibleHistoryCount(HISTORY_CHUNK_SIZE);
      }
    });
  }, []);

  const handleDraftSettingChange = useCallback((key: string, value: string) => {
    setDraftSettings((current) => {
      if (current[key] === value) {
        return current;
      }
      return { ...current, [key]: value };
    });
  }, []);

  const toggleSecretVisibility = useCallback((key: string) => {
    setRevealedKeys((current) => ({ ...current, [key]: !current[key] }));
  }, []);

  const showMoreHistory = useCallback(() => {
    startTransition(() => {
      setVisibleHistoryCount((current) => Math.min(current + HISTORY_CHUNK_SIZE, deferredHistory.length));
    });
  }, [deferredHistory.length]);

  return (
    <div className="app-shell">
      <div className="title-bar">
        <div className="title-drag-area">DictaPilot</div>
        <div className="window-controls">
          <button
            className="window-control-btn"
            type="button"
            onClick={() => window.dictationAPI.minimizeMainWindow()}
            aria-label="Minimize window"
            title="Minimize"
          >
            <Minus size={16} />
          </button>
          <button
            className="window-control-btn"
            type="button"
            onClick={() => window.dictationAPI.toggleMainWindowMaximize()}
            aria-label={isWindowMaximized ? 'Restore window' : 'Maximize window'}
            title={isWindowMaximized ? 'Restore' : 'Maximize'}
          >
            {isWindowMaximized ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
          </button>
          <button
            className="window-control-btn close"
            type="button"
            onClick={() => window.dictationAPI.closeMainWindow()}
            aria-label="Close window"
            title="Close"
          >
            <X size={15} />
          </button>
        </div>
      </div>

      <main className={cn('main-stage', isSidebarOpen && 'sidebar-open', isSidebarAnimating && 'sidebar-transitioning')}>
        <header className="stage-header">
          <div className="status-indicator">
            <span className={cn('status-dot', dictationState)}></span>
            <span className="status-text">{dictationState}</span>
          </div>
          <button className="icon-btn" onClick={openSidebar}>
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
                <button className="action-btn" onClick={() => navigator.clipboard.writeText(transcription)}>
                  <Copy size={16} /> Copy
                </button>
                <button className="action-btn">
                  <Wand2 size={16} /> Refine
                </button>
                <button className="action-btn text-danger" onClick={() => setTranscription('')}>
                  <Trash2 size={16} /> Clear
                </button>
              </div>
            )}
          </div>

          <div className="mic-wrapper">
            <button className={cn('mic-btn', dictationState)} onClick={() => void toggleDictation()}>
              {dictationState === 'recording' ? <Square size={32} /> : <Mic size={32} />}
            </button>
            {dictationState === 'recording' && <div className="mic-rings"></div>}
          </div>
        </div>
      </main>

      <div
        className={cn('sidebar-backdrop', isSidebarOpen && 'visible', isSidebarAnimating && 'animating')}
        onClick={closeSidebar}
      ></div>

      <aside className={cn('sidebar glass', isSidebarOpen && 'open', isSidebarAnimating && 'animating')}>
        <div className="sidebar-header">
          <div className="tab-switcher">
            <button
              className={cn('tab-btn', activeTab === 'history' && 'active')}
              onClick={() => switchTab('history')}
            >
              <History size={16} /> History
            </button>
            <button
              className={cn('tab-btn', activeTab === 'settings' && 'active')}
              onClick={() => switchTab('settings')}
            >
              <Settings size={16} /> Settings
            </button>
          </div>
          <button className="icon-btn" onClick={closeSidebar}>
            <X size={24} />
          </button>
        </div>

        <div className="sidebar-content">
          {isSidebarContentReady && activeTab === 'history' && (
            <HistoryPanel
              history={deferredHistory}
              visibleCount={visibleHistoryCount}
              onShowMore={showMoreHistory}
            />
          )}

          {isSidebarContentReady && activeTab === 'settings' && (
            <SettingsPanel
              settings={settings}
              draftSettings={draftSettings}
              revealedKeys={revealedKeys}
              onDraftChange={handleDraftSettingChange}
              onImmediateChange={(key, value) => {
                void handleImmediateSettingChange(key, value);
              }}
              onCommitDraft={(key, value) => {
                void commitSetting(key, value);
              }}
              onToggleSecretVisibility={toggleSecretVisibility}
            />
          )}
        </div>
      </aside>
    </div>
  );
}

export default App;
