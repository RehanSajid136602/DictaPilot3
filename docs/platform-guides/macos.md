# macOS Setup Guide

Complete guide for setting up DictaPilot3 on macOS.

## System Requirements

- macOS 10.14 (Mojave) or later
- Python 3.10 or higher
- Microphone access
- Accessibility permissions

## Quick Setup

### 1. Install Homebrew (if not installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install Python

```bash
brew install python@3.12
```

### 3. Clone and Setup

```bash
git clone https://github.com/RehanSajid136602/DictaPilot.git
cd DictaPilot
./setup/setup_macos.command
```

### 4. Configure API Key

```bash
echo "GROQ_API_KEY=your_api_key_here" > .env
```

### 5. Grant Permissions

**Accessibility Permission (Required):**
1. Open System Preferences → Security & Privacy → Privacy
2. Select "Accessibility" from the left sidebar
3. Click the lock icon and authenticate
4. Add Terminal (or iTerm2) to the list
5. Check the box to enable

**Microphone Permission:**
1. System Preferences → Security & Privacy → Privacy
2. Select "Microphone"
3. Enable for Terminal/iTerm2

### 6. Run DictaPilot

```bash
python app.py
```

## Backend Configuration

### Recommended Settings

```bash
# In .env
HOTKEY_BACKEND=keyboard
PASTE_BACKEND=osascript
```

### Hotkey Backends

**keyboard** (Recommended):
```bash
HOTKEY_BACKEND=keyboard
```
- Native macOS support
- Most reliable
- Requires Accessibility permission

**pynput** (Alternative):
```bash
HOTKEY_BACKEND=pynput
```
- Cross-platform
- Good fallback
- Also requires Accessibility permission

### Paste Backends

**osascript** (Recommended):
```bash
PASTE_BACKEND=osascript
```
- Native AppleScript integration
- Works with all macOS apps
- Most reliable paste method

**keyboard** (Alternative):
```bash
PASTE_BACKEND=keyboard
```
- Direct keyboard simulation
- Faster but less compatible

**pynput** (Fallback):
```bash
PASTE_BACKEND=pynput
```
- Pure Python implementation
- Slowest but most compatible

## Permissions Setup

### Accessibility Permission

**Why needed:** Required for global hotkey detection and keyboard simulation.

**How to grant:**

1. **System Preferences → Security & Privacy → Privacy → Accessibility**
2. Click the lock icon (bottom left) and enter your password
3. Click the "+" button
4. Navigate to `/Applications/Utilities/Terminal.app` (or iTerm2)
5. Click "Open"
6. Ensure the checkbox next to Terminal is checked

**Troubleshooting:**
- If Terminal is already in the list but not working, remove it and re-add
- Restart Terminal after granting permission
- Some apps may require full disk access as well

### Microphone Permission

**Why needed:** Required for audio recording.

**How to grant:**

1. **System Preferences → Security & Privacy → Privacy → Microphone**
2. Enable checkbox for Terminal (or iTerm2)
3. Restart Terminal

**Verify microphone access:**
```bash
python -c "import sounddevice; print(sounddevice.query_devices())"
```

### Keychain Access (Optional)

DictaPilot can store your API key in macOS Keychain for better security.

**First time:**
- When prompted, click "Always Allow" to grant keychain access
- This stores your API key securely

**Manual keychain setup:**
```bash
security add-generic-password -a "$USER" -s "DictaPilot" -w "your_api_key_here"
```

## Troubleshooting

### Hotkey Not Working

**Problem:** Pressing F9 does nothing

**Solutions:**

1. **Check Accessibility permission:**
   - System Preferences → Security & Privacy → Privacy → Accessibility
   - Ensure Terminal is enabled

2. **Check for conflicts:**
   - F9 may be used by Mission Control or other system features
   - System Preferences → Keyboard → Shortcuts
   - Disable conflicting shortcuts or change DictaPilot hotkey

3. **Change hotkey:**
```bash
HOTKEY=f10
# or
HOTKEY=ctrl+shift+d
```

4. **Try different backend:**
```bash
HOTKEY_BACKEND=pynput
```

5. **Restart Terminal:**
   - Quit Terminal completely (Cmd+Q)
   - Reopen and try again

### Paste Not Working

**Problem:** Text transcribes but doesn't paste

**Solutions:**

1. **Use osascript backend:**
```bash
PASTE_BACKEND=osascript
```

2. **Check Accessibility permission:**
   - Required for keyboard simulation
   - See Accessibility Permission section above

3. **Verify app accepts paste:**
   - Some apps block programmatic input
   - Test with TextEdit or Notes first

4. **Try manual paste:**
   - Text is copied to clipboard
   - Press Cmd+V manually

