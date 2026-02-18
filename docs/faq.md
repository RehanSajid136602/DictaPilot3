# Frequently Asked Questions

Common questions about DictaPilot3.

## General

### What is DictaPilot3?

DictaPilot3 is a cross-platform voice dictation tool that lets you transcribe speech to text using a simple hold-to-talk workflow. Hold a hotkey (F9 by default), speak, release, and your words are transcribed and pasted into any application.

### How is it different from other dictation tools?

- **Open source** - Free and transparent
- **Smart editing** - Voice commands like "delete that", "replace X with Y"
- **Delta paste** - Only sends changed characters, not full text
- **Context-aware** - Different settings per application
- **Developer-focused** - Agent mode for coding workflows
- **Privacy-first** - Local storage, optional cloud

### Does it work offline?

No, DictaPilot3 requires internet connection for the Groq API. However, you can use local whisper.cpp as an alternative backend for offline transcription (requires additional setup).

### Is it free?

Yes, DictaPilot3 is free and open source (MIT license). You need a free Groq API key which has generous usage limits.

### What platforms are supported?

- Linux (X11 and Wayland)
- macOS (10.14+)
- Windows (10/11)

---

## Setup & Configuration

### How do I get a Groq API key?

1. Visit [console.groq.com](https://console.groq.com)
2. Sign up or log in (free)
3. Create a new API key
4. Copy the key (starts with `gsk_`)
5. Add to `.env` file: `GROQ_API_KEY=your_key_here`

### Can I change the hotkey?

Yes, edit `.env` file:

```bash
HOTKEY=f10           # Single key
HOTKEY=ctrl+shift+d  # Key combination
HOTKEY=alt+space     # Alternative
```

### How do I select a different microphone?

List available devices:
```bash
python -c "import sounddevice; print(sounddevice.query_devices())"
```

Set device in `.env`:
```bash
AUDIO_DEVICE=1  # Use index from list
```

### Can I use it with multiple languages?

Yes, Whisper supports 100+ languages. The model auto-detects language, or you can set it per profile.

---

## Privacy & Security

### Where is my data stored?

- **Transcriptions:** Stored locally in `~/.local/share/dictapilot/transcriptions.json` (Linux/macOS) or `%APPDATA%\DictaPilot\transcriptions.json` (Windows)
- **Audio:** Not stored (deleted after transcription)
- **API key:** Stored in `.env` file or system keychain (macOS)

### Is my audio sent to the cloud?

Yes, audio is sent to Groq API for transcription. Groq's privacy policy applies. For offline transcription, use local whisper.cpp backend.

### Can I use it for sensitive information?

- Audio is sent to Groq API (cloud processing)
- Transcriptions stored locally
- For maximum privacy, use local whisper.cpp backend
- Don't use for passwords or highly sensitive data

### Does it collect telemetry?

No, DictaPilot3 does not collect any telemetry or usage data.

---

## Features

### What voice commands are supported?

Common commands:
- "delete that" - Remove last segment
- "clear all" - Clear everything
- "replace X with Y" - Replace text
- "ignore" - Don't include this
- "rewrite formal" - Change tone
- "fix grammar" - Correct grammar

See [Voice Commands Reference](voice-commands.md) for complete list.

### What is delta paste?

Delta paste only sends the characters that changed, not the entire text. This is faster and reduces flicker compared to traditional paste methods.

Example:
- Old text: "Hello world"
- New text: "Hello there world"
- Delta paste: Only sends "there " (not the full text)

### What is agent mode?

Agent mode formats your dictation as structured prompts for coding assistants. It extracts:
- Task description
- File paths and code locations
- Constraints and requirements
- Acceptance criteria

Useful for dictating coding tasks to AI assistants.

### What is smart editing?

Smart editing automatically:
- Removes filler words (um, uh, etc.)
- Fixes repeated words
- Handles inline corrections ("no, I mean...")
- Processes voice commands
- Cleans up punctuation

Can use heuristic rules (fast) or LLM (more accurate).

### What are context-aware profiles?

Profiles let you configure different settings per application:
- Tone (formal, casual, etc.)
- Language
- Custom dictionary
- Cleanup level

Example: Use formal tone in email, casual in chat apps.

---

## Troubleshooting

### Why isn't my hotkey working?

Common causes:
1. **Backend issue** - Try different `HOTKEY_BACKEND`
2. **Conflict** - Another app using same hotkey
3. **Permissions** - macOS needs Accessibility permission
4. **Wrong key format** - Check syntax in `.env`

See [Troubleshooting Guide](troubleshooting.md#issue-hotkey-not-working) for detailed solutions.

### Why isn't text pasting?

Common causes:
1. **Backend issue** - Try different `PASTE_BACKEND`
2. **Permissions** - macOS needs Accessibility permission
3. **App blocks input** - Some apps don't accept programmatic paste
4. **Focus issue** - Text field not focused

See [Troubleshooting Guide](troubleshooting.md#issue-text-not-pasting) for detailed solutions.

### Why isn't it working on Wayland?

DictaPilot3 now has native Wayland support! If you have issues:

1. **Install Wayland dependencies:**
```bash
sudo apt install wl-clipboard wtype  # Ubuntu/Debian
sudo dnf install wl-clipboard wtype  # Fedora
sudo pacman -S wl-clipboard wtype    # Arch
```

2. **Check dependencies:**
```bash
python app.py --wayland-deps
```

3. **Use Wayland backends:**
```bash
HOTKEY_BACKEND=wayland
PASTE_BACKEND=wayland
```

4. **Fallback options:**
```bash
HOTKEY_BACKEND=pynput
PASTE_BACKEND=xdotool
```

See [Linux Guide](platform-guides/linux.md#wayland) for detailed Wayland setup.

### Why is transcription quality poor?

Improve quality:
- Use external microphone
- Reduce background noise
- Speak clearly at normal pace
- Use `DICTATION_MODE=accurate`
- Try `GROQ_WHISPER_MODEL=whisper-large-v3`

### Why is it slow?

Speed it up:
- Use `GROQ_WHISPER_MODEL=whisper-large-v3-turbo`
- Set `INSTANT_REFINE=0`
- Use `SMART_MODE=heuristic`
- Use `PASTE_MODE=delta`

---

## Usage

### How do I dictate punctuation?

Just speak naturally - Whisper adds punctuation automatically. You can also say:
- "period" or "full stop"
- "comma"
- "question mark"
- "exclamation point"

### Can I dictate code?

Yes! Tips for code dictation:
- Speak clearly: "def hello world function"
- Use agent mode for structured tasks
- Create custom snippets for common patterns
- Use voice commands to edit

### How do I undo mistakes?

Say "delete that" or "undo" to remove the last segment. Or use "clear all" to start over.

### Can I use it while typing?

Yes, but it's designed for pure dictation. Mixing typing and dictation works but may be less efficient.

### Does it work in all applications?

Works in most applications that accept text input. Some exceptions:
- Password fields (security restriction)
- Some games (may not accept programmatic input)
- Virtual machines (may need special configuration)

---

## Advanced

### Can I customize voice commands?

Currently, voice commands are built-in. Custom commands are planned for future releases.

### Can I add custom words to dictionary?

Yes, create `dictionary.json` in config directory:

```json
{
  "adelant": "Adelant",
  "dictapilot": "DictaPilot"
}
```

### How do I create custom profiles?

Create `profile_bundle.json` in config directory. See [Profile Ingestion Spec](../docs/profile-ingestion-spec.md) for format.

### Can I use local Whisper instead of Groq?

Yes, but requires additional setup:
1. Install whisper.cpp
2. Download GGML model
3. Configure `WHISPER_BACKEND=local`

(Detailed guide coming soon)

### Can I contribute?

Yes! DictaPilot3 is open source. See [Contributing Guide](developer/contributing.md) for details.

---

## Comparison

### How does it compare to Dragon NaturallySpeaking?

**DictaPilot3:**
- Free and open source
- Cloud-based (requires internet)
- Modern AI models (Whisper)
- Cross-platform
- Developer-focused features

**Dragon:**
- Commercial ($150-300)
- Offline capable
- More mature
- Better for medical/legal
- Windows/macOS only

### How does it compare to built-in OS dictation?

**DictaPilot3:**
- Smart editing and voice commands
- Context-aware profiles
- Delta paste technology
- Customizable
- Works across all apps

**OS Dictation:**
- Built-in (no setup)
- Basic transcription only
- Limited customization
- May have better OS integration

### How does it compare to WhisperFlow?

**DictaPilot3:**
- Open source
- Free (API costs only)
- Developer-focused
- Terminal-first
- Extensive customization

**WhisperFlow:**
- Commercial ($12/month)
- Mobile apps
- Polished GUI
- Real-time streaming
- Enterprise features

See [Comparison Document](../plan.md) for detailed analysis.

---

## Support

### Where can I get help?

- **Documentation:** [Quick Start](quick-start.md), [Troubleshooting](troubleshooting.md)
- **Platform Guides:** [Linux](platform-guides/linux.md), [macOS](platform-guides/macos.md), [Windows](platform-guides/windows.md)
- **GitHub Issues:** [Report bugs or request features](https://github.com/RehanSajid136602/DictaPilot/issues)

### How do I report a bug?

1. Check [Troubleshooting Guide](troubleshooting.md) first
2. Search [existing issues](https://github.com/RehanSajid136602/DictaPilot/issues)
3. Create new issue with:
   - OS and Python version
   - Steps to reproduce
   - Error messages
   - Relevant config settings

### How do I request a feature?

Open a [GitHub issue](https://github.com/RehanSajid136602/DictaPilot/issues) with:
- Clear description of feature
- Use case / why it's needed
- Examples of how it would work

### Is there a community?

- **GitHub Discussions:** Coming soon
- **Discord:** Planned for future
- **Reddit:** r/DictaPilot (planned)

---

## Roadmap

### What features are planned?

See [Improvement Plan](../plan.md) for full roadmap:

**Phase 1 (High Priority):**
- Real-time streaming transcription
- Wayland support for Linux ✓
- Modern GUI dashboard
- Improved documentation ✓ (in progress)

**Phase 2:**
- Enhanced agent mode with IDE integration
- Advanced delta paste optimization
- Context-aware profile enhancements
- Adaptive learning improvements

**Phase 3:**
- Mobile companion app (Android)
- Optional cloud sync

**Phase 4:**
- Performance optimization
- Advanced voice commands
- Plugin system

### When will feature X be released?

Check the [roadmap](../plan.md) for estimated timelines. Contributions are welcome to speed up development!

---

**Last Updated:** 2026-02-17
