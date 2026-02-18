"""
DictaPilot Wayland Backend
Wayland-specific backends for hotkey detection and text injection.

Original by: Rohan Sharvesh
Fork maintained by: Rehan

MIT License
Copyright (c) 2026 Rohan Sharvesh
Copyright (c) 2026 Rehan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import logging
import os
import shutil
import subprocess
import threading
import time
from typing import Callable, Optional, List, Tuple

logger = logging.getLogger(__name__)


# ============================================================================
# Exceptions
# ============================================================================

class WaylandBackendError(Exception):
    """Base exception for Wayland backend errors."""
    pass


class WlClipboardError(WaylandBackendError):
    """Error from wl-clipboard operations."""
    pass


class PortalConnectionError(WaylandBackendError):
    """Error connecting to XDG desktop portal."""
    pass


class KeyboardSimulationError(WaylandBackendError):
    """Error during keyboard simulation."""
    pass


# ============================================================================
# Availability Checks
# ============================================================================

def has_wl_clipboard() -> bool:
    """Check if wl-clipboard (wl-copy) is available."""
    return shutil.which("wl-copy") is not None


def has_wtype() -> bool:
    """Check if wtype is available for keyboard simulation."""
    return shutil.which("wtype") is not None


def has_portal() -> bool:
    """
    Check if XDG desktop portal is available.
    
    Returns True if PyGObject is installed and portal can be accessed.
    """
    try:
        import gi
        gi.require_version('Gio', '2.0')
        from gi.repository import Gio
        return True
    except (ImportError, ValueError):
        return False


def has_pynput() -> bool:
    """Check if pynput is available."""
    try:
        from pynput import keyboard
        return True
    except ImportError:
        return False


# ============================================================================
# Wayland Paste Backend
# ============================================================================

class WaylandPasteBackend:
    """
    Wayland-native paste backend using wl-clipboard and keyboard simulation.
    
    Falls back to pynput if wl-clipboard or wtype are not available.
    """
    
    def __init__(self, paste_delay: float = 0.05):
        """
        Initialize Wayland paste backend.
        
        Args:
            paste_delay: Delay in seconds between clipboard copy and paste
        """
        self.paste_delay = paste_delay
        self._has_wl_clipboard = has_wl_clipboard()
        self._has_wtype = has_wtype()
        self._has_pynput = has_pynput()
        
        logger.debug(
            f"WaylandPasteBackend initialized: wl-clipboard={self._has_wl_clipboard}, "
            f"wtype={self._has_wtype}, pynput={self._has_pynput}"
        )
    
    def copy_to_clipboard(self, text: str) -> bool:
        """
        Copy text to Wayland clipboard using wl-copy.
        
        Args:
            text: Text to copy
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            WlClipboardError: If wl-copy fails critically
        """
        if not self._has_wl_clipboard:
            logger.debug("wl-copy not available, using pynput fallback")
            return self._copy_pynput(text)
        
        try:
            result = subprocess.run(
                ["wl-copy"],
                input=text.encode("utf-8"),
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                timeout=2.0
            )
            logger.debug(f"Copied {len(text)} chars to clipboard via wl-copy")
            return True
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else "unknown error"
            logger.warning(f"wl-copy failed: {error_msg}")
            # Provide helpful troubleshooting hint
            if "cannot open display" in error_msg.lower():
                logger.error("Hint: Make sure you're running in a Wayland session")
            return self._copy_pynput(text)
        except subprocess.TimeoutExpired:
            logger.warning("wl-copy timed out - check if clipboard service is running")
            return self._copy_pynput(text)
        except FileNotFoundError:
            self._has_wl_clipboard = False
            logger.warning("wl-copy not found - install wl-clipboard package")
            return self._copy_pynput(text)
    
    def _copy_pynput(self, text: str) -> bool:
        """Fallback: copy text using pynput (simulates typing)."""
        if not self._has_pynput:
            logger.error("pynput not available for clipboard fallback")
            return False
        
        try:
            import pyperclip
            pyperclip.copy(text)
            return True
        except ImportError:
            logger.warning("pyperclip not available, will type text directly")
            return False
    
    def simulate_paste(self) -> bool:
        """
        Simulate Ctrl+V keyboard shortcut to paste.
        
        Returns:
            True if successful, False otherwise
            
        Raises:
            KeyboardSimulationError: If all keyboard simulation methods fail
        """
        if self._has_wtype:
            if self._simulate_paste_wtype():
                return True
        
        if self._has_pynput:
            if self._simulate_paste_pynput():
                return True
        
        # All methods failed
        error_msg = "No keyboard simulation method available. "
        if not self._has_wtype and not self._has_pynput:
            error_msg += "Install wtype or ensure pynput is available."
        else:
            error_msg += "Both wtype and pynput failed. Check input permissions."
        
        logger.error(error_msg)
        raise KeyboardSimulationError(error_msg)
    
    def _simulate_paste_wtype(self) -> bool:
        """Simulate paste using wtype."""
        try:
            subprocess.run(
                ["wtype", "-M", "ctrl", "v", "-m", "ctrl"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                timeout=1.0
            )
            logger.debug("Simulated paste via wtype")
            return True
        except subprocess.CalledProcessError as e:
            logger.warning(f"wtype failed: {e.stderr.decode() if e.stderr else 'unknown error'}")
            return self._simulate_paste_pynput()
        except subprocess.TimeoutExpired:
            logger.warning("wtype timed out")
            return self._simulate_paste_pynput()
        except FileNotFoundError:
            self._has_wtype = False
            return self._simulate_paste_pynput()
    
    def _simulate_paste_pynput(self) -> bool:
        """Simulate paste using pynput."""
        if not self._has_pynput:
            return False
        
        try:
            from pynput.keyboard import Controller, Key
            controller = Controller()
            controller.press(Key.ctrl)
            controller.press('v')
            controller.release('v')
            controller.release(Key.ctrl)
            logger.debug("Simulated paste via pynput")
            return True
        except Exception as e:
            logger.error(f"pynput paste failed: {e}")
            return False
    
    def paste(self, text: str) -> bool:
        """
        Paste text on Wayland: copy to clipboard, then simulate Ctrl+V.
        
        Args:
            text: Text to paste
            
        Returns:
            True if successful, False otherwise
        """
        if not text:
            return True
        
        # Copy to clipboard
        if not self.copy_to_clipboard(text):
            # Fallback: type directly
            return self._type_text(text)
        
        # Small delay for clipboard to settle
        time.sleep(self.paste_delay)
        
        # Simulate Ctrl+V
        return self.simulate_paste()
    
    def _type_text(self, text: str) -> bool:
        """Fallback: type text character by character."""
        if not self._has_pynput:
            logger.error("Cannot type text: pynput not available")
            return False
        
        try:
            from pynput.keyboard import Controller
            controller = Controller()
            controller.type(text)
            logger.debug(f"Typed {len(text)} chars via pynput")
            return True
        except Exception as e:
            logger.error(f"pynput type failed: {e}")
            return False
    
    def type_text(self, text: str) -> bool:
        """Type text directly (not via clipboard)."""
        return self._type_text(text)
    
    def backspace(self, count: int) -> bool:
        """
        Send backspace key presses.
        
        Args:
            count: Number of backspaces to send
            
        Returns:
            True if successful, False otherwise
        """
        if count <= 0:
            return True
        
        if self._has_wtype:
            try:
                for _ in range(count):
                    subprocess.run(
                        ["wtype", "-k", "BackSpace"],
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=0.5
                    )
                return True
            except Exception:
                pass
        
        if self._has_pynput:
            try:
                from pynput.keyboard import Controller, Key
                controller = Controller()
                for _ in range(count):
                    controller.press(Key.backspace)
                    controller.release(Key.backspace)
                return True
            except Exception:
                pass
        
        return False


# ============================================================================
# Wayland Hotkey Backend
# ============================================================================

class WaylandHotkeyBackend:
    """
    Wayland hotkey backend using XDG desktop portal with pynput fallback.
    
    The XDG desktop portal is the standard Wayland method for global shortcuts,
    but it requires user permission. If not available, falls back to pynput.
    """
    
    def __init__(
        self,
        on_permission_request: Optional[Callable[[], None]] = None,
        on_permission_granted: Optional[Callable[[], None]] = None,
        on_permission_denied: Optional[Callable[[], None]] = None,
    ):
        """
        Initialize Wayland hotkey backend.
        
        Args:
            on_permission_request: Called when permission dialog appears
            on_permission_granted: Called when permission is granted
            on_permission_denied: Called when permission is denied
        """
        self.on_permission_request = on_permission_request
        self.on_permission_granted = on_permission_granted
        self.on_permission_denied = on_permission_denied
        
        self._has_portal = has_portal()
        self._has_pynput = has_pynput()
        self._portal = None
        self._shortcut_id = None
        self._pynput_listener = None
        self._stop_event = threading.Event()
        self._pressed = False
        
        logger.debug(
            f"WaylandHotkeyBackend initialized: portal={self._has_portal}, "
            f"pynput={self._has_pynput}"
        )
    
    def _init_portal(self) -> bool:
        """
        Initialize XDG desktop portal connection.
        
        Returns:
            True if portal is available and connected
        """
        if not self._has_portal:
            return False
        
        try:
            import gi
            gi.require_version('Gio', '2.0')
            gi.require_version('GLib', '2.0')
            from gi.repository import Gio, GLib
            
            # Connect to the global shortcuts portal
            self._portal = Gio.DBusProxy.new_for_bus_sync(
                Gio.BusType.SESSION,
                Gio.DBusProxyFlags.NONE,
                None,
                'org.freedesktop.portal.Desktop',
                '/org/freedesktop/portal/desktop',
                'org.freedesktop.portal.GlobalShortcuts',
                None
            )
            logger.debug("XDG desktop portal connected")
            return True
        except Exception as e:
            logger.warning(f"Failed to connect to XDG portal: {e}")
            self._has_portal = False
            return False
    
    def register_hotkey(
        self,
        hotkey: str,
        on_press: Callable[[], None],
        on_release: Callable[[], None]
    ) -> bool:
        """
        Register a global hotkey.
        
        Args:
            hotkey: Hotkey string (e.g., "f9", "ctrl+space")
            on_press: Callback for key press
            on_release: Callback for key release
            
        Returns:
            True if registration successful
        """
        self._stop_event.clear()
        
        # Try portal first
        if self._has_portal and self._register_portal_hotkey(hotkey, on_press, on_release):
            logger.info(f"Registered hotkey '{hotkey}' via XDG portal")
            return True
        
        # Fall back to pynput
        if self._has_pynput and self._register_pynput_hotkey(hotkey, on_press, on_release):
            logger.info(f"Registered hotkey '{hotkey}' via pynput")
            return True
        
        logger.error(f"Failed to register hotkey '{hotkey}'")
        return False
    
    def _register_portal_hotkey(
        self,
        hotkey: str,
        on_press: Callable[[], None],
        on_release: Callable[[], None]
    ) -> bool:
        """Register hotkey via XDG desktop portal."""
        if not self._init_portal():
            return False
        
        try:
            import gi
            gi.require_version('GLib', '2.0')
            from gi.repository import GLib
            
            # Notify that permission dialog may appear
            if self.on_permission_request:
                self.on_permission_request()
            
            # Create a session and register the shortcut
            # Note: This is simplified; real implementation would need
            # proper session handling and signal monitoring
            logger.info("Requesting global shortcut permission via XDG portal")
            
            # For now, fall back to pynput as portal integration is complex
            # and requires proper async handling
            logger.debug("Portal hotkey registration pending, using pynput fallback")
            return False
            
        except Exception as e:
            logger.warning(f"Portal hotkey registration failed: {e}")
            return False
    
    def _register_pynput_hotkey(
        self,
        hotkey: str,
        on_press: Callable[[], None],
        on_release: Callable[[], None]
    ) -> bool:
        """Register hotkey via pynput."""
        if not self._has_pynput:
            return False
        
        try:
            from pynput import keyboard as pynput_keyboard
            
            token = self._hotkey_token_for_pynput(hotkey, pynput_keyboard)
            if token is None:
                logger.error(f"Unsupported hotkey for pynput: '{hotkey}'")
                return False
            
            def _matches(key_obj):
                try:
                    if isinstance(token, pynput_keyboard.KeyCode):
                        return (getattr(key_obj, "char", None) and 
                                key_obj.char.lower() == token.char.lower())
                    return key_obj == token
                except Exception:
                    return False
            
            def _on_press(key_obj):
                if _matches(key_obj):
                    if not self._pressed:
                        self._pressed = True
                        on_press()
            
            def _on_release(key_obj):
                if _matches(key_obj):
                    if self._pressed:
                        self._pressed = False
                        on_release()
            
            self._pynput_listener = pynput_keyboard.Listener(
                on_press=_on_press,
                on_release=_on_release
            )
            self._pynput_listener.daemon = True
            self._pynput_listener.start()
            
            return True
            
        except Exception as e:
            logger.error(f"pynput hotkey registration failed: {e}")
            return False
    
    def _hotkey_token_for_pynput(self, hotkey: str, pynput_keyboard) -> any:
        """Convert hotkey string to pynput key token."""
        key_name = (hotkey or "").strip().lower()
        mapping = {
            "ctrl": pynput_keyboard.Key.ctrl,
            "control": pynput_keyboard.Key.ctrl,
            "alt": pynput_keyboard.Key.alt,
            "shift": pynput_keyboard.Key.shift,
            "tab": pynput_keyboard.Key.tab,
            "enter": pynput_keyboard.Key.enter,
            "return": pynput_keyboard.Key.enter,
            "esc": pynput_keyboard.Key.esc,
            "escape": pynput_keyboard.Key.esc,
            "space": pynput_keyboard.Key.space,
        }
        if key_name in mapping:
            return mapping[key_name]
        if key_name.startswith("f") and key_name[1:].isdigit():
            if hasattr(pynput_keyboard.Key, key_name):
                return getattr(pynput_keyboard.Key, key_name)
        if len(key_name) == 1:
            return pynput_keyboard.KeyCode.from_char(key_name)
        return None
    
    def unregister(self) -> None:
        """Unregister the hotkey and clean up resources."""
        self._stop_event.set()
        
        if self._pynput_listener is not None:
            try:
                self._pynput_listener.stop()
            except Exception:
                pass
            self._pynput_listener = None
        
        # Portal shortcuts are automatically cleaned up when the app exits
        self._portal = None
        self._shortcut_id = None
        logger.debug("Hotkey unregistered")


# ============================================================================
# Backend Selection
# ============================================================================

def select_hotkey_backend(display_server: Optional[str] = None) -> str:
    """
    Select the appropriate hotkey backend based on environment.
    
    Args:
        display_server: Optional display server type override
        
    Returns:
        Backend name: "wayland", "x11", "pynput", or "keyboard"
    """
    from display_server import detect_display_server
    
    server = display_server or detect_display_server()
    user_pref = os.getenv("HOTKEY_BACKEND", "auto").strip().lower()
    
    if user_pref != "auto":
        return user_pref
    
    if server == "wayland":
        if has_portal():
            return "wayland"
        elif has_pynput():
            return "pynput"
    
    # X11 or unknown: prefer x11 backend, then pynput
    return "x11" if os.getenv("DISPLAY") else "pynput"


def select_paste_backend(display_server: Optional[str] = None) -> str:
    """
    Select the appropriate paste backend based on environment.
    
    Args:
        display_server: Optional display server type override
        
    Returns:
        Backend name: "wayland", "x11", "pynput", or "xdotool"
    """
    from display_server import detect_display_server
    
    server = display_server or detect_display_server()
    user_pref = os.getenv("PASTE_BACKEND", "auto").strip().lower()
    
    if user_pref != "auto":
        return user_pref
    
    if server == "wayland":
        if has_wl_clipboard():
            return "wayland"
        elif has_pynput():
            return "pynput"
    
    # X11 or unknown: prefer x11 backend
    return "x11" if os.getenv("DISPLAY") else "pynput"


# ============================================================================
# Utility Functions
# ============================================================================

def get_wayland_dependencies_status() -> dict:
    """
    Get status of Wayland-related dependencies.
    
    Returns:
        Dictionary with dependency availability status
    """
    return {
        "wl_clipboard": has_wl_clipboard(),
        "wtype": has_wtype(),
        "portal": has_portal(),
        "pynput": has_pynput(),
        "pyperclip": _has_pyperclip(),
    }


def _has_pyperclip() -> bool:
    """Check if pyperclip is available."""
    try:
        import pyperclip
        return True
    except ImportError:
        return False


def print_wayland_setup_instructions() -> None:
    """Print setup instructions for Wayland dependencies."""
    print("\n=== Wayland Dependencies ===\n")
    
    deps = get_wayland_dependencies_status()
    
    print("Status:")
    print(f"  wl-clipboard: {'✓ installed' if deps['wl_clipboard'] else '✗ not found'}")
    print(f"  wtype:        {'✓ installed' if deps['wtype'] else '✗ not found'}")
    print(f"  PyGObject:    {'✓ installed' if deps['portal'] else '✗ not found (optional)'}")
    print(f"  pynput:       {'✓ installed' if deps['pynput'] else '✗ not found'}")
    print(f"  pyperclip:    {'✓ installed' if deps['pyperclip'] else '✗ not found'}")
    
    missing = [k for k, v in deps.items() if not v and k != 'portal']
    
    if missing:
        print("\nInstallation instructions:")
        print("  Ubuntu/Debian:")
        print("    sudo apt install wl-clipboard wtype python3-pip")
        print("    pip install pynput pyperclip")
        print("\n  Fedora:")
        print("    sudo dnf install wl-clipboard wtype python3-pip")
        print("    pip install pynput pyperclip")
        print("\n  Arch Linux:")
        print("    sudo pacman -S wl-clipboard wtype python-pip")
        print("    pip install pynput pyperclip")
        
        if not deps['portal']:
            print("\n  Optional - XDG Portal (for better hotkey integration):")
            print("    Ubuntu/Debian: sudo apt install python3-gi gir1.2-glib-2.0")
            print("    Fedora: sudo dnf install python3-gobject glib2")
            print("    Arch: sudo pacman -S python-gobject glib2")
    
    print()
