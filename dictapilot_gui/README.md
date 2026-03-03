# DictaPilot GUI

A modern, minimal desktop speech-to-text application using faster-whisper for local transcription.

![DictaPilot GUI Screenshot](screenshot.png)

## Features

- 🎙️ **One-click recording** with visual feedback
- 📝 **Local transcription** using faster-whisper (no cloud required)
- ⚡ **Fast & accurate** with multiple model sizes (tiny, base, small, medium)
- 🌍 **Multi-language support** with auto-detection
- 🔒 **Privacy-first** - all processing happens locally
- 🖥️ **Modern UI** inspired by WhisperFlow
- ⚙️ **Configurable** - model, language, device settings

## Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Linux: Install PortAudio (required for audio recording)
# Ubuntu/Debian:
sudo apt-get install portaudio19-dev

# Fedora:
sudo dnf install portaudio-devel

# Arch:
sudo pacman -S portaudio

# Optional: FFmpeg (for additional audio format support)
# Ubuntu/Debian:
sudo apt-get install ffmpeg
```

### 2. Run the Application

```bash
# From the project root
python -m dictapilot_gui

# Or from the dictapilot_gui directory
cd dictapilot_gui
python -m dictapilot_gui
```

## Usage

1. **Click "Record"** to start recording your voice
2. **Speak clearly** into your microphone
3. **Click "Stop"** when finished
4. **Wait** for transcription to complete
5. **Copy or Save** the transcription as needed

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+L` | Clear transcription |
| `Ctrl+Shift+C` | Copy to clipboard |
| `Ctrl+S` | Save to file |
| `Ctrl+,` | Open settings |

## Settings

Open Settings (⚙️) to configure:

- **Model**: tiny (fastest) → base → small → medium (most accurate)
- **Language**: Auto-detect or specify (English, Spanish, French, etc.)
- **Translate**: Convert speech to English text
- **Device**: CPU (works everywhere) or CUDA (requires NVIDIA GPU)
- **Font**: Monospace (good for code) or proportional

Settings are saved to:
- Linux/macOS: `~/.config/dictapilot/gui_config.json`
- Windows: `%APPDATA%\DictaPilot\gui_config.json`

Models are downloaded to:
- Linux/macOS: `~/.cache/whisper/`
- Windows: `%USERPROFILE%\.cache\whisper\`

## System Requirements

### Minimum
- Python 3.8+
- 2GB RAM
- Working microphone

### Recommended
- Python 3.10+
- 4GB+ RAM
- SSD for model storage
- NVIDIA GPU with CUDA (for faster transcription)

## Troubleshooting

### "No audio input devices found"
- Check microphone is connected and not muted
- Grant microphone permissions to the application
- Try: `arecord -l` (Linux) to list audio devices

### "Failed to load model"
- Check internet connection for first-time model download
- Ensure sufficient disk space (~500MB per model)
- Try a smaller model (tiny/base)

### CUDA not available
- Install PyTorch with CUDA support:
  ```bash
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
  ```
- Ensure NVIDIA drivers are installed

### High CPU usage during transcription
- This is normal for CPU inference
- Consider using a smaller model (tiny/base)
- Use CUDA if available

## Project Structure

```
dictapilot_gui/
├── __init__.py          # Package init
├── __main__.py          # Entry point
├── config/              # Settings management
│   ├── __init__.py
│   └── settings.py
├── audio/               # Audio recording
│   ├── __init__.py
│   └── recorder.py
├── stt/                 # Speech-to-text
│   ├── __init__.py
│   └── transcriber.py
└── ui/                  # User interface
    ├── __init__.py
    ├── main_window.py
    └── settings_dialog.py
```

## License

MIT License - See LICENSE file for details.

## Credits

- Built with [faster-whisper](https://github.com/SYSTRAN/faster-whisper) for efficient local transcription
- UI built with [PySide6](https://doc.qt.io/qtforpython/) (Qt for Python)