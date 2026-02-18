# API Reference

Public API documentation for DictaPilot3 modules and functions.

## Core Modules

### app.py

Main application entry point and orchestration.

#### Functions

**`main()`**
```python
def main():
    """
    Main application entry point.
    Initializes components and starts event loop.
    """
```

**`record_audio(duration=None, callback=None)`**
```python
def record_audio(duration=None, callback=None) -> np.ndarray:
    """
    Record audio from microphone.
    
    Args:
        duration: Maximum recording duration in seconds (None = until stopped)
        callback: Function called with audio level updates (0.0-1.0)
    
    Returns:
        numpy array of audio samples (float32, mono)
    
    Raises:
        RuntimeError: If audio device not available
    """
```

### transcriber.py

Audio transcription using Groq Whisper API.

#### Functions

**`transcribe_audio(audio_data, sample_rate=16000)`**
```python
def transcribe_audio(audio_data: np.ndarray, sample_rate: int = 16000) -> str:
    """
    Transcribe audio using Groq Whisper API.
    
    Args:
        audio_data: numpy array of audio samples
        sample_rate: Sample rate of audio (default: 16000)
    
    Returns:
        Transcribed text string
    
    Raises:
        APIError: If API call fails
        ValueError: If audio_data is invalid
    
    Example:
        >>> audio = record_audio(duration=5)
        >>> text = transcribe_audio(audio)
        >>> print(text)
        "Hello world"
    """
```

**`get_groq_client()`**
```python
def get_groq_client() -> Groq:
    """
    Get or create Groq API client.
    
    Returns:
        Groq client instance
    
    Raises:
        ValueError: If GROQ_API_KEY not set
    """
```

### smart_editor.py

Smart text editing with voice commands and cleanup.

#### Classes

**`TranscriptState`**
```python
@dataclass
class TranscriptState:
    """Maintains dictation state."""
    
    segments: List[str] = field(default_factory=list)
    output_text: str = ""
    last_action: str = "append"
    context: Optional[DictationContext] = None
```

#### Functions

**`smart_update_state(state, utterance, context=None)`**
```python
def smart_update_state(
    state: TranscriptState,
    utterance: str,
    context: Optional[DictationContext] = None
) -> Tuple[TranscriptState, str]:
    """
    Update transcript state with new utterance.
    Handles voice commands and text cleanup.
    
    Args:
        state: Current transcript state
        utterance: New spoken text
        context: Dictation context (app, tone, language)
    
    Returns:
        Tuple of (updated_state, action_taken)
        action_taken: "append", "undo", "clear", "ignore"
    
    Example:
        >>> state = TranscriptState()
        >>> state, action = smart_update_state(state, "Hello world")
        >>> print(state.output_text)
        "Hello world"
        >>> state, action = smart_update_state(state, "delete that")
        >>> print(state.output_text)
        ""
    """
```

**`llm_refine(text, context=None)`**
```python
def llm_refine(
    text: str,
    context: Optional[DictationContext] = None
) -> str:
    """
    Refine text using LLM (Groq Chat API).
    
    Args:
        text: Raw transcribed text
        context: Dictation context for tone/language
    
    Returns:
        Refined text with grammar fixes and cleanup
    
    Example:
        >>> text = "um this is uh a test"
        >>> refined = llm_refine(text)
        >>> print(refined)
        "This is a test."
    """
```

**`is_transform_command(utterance)`**
```python
def is_transform_command(utterance: str) -> bool:
    """
    Check if utterance is a transformation command.
    
    Args:
        utterance: Spoken text
    
    Returns:
        True if utterance is a command (rewrite, fix grammar, etc.)
    
    Example:
        >>> is_transform_command("rewrite formal")
        True
        >>> is_transform_command("hello world")
        False
    """
```

### paste_utils.py

Text pasting with delta paste support.

#### Functions

**`paste_text(text, old_text="", mode="delta", backend="auto")`**
```python
def paste_text(
    text: str,
    old_text: str = "",
    mode: str = "delta",
    backend: str = "auto"
) -> bool:
    """
    Paste text to active application.
    
    Args:
        text: Text to paste
        old_text: Previous text (for delta paste)
        mode: "delta" or "full"
        backend: Paste backend to use
    
    Returns:
        True if paste succeeded, False otherwise
    
    Example:
        >>> paste_text("Hello world")
        True
        >>> paste_text("Hello there world", old_text="Hello world", mode="delta")
        True  # Only pastes "there "
    """
```

**`compute_delta(old_text, new_text)`**
```python
def compute_delta(old_text: str, new_text: str) -> Tuple[int, str]:
    """
    Compute minimal edit to transform old_text to new_text.
    
    Args:
        old_text: Previous text
        new_text: New text
    
    Returns:
        Tuple of (num_backspaces, text_to_add)
    
    Example:
        >>> compute_delta("Hello world", "Hello there world")
        (5, "there world")  # Delete "world", add "there world"
    """
```

### app_context.py

Context-aware profile management.

#### Classes

**`DictationContext`**
```python
@dataclass
class DictationContext:
    """Context for current dictation."""
    
    app_name: str = ""
    tone: str = "polite"
    language: str = "english"
    profile: Optional[dict] = None
```

#### Functions

