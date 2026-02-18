"""
DictaPilot Display Server Detection
Detects whether running on X11 or Wayland display server.

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

import os
import logging
from typing import Literal, Optional

logger = logging.getLogger(__name__)

# Cache for display server detection result
_cached_display_server: Optional[str] = None

DisplayServerType = Literal["wayland", "x11", "unknown"]


def detect_display_server() -> DisplayServerType:
    """
    Detect whether running on X11 or Wayland display server.
    
    Detection order:
    1. Check DISPLAY_SERVER env var for manual override
    2. Check XDG_SESSION_TYPE env var (primary method)
    3. Check WAYLAND_DISPLAY env var (fallback)
    4. Check DISPLAY env var (fallback)
    
    Returns:
        "wayland", "x11", or "unknown"
    """
    global _cached_display_server
    
    # Return cached result if available
    if _cached_display_server is not None:
        return _cached_display_server
    
    # 1. Check for manual override
    manual_override = os.getenv("DISPLAY_SERVER", "").strip().lower()
    if manual_override in ("wayland", "x11"):
        logger.info(f"Display server manually set to: {manual_override}")
        _cached_display_server = manual_override
        return manual_override
    
    # 2. Primary detection: XDG_SESSION_TYPE
    session_type = os.getenv("XDG_SESSION_TYPE", "").strip().lower()
    if session_type == "wayland":
        logger.debug("Detected Wayland via XDG_SESSION_TYPE")
        _cached_display_server = "wayland"
        return "wayland"
    elif session_type == "x11":
        logger.debug("Detected X11 via XDG_SESSION_TYPE")
        _cached_display_server = "x11"
        return "x11"
    
    # 3. Fallback: Check WAYLAND_DISPLAY
    if os.getenv("WAYLAND_DISPLAY"):
        logger.debug("Detected Wayland via WAYLAND_DISPLAY")
        _cached_display_server = "wayland"
        return "wayland"
    
    # 4. Fallback: Check DISPLAY
    if os.getenv("DISPLAY"):
        logger.debug("Detected X11 via DISPLAY")
        _cached_display_server = "x11"
        return "x11"
    
    # Unknown display server
    logger.warning("Could not detect display server type")
    _cached_display_server = "unknown"
    return "unknown"


def is_wayland() -> bool:
    """
    Check if running on Wayland display server.
    
    Returns:
        True if on Wayland, False otherwise
    """
    return detect_display_server() == "wayland"


def is_x11() -> bool:
    """
    Check if running on X11 display server.
    
    Returns:
        True if on X11, False otherwise
    """
    return detect_display_server() == "x11"


def clear_detection_cache() -> None:
    """
    Clear the cached display server detection result.
    
    Useful for testing or when the environment changes.
    """
    global _cached_display_server
    _cached_display_server = None


def get_display_server_info() -> dict:
    """
    Get detailed information about the display server environment.
    
    Returns:
        Dictionary with detection details
    """
    return {
        "detected": detect_display_server(),
        "XDG_SESSION_TYPE": os.getenv("XDG_SESSION_TYPE", ""),
        "WAYLAND_DISPLAY": os.getenv("WAYLAND_DISPLAY", ""),
        "DISPLAY": os.getenv("DISPLAY", ""),
        "DISPLAY_SERVER_OVERRIDE": os.getenv("DISPLAY_SERVER", ""),
    }
