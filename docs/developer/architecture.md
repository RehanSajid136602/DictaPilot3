# DictaPilot3 Architecture

Technical overview of DictaPilot3's system design and component interactions.

## System Overview

DictaPilot3 follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                         User Input                          │
│                    (Hold Hotkey to Record)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Hotkey Manager                           │
│              (keyboard/pynput/x11 backends)                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Audio Recorder                           │
│         (sounddevice + VAD + buffer management)             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Transcriber                              │
│              (Groq Whisper API / local)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Smart Editor                             │
│         (Command detection + LLM/heuristic cleanup)         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Paste Utility                            │
│         (Delta paste + multiple backends)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Target Application                       │
│                  (Text appears here)                        │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Application Core (`app.py`)

**Responsibilities:**
- Application lifecycle management
- Component initialization and coordination
- Event loop and threading
- GUI management (floating window, tray icon)
- Configuration loading

**Key Classes:**
- `GUIManager` - Manages floating status window
- `HotkeyManager` - Handles global hotkey registration
- `RecordingState` - Tracks recording state machine

**Threading Model:**
- Main thread: GUI event loop (Qt)
- Hotkey thread: Global hotkey monitoring
- Recording thread: Audio capture
- Transcription thread: API calls
- Worker threads: Background processing

### 2. Audio Recording (`recorder.py`)

**Responsibilities:**
- Audio capture from microphone
- Real-time level monitoring
- Silence trimming
- Buffer management

**Key Functions:**
```python
def record_audio(duration=None, callback=None):
    """
    Record audio from microphone
    
    Args:
        duration: Max recording duration (None = until stopped)
        callback: Function called with audio level updates
    
    Returns:
        numpy array of audio samples
    """
```

**Audio Pipeline:**
1. Initialize PortAudio stream
2. Capture audio chunks (configurable chunk size)
3. Calculate RMS level for visualization
4. Buffer audio data
5. Trim silence from start/end
6. Return audio as numpy array

**Configuration:**
- `SAMPLE_RATE`: Recording sample rate (default: 16000 Hz)
- `CHANNELS`: Number of audio channels (default: 1 - mono)
- `TRIM_SILENCE`: Enable silence trimming (default: True)
- `SILENCE_THRESHOLD`: Threshold for silence detection (default: 0.02)

### 3. Transcription (`transcriber.py`)

**Responsibilities:**
- Send audio to transcription service
- Handle API communication
- Retry logic and error handling
- Health checking

**Key Functions:**
```python
def transcribe_audio(audio_data, sample_rate=16000):
    """
    Transcribe audio using Groq Whisper API
    
    Args:
        audio_data: numpy array of audio samples
        sample_rate: Sample rate of audio
    
    Returns:
        Transcribed text string
    """
```

**Transcription Flow:**
1. Convert numpy array to WAV format
2. Send to Groq Whisper API
3. Parse JSON response
4. Extract transcribed text
5. Handle errors and retries

**Backends:**
- **Groq API** (default): Cloud-based Whisper
- **Local whisper.cpp**: Offline transcription (requires setup)

**Models:**
- `whisper-large-v3-turbo`: Fast, good accuracy (default)
- `whisper-large-v3`: Slower, best accuracy
- `whisper-medium`: Balanced
- `whisper-small`: Fastest, lower accuracy

### 4. Smart Editor (`smart_editor.py`)

**Responsibilities:**
- Voice command detection and execution
- Text cleanup (filler words, repeated words)
- Inline correction handling
- LLM-based refinement
- State management

**Architecture:**

```
Raw Transcript
      │
      ▼
┌─────────────────┐
│ Command         │
│ Detection       │
└────┬────────────┘
     │
     ├─ Command? ──► Execute Command ──► Updated State
     │
     └─ Content ──► Cleanup Pipeline ──► Cleaned Text
                          │
                          ├─ Heuristic Mode (fast)
                          │   ├─ Remove filler words
                          │   ├─ Dedupe repeated words
                          │   ├─ Fix punctuation
                          │   └─ Inline corrections
                          │
                          └─ LLM Mode (accurate)
                              └─ Send to Groq Chat API
                                  └─ Grammar, tone, cleanup
```

**Key Classes:**
```python
@dataclass
class TranscriptState:
    """Maintains dictation state"""
    segments: List[str]           # Individual utterances
    output_text: str              # Current full text
    last_action: str              # Last action taken
    context: DictationContext     # App context
```

