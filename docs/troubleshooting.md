# Troubleshooting Guide

Common issues and solutions for DictaPilot3.

## Quick Diagnostics

Run these commands to check system status:

```bash
# Check Python and dependencies
python --version
python -c "import groq, sounddevice, PySide6; print('Dependencies OK')"

# Check API connectivity
python -c "from groq import Groq; import os; from dotenv import load_dotenv; load_dotenv(); client = Groq(api_key=os.getenv('GROQ_API_KEY')); print('API OK')"

# List audio devices
python -c "import sounddevice; print(sounddevice.query_devices())"

# Check storage
python app.py --stats
```

---

## Issue: Hotkey Not Working

### Symptoms
- Pressing F9 (or configured hotkey) does nothing
- No recording indicator appears
- Application seems unresponsive to hotkey

### Diagnostic Flowchart

```
Is the application running?
├─ NO → Start with: python app.py
└─ YES → Is there output in the console when pressing hotkey?
    ├─ NO → Backend issue (see solutions below)
    └─ YES → Check if "Recording" state is shown
        ├─ NO → Hotkey detected but not triggering recording
        └─ YES → Recording works, check paste issue instead
```

### Solutions

**1. Check backend configuration:**

```bash
# Linux X11
HOTKEY_BACKEND=x11

# Linux Wayland
HOTKEY_BACKEND=pynput

# macOS
HOTKEY_BACKEND=keyboard

# Windows
HOTKEY_BACKEND=keyboard
```

**2. Check for hotkey conflicts:**

- **Linux:** Check desktop environment shortcuts
- **macOS:** System Preferences → Keyboard → Shortcuts
- **Windows:** Check other applications using F9

**3. Change hotkey:**

```bash
HOTKEY=f10
# or
HOTKEY=ctrl+shift+d
```

**4. Check permissions:**

- **Linux:** No special permissions needed for X11
- **macOS:** Grant Accessibility permission (System Preferences → Security & Privacy → Privacy → Accessibility)
- **Windows:** May need to run as administrator

**5. Try alternative backend:**

```bash
HOTKEY_BACKEND=pynput
```

**6. Verify hotkey format:**

Valid formats: `f1`-`f12`, `ctrl+shift+d`, `alt+f9`, `cmd+space`

---

## Issue: Text Not Pasting

### Symptoms
- Transcription appears in console
- Text doesn't appear in target application
- Clipboard may or may not contain text

### Diagnostic Flowchart

```
Is text being transcribed?
├─ NO → See "Transcription Issues" section
└─ YES → Is text in clipboard? (Try Ctrl+V manually)
    ├─ NO → Clipboard not being set (backend issue)
    └─ YES → Paste mechanism failing
        ├─ Try different PASTE_BACKEND
        └─ Check target app accepts programmatic input
```

### Solutions

**1. Try different paste backend:**

```bash
# Linux
PASTE_BACKEND=xdotool  # Requires: sudo apt install xdotool
# or
PASTE_BACKEND=x11
# or
PASTE_BACKEND=pynput

# macOS
PASTE_BACKEND=osascript  # Recommended
# or
PASTE_BACKEND=keyboard

# Windows
PASTE_BACKEND=keyboard  # Recommended
# or
PASTE_BACKEND=pynput
```

**2. Check permissions:**

- **Linux:** No special permissions for xdotool/x11
- **macOS:** Accessibility permission required
- **Windows:** May need admin for some apps

**3. Verify target app accepts input:**

Test with simple apps first:
- **Linux:** gedit, Kate
- **macOS:** TextEdit, Notes
- **Windows:** Notepad

Some apps block programmatic input (security software, password fields).

**4. Check focus:**

- Click in text field before releasing hotkey
- Ensure window is active and focused
- Some apps require explicit focus

**5. Try manual paste:**

If text is in clipboard but not pasting:
- Press Ctrl+V (Cmd+V on macOS) manually
- If this works, it's a paste backend issue

**6. Use delta paste mode:**

```bash
PASTE_MODE=delta  # Only sends changed characters
```

---

## Issue: API Key Errors

### Symptoms
- "Invalid API key" error
- "Authentication failed" message
- 401 Unauthorized errors

### Solutions

**1. Verify API key is set:**

```bash
# Check .env file exists
cat .env

# Should contain:
GROQ_API_KEY=gsk_...
```

**2. Get valid API key:**

