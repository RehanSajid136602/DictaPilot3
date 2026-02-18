## Why

DictaPilot3 currently depends on X11 for Linux support, blocking users on modern Linux desktops that default to Wayland (Ubuntu 22.04+, Fedora, GNOME, KDE Plasma). This creates a significant barrier for Linux adoption as Wayland becomes the standard display server. Implementing native Wayland support removes this limitation and ensures DictaPilot3 works on modern Linux systems without requiring XWayland compatibility layers.

## What Changes

- Implement Wayland-native hotkey backend using XDG desktop portal
- Implement Wayland-native paste backend using wl-clipboard and input method protocols
- Add automatic display server detection (X11 vs Wayland)
- Add backend selection logic with Wayland-first preference on Wayland systems
- Maintain X11 backend as fallback for compatibility
- Add Wayland-specific configuration options
- Update documentation with Wayland setup instructions
- Handle Wayland permission dialogs gracefully
- Test on major Wayland compositors (GNOME, KDE Plasma, Sway)

## Capabilities

### New Capabilities
- `wayland-hotkey-backend`: Native Wayland global hotkey registration using XDG desktop portal
- `wayland-paste-backend`: Native Wayland text pasting using wl-clipboard and input protocols
- `display-server-detection`: Automatic detection of X11 vs Wayland environment
- `wayland-permissions`: Handle Wayland permission dialogs for global shortcuts

### Modified Capabilities
<!-- No existing capabilities being modified - this is additive -->

## Impact

**Code Changes:**
- New: `wayland_backend.py` - Wayland-specific backend implementations
- Modified: `app.py` - Add display server detection and backend selection
- Modified: `paste_utils.py` - Integrate Wayland paste backend
- Modified: `config.py` - Add Wayland configuration options

**Dependencies:**
- Add: `wl-clipboard` (system package, optional)
- Add: `PyGObject` for XDG portal integration (optional)
- Existing: `pynput` (already used, works on Wayland)

**Configuration:**
- New: `DISPLAY_SERVER` - Force X11 or Wayland (auto-detect by default)
- New: `WAYLAND_COMPOSITOR` - Compositor-specific optimizations
- Modified: `HOTKEY_BACKEND` - Add "wayland" option
- Modified: `PASTE_BACKEND` - Add "wayland" option

**User Experience:**
- Wayland users can use DictaPilot3 without XWayland
- Automatic backend selection based on display server
- One-time permission dialog for global shortcuts (Wayland security)
- Graceful fallback to X11 backend if Wayland fails

**Platform Support:**
- Ubuntu 22.04+ (GNOME on Wayland)
- Fedora 35+ (GNOME/KDE on Wayland)
- Arch Linux (various Wayland compositors)
- KDE Plasma 5.24+ (Wayland session)
- Sway (tiling Wayland compositor)

**Documentation:**
- Update Linux platform guide with Wayland instructions
- Add Wayland troubleshooting section
- Document permission requirements
- Add compositor-specific notes

**Testing:**
- Test on GNOME (Wayland)
- Test on KDE Plasma (Wayland)
- Test on Sway
- Verify X11 fallback still works
- Test permission dialogs
- Verify hotkey and paste functionality
