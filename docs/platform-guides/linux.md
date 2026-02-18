# Linux Setup Guide

Complete guide for setting up DictaPilot3 on Linux systems.

## System Requirements

- Linux distribution (Ubuntu 20.04+, Fedora 35+, Arch, Debian, etc.)
- Python 3.10 or higher
- X11 or Wayland display server
- Microphone with working audio input

## Quick Setup

### 1. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv xdotool portaudio19-dev
```

**Fedora:**
```bash
sudo dnf install python3 python3-pip xdotool portaudio-devel
```

**Arch:**
```bash
sudo pacman -S python python-pip xdotool portaudio
```

### 2. Clone and Setup

```bash
git clone https://github.com/RehanSajid136602/DictaPilot.git
cd DictaPilot
./setup/setup_linux.sh
```

### 3. Configure API Key

```bash
echo "GROQ_API_KEY=your_api_key_here" > .env
```

### 4. Run DictaPilot

```bash
python app.py
```

## Display Server Configuration

### X11 (Default)

DictaPilot works out-of-the-box with X11.

**Check if you're using X11:**
```bash
echo $XDG_SESSION_TYPE
# Output: x11
```

**Recommended backends:**
```bash
# In .env
HOTKEY_BACKEND=x11
PASTE_BACKEND=x11
```

### Wayland

DictaPilot now has native Wayland support! It automatically detects your display server and selects the appropriate backends.

**Check if you're using Wayland:**
```bash
echo $XDG_SESSION_TYPE
# Output: wayland
```

**Native Wayland Support (Recommended):**
```bash
# Install wl-clipboard for clipboard operations
sudo apt install wl-clipboard wtype  # Ubuntu/Debian
sudo dnf install wl-clipboard wtype  # Fedora
sudo pacman -S wl-clipboard wtype    # Arch

# DictaPilot will auto-detect and use native Wayland backends
# No configuration needed!
```

**Verify Wayland dependencies:**
```bash
python app.py --wayland-deps
```

**Backend Selection:**
- **Hotkey backend**: Uses pynput on Wayland (XDG portal integration planned)
- **Paste backend**: Uses wl-clipboard + wtype for native Wayland clipboard

**Manual Override:**
```bash
# Force Wayland backends
HOTKEY_BACKEND=wayland
PASTE_BACKEND=wayland

# Force X11 backends (for XWayland compatibility)
HOTKEY_BACKEND=x11
PASTE_BACKEND=x11
```

**Known Wayland Considerations:**
- Global hotkeys work via pynput on most Wayland compositors
- wl-clipboard provides reliable clipboard operations
- Some compositors may have permission dialogs for global shortcuts

## Backend Selection

### Hotkey Backends

**wayland** (Recommended for Wayland):
```bash
HOTKEY_BACKEND=wayland
```
- Native Wayland support via pynput
- Auto-selected when on Wayland
- Works with GNOME, KDE Plasma, Sway

**x11** (Recommended for X11):
```bash
HOTKEY_BACKEND=x11
```
- Direct X11 integration
- Most reliable on X11 systems
- Requires X11 display server

**pynput** (Cross-platform):
```bash
HOTKEY_BACKEND=pynput
```
- Works on X11 and Wayland
- May require accessibility permissions
- Good fallback option

**keyboard** (Alternative):
```bash
HOTKEY_BACKEND=keyboard
```
- May require root permissions
- Not recommended for regular use

### Paste Backends

**wayland** (Recommended for Wayland):
```bash
PASTE_BACKEND=wayland
```
- Uses wl-clipboard and wtype
- Native Wayland clipboard operations
- Requires wl-clipboard package

**x11** (Recommended for X11):
```bash
PASTE_BACKEND=x11
```
- Direct X11 clipboard manipulation
- Fastest paste method
- Requires X11 display server

**xdotool** (Universal):
```bash
PASTE_BACKEND=xdotool
```
- Works on X11 and XWayland
- Requires xdotool package
- Good compatibility

**pynput** (Fallback):
```bash
PASTE_BACKEND=pynput
```
- Pure Python implementation
- Slower but works everywhere
- No additional dependencies

## Permissions

### Microphone Access

Grant microphone permissions:

```bash
# Check available audio devices
python -c "import sounddevice; print(sounddevice.query_devices())"

