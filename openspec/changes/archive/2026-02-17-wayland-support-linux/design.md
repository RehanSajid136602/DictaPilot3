## Context

DictaPilot3 currently relies on X11 for Linux support, using X11-specific APIs for global hotkey registration and text pasting. This creates a hard dependency on X11, preventing the application from running natively on Wayland, which is now the default display server on major Linux distributions (Ubuntu 22.04+, Fedora 35+, modern GNOME and KDE Plasma).

**Current State:**
- Hotkey backend: Uses `keyboard` library (X11-dependent) or `pynput` (works on both)
- Paste backend: Uses `xdotool` or direct X11 API calls
- Display server detection: None (assumes X11)
- Wayland users: Must use XWayland compatibility layer (suboptimal)

**Constraints:**
- Must maintain X11 support (many users still on X11)
- Must work without requiring root/sudo
- Must handle Wayland's security model (permission dialogs)
- Should work across different Wayland compositors (GNOME, KDE, Sway)
- Cannot break existing functionality

**Stakeholders:**
- Linux users on modern distributions (Ubuntu 22.04+, Fedora)
- GNOME and KDE Plasma users
- Tiling window manager users (Sway, Hyprland)

## Goals / Non-Goals

**Goals:**
- Native Wayland support without XWayland dependency
- Automatic display server detection (X11 vs Wayland)
- Wayland-native hotkey registration using XDG desktop portal
- Wayland-native text pasting using wl-clipboard
- Graceful fallback to X11 backend when needed
- Support major Wayland compositors (GNOME, KDE, Sway)
- Handle Wayland permission dialogs appropriately
- Maintain backward compatibility with X11

**Non-Goals:**
- Not removing X11 support (must coexist)
- Not supporting all Wayland compositors (focus on major ones)
- Not implementing custom Wayland protocols (use standard portals)
- Not requiring system-wide installation or root access
- Not implementing Wayland-specific features beyond hotkey/paste

## Decisions

### Decision 1: Display Server Detection

**Choice:** Use `XDG_SESSION_TYPE` environment variable with fallback checks

**Rationale:**
- `XDG_SESSION_TYPE` is the standard way to detect Wayland vs X11
- Set by display managers and session managers
- Reliable across distributions
- Simple to implement

**Alternatives Considered:**
- Check for `WAYLAND_DISPLAY` env var: Less reliable, may be set even on X11
- Try to connect to Wayland socket: More complex, unnecessary
- Check running processes: Fragile, compositor-dependent

**Implementation:**
```python
def detect_display_server() -> str:
    """Detect if running on X11 or Wayland."""
    session_type = os.getenv("XDG_SESSION_TYPE", "").lower()
    
    if session_type == "wayland":
        return "wayland"
    elif session_type == "x11":
        return "x11"
    
    # Fallback: check for WAYLAND_DISPLAY
    if os.getenv("WAYLAND_DISPLAY"):
        return "wayland"
    
    # Fallback: check for DISPLAY (X11)
    if os.getenv("DISPLAY"):
        return "x11"
    
    return "unknown"
```

### Decision 2: Wayland Hotkey Backend

**Choice:** Use XDG desktop portal for global shortcuts with `pynput` fallback

**Rationale:**
- XDG desktop portal is the standard Wayland way for global shortcuts
- Requires user permission (security feature)
- Supported by GNOME, KDE Plasma
- `pynput` works on Wayland but may have limitations

**Alternatives Considered:**
- Custom Wayland protocol: Too complex, not standardized
- Compositor-specific APIs: Not portable
- Only use pynput: Works but may miss some keys

**Implementation:**
```python
class WaylandHotkeyBackend:
    def __init__(self):
        self.portal = self._init_portal()
        self.shortcut_id = None
    
    def _init_portal(self):
        """Initialize XDG desktop portal connection."""
        try:
            import gi
            gi.require_version('Gio', '2.0')
            from gi.repository import Gio
            return Gio.DBusProxy.new_for_bus_sync(...)
        except ImportError:
            return None
    
    def register(self, hotkey: str, callback):
        """Register global shortcut via portal."""
        if self.portal:
            # Use XDG portal
            self.shortcut_id = self.portal.call_sync(
                'CreateShortcut',
                GLib.Variant('(sa{sv})', (hotkey, {}))
            )
        else:
            # Fallback to pynput
            self._register_pynput(hotkey, callback)
```

**Note:** XDG portal requires PyGObject, which is optional. If not available, fall back to pynput.

### Decision 3: Wayland Paste Backend

**Choice:** Use `wl-clipboard` (wl-copy + wl-paste) with keyboard simulation

**Rationale:**
- `wl-clipboard` is the standard Wayland clipboard tool
- Available in most distribution repositories
- Simple command-line interface
- Works across all Wayland compositors

**Alternatives Considered:**
- Direct Wayland protocol: Too complex, requires protocol knowledge
- PyGObject with Wayland bindings: Heavy dependency
- Only keyboard simulation: Slower, less reliable

**Implementation:**
```python
def paste_wayland(text: str) -> bool:
    """Paste text on Wayland using wl-clipboard."""
    try:
        # Copy to clipboard using wl-copy
        subprocess.run(
            ['wl-copy'],
            input=text.encode('utf-8'),
            check=True,
            timeout=2
        )
        
        # Simulate Ctrl+V
        time.sleep(0.05)  # Small delay
        subprocess.run(['wtype', '-M', 'ctrl', 'v', '-m', 'ctrl'], check=True)
        
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback to pynput
        return paste_pynput(text)
```

