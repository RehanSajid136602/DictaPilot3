# DictaPilot3 Documentation

Welcome to DictaPilot3 - cross-platform voice dictation with smart editing.

## What is DictaPilot3?

DictaPilot3 is an open-source voice dictation tool that lets you transcribe speech to text using a simple hold-to-talk workflow. Hold a hotkey (F9 by default), speak, release, and your words are transcribed and pasted into any application.

## Key Features

- **Hold-to-Talk** - Press F9, speak, release. That's it.
- **Smart Voice Commands** - "delete that", "replace X with Y", "rewrite formal"
- **Delta Paste** - Only sends changed characters, not full text (faster, less flicker)
- **Context-Aware** - Different settings per application
- **Developer-Focused** - Agent mode for coding workflows
- **Privacy-First** - Local storage, open source

## Quick Links

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Quick Start**

    ---

    Get started in under 5 minutes

    [:octicons-arrow-right-24: Quick Start Guide](quick-start.md)

-   :material-microphone:{ .lg .middle } **Voice Commands**

    ---

    Learn all available voice commands

    [:octicons-arrow-right-24: Command Reference](voice-commands.md)

-   :material-help-circle:{ .lg .middle } **Troubleshooting**

    ---

    Common issues and solutions

    [:octicons-arrow-right-24: Troubleshooting Guide](troubleshooting.md)

-   :material-code-braces:{ .lg .middle } **For Developers**

    ---

    Architecture and API documentation

    [:octicons-arrow-right-24: Developer Docs](developer/architecture.md)

</div>

## How It Works

```mermaid
graph LR
    A[Hold F9] --> B[Speak]
    B --> C[Release F9]
    C --> D[Transcription]
    D --> E[Smart Editing]
    E --> F[Auto-Paste]
    F --> G[Text Appears]
```

1. **Hold F9** - Start recording
2. **Speak naturally** - Audio captured
3. **Release F9** - Transcription begins
4. **Smart editing** - Commands processed, text cleaned
5. **Auto-paste** - Text appears in your app

## Platform Support

DictaPilot3 works on:

- **Linux** (X11 and Wayland) - [Setup Guide](platform-guides/linux.md)
- **macOS** (10.14+) - [Setup Guide](platform-guides/macos.md)
- **Windows** (10/11) - [Setup Guide](platform-guides/windows.md)

## Getting Started

### Installation

```bash
# Clone repository
git clone https://github.com/RehanSajid136602/DictaPilot.git
cd DictaPilot

# Run setup script
./setup/setup_linux.sh      # Linux
./setup/setup_macos.command  # macOS
setup\setup_windows.bat      # Windows

# Add API key
echo "GROQ_API_KEY=your_key_here" > .env

# Start dictating
python app.py
```

**Get your free API key:** [console.groq.com](https://console.groq.com)

### First Dictation

1. Open any text editor
2. Click in a text field
3. Hold F9
4. Say: "Hello world, this is a test"
5. Release F9
6. Text appears!

## Example Usage

**Basic dictation:**
```
You say: "Hello world"
Result: "Hello world"
```

**With voice commands:**
```
You say: "Hello world... delete that... Goodbye world"
Result: "Goodbye world"
```

**Smart editing:**
```
You say: "um this is uh a test"
Result: "This is a test."
```

## Documentation Structure

### Getting Started
- [Quick Start Guide](quick-start.md) - 5-step setup
- [Voice Commands](voice-commands.md) - Complete command reference
- [Troubleshooting](troubleshooting.md) - Common issues
- [FAQ](faq.md) - Frequently asked questions

### Platform Guides
- [Linux Setup](platform-guides/linux.md) - X11/Wayland, backends
- [macOS Setup](platform-guides/macos.md) - Permissions, Keychain
- [Windows Setup](platform-guides/windows.md) - Setup and troubleshooting

### Developer Documentation
- [Architecture](developer/architecture.md) - System design
- [API Reference](developer/api-reference.md) - Public API
- [Contributing](developer/contributing.md) - Development guide

## Community & Support

- **GitHub:** [RehanSajid136602/DictaPilot](https://github.com/RehanSajid136602/DictaPilot)
- **Issues:** [Report bugs or request features](https://github.com/RehanSajid136602/DictaPilot/issues)
- **Discussions:** Coming soon
- **Discord:** Planned

## License

DictaPilot3 is open source under the MIT License.

---

**Ready to get started?** Follow the [Quick Start Guide](quick-start.md) →