# Test microphone
arecord -d 5 test.wav
aplay test.wav
```

### Input Permissions

Some desktop environments require accessibility permissions:

**GNOME:**
- Settings → Privacy → Screen Recording
- Enable for Terminal or your Python interpreter

**KDE Plasma:**
- Usually no additional permissions needed

## Desktop Environment Specific

### GNOME

**Hotkey conflicts:**
GNOME may use F9 for other functions. Change the hotkey:
```bash
HOTKEY=f10
```

**Wayland support:**
GNOME on Wayland works well with native Wayland backends:
```bash
# Native Wayland (recommended)
HOTKEY_BACKEND=wayland
PASTE_BACKEND=wayland

# Or fallback
HOTKEY_BACKEND=pynput
PASTE_BACKEND=xdotool
```

**Permission dialogs:**
- GNOME may show permission dialogs for global shortcuts
- Click "Allow" when prompted

### KDE Plasma

**Works well with default settings.**

**For Wayland:**
```bash
HOTKEY_BACKEND=wayland
PASTE_BACKEND=wayland
```

**X11 session:**
```bash
HOTKEY_BACKEND=x11
PASTE_BACKEND=x11
```

### i3/Sway

**i3 (X11):**
```bash
HOTKEY_BACKEND=x11
PASTE_BACKEND=x11
```

**Sway (Wayland):**
Sway works excellently with native Wayland support:
```bash
# Install dependencies
sudo apt install wl-clipboard wtype  # Ubuntu/Debian

# Native Wayland backends
HOTKEY_BACKEND=wayland
PASTE_BACKEND=wayland
```

**Sway-specific tip:**
Sway's security model is more permissive, so hotkey detection usually works without issues.

### Hyprland

**Wayland native:**
```bash
# Install dependencies
sudo pacman -S wl-clipboard wtype  # Arch

# Use Wayland backends
HOTKEY_BACKEND=wayland
PASTE_BACKEND=wayland
```

**Note:** Hyprland works well with both pynput and native Wayland backends.

## Troubleshooting

### Hotkey Not Working

**Problem:** Pressing F9 does nothing

**Solutions:**

1. **Check backend:**
```bash
# Try different backends
HOTKEY_BACKEND=x11      # For X11
HOTKEY_BACKEND=pynput   # For Wayland
```

2. **Check for conflicts:**
```bash
# List all hotkeys
gsettings list-recursively | grep -i f9  # GNOME
```

3. **Test hotkey detection:**
```bash
# Run with debug output
python app.py
# Press F9 and check console output
```

4. **Change hotkey:**
```bash
HOTKEY=f10  # Or any other key
```

### Paste Not Working

**Problem:** Text is transcribed but doesn't paste

**Solutions:**

1. **Try different paste backends:**
```bash
PASTE_BACKEND=xdotool
# or
PASTE_BACKEND=pynput
# or
PASTE_BACKEND=x11
```

2. **Install xdotool:**
```bash
sudo apt install xdotool
```

3. **Check clipboard:**
```bash
# Test clipboard manually
echo "test" | xclip -selection clipboard
xdotool key ctrl+v
```

4. **Verify focus:**
- Ensure text field is focused before releasing hotkey
- Some apps don't accept programmatic paste

### Audio Issues

**Problem:** No audio input or poor quality

**Solutions:**

1. **List audio devices:**
```bash
python -c "import sounddevice; print(sounddevice.query_devices())"
```

2. **Select specific device:**
```bash
# In .env
AUDIO_DEVICE=1  # Use device index from list above
```

3. **Test microphone:**
```bash
arecord -d 5 -f cd test.wav
aplay test.wav
```

4. **Check PulseAudio/PipeWire:**
```bash
# PulseAudio
pactl list sources

