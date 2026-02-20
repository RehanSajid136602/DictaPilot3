import { useState, useEffect, useRef, useCallback } from 'react';
import { Toaster } from '@/components/ui/sonner';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { 
  Mic, 
  MicOff, 
  Settings, 
  History, 
  Home,
  Volume2,
  Trash2,
  Copy,
  RefreshCw,
  Wifi,
  WifiOff,
  User,
  Palette,
  Globe
} from 'lucide-react';

// Types
interface TranscriptionEntry {
  id: string;
  timestamp: string;
  original_text: string;
  processed_text: string;
  action: string;
  word_count: number;
  tags: string[];
  quality_score: number;
}

interface WebSocketMessage {
  type: string;
  [key: string]: unknown;
}

interface Settings {
  language: string;
  theme: 'light' | 'dark';
  streaming_enabled: boolean;
}

// WebSocket connection hook
function useWebSocket(url: string) {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    try {
      setConnectionError(null);
      const websocket = new WebSocket(url);

      websocket.onopen = () => {
        setConnected(true);
        setConnectionError(null);
        console.log('Connected to DictaPilot');
      };

      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as WebSocketMessage;
          setLastMessage(data);
        } catch (e) {
          console.error('Failed to parse message:', e);
        }
      };

      websocket.onclose = () => {
        setConnected(false);
        setWs(null);
        console.log('Disconnected from DictaPilot');
        // Auto-reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('Attempting to reconnect...');
          connect();
        }, 3000);
      };

      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionError('Failed to connect to server. Make sure the backend is running on port 8080.');
      };

      setWs(websocket);
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      setConnectionError('Failed to create connection');
    }
  }, [url]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (ws) {
        ws.close();
      }
    };
  }, [connect]);

  const send = useCallback((data: WebSocketMessage) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(data));
    }
  }, [ws]);

  return { connected, lastMessage, send, connectionError };
}

