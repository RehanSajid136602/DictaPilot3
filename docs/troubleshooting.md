# Troubleshooting Guide

Common issues and solutions for DictaPilot3.

## Quick Diagnostics

Run these commands to check system status:

```bash
# Check Python and dependencies
python --version
python -c "import openai, sounddevice, PySide6; print('Dependencies OK')"

# Check API connectivity
python -c "from openai import OpenAI; import os; from dotenv import load_dotenv; load_dotenv(); client = OpenAI(base_url='https://integrate.api.nvidia.com/v1', api_key=os.getenv('NVIDIA_API_KEY')); print('API OK')"

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

---

## Modern UI Issues

### Animations are choppy or laggy

**Symptoms:** Floating window animations stutter or drop frames

**Diagnostic:**
```bash
# Check CPU usage while recording
top  # Linux/macOS
# or Task Manager on Windows
```

**Solutions:**

1. **Enable reduced motion:**
   ```bash
   FLOATING_REDUCED_MOTION=1
   ```
   This keeps essential animations but removes decorative effects.

2. **Disable animations completely:**
   ```bash
   FLOATING_ANIMATIONS=0
   ```

3. **Switch to classic UI:**
   ```bash
   FLOATING_UI_STYLE=classic
   ```

4. **Check CPU usage:**
   - Close other resource-intensive applications
   - Check background processes
   - Verify system isn't thermal throttling

5. **Reduce window size:**
   ```bash
   FLOATING_WIDTH=150
   FLOATING_HEIGHT=40
   ```

**Note:** Animations target 60 FPS and should use <5% CPU on modern hardware.

### Glassmorphism effect not visible

**Symptoms:** Floating window appears solid, not translucent

**Diagnostic:**
```bash
# Check if compositor is running (Linux)
ps aux | grep -i compos

# Check Qt transparency support
python -c "from PySide6.QtWidgets import QApplication; app = QApplication([]); print('Qt OK')"
```

**Solutions:**

1. **Ensure glassmorphism is enabled:**
   ```bash
   FLOATING_GLASSMORPHISM=1
   ```

2. **Linux: Enable compositor**
   - GNOME/KDE: Usually enabled by default
   - i3/bspwm: Install and run `picom` or `compton`
   - Check compositor: `ps aux | grep picom`

3. **Try different accent colors:**
   ```bash
   FLOATING_ACCENT_COLOR=purple
   # or
   FLOATING_ACCENT_COLOR=green
   ```

4. **Verify Qt supports transparency:**
   - Update PySide6: `pip install --upgrade PySide6`
   - Check Qt version: `python -c "from PySide6 import __version__; print(__version__)"`

5. **Switch to classic UI if transparency not supported:**
   ```bash
   FLOATING_UI_STYLE=classic
   ```

**Platform-specific notes:**
- **Linux X11:** Requires compositor (picom, compton, etc.)
- **Linux Wayland:** Compositor built-in, should work out of the box
- **macOS:** Works natively, no additional setup
- **Windows 10/11:** Works natively with DWM

### Accent color not changing

**Symptoms:** Floating window stays same color despite changing setting

**Diagnostic:**
```bash
# Check current setting
grep FLOATING_ACCENT_COLOR .env
```

**Solutions:**

1. **Restart DictaPilot after changing .env:**
   - Stop the application (Ctrl+C)
   - Edit `.env` file
   - Start again: `python app.py`

2. **Verify spelling:**
   ```bash
   FLOATING_ACCENT_COLOR=blue     # ✓ Correct
   FLOATING_ACCENT_COLOR=purple   # ✓ Correct
   FLOATING_ACCENT_COLOR=green    # ✓ Correct
   FLOATING_ACCENT_COLOR=Blue     # ✗ Wrong (case-sensitive)
   FLOATING_ACCENT_COLOR=red      # ✗ Not supported
   ```

3. **Check for typos in .env file:**
   - No extra spaces: `FLOATING_ACCENT_COLOR=blue` (not `= blue`)
   - No quotes needed: `blue` (not `"blue"`)

4. **Clear cache and restart:**
   ```bash
   rm -rf __pycache__
   python app.py
   ```

5. **Verify modern UI is enabled:**
   ```bash
   FLOATING_UI_STYLE=modern
   ```

### Floating window too small or too large

**Symptoms:** Window size doesn't match expectations

**Solutions:**

1. **Adjust dimensions:**
   ```bash
   FLOATING_WIDTH=200
   FLOATING_HEIGHT=50
   ```

2. **Check DPI scaling:**
   - High DPI displays may scale differently
   - Window should scale appropriately automatically

3. **Try different layout:**
   ```bash
   FLOATING_LAYOUT=pill      # Default, balanced
   FLOATING_LAYOUT=circular  # Compact
   FLOATING_LAYOUT=card      # Larger
   ```

### Hover effects not working

**Symptoms:** No visual change when hovering over floating window

**Solutions:**

1. **Ensure animations are enabled:**
   ```bash
   FLOATING_ANIMATIONS=1
   FLOATING_REDUCED_MOTION=0
   ```

2. **Check if modern UI is active:**
   ```bash
   FLOATING_UI_STYLE=modern
   ```

3. **Restart application** after changing settings

### Performance impact from modern UI

**Symptoms:** System feels slower with modern UI enabled

**Diagnostic:**
```bash
# Monitor CPU usage
top -p $(pgrep -f "python.*app.py")
```

**Solutions:**

1. **Use reduced motion:**
   ```bash
   FLOATING_REDUCED_MOTION=1
   ```
   Reduces animation complexity while keeping functionality.

2. **Disable specific features:**
   ```bash
   FLOATING_GLASSMORPHISM=0  # Disable glass effect
   FLOATING_ANIMATIONS=0     # Disable animations
   ```

3. **Switch to classic UI:**
   ```bash
   FLOATING_UI_STYLE=classic
   ```
   Classic UI has minimal overhead.

4. **Reduce bar count:**
   ```bash
   FLOATING_BAR_COUNT=3  # Fewer bars = less rendering
   ```

**Expected performance:**
- CPU usage: <5% during animations
- Memory: ~50KB additional for animation state
- No impact on transcription quality or speed

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
NVIDIA_API_KEY=nvapi_...
```

**2. Get valid API key:**

- Visit [build.nvidia.com](https://build.nvidia.com)
- Sign up or log in
- Create new API key
- Copy entire key (starts with `nvapi_`)

**3. Check for whitespace:**

```bash
# Remove any spaces or newlines
NVIDIA_API_KEY=your_key_here
```

**4. Test API key:**

```bash
python -c "from openai import OpenAI; import os; from dotenv import load_dotenv; load_dotenv(); client = OpenAI(base_url='https://integrate.api.nvidia.com/v1', api_key=os.getenv('NVIDIA_API_KEY')); print('API key valid')"
```

**5. Check internet connection:**

```bash
ping build.nvidia.com
```

**6. Check for rate limits:**

- Free tier has usage limits
- Wait a few minutes and try again
- Check NVIDIA console for quota

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
NVIDIA_WHISPER_MODEL=openai/whisper-large-v3  # More accurate but slower
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
NVIDIA_WHISPER_MODEL=openai/whisper-large-v3-turbo
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