- Visit [console.groq.com](https://console.groq.com)
- Sign up or log in
- Create new API key
- Copy entire key (starts with `gsk_`)

**3. Check for whitespace:**

```bash
# Remove any spaces or newlines
GROQ_API_KEY=gsk_your_key_here
```

**4. Test API key:**

```bash
python -c "from groq import Groq; import os; from dotenv import load_dotenv; load_dotenv(); client = Groq(api_key=os.getenv('GROQ_API_KEY')); print('API key valid')"
```

**5. Check internet connection:**

```bash
ping console.groq.com
```

**6. Check for rate limits:**

- Free tier has usage limits
- Wait a few minutes and try again
- Check Groq console for quota

---

## Issue: No Audio Input

### Symptoms
- "No audio detected" message
- Recording indicator shows but no transcription
- Empty or silent audio file

### Diagnostic Flowchart

```
Can you record audio with other apps?
├─ NO → System audio issue (check OS settings)
└─ YES → Is microphone listed in device query?
    ├─ NO → Microphone not detected by Python
    └─ YES → Is correct device selected?
        ├─ NO → Set AUDIO_DEVICE
        └─ YES → Check permissions
```

### Solutions

**1. List available devices:**

```bash
python -c "import sounddevice; print(sounddevice.query_devices())"
```

**2. Select specific device:**

```bash
# In .env
AUDIO_DEVICE=1  # Use index from device list
```

**3. Check microphone permissions:**

- **Linux:** Usually no permission needed
- **macOS:** System Preferences → Security & Privacy → Privacy → Microphone
- **Windows:** Settings → Privacy → Microphone

**4. Test microphone:**

```bash
# Linux
arecord -d 5 test.wav && aplay test.wav

# macOS
python -c "import sounddevice as sd; import soundfile as sf; rec = sd.rec(int(5 * 16000), samplerate=16000, channels=1); sd.wait(); sf.write('test.wav', rec, 16000)"
afplay test.wav

# Windows
# Use Sound Recorder app to test
```

**5. Adjust sample rate:**

```bash
SAMPLE_RATE=44100  # Try: 16000, 44100, 48000
```

**6. Check system audio settings:**

- Verify correct microphone is selected as default
- Check input level is not muted
- Adjust input volume

---

## Issue: Poor Transcription Quality

### Symptoms
- Many incorrect words
- Missing words
- Garbled transcription

### Solutions

**1. Improve audio quality:**

- Use external microphone (better than built-in)
- Reduce background noise
- Speak clearly at normal pace
- Position microphone 6-12 inches from mouth

**2. Adjust sample rate:**

```bash
SAMPLE_RATE=44100  # Higher quality
```

**3. Use accurate mode:**

```bash
DICTATION_MODE=accurate
```

**4. Try different model:**

```bash
GROQ_WHISPER_MODEL=whisper-large-v3  # More accurate but slower
```

**5. Check internet speed:**

- Slow connection affects transcription
- Test with: `speedtest-cli`

**6. Reduce cleanup aggressiveness:**

```bash
CLEANUP_LEVEL=basic
CLEANUP_STRICTNESS=conservative
```

---

## Issue: Slow Performance

### Symptoms
- Long delay between speaking and paste
- High CPU/memory usage
- Application feels sluggish

### Solutions

**1. Use faster model:**

```bash
GROQ_WHISPER_MODEL=whisper-large-v3-turbo
```

**2. Disable instant refine:**

```bash
INSTANT_REFINE=0
```

**3. Use heuristic mode:**

```bash
SMART_MODE=heuristic  # No LLM calls
```

**4. Use delta paste:**

```bash
PASTE_MODE=delta
```

**5. Lower sample rate:**

```bash
SAMPLE_RATE=16000
```

**6. Reduce cleanup:**

```bash
CLEANUP_LEVEL=basic
```

---

## Issue: Application Crashes

### Symptoms
- Application exits unexpectedly
- Python error messages
- Segmentation fault

### Solutions

**1. Check Python version:**

```bash
python --version
# Should be 3.10 or higher
```

**2. Reinstall dependencies:**

```bash
pip install --force-reinstall -r requirements.txt
```

**3. Check for conflicts:**

```bash
# Use virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

**4. Check logs:**

```bash
# Run with verbose output
python app.py 2>&1 | tee dictapilot.log
```

**5. Update system libraries:**

- **Linux:** `sudo apt update && sudo apt upgrade`
- **macOS:** `brew update && brew upgrade`
- **Windows:** Update via Windows Update

---

## Platform-Specific Issues

### Linux

**Wayland hotkey issues:**
```bash
HOTKEY_BACKEND=pynput
```

**X11 paste fails:**
```bash
sudo apt install xdotool
PASTE_BACKEND=xdotool
```

**Permission denied:**
```bash
# Don't run as root
# Check file permissions
chmod +x app.py
```

### macOS

**Accessibility permission:**
- System Preferences → Security & Privacy → Privacy → Accessibility
- Add Terminal/iTerm2

**Keychain prompts:**
- Click "Always Allow" when prompted

**osascript slow:**
```bash
PASTE_BACKEND=keyboard
```

### Windows

**Python not found:**
- Add Python to PATH
- Reinstall Python with "Add to PATH" checked

**Antivirus blocking:**
- Add DictaPilot folder to exceptions
- Add python.exe to exceptions

**Admin required:**
- Right-click Command Prompt → Run as administrator

---

## Getting More Help

**Check logs:**
```bash
python app.py 2>&1 | tee debug.log
```

**Report issue:**
- GitHub Issues: [github.com/RehanSajid136602/DictaPilot/issues](https://github.com/RehanSajid136602/DictaPilot/issues)
- Include: OS, Python version, error message, steps to reproduce

**See also:**
- [Platform Guides](platform-guides/) - Platform-specific setup
- [FAQ](faq.md) - Frequently asked questions
- [Quick Start](quick-start.md) - Setup guide

---

**Last Updated:** 2026-02-17