// Recording Component
function RecordingTab({ 
  onTranscription, 
  connected 
}: { 
  onTranscription: (text: string) => void;
  connected: boolean;
}) {
  const [recording, setRecording] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [transcript, setTranscript] = useState('');
  const [processing, setProcessing] = useState(false);
  const [micError, setMicError] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const animationRef = useRef<number>();
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const startRecording = async () => {
    setMicError(null);
    try {
      // Check for HTTPS
      if (window.location.protocol !== 'https:' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        setMicError('Microphone requires HTTPS. Please use localhost or enable HTTPS.');
        return;
      }
      
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const reader = new FileReader();
        reader.readAsDataURL(audioBlob);
        reader.onloadend = () => {
          const base64Audio = (reader.result as string).split(',')[1];
          onTranscription(base64Audio);
        };
        
        stream.getTracks().forEach(track => track.stop());
      };

      // Audio visualization
      const audioContext = new AudioContext();
      const analyser = audioContext.createAnalyser();
      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);
      analyser.fftSize = 256;

      const dataArray = new Uint8Array(analyser.frequencyBinCount);

      const visualize = () => {
        if (!recording) return;
        analyser.getByteFrequencyData(dataArray);
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
        setAudioLevel(average / 255);
        
        // Draw waveform
        const canvas = canvasRef.current;
        if (canvas) {
          const ctx = canvas.getContext('2d');
          if (ctx) {
            ctx.fillStyle = '#1a1a2e';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            const barWidth = (canvas.width / dataArray.length) * 2.5;
            let x = 0;
            for (let i = 0; i < dataArray.length; i++) {
              const barHeight = (dataArray[i] / 255) * canvas.height;
              const gradient = ctx.createLinearGradient(0, canvas.height - barHeight, 0, canvas.height);
              gradient.addColorStop(0, '#3b82f6');
              gradient.addColorStop(1, '#8b5cf6');
              ctx.fillStyle = gradient;
              ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
              x += barWidth + 1;
            }
          }
        }
        
        animationRef.current = requestAnimationFrame(visualize);
      };

      mediaRecorder.start(100);
      setRecording(true);
      visualize();
    } catch (error: unknown) {
      console.error('Error starting recording:', error);
      const err = error as Error;
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setMicError('Microphone permission denied. Please allow microphone access in your browser settings.');
      } else if (err.name === 'NotFoundError') {
        setMicError('No microphone found. Please connect a microphone and try again.');
      } else if (err.name === 'NotReadableError') {
        setMicError('Microphone is in use by another application.');
      } else {
        setMicError(`Microphone error: ${err.message || 'Unknown error'}`);
      }
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
      setProcessing(true);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    }
  };

  const handleTranscription = (base64Audio: string) => {
    // This would send to the API
    setProcessing(false);
    setTranscript('Transcription would appear here...');
  };

  useEffect(() => {
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  return (
    <div className="space-y-6">
      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader className="text-center">
          <CardTitle className="text-zinc-100 flex items-center justify-center gap-2">
            {connected ? <Wifi className="w-5 h-5 text-green-500" /> : <WifiOff className="w-5 h-5 text-red-500" />}
            {connected ? 'Connected to DictaPilot' : 'Not Connected'}
          </CardTitle>
          <CardDescription className="text-zinc-400">
            Click the microphone to start recording
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col items-center space-y-6">
          {/* Waveform Canvas */}
          <canvas
            ref={canvasRef}
            width={400}
            height={120}
            className="w-full max-w-md rounded-lg bg-zinc-950"
          />

          {/* Record Button */}
          <Button
            size="lg"
            className={`w-24 h-24 rounded-full transition-all ${
              recording 
                ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
            onClick={recording ? stopRecording : startRecording}
            disabled={!connected}
          >
            {recording ? (
              <MicOff className="w-10 h-10" />
            ) : (
              <Mic className="w-10 h-10" />
            )}
          </Button>

          {/* Status */}
          <div className="text-center space-y-2">
            {micError && (
              <Badge variant="destructive" className="bg-red-600">
                {micError}
              </Badge>
            )}
            {recording && (
              <Badge variant="destructive" className="animate-pulse">
                Recording...
              </Badge>
            )}
            {processing && (
              <Badge className="bg-yellow-600">
                Processing...
              </Badge>
            )}
          </div>

          {/* Audio Level Indicator */}
          <div className="w-full max-w-md">
            <div className="flex items-center gap-2">
              <Volume2 className="w-4 h-4 text-zinc-400" />
              <div className="flex-1 h-2 bg-zinc-800 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all"
                  style={{ width: `${audioLevel * 100}%` }}
                />
              </div>
            </div>
          </div>

          {/* Transcript Display */}
          {transcript && (
            <div className="w-full max-w-md space-y-2">
              <Label className="text-zinc-400">Transcript</Label>
              <Textarea
                value={transcript}
                onChange={(e) => setTranscript(e.target.value)}
                className="min-h-[100px] bg-zinc-950 border-zinc-800"
                placeholder="Your transcription will appear here..."
              />
              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => navigator.clipboard.writeText(transcript)}
                >
                  <Copy className="w-4 h-4 mr-1" />
                  Copy
                </Button>
                <Button variant="outline" size="sm">
                  <RefreshCw className="w-4 h-4 mr-1" />
                  Retry
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// History Component
function HistoryTab({ 
  connected 
}: { 
  connected: boolean;
}) {
  const [entries, setEntries] = useState<TranscriptionEntry[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchHistory = async () => {
    if (!connected) return;
    setLoading(true);
    try {
      const response = await fetch('/api/transcriptions?limit=50');
      const data = await response.json();
      setEntries(data.entries || []);
    } catch (error) {
      console.error('Error fetching history:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchHistory();
  }, [connected]);

  const filteredEntries = entries.filter(entry => 
    entry.original_text.toLowerCase().includes(search.toLowerCase())
  );

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <Input
          placeholder="Search transcriptions..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="bg-zinc-900 border-zinc-800"
        />
        <Button variant="outline" onClick={fetchHistory}>
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </Button>
      </div>

      <ScrollArea className="h-[500px]">
        <div className="space-y-3">
          {filteredEntries.length === 0 ? (
            <div className="text-center py-8 text-zinc-500">
              <History className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>No transcriptions yet</p>
              <p className="text-sm">Start recording to create your first transcription</p>
            </div>
          ) : (
            filteredEntries.map((entry) => (
              <Card key={entry.id} className="bg-zinc-900 border-zinc-800">
                <CardContent className="pt-4">
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-zinc-400">
                        {entry.word_count} words
                      </Badge>
                      <Badge variant="outline" className="text-zinc-400">
                        {entry.action}
                      </Badge>
                    </div>
                    <span className="text-xs text-zinc-500">
                      {formatDate(entry.timestamp)}
                    </span>
                  </div>
                  <p className="text-zinc-200 text-sm line-clamp-3">
                    {entry.original_text}
                  </p>
                  <div className="flex gap-2 mt-3">
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => navigator.clipboard.writeText(entry.original_text)}
                    >
                      <Copy className="w-4 h-4 mr-1" />
                      Copy
                    </Button>
                    <Button variant="ghost" size="sm" className="text-red-400">
                      <Trash2 className="w-4 h-4 mr-1" />
                      Delete
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
}

// Settings Component
function SettingsTab({ 
  connected,
  settings,
  onSettingsChange 
}: { 
  connected: boolean;
  settings: Settings;
  onSettingsChange: (settings: Settings) => void;
}) {
  const [localSettings, setLocalSettings] = useState(settings);

  useEffect(() => {
    setLocalSettings(settings);
  }, [settings]);

  const updateSetting = (key: keyof Settings, value: unknown) => {
    const newSettings = { ...localSettings, [key]: value };
    setLocalSettings(newSettings);
    onSettingsChange(newSettings);
  };

  return (
    <div className="space-y-6">
      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="w-5 h-5" />
            Profile
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm text-zinc-400 mb-2 block">Active Profile</label>
            <select className="w-full bg-zinc-950 border border-zinc-800 rounded-md p-2 text-zinc-200">
              <option value="default">Default</option>
            </select>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Globe className="w-5 h-5" />
            Language
          </CardTitle>
        </CardHeader>
        <CardContent>
          <select 
            className="w-full bg-zinc-950 border border-zinc-800 rounded-md p-2 text-zinc-200"
            value={localSettings.language}
            onChange={(e) => updateSetting('language', e.target.value)}
          >
            <option value="en">English</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="de">German</option>
            <option value="zh">Chinese</option>
            <option value="ja">Japanese</option>
          </select>
        </CardContent>
      </Card>

      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Palette className="w-5 h-5" />
            Appearance
          </CardTitle>
        </CardHeader>
        <CardContent>
          <select 
            className="w-full bg-zinc-950 border border-zinc-800 rounded-md p-2 text-zinc-200"
            value={localSettings.theme}
            onChange={(e) => updateSetting('theme', e.target.value)}
          >
            <option value="dark">Dark</option>
            <option value="light">Light</option>
          </select>
        </CardContent>
      </Card>

      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Connection
          </CardTitle>
          <CardDescription className="text-zinc-400">
                              Server: ws://127.0.0.1:8080/ws          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-zinc-200">
              {connected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// Label component (simple replacement)
function Label({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <label className={`text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 ${className}`}>
      {children}
    </label>
  );
}

// Main App
function App() {
  const [activeTab, setActiveTab] = useState('record');
  const [settings, setSettings] = useState<Settings>({
    language: 'en',
    theme: 'dark',
    streaming_enabled: true
  });
  const { connected, lastMessage, send, connectionError } = useWebSocket('ws://127.0.0.1:8080/ws');

  // Handle transcription from recording
  const handleTranscription = async (base64Audio: string) => {
    try {
      const response = await fetch('/api/transcribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          audio_data: base64Audio,
          language: settings.language
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('Transcription:', data.text);
      }
    } catch (error) {
      console.error('Transcription error:', error);
    }
  };

  // Listen for messages from server
  useEffect(() => {
    if (lastMessage) {
      console.log('WebSocket message:', lastMessage);
      if (lastMessage.type === 'transcription_result') {
        // Handle transcription result
      }
    }
  }, [lastMessage]);

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <div className="max-w-2xl mx-auto p-4">
        {/* Header */}
        <header className="mb-8 pt-4">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            DictaPilot
          </h1>
          <p className="text-zinc-400">Voice transcription made simple</p>
        </header>

        {/* Connection Status */}
        <div className="mb-4 space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'} animate-pulse`} />
              <span className="text-sm text-zinc-400">
                {connected ? 'Connected to server' : connectionError ? 'Connection failed' : 'Connecting...'}
              </span>
            </div>
            <Badge variant="outline" className="text-zinc-400">
              Web UI v1.0
            </Badge>
          </div>
          {connectionError && (
            <div className="text-xs text-red-400 bg-red-950/30 p-2 rounded border border-red-900">
              {connectionError}
            </div>
          )}
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3 bg-zinc-900">
            <TabsTrigger value="record" className="flex items-center gap-2">
              <Mic className="w-4 h-4" />
              Record
            </TabsTrigger>
            <TabsTrigger value="history" className="flex items-center gap-2">
              <History className="w-4 h-4" />
              History
            </TabsTrigger>
            <TabsTrigger value="settings" className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              Settings
            </TabsTrigger>
          </TabsList>

          <div className="mt-6">
            <TabsContent value="record">
              <RecordingTab 
                onTranscription={handleTranscription} 
                connected={connected} 
              />
            </TabsContent>

            <TabsContent value="history">
              <HistoryTab connected={connected} />
            </TabsContent>

            <TabsContent value="settings">
              <SettingsTab 
                connected={connected}
                settings={settings}
                onSettingsChange={setSettings}
              />
            </TabsContent>
          </div>
        </Tabs>
      </div>

      <Toaster />
    </div>
  );
}

export default App;