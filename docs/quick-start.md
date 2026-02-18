# Quick Start Guide

Get DictaPilot3 up and running in under 5 minutes.

## Prerequisites

- Python 3.10 or higher
- Microphone
- Groq API key (free at [console.groq.com](https://console.groq.com))

## Step 1: Install Dependencies

Clone the repository and install dependencies:

```bash
git clone https://github.com/RehanSajid136602/DictaPilot.git
cd DictaPilot
```

Run the setup script for your platform:

**Linux:**
```bash
./setup/setup_linux.sh
```

**macOS:**
```bash
./setup/setup_macos.command
```

**Windows:**
```bash
setup\setup_windows.bat
```

**Verification:** Check that Python packages are installed:
```bash
python -c "import groq, sounddevice, PySide6; print('Dependencies OK')"
```

## Step 2: Configure API Key

Get your free Groq API key from [console.groq.com](https://console.groq.com).

Create a `.env` file in the project root:

```bash
echo "GROQ_API_KEY=your_api_key_here" > .env
```

**Verification:** Test API connectivity:
```bash
python -c "from groq import Groq; import os; from dotenv import load_dotenv; load_dotenv(); client = Groq(api_key=os.getenv('GROQ_API_KEY')); print('API key valid')"
```

## Step 3: Run DictaPilot

Start the application:

```bash
python app.py
```

You should see:
- "DictaPilot started" message
- Floating status window (optional)
- System tray icon (if available)

**Verification:** Check that the app is running without errors.

## Step 4: Configure Hotkey (Optional)

The default hotkey is `F9`. To change it, edit `.env`:

```bash
HOTKEY=f10
```

Available keys: `f1`-`f12`, `ctrl+shift+d`, etc.

**Verification:** Press your hotkey - the floating window should show "Recording" state.

## Step 5: Test Dictation

1. Open any text editor (Notepad, VS Code, etc.)
2. Click in a text field
3. **Hold** the hotkey (F9)
4. Speak: "Hello world, this is a test"
5. **Release** the hotkey
6. Text should appear in your editor

**Verification:** If text appears correctly, setup is complete! 🎉

## Troubleshooting

**Hotkey not working?**
- Linux: See [Linux Platform Guide](platform-guides/linux.md) for X11/Wayland setup
- macOS: Grant Accessibility permissions in System Preferences
- Windows: Run as administrator if needed

**Text not pasting?**
- Check that you released the hotkey
- Try different paste backend: `PASTE_BACKEND=xdotool` (Linux) or `PASTE_BACKEND=osascript` (macOS)

**API errors?**
- Verify API key is correct in `.env`
- Check internet connection
- See [Troubleshooting Guide](troubleshooting.md)

**Audio issues?**
- Check microphone permissions
- List available devices: `python -c "import sounddevice; print(sounddevice.query_devices())"`
- Set specific device: `AUDIO_DEVICE=1` in `.env`

## Next Steps

- **Learn voice commands:** See [Voice Commands Reference](voice-commands.md)
- **Platform-specific setup:** [Linux](platform-guides/linux.md) | [macOS](platform-guides/macos.md) | [Windows](platform-guides/windows.md)
- **Customize settings:** See [Configuration Guide](../README.md#environment-variables)
- **Advanced features:** Context profiles, smart editing, agent mode

## Need Help?

- **Troubleshooting:** [Troubleshooting Guide](troubleshooting.md)
- **FAQ:** [Frequently Asked Questions](faq.md)
- **Issues:** [GitHub Issues](https://github.com/RehanSajid136602/DictaPilot/issues)

---

**Estimated Time:** 3-5 minutes | **Difficulty:** Easy
