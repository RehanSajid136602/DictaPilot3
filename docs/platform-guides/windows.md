# Windows Setup Guide

Complete guide for setting up DictaPilot3 on Windows.

## System Requirements

- Windows 10 or Windows 11
- Python 3.10 or higher
- Microphone access
- Administrator privileges (for some features)

## Quick Setup

### 1. Install Python

Download Python from [python.org](https://www.python.org/downloads/):
- Check "Add Python to PATH" during installation
- Install for all users (recommended)

**Verify installation:**
```powershell
python --version
```

### 2. Clone Repository

Using Git:
```powershell
git clone https://github.com/RehanSajid136602/DictaPilot.git
cd DictaPilot
```

Or download ZIP from GitHub and extract.

### 3. Run Setup Script

```powershell
setup\setup_windows.bat
```

This installs all required dependencies.

### 4. Configure API Key

Create `.env` file in project root:
```powershell
echo GROQ_API_KEY=your_api_key_here > .env
```

Or use Notepad:
```powershell
notepad .env
```
Add: `GROQ_API_KEY=your_api_key_here`

### 5. Grant Microphone Permission

**Windows 10/11:**
1. Settings → Privacy → Microphone
2. Enable "Allow apps to access your microphone"
3. Enable for Python or Terminal

### 6. Run DictaPilot

```powershell
python app.py
```

## Backend Configuration

### Recommended Settings

```bash
# In .env
HOTKEY_BACKEND=keyboard
PASTE_BACKEND=keyboard
```

### Hotkey Backends

**keyboard** (Recommended):
```bash
HOTKEY_BACKEND=keyboard
```
- Native Windows support
- Most reliable
- May require admin for some apps

**pynput** (Alternative):
```bash
HOTKEY_BACKEND=pynput
```
- Cross-platform
- Good fallback
- Works without admin

### Paste Backends

**keyboard** (Recommended):
```bash
PASTE_BACKEND=keyboard
```
- Direct keyboard simulation
- Fast and reliable
- Works with most apps

**pynput** (Alternative):
```bash
PASTE_BACKEND=pynput
```
- Pure Python implementation
- Good compatibility
- Slightly slower

## Permissions

### Microphone Access

**Windows 10/11:**

1. **Settings → Privacy → Microphone**
2. Enable "Allow apps to access your microphone"
3. Scroll down and enable for:
   - Python
   - Windows Terminal
   - PowerShell
   - Command Prompt

**Verify microphone:**
```powershell
python -c "import sounddevice; print(sounddevice.query_devices())"
```

### Administrator Privileges

Some features may require admin rights:

**When needed:**
- Global hotkeys in some applications
- Keyboard hooks for certain apps
- System-wide clipboard access

**How to run as admin:**
1. Right-click Command Prompt or PowerShell
2. Select "Run as administrator"
3. Navigate to DictaPilot directory
4. Run `python app.py`

**Note:** Try running as normal user first. Only use admin if needed.

## Troubleshooting

### Hotkey Not Working

**Problem:** Pressing F9 does nothing

**Solutions:**

1. **Check for conflicts:**
   - F9 may be used by other applications
   - Try different hotkey:
```bash
HOTKEY=f10
```

2. **Try different backend:**
```bash
HOTKEY_BACKEND=pynput
```

3. **Run as administrator:**
   - Right-click Command Prompt → Run as administrator
   - Navigate to DictaPilot folder
   - Run `python app.py`

4. **Check antivirus:**
   - Some antivirus software blocks keyboard hooks
   - Add DictaPilot to exceptions

5. **Verify Python is in PATH:**
```powershell
where python
```

### Paste Not Working

**Problem:** Text transcribes but doesn't paste

**Solutions:**

1. **Try different backend:**
```bash
PASTE_BACKEND=pynput
```

2. **Check clipboard:**
```powershell
# Text should be in clipboard
# Try manual paste with Ctrl+V
```

3. **Verify app accepts input:**
   - Some apps block programmatic input
   - Test with Notepad first

4. **Check focus:**
   - Ensure text field is focused before releasing hotkey
   - Click in the text field first

5. **Disable clipboard managers:**
   - Third-party clipboard managers may interfere
   - Temporarily disable and test

### Audio Issues

**Problem:** No audio input or poor quality

**Solutions:**

1. **Check microphone permission:**
   - Settings → Privacy → Microphone
   - Enable for Python/Terminal

2. **List audio devices:**
```powershell
python -c "import sounddevice; print(sounddevice.query_devices())"
```

3. **Select specific device:**
```bash
# In .env
AUDIO_DEVICE=1  # Use device index from list
```

4. **Test microphone:**
   - Settings → System → Sound → Input
   - Test your microphone
   - Adjust input volume

5. **Update audio drivers:**
   - Device Manager → Sound, video and game controllers
   - Right-click microphone → Update driver

6. **Adjust sample rate:**
```bash
SAMPLE_RATE=44100  # Try: 16000, 44100, 48000
```

### Python Not Found

**Problem:** `python` command not recognized

**Solutions:**

1. **Add Python to PATH:**
   - Search "Environment Variables" in Start Menu
   - Edit "Path" variable
   - Add Python installation directory
   - Example: `C:\Users\YourName\AppData\Local\Programs\Python\Python312`

2. **Use full path:**
```powershell
C:\Users\YourName\AppData\Local\Programs\Python\Python312\python.exe app.py
```

3. **Reinstall Python:**
   - Download from python.org
   - Check "Add Python to PATH" during installation

### Module Import Errors

**Problem:** `ModuleNotFoundError` when running

**Solutions:**

1. **Reinstall dependencies:**
```powershell
pip install -r requirements.txt
```

2. **Use virtual environment:**
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

3. **Check Python version:**
```powershell
python --version
# Should be 3.10 or higher
```

### Antivirus Blocking

**Problem:** Antivirus flags DictaPilot

**Solutions:**

1. **Add to exceptions:**
   - Open your antivirus software
   - Add DictaPilot folder to exceptions
   - Add python.exe to exceptions

2. **Temporarily disable:**
   - Disable antivirus temporarily
   - Test if DictaPilot works
   - Re-enable and add exceptions

3. **Windows Defender:**
   - Settings → Update & Security → Windows Security
   - Virus & threat protection → Manage settings
   - Add exclusion for DictaPilot folder

## Performance Optimization

### Reduce Latency

```bash
# Faster transcription model
GROQ_WHISPER_MODEL=whisper-large-v3-turbo

# Disable instant refine
INSTANT_REFINE=0

# Use delta paste
PASTE_MODE=delta

# Use keyboard backend (fastest)
PASTE_BACKEND=keyboard
```

### Reduce Resource Usage

```bash
# Heuristic mode (no LLM)
SMART_MODE=heuristic

# Lower sample rate
SAMPLE_RATE=16000
```

## Auto-Start on Login

### Using Task Scheduler

1. **Open Task Scheduler:**
   - Press Win+R
   - Type `taskschd.msc`
   - Press Enter

2. **Create Basic Task:**
   - Click "Create Basic Task"
   - Name: "DictaPilot"
   - Trigger: "When I log on"
   - Action: "Start a program"
   - Program: `C:\Users\YourName\AppData\Local\Programs\Python\Python312\python.exe`
   - Arguments: `C:\path\to\DictaPilot\app.py`
   - Start in: `C:\path\to\DictaPilot`

3. **Configure:**
   - Check "Run with highest privileges" if needed
   - Finish

### Using Startup Folder

1. **Create shortcut:**
   - Right-click `app.py`
   - Create shortcut

2. **Edit shortcut:**
   - Right-click shortcut → Properties
   - Target: `C:\Users\YourName\AppData\Local\Programs\Python\Python312\python.exe "C:\path\to\DictaPilot\app.py"`
   - Start in: `C:\path\to\DictaPilot`

3. **Move to Startup:**
   - Press Win+R
   - Type `shell:startup`
   - Move shortcut to this folder

## Advanced Configuration

### Custom Hotkey Combinations

```bash
# Modifier keys
HOTKEY=ctrl+shift+d
HOTKEY=alt+f9
HOTKEY=win+space
```

### Multiple Audio Devices

```bash
# List all devices
python -c "import sounddevice; print(sounddevice.query_devices())"

# Select by index
AUDIO_DEVICE=2

# Or by name
AUDIO_DEVICE="USB Microphone"
```

### Network Configuration

```bash
# Use proxy
set HTTP_PROXY=http://proxy.example.com:8080
set HTTPS_PROXY=http://proxy.example.com:8080
```

### Firewall Configuration

If Windows Firewall blocks network access:

1. **Windows Defender Firewall → Allow an app**
2. Click "Change settings"
3. Click "Allow another app"
4. Browse to python.exe
5. Add and enable for Private and Public networks

## Windows Version Specific

### Windows 10

- Works with all features
- May need admin for some apps
- Microphone permission in Settings → Privacy

### Windows 11

- Enhanced security features
- Microphone permission in Settings → Privacy & security
- May show additional security prompts
- Recommended to use latest Python version

## Common Issues

### DLL Load Failed

**Problem:** `ImportError: DLL load failed`

**Solution:**
Install Visual C++ Redistributable:
- Download from Microsoft website
- Install both x86 and x64 versions

### PortAudio Error

**Problem:** `Error loading PortAudio`

**Solution:**
```powershell
pip uninstall sounddevice soundfile
pip install sounddevice soundfile
```

### Encoding Errors

**Problem:** `UnicodeDecodeError` or encoding issues

**Solution:**
```bash
# In .env
PYTHONIOENCODING=utf-8
```

## See Also

- [Quick Start Guide](../quick-start.md)
- [Voice Commands](../voice-commands.md)
- [Troubleshooting](../troubleshooting.md)
- [Linux Guide](linux.md)
- [macOS Guide](macos.md)

---

**Last Updated:** 2026-02-17