**Command Patterns:**
- Deletion: `_UNDO_RE`, `_CLEAR_RE`
- Replacement: `_REPLACE_RE`
- Formatting: `_REWRITE_RE`, `_GRAMMAR_RE`
- Control: `_IGNORE_RE`
- Inline: `_INLINE_CORRECTION_RE`

**Cleanup Pipeline:**
1. **Preface removal**: Remove "oh no", "oops", etc.
2. **Filler word removal**: Remove "um", "uh", "hmm"
3. **Repeated word deduplication**: "the the" → "the"
4. **Inline corrections**: "no, I mean X" → "X"
5. **Punctuation cleanup**: Fix repeated punctuation
6. **Capitalization**: Sentence-initial caps

**LLM Integration:**
```python
def llm_refine(text: str, context: DictationContext) -> str:
    """
    Refine text using LLM
    
    Args:
        text: Raw transcribed text
        context: Dictation context (app, tone, language)
    
    Returns:
        Refined text
    """
```

### 5. Paste Utility (`paste_utils.py`)

**Responsibilities:**
- Text pasting to target application
- Delta paste computation
- Multiple backend support
- Clipboard management

**Delta Paste Algorithm:**
```python
def compute_delta(old_text: str, new_text: str) -> Tuple[int, str]:
    """
    Compute minimal edit to transform old_text to new_text
    
    Returns:
        (num_backspaces, text_to_add)
    
    Example:
        old: "Hello world"
        new: "Hello there world"
        returns: (5, "there world")  # Delete "world", add "there world"
    """
```

**Paste Backends:**

| Backend | Platform | Method | Speed | Reliability |
|---------|----------|--------|-------|-------------|
| `x11` | Linux X11 | Direct X11 API | Fast | High |
| `xdotool` | Linux | xdotool command | Medium | High |
| `osascript` | macOS | AppleScript | Medium | High |
| `keyboard` | All | Keyboard simulation | Fast | Medium |
| `pynput` | All | Python keyboard lib | Slow | High |

**Backend Selection Logic:**
1. Check `PASTE_BACKEND` env var
2. If `auto`, detect platform and display server
3. Select optimal backend for platform
4. Fall back to `pynput` if preferred fails

### 6. Context Management (`app_context.py`)

**Responsibilities:**
- Detect active application
- Load context-aware profiles
- Manage tone and language settings
- Profile switching

**Key Classes:**
```python
@dataclass
class DictationContext:
    """Context for current dictation"""
    app_name: str                 # Active application
    tone: str                     # Desired tone
    language: str                 # Target language
    profile: Optional[dict]       # Active profile
```

**Profile System:**
```json
{
  "profiles": {
    "gmail": {
      "tone": "professional",
      "language": "english",
      "cleanup_level": "aggressive"
    },
    "slack": {
      "tone": "casual",
      "language": "english",
      "cleanup_level": "balanced"
    }
  }
}
```

### 7. Configuration (`config.py`)

**Responsibilities:**
- Load configuration from multiple sources
- Environment variable overrides
- Persistent config storage
- Validation

**Configuration Priority:**
1. Environment variables (highest)
2. `.env` file
3. `config.json`
4. Default values (lowest)

**Key Functions:**
```python
def load_config() -> DictaPilotConfig:
    """Load configuration with env overrides"""

def save_config(config: DictaPilotConfig):
    """Persist configuration to disk"""
```

## Data Flow

### Complete Dictation Flow

```
1. User presses F9
   └─► HotkeyManager detects press
       └─► RecordingState → RECORDING
           └─► GUIManager updates UI (show "Recording")

2. Audio capture begins
   └─► recorder.py starts PortAudio stream
       └─► Audio chunks buffered
           └─► RMS levels sent to GUI for visualization

3. User releases F9
   └─► HotkeyManager detects release
       └─► RecordingState → PROCESSING
           └─► GUIManager updates UI (show "Processing")
               └─► Audio recording stops

4. Transcription
   └─► Audio sent to transcriber.py
       └─► Groq Whisper API call
           └─► JSON response parsed
               └─► Raw transcript extracted

5. Smart editing
   └─► Raw transcript → smart_editor.py
       ├─► Command detection
       │   ├─► If command: execute and update state
       │   └─► If content: continue to cleanup
       └─► Cleanup pipeline
           ├─► Heuristic mode: regex-based cleanup
           └─► LLM mode: Groq Chat API refinement

6. Paste
   └─► Cleaned text → paste_utils.py
       ├─► Delta paste computation
       │   └─► Calculate minimal edit
       └─► Backend execution
           ├─► Set clipboard
           └─► Simulate Ctrl+V (or direct paste)

7. Complete
   └─► RecordingState → IDLE
       └─► GUIManager updates UI (show "Done" briefly)
           └─► Transcription stored in history
```