**`get_context()`**
```python
def get_context() -> DictationContext:
    """
    Get current dictation context.
    Detects active application and loads profile.
    
    Returns:
        DictationContext with app name and settings
    
    Example:
        >>> context = get_context()
        >>> print(context.app_name)
        "gmail"
        >>> print(context.tone)
        "professional"
    """
```

**`update_profile(app_name, settings)`**
```python
def update_profile(app_name: str, settings: dict) -> None:
    """
    Update profile for application.
    
    Args:
        app_name: Application identifier
        settings: Profile settings (tone, language, etc.)
    
    Example:
        >>> update_profile("slack", {"tone": "casual", "language": "english"})
    """
```

### config.py

Configuration management.

#### Classes

**`DictaPilotConfig`**
```python
@dataclass
class DictaPilotConfig:
    """Application configuration."""
    
    hotkey: str = "f9"
    model: str = "whisper-large-v3-turbo"
    smart_mode: str = "llm"
    smart_edit: bool = True
    paste_mode: str = "delta"
    # ... (40+ configuration options)
```

#### Functions

**`load_config()`**
```python
def load_config() -> DictaPilotConfig:
    """
    Load configuration with environment variable overrides.
    
    Priority: env vars > .env file > config.json > defaults
    
    Returns:
        DictaPilotConfig instance
    """
```

**`save_config(config)`**
```python
def save_config(config: DictaPilotConfig) -> None:
    """
    Save configuration to disk.
    
    Args:
        config: Configuration to save
    """
```

### transcription_store.py

Transcription history storage.

#### Functions

**`add_transcription(text, metadata=None)`**
```python
def add_transcription(text: str, metadata: dict = None) -> None:
    """
    Add transcription to history.
    
    Args:
        text: Transcribed text
        metadata: Optional metadata (timestamp, app, duration, etc.)
    
    Example:
        >>> add_transcription("Hello world", {
        ...     "app_name": "notepad",
        ...     "duration": 2.5,
        ...     "word_count": 2
        ... })
    """
```

**`get_storage_info()`**
```python
def get_storage_info() -> dict:
    """
    Get transcription storage statistics.
    
    Returns:
        Dict with total_count, total_words, storage_size, etc.
    
    Example:
        >>> info = get_storage_info()
        >>> print(f"Total transcriptions: {info['total_count']}")
    """
```

**`export_all_to_text(output_path)`**
```python
def export_all_to_text(output_path: str) -> None:
    """
    Export all transcriptions to text file.
    
    Args:
        output_path: Path to output file
    
    Example:
        >>> export_all_to_text("my_transcriptions.txt")
    """
```

## Environment Variables

All configuration can be set via environment variables. See [Configuration Guide](../README.md#environment-variables) for complete list.

### Core Settings

```python
GROQ_API_KEY: str          # Required: Groq API key
HOTKEY: str = "f9"         # Global hotkey
SMART_EDIT: bool = True    # Enable smart editing
SMART_MODE: str = "llm"    # "llm" or "heuristic"
PASTE_MODE: str = "delta"  # "delta" or "full"
```

### Audio Settings

```python
SAMPLE_RATE: int = 16000   # Recording sample rate
CHANNELS: int = 1          # Number of channels
TRIM_SILENCE: bool = True  # Trim silence
AUDIO_DEVICE: int = None   # Audio device index
```

### Backend Settings

```python
HOTKEY_BACKEND: str = "auto"  # "auto", "keyboard", "pynput", "x11"
PASTE_BACKEND: str = "auto"   # "auto", "keyboard", "pynput", "xdotool", "x11", "osascript"
```

## Error Handling

All public functions may raise:

- `ValueError`: Invalid arguments
- `RuntimeError`: Runtime errors (device not available, etc.)
- `APIError`: API call failures (network, authentication, etc.)

Example error handling:

```python
try:
    audio = record_audio(duration=5)
    text = transcribe_audio(audio)
    paste_text(text)
except ValueError as e:
    print(f"Invalid input: {e}")
except RuntimeError as e:
    print(f"Runtime error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Extension Examples

### Custom Backend

```python
# Add custom paste backend
def paste_custom(text: str) -> bool:
    """Custom paste implementation."""
    # Your implementation
    return True

# Register in paste_utils.py
PASTE_BACKENDS["custom"] = paste_custom
```

### Custom Command

```python
# Add custom voice command
import re
from smart_editor import TranscriptState

CUSTOM_CMD = re.compile(r"^my command (.+)$", re.IGNORECASE)

def handle_custom_command(state: TranscriptState, utterance: str) -> str:
    match = CUSTOM_CMD.match(utterance)
    if match:
        arg = match.group(1)
        # Your logic here
        return f"Processed: {arg}"
    return utterance
```

### Custom Profile

```python
# Create custom profile
from app_context import update_profile

update_profile("my-app", {
    "tone": "professional",
    "language": "english",
    "cleanup_level": "aggressive",
    "custom_dictionary": {
        "myword": "MyWord"
    }
})
```

## See Also

- [Architecture](architecture.md) - System design overview
- [Contributing](contributing.md) - Development guidelines
- [Configuration](../README.md#environment-variables) - All config options

---

**Last Updated:** 2026-02-17