5. **Check focus:**
   - Ensure text field is focused before releasing hotkey
   - Click in the text field first

### Audio Issues

**Problem:** No audio input or poor quality

**Solutions:**

1. **Check microphone permission:**
   - System Preferences → Security & Privacy → Privacy → Microphone
   - Enable for Terminal

2. **List audio devices:**
```bash
python -c "import sounddevice; print(sounddevice.query_devices())"
```

3. **Select specific device:**
```bash
# In .env
AUDIO_DEVICE=1  # Use device index from list
```

4. **Test microphone:**
```bash
# Record 5 seconds
python -c "import sounddevice as sd; import soundfile as sf; rec = sd.rec(int(5 * 16000), samplerate=16000, channels=1); sd.wait(); sf.write('test.wav', rec, 16000)"

# Play back
afplay test.wav
```

5. **Adjust sample rate:**
```bash
SAMPLE_RATE=44100  # Try: 16000, 44100, 48000
```

6. **Check system audio settings:**
   - System Preferences → Sound → Input
   - Verify correct microphone is selected
   - Check input level

### Permission Prompts Keep Appearing

**Problem:** macOS keeps asking for permissions

**Solutions:**

1. **Grant "Always Allow" instead of "Allow"**

2. **Add to Full Disk Access:**
   - System Preferences → Security & Privacy → Privacy → Full Disk Access
   - Add Terminal

3. **Reset permissions:**
```bash
tccutil reset Accessibility
tccutil reset Microphone
```
   - Then re-grant permissions

### API Key Not Saved

**Problem:** API key not persisting between sessions

**Solutions:**

1. **Check .env file exists:**
```bash
ls -la .env
cat .env
```

2. **Use Keychain storage:**
```bash
# Store in Keychain
security add-generic-password -a "$USER" -s "DictaPilot" -w "your_api_key_here"

# Verify
security find-generic-password -a "$USER" -s "DictaPilot" -w
```

3. **Check file permissions:**
```bash
chmod 600 .env
```

## Performance Optimization

### Reduce Latency

```bash
# Faster transcription model
GROQ_WHISPER_MODEL=whisper-large-v3-turbo

# Disable instant refine
INSTANT_REFINE=0

# Use delta paste
PASTE_MODE=delta

# Use osascript (fastest on macOS)
PASTE_BACKEND=osascript
```

### Reduce Resource Usage

```bash
# Heuristic mode (no LLM)
SMART_MODE=heuristic

# Lower sample rate
SAMPLE_RATE=16000
```

## Auto-Start on Login

### Using Login Items

1. **Create Application Bundle:**
```bash
# Create app wrapper
mkdir -p ~/Applications/DictaPilot.app/Contents/MacOS
cat > ~/Applications/DictaPilot.app/Contents/MacOS/DictaPilot << 'SCRIPT'
#!/bin/bash
cd /path/to/DictaPilot
python app.py
SCRIPT
chmod +x ~/Applications/DictaPilot.app/Contents/MacOS/DictaPilot
```

2. **Add to Login Items:**
   - System Preferences → Users & Groups → Login Items
   - Click "+" and select DictaPilot.app

### Using LaunchAgent

Create `~/Library/LaunchAgents/com.dictapilot.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dictapilot</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/path/to/DictaPilot/app.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Load the agent:
```bash
launchctl load ~/Library/LaunchAgents/com.dictapilot.plist
```

## Advanced Configuration

### Custom Hotkey Combinations

```bash
# Modifier keys
HOTKEY=cmd+shift+d
HOTKEY=ctrl+option+space
HOTKEY=cmd+f9
```

### Multiple Audio Devices

```bash
# List all devices
python -c "import sounddevice; print(sounddevice.query_devices())"

# Select by index
AUDIO_DEVICE=2

# Or by name
AUDIO_DEVICE="External Microphone"
```

### Network Configuration

```bash
# Use proxy
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
```

## macOS Version Specific

### macOS Monterey (12.x) and later

- Enhanced privacy controls
- May require additional permissions
- Accessibility permission is mandatory

### macOS Ventura (13.x) and later

- New privacy prompts
- Keychain access may require additional confirmation
- Full Disk Access may be needed for some features

### macOS Sonoma (14.x) and later

- Stricter security policies
- May need to approve app in System Settings → Privacy & Security
- Screen Recording permission may be requested

## See Also

- [Quick Start Guide](../quick-start.md)
- [Voice Commands](../voice-commands.md)
- [Troubleshooting](../troubleshooting.md)
- [Linux Guide](linux.md)
- [Windows Guide](windows.md)

---

**Last Updated:** 2026-02-17
