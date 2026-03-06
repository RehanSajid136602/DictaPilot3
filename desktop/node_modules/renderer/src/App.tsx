import { useEffect, useState, useRef } from 'react';
import { Mic, History, Settings, Menu, X, Copy, Trash2, Wand2, Square } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import './App.css';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

function App() {
  const [dictationState, setDictationState] = useState<'idle' | 'recording' | 'processing' | 'error'>('idle');
  const [transcription, setTranscription] = useState('');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'history' | 'settings'>('history');
  
  const [history, setHistory] = useState<any[]>([]);
  const [settings, setSettings] = useState<any>({ hotkey: 'F9', model: 'default' });

  const audioContextRef = useRef<AudioContext | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);

  // Use a ref to always access the latest state in our event listeners
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
    if (settingsRes.success) setSettings(settingsRes.data);

    // @ts-ignore
    const historyRes = await window.dictationAPI.getHistory();
    if (historyRes.success) setHistory(historyRes.data);
  };

  useEffect(() => {
    if (dictationState === 'recording') {
        navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
            streamRef.current = stream;
            // Use standard AudioContext, fallback to webkitAudioContext for broader compatibility
            const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
            const ctx = new AudioCtx({ sampleRate: 16000 });
            audioContextRef.current = ctx;
            const source = ctx.createMediaStreamSource(stream);
            
            // createScriptProcessor is deprecated but works reliably without external files in Electron
            const processor = ctx.createScriptProcessor(4096, 1, 1);
            processorRef.current = processor;

            processor.onaudioprocess = (e) => {
                const inputData = e.inputBuffer.getChannelData(0);
                const pcm16 = new Int16Array(inputData.length);
                for (let i = 0; i < inputData.length; i++) {
                    const s = Math.max(-1, Math.min(1, inputData[i]));
                    pcm16[i] = s * 0x7FFF;
                }
                
                // @ts-ignore
                if (window.dictationAPI && window.dictationAPI.sendAudioData) {
                    // @ts-ignore
                    window.dictationAPI.sendAudioData(pcm16.buffer);
                }
            };

            source.connect(processor);
            processor.connect(ctx.destination);
        }).catch(err => {
            console.error("Mic access error:", err);
            setDictationState('error');
        });
    } else {
        if (processorRef.current) {
            processorRef.current.disconnect();
            processorRef.current = null;
        }
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(t => t.stop());
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
    if (window.dictationAPI) {
      // @ts-ignore
      const unsubState = window.dictationAPI.onStateChange((data: any) => {
        console.log("Main UI received state change:", data);
        setDictationState(data.state);
        if (data.state === 'recording') setTranscription('');
        // Reload history when processing is done
        if (data.state === 'idle') loadData();
      });

      // @ts-ignore
      const unsubTranscription = window.dictationAPI.onTranscriptionUpdate((data: any) => {
        setTranscription(data.text);
        if (data.isFinal) {
           // We could reload history here too
           setTimeout(loadData, 500); 
        }
      });

      // @ts-ignore
      const unsubHotkey = window.dictationAPI.onHotkeyPress(() => {
        toggleDictation();
      });

      return () => {
        unsubState();
        unsubTranscription();
        unsubHotkey();
      };
    }
  }, []);

  const handleSettingChange = (key: string, value: any) => {
    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);
    // @ts-ignore
    if (window.dictationAPI) {
      // @ts-ignore
      window.dictationAPI.updateSettings(newSettings);
    }
  };

  return (
      <div className="app-shell">
        <div className="title-bar">
          <div className="title-drag-area">DictaPilot</div>
        </div>
        
        {/* Main Content */}
        <main className={cn("main-stage", isSidebarOpen && "sidebar-open")}>
           {/* Header with Menu Toggle */}
           <header className="stage-header">
             <button className="icon-btn" onClick={() => setIsSidebarOpen(true)}>
               <Menu size={24} />
             </button>
             <div className="status-indicator">
               <span className={cn('status-dot', dictationState)}></span>
               <span className="status-text">{dictationState}</span>
             </div>
           </header>
           
           {/* Center Stage: Input & Mic */}
           <div className="center-stage">
              <div className="input-container glass">
                <textarea 
                  className="transcription-input"
                  value={transcription}
                  onChange={(e) => setTranscription(e.target.value)}
                  placeholder={`Press ${settings.hotkey || 'F9'} or click the mic to start...`}
                />
                {transcription && (
                  <div className="action-bar fade-in">
                    <button className="action-btn" onClick={() => navigator.clipboard.writeText(transcription)}><Copy size={16}/> Copy</button>
                    <button className="action-btn"><Wand2 size={16}/> Refine</button>
                    <button className="action-btn text-danger" onClick={() => setTranscription('')}><Trash2 size={16}/> Clear</button>
                  </div>
                )}
              </div>
              
              <div className="mic-wrapper">
                <button 
                  className={cn("mic-btn", dictationState)}
                  onClick={toggleDictation}
                >
                  {dictationState === 'recording' ? <Square size={32} /> : <Mic size={32} />}
                </button>
                {dictationState === 'recording' && <div className="mic-rings"></div>}
              </div>
           </div>
        </main>
        
        {/* Sidebar Overlay */}
        <div className={cn("sidebar-backdrop", isSidebarOpen && "visible")} onClick={() => setIsSidebarOpen(false)}></div>
        
        {/* Sidebar Panel */}
        <aside className={cn("sidebar glass", isSidebarOpen && "open")}>
           <div className="sidebar-header">
              <div className="tab-switcher">
                <button className={cn("tab-btn", activeTab === 'history' && 'active')} onClick={() => { setActiveTab('history'); loadData(); }}>
                  <History size={16}/> History
                </button>
                <button className={cn("tab-btn", activeTab === 'settings' && 'active')} onClick={() => setActiveTab('settings')}>
                  <Settings size={16}/> Settings
                </button>
              </div>
              <button className="icon-btn" onClick={() => setIsSidebarOpen(false)}><X size={24}/></button>
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
                 <div className="setting-group">
                   <label>Global Hotkey</label>
                   <input 
                     className="glass-input" 
                     type="text" 
                     value={settings.hotkey || ''} 
                     onChange={(e) => handleSettingChange('hotkey', e.target.value)}
                   />
                 </div>
                 <div className="setting-group">
                   <label>AI Model</label>
                   <select 
                     className="glass-input"
                     value={settings.model || 'default'}
                     onChange={(e) => handleSettingChange('model', e.target.value)}
                   >
                     <option value="default">Whisper Large v3 (Groq)</option>
                     <option value="local">Local Whisper (CPU)</option>
                   </select>
                 </div>
               </div>
             )}
           </div>
        </aside>
      </div>
  );
}

export default App;