**Dependencies:**
- `wl-clipboard` (system package): For clipboard operations
- `wtype` (optional): For keyboard simulation (alternative: `ydotool`)

### Decision 4: Backend Selection Logic

**Choice:** Automatic selection based on display server with manual override

**Rationale:**
- Most users want it to "just work"
- Power users can override if needed
- Graceful fallback if preferred backend fails

**Selection Logic:**
```python
def select_backend(backend_type: str) -> str:
    """Select appropriate backend based on environment."""
    display_server = detect_display_server()
    user_preference = os.getenv(f"{backend_type.upper()}_BACKEND", "auto")
    
    if user_preference != "auto":
        return user_preference
    
    if display_server == "wayland":
        # Prefer Wayland backends
        if backend_type == "hotkey":
            return "wayland" if has_portal() else "pynput"
        elif backend_type == "paste":
            return "wayland" if has_wl_clipboard() else "pynput"
    else:
        # Prefer X11 backends
        if backend_type == "hotkey":
            return "x11" if has_x11() else "keyboard"
        elif backend_type == "paste":
            return "x11" if has_x11() else "xdotool"
    
    return "pynput"  # Universal fallback
```

### Decision 5: Permission Handling

**Choice:** Show clear instructions when permission dialog appears

**Rationale:**
- Wayland requires explicit user permission for global shortcuts
- First-time users may be confused by permission dialog
- Clear instructions improve UX

**Implementation:**
- Detect when portal permission is needed
- Show console message: "Please grant permission in the dialog"
- Log permission grant/deny
- Provide troubleshooting if permission denied

## Risks / Trade-offs

### Risk 1: XDG Portal Not Available
**Risk:** Some Wayland compositors may not support XDG desktop portal

**Mitigation:**
- Fallback to pynput (works on most Wayland compositors)
- Document which compositors support portal
- Provide clear error messages

### Risk 2: wl-clipboard Not Installed
**Risk:** Users may not have wl-clipboard installed

**Mitigation:**
- Check for wl-clipboard at startup
- Show installation instructions if missing
- Fallback to pynput keyboard simulation
- Document in setup guide

### Risk 3: Permission Dialog Confusion
**Risk:** Users may deny permission or not understand dialog

**Mitigation:**
- Show clear console message when dialog appears
- Document permission requirements
- Provide troubleshooting for denied permissions
- Allow re-requesting permission

### Risk 4: Compositor-Specific Issues
**Risk:** Different Wayland compositors may behave differently

**Mitigation:**
- Test on major compositors (GNOME, KDE, Sway)
- Document known issues per compositor
- Provide compositor-specific workarounds
- Community testing and feedback

### Risk 5: Performance Overhead
**Risk:** Subprocess calls (wl-copy, wtype) may be slower than direct APIs

**Mitigation:**
- Measure performance impact
- Optimize subprocess calls (reuse, caching)
- Consider direct protocol implementation if needed
- Document performance characteristics

## Migration Plan

### Phase 1: Implementation
1. Implement display server detection
2. Implement Wayland hotkey backend
3. Implement Wayland paste backend
4. Add backend selection logic
5. Add configuration options

### Phase 2: Testing
1. Test on GNOME (Wayland)
2. Test on KDE Plasma (Wayland)
3. Test on Sway
4. Verify X11 fallback still works
5. Test permission dialogs
6. Performance testing

### Phase 3: Documentation
1. Update Linux platform guide
2. Add Wayland setup instructions
3. Document permission requirements
4. Add compositor-specific notes
5. Update troubleshooting guide

### Phase 4: Rollout
1. Release as beta feature (opt-in)
2. Collect user feedback
3. Fix reported issues
4. Enable by default
5. Announce Wayland support

### Rollback Strategy
- Wayland support is additive (doesn't break X11)
- Can disable with `DISPLAY_SERVER=x11` env var
- X11 backend remains unchanged
- No breaking changes to existing functionality

## Open Questions

1. **Should we require PyGObject for XDG portal?**
   - Pro: Better integration, more reliable
   - Con: Heavy dependency, installation complexity
   - Decision: Make it optional, fallback to pynput

2. **Which keyboard simulator for Wayland?**
   - Options: wtype, ydotool, pynput
   - wtype: Simple, no root required
   - ydotool: More features, may need setup
   - pynput: Already used, works everywhere
   - Decision: Prefer wtype, fallback to pynput

3. **Should we support Wayland-specific features?**
   - Examples: Layer shell, custom protocols
   - Decision: No, keep it simple, focus on core functionality

4. **How to handle mixed X11/Wayland environments?**
   - Some apps run under XWayland even on Wayland session
   - Decision: Detect per-session, not per-app

5. **Should we cache display server detection?**
   - Pro: Faster, fewer checks
   - Con: Won't detect session changes
   - Decision: Detect once at startup, allow manual override

---

**Implementation Priority:**
1. Display server detection (foundation)
2. Wayland paste backend (most impactful)
3. Wayland hotkey backend (requires portal)
4. Testing and documentation
5. Performance optimization
