import { useEffect, useRef, useState } from 'react';
import {
  Mic,
  History,
  Settings,
  Menu,
  X,
  Copy,
  Trash2,
  Wand2,
  Square,
  Eye,
  EyeOff,
  Minus,
  Maximize2,
  Minimize2,
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

function App() {
  const [dictationState, setDictationState] = useState<'idle' | 'recording' | 'processing' | 'error'>('idle');
  const [transcription, setTranscription] = useState('');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'history' | 'settings'>('history');
  const [history, setHistory] = useState<any[]>([]);
  const [settings, setSettings] = useState<DesktopSettings>({} as DesktopSettings);
  const [revealedKeys, setRevealedKeys] = useState<Record<string, boolean>>({});
  const [isWindowMaximized, setIsWindowMaximized] = useState(false);

  const audioContextRef = useRef<AudioContext | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const stateRef = useRef(dictationState);
  stateRef.current = dictationState;

  const toggleDictation = async () => {
    // @ts-ignore
    if (!window.dictationAPI) return;

    if (stateRef.current === 'idle') {
      // @ts-ignore
      await window.dictationAPI.startDictation();
    } else if (stateRef.current === 'recording') {
      // @ts-ignore
      await window.dictationAPI.stopDictation();
    }
  };

  const loadData = async () => {
    // @ts-ignore
    if (!window.dictationAPI) return;

    // @ts-ignore
    const settingsRes = await window.dictationAPI.getSettings();
    if (settingsRes.success) {
      setSettings(settingsRes.data ?? ({} as DesktopSettings));
    }

    // @ts-ignore
    const historyRes = await window.dictationAPI.getHistory();
    if (historyRes.success) {
      setHistory(historyRes.data ?? []);
    }
  };

  useEffect(() => {
    if (dictationState === 'recording') {
      navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
        streamRef.current = stream;
        const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
        const ctx = new AudioCtx({ sampleRate: 16000 });
        audioContextRef.current = ctx;
        const source = ctx.createMediaStreamSource(stream);
        const processor = ctx.createScriptProcessor(4096, 1, 1);
        processorRef.current = processor;

        processor.onaudioprocess = (e) => {
          const inputData = e.inputBuffer.getChannelData(0);
          const pcm16 = new Int16Array(inputData.length);
          for (let i = 0; i < inputData.length; i++) {
            const sample = Math.max(-1, Math.min(1, inputData[i]));
            pcm16[i] = sample * 0x7FFF;
          }

          // @ts-ignore
          if (window.dictationAPI?.sendAudioData) {
            // @ts-ignore
            window.dictationAPI.sendAudioData(pcm16.buffer);
          }
        };

        source.connect(processor);
        processor.connect(ctx.destination);
      }).catch((err) => {
        console.error('Mic access error:', err);
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
    loadData();

    // @ts-ignore
    if (!window.dictationAPI) return;

    // @ts-ignore
    const unsubState = window.dictationAPI.onStateChange((data: any) => {
      setDictationState(data.state);
      if (data.state === 'recording') {
        setTranscription('');
      }
      if (data.state === 'idle') {
        loadData();
      }
    });

    // @ts-ignore
    const unsubTranscription = window.dictationAPI.onTranscriptionUpdate((data: any) => {
      setTranscription(data.text);
      if (data.isFinal) {
        setTimeout(loadData, 500);
      }
    });

    // @ts-ignore
    const unsubHotkey = window.dictationAPI.onHotkeyPress(() => {
      toggleDictation();
    });

    const unsubMainWindowState = window.dictationAPI.onMainWindowStateChange((data: { isMaximized: boolean }) => {
      setIsWindowMaximized(Boolean(data?.isMaximized));
    });

    window.dictationAPI.getMainWindowState().then((response: any) => {
      if (response?.success) {
        setIsWindowMaximized(Boolean(response.data?.isMaximized));
      }
    });

    return () => {
      unsubState();
      unsubTranscription();
      unsubHotkey();
      unsubMainWindowState();
    };
  }, []);

  const handleSettingChange = (key: string, value: string) => {
    const nextSettings = { ...settings, [key]: value };
    setSettings(nextSettings);
    // @ts-ignore
    window.dictationAPI?.updateSettings({ [key]: value });
  };

  const toggleSecretVisibility = (key: string) => {
    setRevealedKeys((current) => ({ ...current, [key]: !current[key] }));
  };

  const renderSettingControl = (definition: DesktopSettingDefinition) => {
    const value = settings[definition.key] ?? '';

    if (definition.input === 'toggle') {
      return (
        <label className="toggle-control">
          <input
            type="checkbox"
            checked={value === '1'}
            onChange={(event) => handleSettingChange(definition.key, event.target.checked ? '1' : '0')}
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
          onChange={(event) => handleSettingChange(definition.key, event.target.value)}
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
          onChange={(event) => handleSettingChange(definition.key, event.target.value)}
        />
      );
    }

    const inputType =
      definition.input === 'password'
        ? (revealedKeys[definition.key] ? 'text' : 'password')
        : definition.input === 'number'
          ? 'number'
          : 'text';

    const input = (
      <input
        className="glass-input"
        type={inputType}
        value={value}
        placeholder={definition.placeholder}
        onChange={(event) => handleSettingChange(definition.key, event.target.value)}
      />
    );

    if (definition.input === 'password') {
      return (
        <div className="secret-input">
          {input}
          <button
            className="secret-toggle"
            type="button"
            onClick={() => toggleSecretVisibility(definition.key)}
            aria-label={revealedKeys[definition.key] ? 'Hide secret' : 'Show secret'}
          >
            {revealedKeys[definition.key] ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        </div>
      );
    }

    return input;
  };

  return (
    <div className="app-shell">
      <div className="title-bar">
        <div className="title-drag-area">DictaPilot</div>
        <div className="window-controls">
          <button
            className="window-control-btn"
            type="button"
            onClick={() => window.dictationAPI?.minimizeMainWindow()}
            aria-label="Minimize window"
            title="Minimize"
          >
            <Minus size={16} />
          </button>
          <button
            className="window-control-btn"
            type="button"
            onClick={() => window.dictationAPI?.toggleMainWindowMaximize()}
            aria-label={isWindowMaximized ? 'Restore window' : 'Maximize window'}
            title={isWindowMaximized ? 'Restore' : 'Maximize'}
          >
            {isWindowMaximized ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
          </button>
          <button
            className="window-control-btn close"
            type="button"
            onClick={() => window.dictationAPI?.closeMainWindow()}
            aria-label="Close window"
            title="Close"
          >
            <X size={15} />
          </button>
        </div>
      </div>

      <main className={cn('main-stage', isSidebarOpen && 'sidebar-open')}>
        <header className="stage-header">
          <div className="status-indicator">
            <span className={cn('status-dot', dictationState)}></span>
            <span className="status-text">{dictationState}</span>
          </div>
          <button className="icon-btn" onClick={() => setIsSidebarOpen(true)}>
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
            <button className={cn('mic-btn', dictationState)} onClick={toggleDictation}>
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
              onClick={() => {
                setActiveTab('history');
                loadData();
              }}
            >
              <History size={16} /> History
            </button>
            <button
              className={cn('tab-btn', activeTab === 'settings' && 'active')}
              onClick={() => setActiveTab('settings')}
            >
              <Settings size={16} /> Settings
            </button>
          </div>
          <button className="icon-btn" onClick={() => setIsSidebarOpen(false)}>
            <X size={24} />
          </button>
        </div>

        <div className="sidebar-content">
          {activeTab === 'history' && (
            <div className="history-list fade-in">
              {history.length === 0 ? (
                <p style={{ color: 'var(--text-muted)', textAlign: 'center', marginTop: '20px' }}>No history yet.</p>
              ) : (
                history.map((item: any) => (
                  <div className="history-card" key={item.id} onClick={() => navigator.clipboard.writeText(item.text)}>
                    <p className="history-text">{item.text}</p>
                    <span className="history-time">{new Date(item.timestamp).toLocaleTimeString()}</span>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="settings-panel fade-in">
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