# PipeWire
pw-cli list-objects | grep -i audio
```

5. **Adjust sample rate:**
```bash
SAMPLE_RATE=44100  # Try different rates: 16000, 44100, 48000
```

### Permission Denied Errors

**Problem:** Permission errors when running

**Solutions:**

1. **Don't run as root:**
```bash
# Run as regular user
python app.py
```

2. **Check file permissions:**
```bash
chmod +x setup/setup_linux.sh
chmod +x app.py
```

3. **Virtual environment:**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### X11 Backend Fails on Wayland

**Problem:** X11 backend doesn't work on Wayland

**Solution:**
```bash
# Use native Wayland backends
HOTKEY_BACKEND=wayland
PASTE_BACKEND=wayland

# Or use pynput/xdotool for XWayland compatibility
HOTKEY_BACKEND=pynput
PASTE_BACKEND=xdotool
```

### Wayland Clipboard Not Working

**Problem:** wl-clipboard operations fail on Wayland

**Solutions:**

1. **Install wl-clipboard:**
```bash
sudo apt install wl-clipboard  # Ubuntu/Debian
sudo dnf install wl-clipboard  # Fedora
sudo pacman -S wl-clipboard    # Arch
```

2. **Check Wayland session:**
```bash
echo $WAYLAND_DISPLAY
# Should show something like: wayland-0
```

3. **Test wl-copy manually:**
```bash
echo "test" | wl-copy
wl-paste
```

4. **Install wtype for keyboard simulation:**
```bash
sudo apt install wtype  # Ubuntu/Debian (may need to build from source)
# or use pynput fallback
```

### Wayland Hotkey Not Detected

**Problem:** Hotkey not detected on Wayland

**Solutions:**

1. **Use pynput backend:**
```bash
HOTKEY_BACKEND=pynput
```

2. **Check compositor permissions:**
- Some Wayland compositors restrict global hotkeys
- Check your compositor's accessibility settings

3. **Try a different hotkey:**
```bash
HOTKEY=f10  # Avoid F9 which may be reserved
```

## Performance Optimization

### Reduce Latency

```bash
# Use faster transcription model
GROQ_WHISPER_MODEL=whisper-large-v3-turbo

# Disable instant refine
INSTANT_REFINE=0

# Use delta paste
PASTE_MODE=delta
```

### Reduce Resource Usage

```bash
# Use heuristic mode (no LLM)
SMART_MODE=heuristic

# Reduce sample rate
SAMPLE_RATE=16000
```

## Auto-Start on Login

### systemd User Service

Create `~/.config/systemd/user/dictapilot.service`:

```ini
[Unit]
Description=DictaPilot Voice Dictation
After=graphical-session.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /path/to/DictaPilot/app.py
Restart=on-failure
Environment="DISPLAY=:0"
Environment="XAUTHORITY=%h/.Xauthority"

[Install]
WantedBy=default.target
```

Enable and start:
```bash
systemctl --user enable dictapilot
systemctl --user start dictapilot
```

### Desktop Entry

Create `~/.config/autostart/dictapilot.desktop`:

```ini
[Desktop Entry]
Type=Application
Name=DictaPilot
Exec=/usr/bin/python3 /path/to/DictaPilot/app.py
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
```

## Advanced Configuration

### Custom Hotkey Combinations

```bash
# Modifier keys
HOTKEY=ctrl+shift+d
HOTKEY=alt+f9
HOTKEY=super+space
```

### Multiple Audio Devices

```bash
# List devices
python -c "import sounddevice; print(sounddevice.query_devices())"

# Select by index
AUDIO_DEVICE=2

# Or by name (partial match)
AUDIO_DEVICE="USB Microphone"
```

### Network Configuration

```bash
# Use proxy
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
```

## See Also

- [Quick Start Guide](../quick-start.md)
- [Voice Commands](../voice-commands.md)
- [Troubleshooting](../troubleshooting.md)
- [macOS Guide](macos.md)
- [Windows Guide](windows.md)

---

**Last Updated:** 2026-02-17