## Threading and Concurrency

### Thread Safety

**Main Thread:**
- Qt event loop
- GUI updates
- User interaction

**Hotkey Thread:**
- Global hotkey monitoring
- Signals main thread on press/release

**Recording Thread:**
- Audio capture
- Level monitoring
- Signals main thread with audio data

**Transcription Thread:**
- API calls (blocking I/O)
- Signals main thread with results

**Worker Pool:**
- LLM refinement (optional)
- Background tasks

**Synchronization:**
- `threading.Lock` for shared state
- `queue.Queue` for inter-thread communication
- Qt signals/slots for GUI updates

### State Machine

```
IDLE ──► RECORDING ──► PROCESSING ──► IDLE
  ▲                                     │
  └─────────────────────────────────────┘
```

**State Transitions:**
- `IDLE → RECORDING`: Hotkey pressed
- `RECORDING → PROCESSING`: Hotkey released
- `PROCESSING → IDLE`: Transcription complete

## Extension Points

### Adding Custom Backends

**Hotkey Backend:**
```python
# In app.py
class CustomHotkeyBackend:
    def register(self, hotkey: str, callback):
        """Register global hotkey"""
        pass
    
    def unregister(self):
        """Unregister hotkey"""
        pass
```

**Paste Backend:**
```python
# In paste_utils.py
def paste_custom(text: str) -> bool:
    """Custom paste implementation"""
    # Your implementation here
    return True
```

### Adding Custom Commands

```python
# In smart_editor.py
_CUSTOM_COMMAND_RE = re.compile(
    r"^your pattern here$",
    re.IGNORECASE
)

def handle_custom_command(state: TranscriptState, match) -> str:
    """Handle custom command"""
    # Your logic here
    return "updated_text"
```

### Adding Custom Profiles

```json
{
  "profiles": {
    "custom-app": {
      "tone": "custom",
      "language": "english",
      "cleanup_level": "balanced",
      "custom_dictionary": {
        "myword": "MyWord"
      }
    }
  }
}
```

## Performance Considerations

### Optimization Strategies

**Audio Processing:**
- Use appropriate sample rate (16kHz for speech)
- Minimize buffer size for lower latency
- Trim silence to reduce API payload

**Transcription:**
- Use turbo model for speed
- Batch multiple short recordings
- Cache common phrases

**Smart Editing:**
- Heuristic mode for speed (no LLM)
- Lazy LLM refinement (background)
- Regex compilation and caching

**Paste:**
- Delta paste reduces keystrokes
- Direct API calls faster than subprocess
- Clipboard caching

### Memory Management

- Audio buffers released after transcription
- Transcription history limited (configurable)
- LRU cache for LLM responses
- Profile lazy loading

## Error Handling

### Error Categories

**Recoverable:**
- API rate limits → Retry with backoff
- Network timeouts → Retry
- Audio device busy → Wait and retry

**User-fixable:**
- Invalid API key → Show error, prompt for key
- Missing permissions → Show instructions
- Hotkey conflict → Suggest alternative

**Fatal:**
- Missing dependencies → Exit with message
- Unsupported platform → Exit with message
- Configuration corruption → Reset to defaults

### Logging

```python
import logging

logger = logging.getLogger("dictapilot")
logger.setLevel(logging.INFO)

# Levels:
# DEBUG: Detailed diagnostic info
# INFO: General informational messages
# WARNING: Warning messages
# ERROR: Error messages
# CRITICAL: Critical errors
```

## Testing

See [Contributing Guide](contributing.md) for testing guidelines.

## See Also

- [API Reference](api-reference.md) - Public API documentation
- [Contributing Guide](contributing.md) - Development setup
- [Configuration Guide](../README.md#environment-variables) - All config options

---

**Last Updated:** 2026-02-17
