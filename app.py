"""
DictaPilot - Cross-platform press-and-hold dictation with smart editing.

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
import threading
import tempfile
import queue
import time
import sys
import signal
import platform
import traceback
from pathlib import Path
import numpy as np
import sounddevice as sd
import soundfile as sf
from dotenv import load_dotenv

# Check for first run before loading other modules
load_dotenv()
SETUP_COMPLETED = os.getenv("SETUP_COMPLETED", "0").strip() not in {
    "0",
    "false",
    "no",
    "off",
}


# Detect if running as PyInstaller frozen executable
def is_frozen():
    """Check if running as a frozen (packaged) executable."""
    return getattr(sys, "frozen", False)


def get_bundle_dir():
    """Get the directory where the bundled resources are located."""
    if is_frozen():
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


# Launch onboarding wizard if first run
if not SETUP_COMPLETED and "--no-wizard" not in sys.argv:
    try:
        from onboarding_wizard import run_wizard

        print("First run detected. Launching setup wizard...")
        if not run_wizard():
            print("Setup cancelled. Exiting.")
            sys.exit(0)
        # Reload environment after wizard
        load_dotenv(override=True)
    except ImportError:
        print("First run detected. Please set GROQ_API_KEY in .env file or environment.")
        print("Continuing with manual setup.")
    except Exception as e:
        print(f"Warning: Could not launch wizard: {e}")
        print("Continuing with manual setup.")

from paste_utils import paste_text
from display_server import (
    detect_display_server,
    is_wayland,
    is_x11,
    get_display_server_info,
)
from smart_editor import (
    TranscriptState,
    smart_update_state,
    llm_refine,
    sync_state_to_output,
    is_transform_command,
    DICTATION_MODE,
    CLEANUP_LEVEL,
)
from transcription_store import add_transcription, get_storage_info, export_all_to_text
from audio_buffer import ChunkedAudioBuffer, AudioChunk

try:
    from PySide6.QtCore import QPoint, QRectF, Qt, QTimer
    from PySide6.QtGui import (
        QColor,
        QGuiApplication,
        QImage,
        QLinearGradient,
        QPainter,
        QPainterPath,
        QPixmap,
    )
    from PySide6.QtWidgets import QApplication, QWidget

    PYSIDE6_AVAILABLE = True
except Exception:
    QPoint = QRectF = Qt = QTimer = None
    QColor = QGuiApplication = QImage = QLinearGradient = QPainter = QPainterPath = (
        QPixmap
    ) = None
    QApplication = QWidget = None
    PYSIDE6_AVAILABLE = False

# load environment variables from .env (if present)
load_dotenv()

try:
    from groq import Groq
except Exception:
    Groq = None

_GROQ_CLIENT = None

API_KEY = os.getenv("GROQ_API_KEY")
HOTKEY = os.getenv("HOTKEY", "f9")  # default hotkey: F9 (press-and-hold)
GROQ_WHISPER_MODEL = (
    os.getenv("GROQ_WHISPER_MODEL", "whisper-large-v3-turbo").strip()
    or "whisper-large-v3-turbo"
)
GROQ_CHAT_MODEL = (
    os.getenv("GROQ_CHAT_MODEL", "openai/gpt-oss-120b").strip() or "openai/gpt-oss-120b"
)


def _env_flag(name: str, default: str = "1") -> bool:
    value = os.getenv(name, default).strip().lower()
    return value not in {"0", "false", "no", "off"}


SMART_EDIT = _env_flag("SMART_EDIT", "1")
SMART_MODE = os.getenv("SMART_MODE", "llm").strip().lower()
PASTE_MODE = os.getenv("PASTE_MODE", "full").strip().lower()
PASTE_POLICY = os.getenv("PASTE_POLICY", "final_only").strip().lower()
PASTE_BACKEND = os.getenv("PASTE_BACKEND", "auto").strip().lower()
HOTKEY_BACKEND = os.getenv("HOTKEY_BACKEND", "auto").strip().lower()
RESET_TRANSCRIPT_EACH_RECORDING = _env_flag("RESET_TRANSCRIPT_EACH_RECORDING", "1")
LLM_ALWAYS_CLEAN = _env_flag("LLM_ALWAYS_CLEAN", "1")
INSTANT_REFINE = _env_flag("INSTANT_REFINE", "1")
if SMART_MODE not in {"heuristic", "llm"}:
    SMART_MODE = "llm"
if PASTE_MODE not in {"delta", "full"}:
    PASTE_MODE = "delta"
if PASTE_BACKEND not in {"auto", "keyboard", "pynput", "xdotool", "x11", "osascript"}:
    PASTE_BACKEND = "auto"
if HOTKEY_BACKEND not in {"auto", "keyboard", "pynput", "x11"}:
    HOTKEY_BACKEND = "auto"


# audio defaults
def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)).strip())
    except Exception:
        return default


def _env_float(
    name: str,
    default: float,
    minimum: float | None = None,
    maximum: float | None = None,
) -> float:
    try:
        value = float(os.getenv(name, str(default)).strip())
    except Exception:
        value = float(default)
    if minimum is not None:
        value = max(float(minimum), value)
    if maximum is not None:
        value = min(float(maximum), value)
    return value


SR = _env_int("SAMPLE_RATE", 16000)
CHANNELS = _env_int("CHANNELS", 1)
TRIM_SILENCE = _env_flag("TRIM_SILENCE", "1")
SILENCE_THRESHOLD = float(os.getenv("SILENCE_THRESHOLD", "0.02"))

FLOATING_THEME = os.getenv("FLOATING_THEME", "professional_minimal").strip().lower()
FLOATING_MOTION_PROFILE = (
    os.getenv("FLOATING_MOTION_PROFILE", "expressive").strip().lower()
)
FLOATING_GLOW_INTENSITY = _env_float("FLOATING_GLOW_INTENSITY", 1.0, 0.0, 1.6)
FLOATING_BAR_RADIUS = _env_float("FLOATING_BAR_RADIUS", 1.0, 0.5, 1.5)
FLOATING_BORDER_ALPHA = int(_env_float("FLOATING_BORDER_ALPHA", 72.0, 8.0, 255.0))
FLOATING_WAVE_DEBUG = _env_flag("FLOATING_WAVE_DEBUG", "0")

# Modern UI/UX settings (2026 redesign)
FLOATING_UI_STYLE = os.getenv("FLOATING_UI_STYLE", "modern").strip().lower()
FLOATING_ACCENT_COLOR = os.getenv("FLOATING_ACCENT_COLOR", "blue").strip().lower()
FLOATING_GLASSMORPHISM = _env_flag("FLOATING_GLASSMORPHISM", "1")
FLOATING_ANIMATIONS = _env_flag("FLOATING_ANIMATIONS", "1")
FLOATING_REDUCED_MOTION = _env_flag("FLOATING_REDUCED_MOTION", "0")
FLOATING_LAYOUT = os.getenv("FLOATING_LAYOUT", "pill").strip().lower()

# Enhanced waveform visualization settings (2026 redesign)
FLOATING_WAVEFORM_BARS = _env_int(
    "FLOATING_WAVEFORM_BARS", 11
)  # 11 bars for richer visualization
FLOATING_WAVEFORM_SMOOTHING = (
    os.getenv("FLOATING_WAVEFORM_SMOOTHING", "responsive").strip().lower()
)
FLOATING_WAVEFORM_GLOW = _env_flag("FLOATING_WAVEFORM_GLOW", "1")
FLOATING_STATE_ANIMATION_MS = _env_int("FLOATING_STATE_ANIMATION_MS", 250)

# State-specific accent colors for enhanced visual feedback
# "listening" (record) uses cyan/blue, "speaking" (processing) uses purple/magenta
FLOATING_RECORDING_COLOR = os.getenv("FLOATING_RECORDING_COLOR", "cyan").strip().lower()
FLOATING_PROCESSING_COLOR = (
    os.getenv("FLOATING_PROCESSING_COLOR", "purple").strip().lower()
)

# Wispr Flow UI integration: Apply Wispr Flow defaults when UI_STYLE=wispr_flow
_UI_STYLE = os.getenv("UI_STYLE", "classic").strip().lower()
if _UI_STYLE == "wispr_flow":
    # Apply Wispr Flow default colors and settings
    if "FLOATING_UI_STYLE" not in os.environ:
        FLOATING_UI_STYLE = "modern"
    if "FLOATING_GLASSMORPHISM" not in os.environ:
        FLOATING_GLASSMORPHISM = True
    if "FLOATING_ANIMATIONS" not in os.environ:
        FLOATING_ANIMATIONS = True
    if "FLOATING_RECORDING_COLOR" not in os.environ:
        FLOATING_RECORDING_COLOR = "cyan"
    if "FLOATING_PROCESSING_COLOR" not in os.environ:
        FLOATING_PROCESSING_COLOR = "purple"
    if "FLOATING_LAYOUT" not in os.environ:
        FLOATING_LAYOUT = "pill"

_VISUAL_STATE_BY_MODE = {
    "record": "record",
    "recording": "record",
    "processing": "processing",
    "transcribing": "processing",
    "done": "done",
    "complete": "done",
    "idle": "idle",
}

# Accent color palettes for modern UI
_ACCENT_COLOR_PALETTES = {
    "blue": {
        "primary": "#3B82F6",
        "light": "#60A5FA",
        "dark": "#2563EB",
        "glow": (59, 130, 246, 102),
    },
    "cyan": {
        "primary": "#06B6D4",
        "light": "#22D3EE",
        "dark": "#0891B2",
        "glow": (6, 182, 212, 102),
    },
    "purple": {
        "primary": "#8B5CF6",
        "light": "#A78BFA",
        "dark": "#7C3AED",
        "glow": (139, 92, 246, 102),
    },
    "magenta": {
        "primary": "#D946EF",
        "light": "#E879F9",
        "dark": "#C026D3",
        "glow": (217, 70, 239, 102),
    },
    "green": {
        "primary": "#10B981",
        "light": "#34D399",
        "dark": "#059669",
        "glow": (16, 185, 129, 102),
    },
}

if FLOATING_ACCENT_COLOR not in _ACCENT_COLOR_PALETTES:
    FLOATING_ACCENT_COLOR = "blue"
if FLOATING_UI_STYLE not in {"modern", "classic"}:
    FLOATING_UI_STYLE = "modern"
if FLOATING_LAYOUT not in {"circular", "pill", "card"}:
    FLOATING_LAYOUT = "pill"

_FLOATING_THEME_PRESETS = {
    "professional_minimal": {
        "shell_outer": "#0b1324",
        "shell_inner": "#111d35",
        "shell_border": "#94a3b8",
        "shell_highlight": "#f8fafc",
        "close_idle": "#dc2626",
        "close_hover": "#ef4444",
        "close_pressed": "#991b1b",
        "close_halo": (255, 255, 255, 26),
        "close_halo_active": (255, 255, 255, 52),
        "states": {
            "record": {
                "top": "#bbf7d0",
                "mid": "#22c55e",
                "bottom": "#15803d",
                "glow": (34, 197, 94, 104),
            },
            "processing": {
                "top": "#fde68a",
                "mid": "#f59e0b",
                "bottom": "#b45309",
                "glow": (245, 158, 11, 88),
            },
            "done": {
                "top": "#86efac",
                "mid": "#22c55e",
                "bottom": "#166534",
                "glow": (34, 197, 94, 84),
            },
            "idle": {
                "top": "#cbd5e1",
                "mid": "#94a3b8",
                "bottom": "#475569",
                "glow": (148, 163, 184, 62),
            },
        },
    },
    "high_contrast": {
        "shell_outer": "#090f1f",
        "shell_inner": "#0b1428",
        "shell_border": "#e2e8f0",
        "shell_highlight": "#ffffff",
        "close_idle": "#ef4444",
        "close_hover": "#f87171",
        "close_pressed": "#b91c1c",
        "close_halo": (255, 255, 255, 32),
        "close_halo_active": (255, 255, 255, 64),
        "states": {
            "record": {
                "top": "#dcfce7",
                "mid": "#22c55e",
                "bottom": "#166534",
                "glow": (34, 197, 94, 112),
            },
            "processing": {
                "top": "#fef08a",
                "mid": "#facc15",
                "bottom": "#ca8a04",
                "glow": (250, 204, 21, 96),
            },
            "done": {
                "top": "#bbf7d0",
                "mid": "#22c55e",
                "bottom": "#15803d",
                "glow": (34, 197, 94, 90),
            },
            "idle": {
                "top": "#e2e8f0",
                "mid": "#cbd5e1",
                "bottom": "#64748b",
                "glow": (203, 213, 225, 68),
            },
        },
    },
}

_MOTION_PROFILE_PRESETS = {
    "expressive": {
        "rise": 0.82,
        "decay": 0.20,
        "env_keep": 0.68,
        "env_new": 0.32,
        "center_drop": 0.30,
        "record_local_mix": 0.72,
        "record_local_gamma": 0.44,
        "record_base": 0.92,
        "record_wave": 0.18,
        "record_freq": 11.1,
        "record_phase": 0.68,
        "record_floor": 0.08,
        "processing_floor": 0.21,
        "processing_wave": 0.11,
        "processing_freq": 4.5,
        "processing_phase": 0.42,
        "done_floor": 0.16,
        "done_wave": 0.08,
        "done_freq": 3.2,
        "done_phase": 0.40,
        "idle_floor": 0.06,
        "idle_wave": 0.028,
        "idle_freq": 2.1,
        "idle_phase": 0.48,
    },
    "balanced": {
        "rise": 0.74,
        "decay": 0.19,
        "env_keep": 0.72,
        "env_new": 0.28,
        "center_drop": 0.32,
        "record_local_mix": 0.68,
        "record_local_gamma": 0.48,
        "record_base": 0.90,
        "record_wave": 0.15,
        "record_freq": 9.5,
        "record_phase": 0.60,
        "record_floor": 0.08,
        "processing_floor": 0.20,
        "processing_wave": 0.095,
        "processing_freq": 4.0,
        "processing_phase": 0.40,
        "done_floor": 0.155,
        "done_wave": 0.065,
        "done_freq": 2.9,
        "done_phase": 0.38,
        "idle_floor": 0.06,
        "idle_wave": 0.022,
        "idle_freq": 1.8,
        "idle_phase": 0.46,
    },
    "reduced": {
        "rise": 0.60,
        "decay": 0.15,
        "env_keep": 0.79,
        "env_new": 0.21,
        "center_drop": 0.36,
        "record_local_mix": 0.60,
        "record_local_gamma": 0.58,
        "record_base": 0.88,
        "record_wave": 0.10,
        "record_freq": 7.2,
        "record_phase": 0.56,
        "record_floor": 0.07,
        "processing_floor": 0.18,
        "processing_wave": 0.065,
        "processing_freq": 3.1,
        "processing_phase": 0.38,
        "done_floor": 0.14,
        "done_wave": 0.045,
        "done_freq": 2.4,
        "done_phase": 0.34,
        "idle_floor": 0.055,
        "idle_wave": 0.012,
        "idle_freq": 1.35,
        "idle_phase": 0.44,
    },
}

if FLOATING_THEME not in _FLOATING_THEME_PRESETS:
    FLOATING_THEME = "professional_minimal"
if FLOATING_MOTION_PROFILE not in _MOTION_PROFILE_PRESETS:
    FLOATING_MOTION_PROFILE = "expressive"


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _resolve_visual_state(mode: str) -> str:
    return _VISUAL_STATE_BY_MODE.get((mode or "").strip().lower(), "idle")


def _resolve_theme(theme_name: str) -> dict:
    return _FLOATING_THEME_PRESETS.get(
        theme_name, _FLOATING_THEME_PRESETS["professional_minimal"]
    )


def _resolve_motion_profile(profile_name: str) -> dict:
    return _MOTION_PROFILE_PRESETS.get(
        profile_name, _MOTION_PROFILE_PRESETS["expressive"]
    )


def _resolve_accent_color(color_name: str) -> dict:
    return _ACCENT_COLOR_PALETTES.get(color_name, _ACCENT_COLOR_PALETTES["blue"])


def _compute_bar_target(
    mode: str,
    bar_idx: int,
    bar_count: int,
    amplitudes: list[float],
    level_peak: float,
    expressive_level: float,
    now: float,
    motion: dict,
) -> float:
    half = max(1.0, (bar_count - 1) / 2.0)
    center_bias = 1.16 - (abs(bar_idx - half) / half) * motion["center_drop"]
    visual_state = _resolve_visual_state(mode)

    if visual_state == "record":
        amp_idx = min(bar_idx, len(amplitudes) - 1)
        local = min(1.0, amplitudes[amp_idx] / max(0.10, level_peak))
        local_drive = local ** motion["record_local_gamma"]
        rhythm = motion["record_base"] + motion["record_wave"] * np.sin(
            now * motion["record_freq"] + bar_idx * motion["record_phase"]
        )
        drive = (motion["record_local_mix"] * local_drive) + (
            (1.0 - motion["record_local_mix"]) * expressive_level
        )
        target = motion["record_floor"] + (drive * center_bias * rhythm)
    elif visual_state == "processing":
        target = (
            motion["processing_floor"]
            + (
                np.sin(
                    now * motion["processing_freq"]
                    + bar_idx * motion["processing_phase"]
                )
                + 1.0
            )
            * motion["processing_wave"]
        )
    elif visual_state == "done":
        target = (
            motion["done_floor"]
            + (np.sin(now * motion["done_freq"] + bar_idx * motion["done_phase"]) + 1.0)
            * motion["done_wave"]
        )
    else:
        target = (
            motion["idle_floor"]
            + (np.sin(now * motion["idle_freq"] + bar_idx * motion["idle_phase"]) + 1.0)
            * motion["idle_wave"]
        )
    return _clamp(target, 0.0, 1.0)


def _build_waveform_points(
    current_heights: list[float],
    bar_count: int,
    mid_x: float,
    mid_y: float,
    icon_w: float,
    icon_h: float,
    now: float,
    is_recording: bool,
) -> list[tuple[float, float]]:
    if bar_count <= 0:
        return []

    heights = list(current_heights or [])
    if not heights:
        heights = [0.0] * max(1, bar_count)

    if len(heights) < bar_count:
        heights.extend([heights[-1]] * (bar_count - len(heights)))
    elif len(heights) > bar_count:
        heights = heights[:bar_count]

    sample_count = 33
    center_idx = (sample_count - 1) / 2.0
    span_w = icon_w * 0.92
    step_x = span_w / max(1, sample_count - 1)
    start_x = mid_x - (span_w / 2.0)
    min_y = mid_y - icon_h * 0.46
    max_y = mid_y + icon_h * 0.46
    energy_floor = 0.28 if is_recording else 0.22
    base_speed = 8.1 if is_recording else 6.7
    excursion = icon_h * (0.43 if is_recording else 0.39)
    points = []

    for i in range(sample_count):
        sample_pos = i * max(1, bar_count - 1) / max(1, sample_count - 1)
        left_idx = int(sample_pos)
        right_idx = min(bar_count - 1, left_idx + 1)
        blend = sample_pos - left_idx
        amp = (heights[left_idx] * (1.0 - blend)) + (heights[right_idx] * blend)

        edge = (np.cos(((i - center_idx) / center_idx) * np.pi) * 0.5 + 0.5) ** 0.64
        carrier = np.sin(now * base_speed + i * 0.62)
        texture = np.sin(now * 3.8 + i * 0.31) * 0.14
        drive = _clamp(max(amp, energy_floor), 0.0, 1.0)
        strength = _clamp(
            (0.30 + drive * 0.88) * edge + (0.16 if is_recording else 0.13), 0.30, 1.0
        )
        y = mid_y + (carrier + texture) * (excursion * strength)
        x = start_x + i * step_x
        points.append((x, _clamp(y, min_y, max_y)))

    return points


def _hotkey_token_for_pynput(hotkey: str, pynput_keyboard):
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
    if (
        key_name.startswith("f")
        and key_name[1:].isdigit()
        and hasattr(pynput_keyboard.Key, key_name)
    ):
        return getattr(pynput_keyboard.Key, key_name)
    if len(key_name) == 1:
        return pynput_keyboard.KeyCode.from_char(key_name)
    return None


class HotkeyManager:
    def __init__(self, hotkey: str, on_press, on_release, backend: str = "auto"):
        self.hotkey = (hotkey or "").strip()
        self.on_press = on_press
        self.on_release = on_release
        self.backend = (backend or "auto").strip().lower()
        self.active_backend = None
        self._stop = None
        self._pressed = False

    def _try_start_keyboard(self):
        import keyboard

        press_hook = keyboard.on_press_key(self.hotkey, lambda _: self._handle_press())
        release_hook = keyboard.on_release_key(
            self.hotkey, lambda _: self._handle_release()
        )

        def _stop():
            try:
                keyboard.unhook(press_hook)
            except Exception:
                pass
            try:
                keyboard.unhook(release_hook)
            except Exception:
                pass

        self._stop = _stop

    def _try_start_pynput(self):
        from pynput import keyboard as pynput_keyboard

        token = _hotkey_token_for_pynput(self.hotkey, pynput_keyboard)
        if token is None:
            raise ValueError(f"Unsupported hotkey for pynput backend: '{self.hotkey}'")

        def _matches(key_obj):
            try:
                if isinstance(token, pynput_keyboard.KeyCode):
                    return (
                        getattr(key_obj, "char", None)
                        and key_obj.char.lower() == token.char.lower()
                    )
                return key_obj == token
            except Exception:
                return False

        def _on_press(key_obj):
            if _matches(key_obj):
                self._handle_press()

        def _on_release(key_obj):
            if _matches(key_obj):
                self._handle_release()

        listener = pynput_keyboard.Listener(on_press=_on_press, on_release=_on_release)
        listener.daemon = True
        listener.start()

        def _stop():
            try:
                listener.stop()
            except Exception:
                pass

        self._stop = _stop

    def _try_start_x11(self):
        from x11_backend import X11HotkeyListener

        listener = X11HotkeyListener(
            hotkey=self.hotkey,
            on_press=lambda: self._handle_press(),
            on_release=lambda: self._handle_release(),
        )
        listener.start()

        def _stop():
            try:
                listener.stop()
            except Exception:
                pass

        self._stop = _stop

    def _try_start_wayland(self):
        """Start hotkey listener using Wayland backend (pynput fallback for now)."""
        from wayland_backend import WaylandHotkeyBackend, has_portal, has_pynput

        # For now, use pynput on Wayland as portal integration requires
        # more complex async handling
        if has_pynput():
            self._try_start_pynput()
            return

        if not has_portal() and not has_pynput():
            raise RuntimeError(
                "Neither PyGObject (portal) nor pynput available for Wayland hotkey backend"
            )

        # Fall back to pynput
        self._try_start_pynput()

    def _handle_press(self):
        if self._pressed:
            return
        self._pressed = True
        self.on_press(None)

    def _handle_release(self):
        if not self._pressed:
            return
        self._pressed = False
        self.on_release(None)

    def start(self):
        order = []
        if self.backend == "auto":
            # Detect display server and select appropriate backend
            display_server = detect_display_server()
            if display_server == "wayland":
                # On Wayland: prefer pynput (portal needs more work)
                order = ["pynput"]
            elif sys.platform.startswith("linux"):
                # Linux X11: prefer X11 native, then pynput
                order = ["x11", "pynput"]
            elif sys.platform == "darwin":
                order = ["pynput", "keyboard"]
            else:
                order = ["keyboard", "pynput"]
        else:
            order = [self.backend]

        errors = []
        for candidate in order:
            try:
                if candidate == "keyboard":
                    self._try_start_keyboard()
                elif candidate == "pynput":
                    self._try_start_pynput()
                elif candidate == "x11":
                    self._try_start_x11()
                elif candidate == "wayland":
                    self._try_start_wayland()
                else:
                    raise ValueError(f"Unsupported hotkey backend '{candidate}'")
                self.active_backend = candidate
                return candidate
            except Exception as ex:
                errors.append(f"{candidate}: {ex}")

        raise RuntimeError("Unable to start hotkey listener. " + " | ".join(errors))

    def stop(self):
        if self._stop is not None:
            self._stop()
            self._stop = None


class Recorder:
    def __init__(self, samplerate=SR, channels=CHANNELS):
        self.sr = samplerate
        self.channels = channels
        self._active_sr = samplerate
        self._frames = []
        self._rec_thread = None
        self._running = threading.Event()
        self.last_error = None
        self._started_event = threading.Event()
        self.amplitude_callback = None

    def _callback(self, indata, frames, time_info, status):
        if status:
            print("Recording status:", status, file=sys.stderr)
        # copy because indata is reused by sounddevice
        self._frames.append(indata.copy())

        if self.amplitude_callback:
            # Stronger, compressed level mapping so normal speech visibly animates bars.
            try:
                rms = float(np.sqrt(np.mean(indata**2)))
                peak = float(np.max(np.abs(indata)))
                raw_level = max(rms * 2.0, peak * 0.9)
                norm_level = float(np.log1p(raw_level * 120.0) / np.log1p(120.0))
                if norm_level < 0.02:
                    norm_level = 0.0
                self.amplitude_callback(max(0.0, min(1.0, norm_level)))
            except Exception:
                pass

    def start(self, amplitude_callback=None):
        self._frames = []
        self.last_error = None
        self._started_event.clear()
        self._running.set()
        self.amplitude_callback = amplitude_callback

        def _run():
            errors = []
            candidates = []
            for candidate in (self.sr, 16000, 44100, 48000):
                if candidate not in candidates:
                    candidates.append(candidate)

            for candidate in candidates:
                try:
                    with sd.InputStream(
                        samplerate=candidate,
                        channels=self.channels,
                        callback=self._callback,
                    ):
                        self._active_sr = candidate
                        # signal that the input stream opened successfully
                        self._started_event.set()
                        while self._running.is_set():
                            sd.sleep(100)
                        return
                except Exception as e:
                    errors.append(f"{candidate}Hz: {e}")
                    self.last_error = str(e)
                    self._frames = []
                    continue

            if errors:
                self.last_error = " | ".join(errors)
            self._running.clear()

        self._rec_thread = threading.Thread(target=_run, daemon=True)
        self._rec_thread.start()

    def stop(self, outpath: str):
        self._running.clear()
        if self._rec_thread is not None:
            self._rec_thread.join()
        if self.last_error:
            raise RuntimeError(self.last_error)
        if not self._frames:
            raise RuntimeError("No audio recorded")
        data = np.concatenate(self._frames, axis=0)
        if TRIM_SILENCE:
            data = _trim_silence(data, SILENCE_THRESHOLD)
            if data.size == 0:
                raise RuntimeError("No audio detected after trimming")
        # ensure shape (n, channels)
        sf.write(outpath, data, self._active_sr)
        return outpath


def transcribe_with_groq(audio_path: str):
    if Groq is None:
        raise RuntimeError("Groq package not installed or failed to import")
    if not API_KEY:
        raise RuntimeError("Set GROQ_API_KEY environment variable first")

    global _GROQ_CLIENT
    if _GROQ_CLIENT is None:
        _GROQ_CLIENT = Groq(api_key=API_KEY)
    client = _GROQ_CLIENT
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()
    resp = client.audio.transcriptions.create(
        file=(os.path.basename(audio_path), audio_bytes),
        model=GROQ_WHISPER_MODEL,
        temperature=0,
        response_format="verbose_json",
    )
    # object shape depends on SDK; try common access patterns
    if hasattr(resp, "text"):
        return resp.text
    if isinstance(resp, dict):
        return resp.get("text") or resp.get("transcription") or str(resp)
    return str(resp)


def _trim_silence(data: np.ndarray, threshold: float) -> np.ndarray:
    if data.size == 0:
        return data
    mono = np.abs(data.mean(axis=1)) if data.ndim > 1 else np.abs(data)
    peak = float(mono.max())
    if peak <= 0:
        return data
    cutoff = peak * max(threshold, 0.0)
    idx = np.where(mono > cutoff)[0]
    if idx.size == 0:
        return data[:0]
    return data[idx[0] : idx[-1] + 1]


class _QtFloatingWindow(QWidget):
    def __init__(self, manager):
        super().__init__(None)
        self._manager = manager
        self._drag_offset = None
        self._close_pressed = False
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self._manager._point_in_close_button(event.position()):
                self._close_pressed = True
                self._manager._set_close_button_pressed(True)
                event.accept()
                return
            self._drag_offset = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self._manager._set_window_hover(True)
        hovering_close = self._manager._point_in_close_button(event.position())
        self._manager._set_close_button_hover(hovering_close)

        if self._close_pressed:
            self._manager._set_close_button_pressed(hovering_close)
            event.accept()
            return

        if self._drag_offset is not None and (event.buttons() & Qt.LeftButton):
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._close_pressed:
            should_close = self._manager._point_in_close_button(event.position())
            self._close_pressed = False
            self._manager._set_close_button_pressed(False)
            if should_close:
                self._manager._handle_close_button_clicked()
            event.accept()
            return

        self._drag_offset = None
        self._manager._set_close_button_pressed(False)
        event.accept()

    def leaveEvent(self, event):
        if not self._close_pressed:
            self._manager._set_close_button_pressed(False)
        self._manager._set_window_hover(False)
        self._manager._set_close_button_hover(False)
        super().leaveEvent(event)

    def enterEvent(self, event):
        self._manager._set_window_hover(True)
        super().enterEvent(event)

    def paintEvent(self, event):
        self._manager._paint_window(self)


class _QtPreviewWindow(QWidget):
    """Preview window for streaming transcription results"""

    def __init__(self, manager):
        super().__init__(None)
        self._manager = manager
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)

    def paintEvent(self, event):
        self._manager._paint_preview(self)


class GUIManager:
    def __init__(self, on_close_requested=None):
        if not PYSIDE6_AVAILABLE:
            raise RuntimeError(
                "PySide6 is required for the floating window UI. Install with: pip install PySide6"
            )

        self._queue = queue.Queue()
        self._audio_queue = queue.Queue()
        self._app = QApplication.instance() or QApplication(sys.argv[:1])
        self._app.setQuitOnLastWindowClosed(False)

        self._mode = "idle"
        self._display_text = "Ready"

        # Modern UI settings
        self._ui_style = FLOATING_UI_STYLE
        self._accent_color = _resolve_accent_color(FLOATING_ACCENT_COLOR)
        # State-specific accent colors for enhanced visual feedback
        self._recording_accent = _resolve_accent_color(FLOATING_RECORDING_COLOR)
        self._processing_accent = _resolve_accent_color(FLOATING_PROCESSING_COLOR)
        self._glassmorphism_enabled = FLOATING_GLASSMORPHISM
        self._animations_enabled = FLOATING_ANIMATIONS
        self._reduced_motion = FLOATING_REDUCED_MOTION
        self._layout_style = FLOATING_LAYOUT

        # Animation state for modern UI
        self._breathing_phase = 0.0
        self._pulse_phase = 0.0
        self._glow_intensity_current = 0.0
        self._state_transition_progress = 1.0
        self._last_state = "idle"

        self._full_width = max(120, _env_int("FLOATING_WIDTH", 180))
        self._full_height = max(34, _env_int("FLOATING_HEIGHT", 44))
        self._idle_scale = 0.50
        self._window_scale = 1.0
        self._target_window_scale = 1.0
        self._scale_smoothing = 0.34
        self._hover_scale = 1.02
        self._window_hover = False
        self._width = self._full_width
        self._height = self._full_height
        self._bar_count = max(7, min(15, _env_int("FLOATING_WAVEFORM_BARS", 11)))
        self._amplitudes = [0.0] * self._bar_count
        self._current_heights = [0.0] * self._bar_count
        # Enhanced amplitude tracking with peak hold
        self._level_env = 0.0
        self._level_peak = 0.12
        self._peak_hold = 0.0
        self._peak_decay = 0.97  # Slow decay for visual appeal
        self._attack_speed = 0.65  # Fast attack for responsiveness
        self._release_speed = 0.12  # Slow release for smooth transitions
        self._logo_image = None
        self._logo_mtime = None
        self._last_logo_check = 0.0
        self._platform_name = platform.system()
        self._show_close_button = os.getenv(
            "FLOATING_CLOSE_BUTTON", "0"
        ).strip().lower() not in {"0", "false", "no", "off"}
        self._close_button_hover = False
        self._close_button_pressed = False
        self._on_close_requested = on_close_requested
        self._theme_name = FLOATING_THEME
        self._theme = _resolve_theme(self._theme_name)
        self._motion_profile = FLOATING_MOTION_PROFILE
        self._motion = _resolve_motion_profile(self._motion_profile)
        self._glow_intensity = FLOATING_GLOW_INTENSITY
        self._bar_radius = FLOATING_BAR_RADIUS
        self._border_alpha = FLOATING_BORDER_ALPHA
        self._wave_debug = FLOATING_WAVE_DEBUG
        self._last_wave_debug_log = 0.0

        # Preview window state
        self._preview_window = _QtPreviewWindow(self)
        self._preview_text = ""
        self._preview_visible = False
        self._preview_debounce_time = 0.0
        self._preview_debounce_interval = 0.1  # 100ms debounce
        self._preview_max_width = 400
        self._preview_max_height = 100

        self._window = _QtFloatingWindow(self)
        self._setup_window()
        self._load_logo_image()

        self._timer = QTimer()
        self._timer.timeout.connect(self._poll)
        self._timer.start(16)

    def _logo_path(self) -> Path:
        return Path(__file__).resolve().parent / "public" / "asset" / "logo.png"

    def _setup_window(self):
        initial_scale = (
            1.0 if _resolve_visual_state(self._mode) == "record" else self._idle_scale
        )
        self._target_window_scale = initial_scale
        self._apply_window_scale(initial_scale, keep_center=False)
        screen = QGuiApplication.primaryScreen()
        if screen is not None:
            geometry = screen.availableGeometry()
            x = geometry.x() + (geometry.width() - self._width) // 2
            y = geometry.y() + geometry.height() - self._height - 26
            self._window.move(x, y)
        self._window.show()

    def _apply_window_scale(self, scale: float, keep_center: bool = True):
        scale = _clamp(float(scale), 0.35, 1.08)
        target_w = max(72, int(round(self._full_width * scale)))
        target_h = max(18, int(round(self._full_height * scale)))

        if (
            target_w == self._width
            and target_h == self._height
            and abs(scale - self._window_scale) < 1e-6
        ):
            return

        old_x = old_y = old_w = old_h = 0
        if keep_center:
            old_x = self._window.x()
            old_y = self._window.y()
            old_w = self._window.width()
            old_h = self._window.height()

        self._window_scale = scale
        self._width = target_w
        self._height = target_h
        self._window.setFixedSize(self._width, self._height)

        if keep_center and old_w > 0 and old_h > 0:
            center_x = old_x + (old_w // 2)
            center_y = old_y + (old_h // 2)
            new_x = center_x - (self._width // 2)
            new_y = center_y - (self._height // 2)
            self._window.move(new_x, new_y)

    def _tick_window_scale(self):
        target = _clamp(float(self._target_window_scale), 0.35, 1.08)
        current = float(self._window_scale)
        delta = target - current
        if abs(delta) < 0.004:
            next_scale = target
        else:
            # Use smoother easing for modern UI
            if (
                self._ui_style == "modern"
                and self._animations_enabled
                and not self._reduced_motion
            ):
                # Elastic easing for natural motion
                smoothing = 0.25
                next_scale = current + (delta * smoothing)
            else:
                next_scale = current + (delta * self._scale_smoothing)
        self._apply_window_scale(next_scale)

    def set_close_callback(self, callback):
        self._on_close_requested = callback

    def _set_window_hover(self, hovered: bool):
        hovered = bool(hovered)
        if hovered != self._window_hover:
            self._window_hover = hovered
            # Trigger hover animation for modern UI
            if (
                self._ui_style == "modern"
                and self._animations_enabled
                and not self._reduced_motion
            ):
                if hovered:
                    # Scale up slightly on hover
                    visual_state = _resolve_visual_state(self._mode)
                    base_scale = (
                        1.0
                        if visual_state in {"record", "processing"}
                        else self._idle_scale
                    )
                    self._target_window_scale = base_scale * self._hover_scale
                else:
                    # Return to normal scale
                    visual_state = _resolve_visual_state(self._mode)
                    self._target_window_scale = (
                        1.0
                        if visual_state in {"record", "processing"}
                        else self._idle_scale
                    )
            self._window.update()

    def _close_button_rect(self) -> QRectF:
        if not self._show_close_button:
            return QRectF(0.0, 0.0, 0.0, 0.0)
        size = max(12.0, min(15.0, self._height * 0.28))
        margin_x = 8.0
        margin_y = (self._height - size) / 2.0
        x = self._width - margin_x - size
        return QRectF(float(x), float(margin_y), float(size), float(size))

    def _point_in_close_button(self, point) -> bool:
        if not self._show_close_button or point is None:
            return False
        rect = self._close_button_rect()
        return rect.contains(float(point.x()), float(point.y()))

    def _set_close_button_hover(self, hovered: bool):
        if not self._show_close_button:
            return
        hovered = bool(hovered)
        try:
            self._window.setCursor(Qt.PointingHandCursor if hovered else Qt.ArrowCursor)
        except Exception:
            pass
        if hovered != self._close_button_hover:
            self._close_button_hover = hovered
            self._window.update()

    def _set_close_button_pressed(self, pressed: bool):
        if not self._show_close_button:
            return
        pressed = bool(pressed)
        if pressed != self._close_button_pressed:
            self._close_button_pressed = pressed
            self._window.update()

    def _handle_close_button_clicked(self):
        self._mode = "idle"
        self._display_text = "Ready"
        self._close_button_pressed = False
        self._close_button_hover = False
        self._window.hide()

        callback = self._on_close_requested
        if callback is not None:
            try:
                callback()
                return
            except Exception:
                pass

        self.quit()

    def _refresh_logo_if_changed(self):
        now = time.time()
        if now - self._last_logo_check < 1.0:
            return
        self._last_logo_check = now

        logo_path = self._logo_path()
        try:
            mtime = logo_path.stat().st_mtime
        except Exception:
            mtime = None

        if mtime != self._logo_mtime:
            self._logo_mtime = mtime
            self._load_logo_image()

    def _load_logo_image(self):
        logo_path = self._logo_path()
        if not logo_path.exists():
            self._logo_image = None
            return

        try:
            from PIL import Image

            with Image.open(logo_path) as source:
                logo = source.convert("RGBA")
                hsv = np.array(logo.convert("HSV"))
                sat = hsv[:, :, 1]
                val = hsv[:, :, 2]

                # Glow reaches image edges; crop by dense high-saturation/high-value regions.
                active = (sat >= 80) & (val >= 180)
                rows = np.where(active.mean(axis=1) >= 0.01)[0]
                cols = np.where(active.mean(axis=0) >= 0.02)[0]

                if rows.size and cols.size:
                    top, bottom = int(rows[0]), int(rows[-1]) + 1
                    left, right = int(cols[0]), int(cols[-1]) + 1
                    logo = logo.crop((left, top, right, bottom))
                else:
                    rgba = np.array(logo)
                    alpha = rgba[:, :, 3]
                    rgb = rgba[:, :, :3]
                    non_black = (alpha > 16) & (rgb.max(axis=2) > 20)
                    ys, xs = np.where(non_black)
                    if xs.size and ys.size:
                        left, right = int(xs.min()), int(xs.max()) + 1
                        top, bottom = int(ys.min()), int(ys.max()) + 1
                        logo = logo.crop((left, top, right, bottom))

                target_h = 30
                target_w = max(1, int((logo.width / logo.height) * target_h))
                logo = logo.resize((target_w, target_h), Image.Resampling.LANCZOS)

                rgba = np.ascontiguousarray(
                    np.array(logo.convert("RGBA"), dtype=np.uint8)
                )
                h, w, _ = rgba.shape
                qimg = QImage(rgba.data, w, h, 4 * w, QImage.Format_RGBA8888).copy()
                self._logo_image = QPixmap.fromImage(qimg)
                return
        except Exception:
            pass

        pix = QPixmap(str(logo_path))
        if pix.isNull():
            self._logo_image = None
            return
        self._logo_image = pix.scaledToHeight(30, Qt.SmoothTransformation)

    def _poll(self):
        self._refresh_logo_if_changed()

        # Update animation phases for modern UI
        if (
            self._ui_style == "modern"
            and self._animations_enabled
            and not self._reduced_motion
        ):
            dt = 0.016  # ~60fps
            self._breathing_phase += dt
            self._pulse_phase += dt

            visual_state = _resolve_visual_state(self._mode)
            if visual_state != self._last_state:
                self._state_transition_progress = 0.0
                self._last_state = visual_state
            else:
                self._state_transition_progress = min(
                    1.0, self._state_transition_progress + dt * 3.0
                )

            # Update glow intensity based on state and amplitude
            target_glow = 0.0
            if visual_state == "record":
                # Enhanced pulse glow - responds to audio level
                base_pulse = 0.35 + 0.25 * np.sin(self._pulse_phase * 4.0)
                # Add amplitude-based glow boost
                amplitude_boost = self._level_env * 0.4
                target_glow = base_pulse + amplitude_boost
            elif visual_state == "processing":
                # Processing state has subtle glow
                base_glow = 0.25
                amplitude_boost = self._level_env * 0.3
                target_glow = base_glow + amplitude_boost

            self._glow_intensity_current += (
                target_glow - self._glow_intensity_current
            ) * 0.18  # Slightly faster response

        try:
            while True:
                cmd, arg = self._queue.get_nowait()
                if cmd in {"show", "update"}:
                    mode = self._mode
                    body = arg
                    if isinstance(arg, (tuple, list)):
                        mode, body = arg[0], arg[1]
                    elif mode != "record":
                        mode = "processing"
                    if mode == "textpopup":
                        mode = "processing"
                    self._mode = mode
                    self._display_text = body
                    if not self._window.isVisible():
                        self._window.show()
                elif cmd == "close":
                    self._mode = "idle"
                    self._display_text = "Ready"
                    self._window.hide()
                elif cmd == "feedback":
                    # Handle success/error feedback animations
                    feedback_type = arg
                    if feedback_type == "success":
                        # Brief green flash and bounce
                        self._show_feedback_animation("success")
                    elif feedback_type == "error":
                        # Brief red flash and shake
                        self._show_feedback_animation("error")
                elif cmd == "clipboard":
                    try:
                        self._app.clipboard().setText(str(arg))
                    except Exception:
                        pass
        except queue.Empty:
            pass

        visual_state = _resolve_visual_state(self._mode)
        is_recording = visual_state == "record"
        is_processing = visual_state == "processing"

        # Update accent color based on state for enhanced visual feedback
        if is_recording:
            self._accent_color = self._recording_accent
        elif is_processing:
            self._accent_color = self._processing_accent

        # Enhanced amplitude processing with fast attack, slow release
        try:
            while True:
                amp = float(self._audio_queue.get_nowait())
                if not is_recording:
                    continue
                amp = max(0.0, min(1.0, amp))
                self._amplitudes.pop(0)
                self._amplitudes.append(amp)
                # Fast attack for responsive visualization
                self._level_env = (self._level_env * (1.0 - self._attack_speed)) + (
                    amp * self._attack_speed
                )
                # Update peak hold with slow decay
                if amp > self._peak_hold:
                    self._peak_hold = amp
        except queue.Empty:
            pass
        except Exception:
            pass

        if is_recording:
            # Slow peak decay for visual appeal
            self._peak_hold = max(self._peak_hold * self._peak_decay, self._level_env)
            self._level_peak = max(self._level_peak * 0.992, self._level_env, 0.09)
        else:
            # Slow release for smooth transitions
            self._level_env *= 1.0 - self._release_speed
            self._peak_hold *= self._peak_decay
            self._level_peak = max(0.09, self._level_peak * 0.96)

        base_scale = (
            1.0 if visual_state in {"record", "processing"} else self._idle_scale
        )
        if self._window_hover:
            base_scale *= self._hover_scale
        self._target_window_scale = base_scale
        self._tick_window_scale()

        half = max(1.0, (self._bar_count - 1) / 2.0)
        for i in range(self._bar_count):
            if is_recording or is_processing:
                # Use peak hold for more responsive visualization
                peak_ref = max(0.10, self._peak_hold * 0.8 + self._level_peak * 0.2)
                local = self._amplitudes[i] / peak_ref
                local = _clamp(local, 0.0, 1.0)

                # Enhanced center bias for more dynamic arch effect
                center_bias = 1.20 - (abs(i - half) / half) * 0.32

                # Apply amplitude-responsive strength
                strength = (local**0.55) * center_bias
                target = _clamp(0.06 + (strength * 0.92), 0.0, 1.0)
            else:
                target = 0.0

            diff = target - self._current_heights[i]
            # Fast rise, slow decay for smooth yet responsive animation
            if diff > 0:
                self._current_heights[i] += diff * 0.45  # Fast attack
            else:
                decay = 0.38 if not is_recording else 0.28  # Slow decay
                self._current_heights[i] += diff * decay
            self._current_heights[i] = max(0.0, min(1.0, self._current_heights[i]))

        self._window.update()

    def _draw_rounded_rect(self, painter, x, y, w, h, color, r):
        rect = QRectF(float(x), float(y), float(w), float(h))
        path = QPainterPath()
        radius = max(1.0, min(float(r), rect.width() / 2.0, rect.height() / 2.0))
        path.addRoundedRect(rect, radius, radius)
        painter.fillPath(path, QColor(color))

    def _draw_close_button(self, painter):
        if not self._show_close_button:
            return

        rect = self._close_button_rect()
        halo_rgba = (
            self._theme["close_halo_active"]
            if (self._close_button_hover or self._close_button_pressed)
            else self._theme["close_halo"]
        )
        halo = QColor(*halo_rgba)
        painter.setPen(Qt.NoPen)
        painter.setBrush(halo)
        painter.drawRoundedRect(rect.adjusted(-1.2, -1.2, 1.2, 1.2), 5.2, 5.2)

        if self._close_button_pressed:
            fill = QColor(self._theme["close_pressed"])
        elif self._close_button_hover:
            fill = QColor(self._theme["close_hover"])
        else:
            fill = QColor(self._theme["close_idle"])

        border = QColor("#ffffff")
        pen = painter.pen()
        pen.setColor(border)
        pen.setWidthF(1.2)
        painter.setPen(pen)
        painter.setBrush(fill)
        painter.drawRoundedRect(rect, 4.0, 4.0)

        inset = 4.0
        pen = painter.pen()
        pen.setColor(QColor("#ffffff"))
        pen.setWidthF(2.05)
        painter.setPen(pen)
        painter.drawLine(
            int(rect.left() + inset),
            int(rect.top() + inset),
            int(rect.right() - inset),
            int(rect.bottom() - inset),
        )
        painter.drawLine(
            int(rect.left() + inset),
            int(rect.bottom() - inset),
            int(rect.right() - inset),
            int(rect.top() + inset),
        )
        painter.setPen(Qt.NoPen)

    def _paint_shell(
        self, painter, w: float, h: float, outer_radius: float, inner_radius: float
    ):
        visual_state = _resolve_visual_state(self._mode)
        is_recording = visual_state == "record"
        is_hovered = self._window_hover

        # Use modern glassmorphism style if enabled
        if self._ui_style == "modern" and self._glassmorphism_enabled:
            self._paint_modern_shell(
                painter,
                w,
                h,
                outer_radius,
                inner_radius,
                visual_state,
                is_recording,
                is_hovered,
            )
            return

        shadow_alpha = 44 + (12 if is_hovered else 0) + (10 if is_recording else 0)
        shadow_rect = QRectF(2.0, 3.0, max(0.0, w - 4.0), max(0.0, h - 5.0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, int(_clamp(shadow_alpha, 0.0, 120.0))))
        painter.drawRoundedRect(shadow_rect, outer_radius, outer_radius)

        fill = QColor("#121212" if is_hovered else "#0f0f10")
        if is_recording:
            fill = QColor("#101311")
        shell_rect = QRectF(1.0, 1.0, max(0.0, w - 2.0), max(0.0, h - 2.0))
        painter.setBrush(fill)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(shell_rect, inner_radius, inner_radius)

        border_width = 2.0 if is_recording else 1.75
        border_alpha = 245 if is_hovered else 228
        border_inset = border_width / 2.0 + 0.55
        border_rect = QRectF(
            border_inset,
            border_inset,
            max(0.0, w - border_inset * 2.0),
            max(0.0, h - border_inset * 2.0),
        )

        if is_recording:
            glow_pen = painter.pen()
            glow_pen.setColor(QColor(255, 255, 255, 48))
            glow_pen.setWidthF(border_width + 1.2)
            painter.setPen(glow_pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(border_rect, inner_radius, inner_radius)

        border_pen = painter.pen()
        border_pen.setColor(QColor(255, 255, 255, border_alpha))
        border_pen.setWidthF(border_width)
        painter.setPen(border_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(border_rect, inner_radius, inner_radius)
        painter.setPen(Qt.NoPen)

    def _paint_modern_shell(
        self,
        painter,
        w: float,
        h: float,
        outer_radius: float,
        inner_radius: float,
        visual_state: str,
        is_recording: bool,
        is_hovered: bool,
    ):
        """Paint modern glassmorphism shell with 2026 UI/UX design"""

        # Enhanced shadow with depth
        shadow_blur = 32 if is_recording else 24
        shadow_alpha = 25 + (10 if is_hovered else 0) + (15 if is_recording else 0)
        for i in range(3):
            offset = (i + 1) * 2.0
            shadow_rect = QRectF(
                offset, offset + 2, max(0.0, w - offset * 2), max(0.0, h - offset * 2)
            )
            alpha = int(shadow_alpha / (i + 1))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 0, 0, alpha))
            painter.drawRoundedRect(shadow_rect, outer_radius, outer_radius)

        # Glassmorphic background with translucency
        glass_alpha = 30 if is_recording else 25
        if is_hovered:
            glass_alpha += 5

        shell_rect = QRectF(1.0, 1.0, max(0.0, w - 2.0), max(0.0, h - 2.0))

        # Background fill with slight tint based on state
        if is_recording:
            bg_color = QColor(255, 255, 255, glass_alpha)
        else:
            bg_color = QColor(255, 255, 255, glass_alpha)

        painter.setPen(Qt.NoPen)
        painter.setBrush(bg_color)
        painter.drawRoundedRect(shell_rect, inner_radius, inner_radius)

        # Outer glow effect for active states
        if is_recording and self._glow_intensity_current > 0.01:
            accent = self._accent_color
            glow_color = QColor(*accent["glow"])
            glow_alpha = int(self._glow_intensity_current * 255)
            glow_color.setAlpha(glow_alpha)

            for i in range(4):
                glow_offset = (i + 1) * 4.0
                glow_rect = QRectF(
                    1.0 - glow_offset,
                    1.0 - glow_offset,
                    max(0.0, w - 2.0 + glow_offset * 2),
                    max(0.0, h - 2.0 + glow_offset * 2),
                )
                glow_alpha_layer = int(glow_alpha / (i + 1) * 0.6)
                glow_color.setAlpha(glow_alpha_layer)
                painter.setBrush(glow_color)
                painter.drawRoundedRect(
                    glow_rect,
                    inner_radius + glow_offset / 2,
                    inner_radius + glow_offset / 2,
                )

        # Border with accent color for active states
        border_width = 1.5
        border_inset = border_width / 2.0 + 0.5
        border_rect = QRectF(
            border_inset,
            border_inset,
            max(0.0, w - border_inset * 2.0),
            max(0.0, h - border_inset * 2.0),
        )

        border_pen = painter.pen()
        if is_recording:
            accent = self._accent_color
            border_color = QColor(accent["primary"])
            border_alpha = int(153 + self._glow_intensity_current * 50)
            border_color.setAlpha(border_alpha)
            border_pen.setColor(border_color)
            border_width = 2.0
        else:
            border_alpha = 51 if not is_hovered else 76
            border_pen.setColor(QColor(255, 255, 255, border_alpha))

        border_pen.setWidthF(border_width)
        painter.setPen(border_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(border_rect, inner_radius, inner_radius)
        painter.setPen(Qt.NoPen)

    def _state_palette(self) -> dict:
        state = _resolve_visual_state(self._mode)
        states = self._theme["states"]
        return states.get(state, states["idle"])

    def _paint_bars(self, painter, w: float, h: float):
        visual_state = _resolve_visual_state(self._mode)
        if visual_state != "record":
            return

        # Use modern waveform visualization if enabled
        if self._ui_style == "modern":
            self._paint_modern_waveform(painter, w, h, visual_state)
            return

        now = time.time()

        right_pad = 30.0 if self._show_close_button else 0.0
        draw_w = max(24.0, w - right_pad)
        mid_x = draw_w / 2.0
        mid_y = h / 2.0
        icon_w = max(34.0, draw_w * 0.74)
        icon_h = max(12.0, min(18.0, h * 0.44))
        badge_rect = QRectF(mid_x - icon_w / 2.0, mid_y - icon_h / 2.0, icon_w, icon_h)

        badge_pen = painter.pen()
        badge_pen.setColor(QColor(255, 255, 255, 238 if self._window_hover else 226))
        badge_pen.setWidthF(max(1.2, min(1.45, h * 0.042)))
        painter.setPen(badge_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(badge_rect, icon_h / 2.0, icon_h / 2.0)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255, 6))
        painter.drawRoundedRect(
            badge_rect.adjusted(1.2, 1.2, -1.2, -1.2), icon_h / 2.2, icon_h / 2.2
        )
        painter.setBrush(Qt.NoBrush)

        if self._wave_debug:
            debug_pen = painter.pen()
            debug_pen.setColor(QColor(100, 200, 255, 160))
            debug_pen.setWidthF(1.0)
            painter.setPen(debug_pen)
            painter.drawRoundedRect(
                badge_rect.adjusted(0.6, 0.6, -0.6, -0.6), icon_h / 2.1, icon_h / 2.1
            )
            painter.setPen(Qt.NoPen)

        heights_for_render = list(self._current_heights[: self._bar_count])
        if len(heights_for_render) < self._bar_count:
            heights_for_render.extend(
                [0.0] * (self._bar_count - len(heights_for_render))
            )
        bar_count = 17
        center_idx = (bar_count - 1) / 2.0
        span_w = icon_w * 0.66
        step_x = span_w / max(1, bar_count - 1)
        start_x = mid_x - (span_w / 2.0)
        min_bar_h = icon_h * 0.22
        max_bar_h = icon_h * 0.74
        base_floor = 0.16
        bar_w = max(1.4, min(2.2, step_x * 0.56))
        bar_radius = max(0.9, min(1.8, bar_w * 0.8))

        bar_values = []
        for i in range(bar_count):
            sample_pos = i * max(1, self._bar_count - 1) / max(1, bar_count - 1)
            left_idx = int(sample_pos)
            right_idx = min(self._bar_count - 1, left_idx + 1)
            blend = sample_pos - left_idx
            level = (heights_for_render[left_idx] * (1.0 - blend)) + (
                heights_for_render[right_idx] * blend
            )

            center_dist = abs(i - center_idx) / max(1.0, center_idx)
            arch = 1.0 - (center_dist**1.15) * 0.27
            strength = _clamp(base_floor + ((level**0.62) * 0.92), 0.0, 1.0)
            bar_h = min_bar_h + ((max_bar_h - min_bar_h) * strength * arch)
            x = start_x + (i * step_x)
            bar_values.append((x, _clamp(bar_h, min_bar_h, max_bar_h)))

        glow_alpha = int(_clamp((148.0 * self._glow_intensity) + 48.0, 90.0, 225.0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255, glow_alpha))
        for x, bar_h in bar_values:
            glow_rect = QRectF(
                float(x - (bar_w * 0.9)),
                float(mid_y - (bar_h / 2.0) - 0.8),
                float(bar_w * 1.8),
                float(bar_h + 1.6),
            )
            painter.drawRoundedRect(glow_rect, bar_radius + 0.7, bar_radius + 0.7)

        painter.setBrush(QColor(255, 255, 255, 252))
        for x, bar_h in bar_values:
            bar_rect = QRectF(
                float(x - (bar_w / 2.0)),
                float(mid_y - (bar_h / 2.0)),
                float(bar_w),
                float(bar_h),
            )
            painter.drawRoundedRect(bar_rect, bar_radius, bar_radius)

        if self._wave_debug and (now - self._last_wave_debug_log) > 0.35:
            bars_only = [bar_h for _, bar_h in bar_values]
            wave_span = (max(bars_only) - min(bars_only)) if bars_only else 0.0
            print(
                f"[wave-debug] mode={visual_state} bars={len(bar_values)} span={wave_span:.2f} "
                f"icon_h={icon_h:.2f} level_env={self._level_env:.3f}",
                file=sys.stderr,
            )
            self._last_wave_debug_log = now

        painter.setPen(Qt.NoPen)

    def _paint_modern_waveform(self, painter, w: float, h: float, visual_state: str):
        """Paint modern smooth waveform visualization with gradient and glow"""

        now = time.time()
        right_pad = 30.0 if self._show_close_button else 0.0
        draw_w = max(24.0, w - right_pad)
        mid_x = draw_w / 2.0
        mid_y = h / 2.0

        # Enhanced waveform parameters - 11 bars for richer visualization
        bar_count = 11  # Increased from 7 for more dynamic visualization
        bar_spacing = 6.0  # Slightly tighter spacing
        bar_width = 3.5  # Slightly narrower bars
        bar_radius = 1.8
        min_bar_h = 3.0
        max_bar_h = h * 0.65  # More height range for better amplitude response

        # Calculate total width and starting position
        total_width = (bar_count * bar_width) + ((bar_count - 1) * bar_spacing)
        start_x = mid_x - (total_width / 2.0)

        # Get current heights with peak hold for more responsive visualization
        heights_for_render = list(self._current_heights[: self._bar_count])
        if len(heights_for_render) < self._bar_count:
            heights_for_render.extend(
                [0.0] * (self._bar_count - len(heights_for_render))
            )

        # Interpolate to bar_count with enhanced amplitude responsiveness
        bar_values = []
        for i in range(bar_count):
            sample_pos = i * max(1, self._bar_count - 1) / max(1, bar_count - 1)
            left_idx = int(sample_pos)
            right_idx = min(self._bar_count - 1, left_idx + 1)
            blend = sample_pos - left_idx
            level = (heights_for_render[left_idx] * (1.0 - blend)) + (
                heights_for_render[right_idx] * blend
            )

            # Enhanced center bias for more dynamic arch effect
            center_idx = (bar_count - 1) / 2.0
            center_dist = abs(i - center_idx) / max(1.0, center_idx)
            arch = 1.0 - (center_dist**1.1) * 0.35  # More pronounced arch

            # Apply amplitude-responsive strength with softer power curve
            strength = _clamp(level**0.5, 0.0, 1.0)
            bar_h = min_bar_h + ((max_bar_h - min_bar_h) * strength * arch)
            x = start_x + (i * (bar_width + bar_spacing))
            bar_values.append((x, _clamp(bar_h, min_bar_h, max_bar_h)))

        # Get accent color
        accent = self._accent_color

        # Enhanced glow effect - more prominent and responsive to amplitude
        if self._glow_intensity_current > 0.01:
            glow_color = QColor(*accent["glow"])
            glow_alpha = int(self._glow_intensity_current * 220)  # Increased intensity
            glow_color.setAlpha(glow_alpha)
            painter.setPen(Qt.NoPen)
            painter.setBrush(glow_color)

            for x, bar_h in bar_values:
                # Glow scales with bar height for more dynamic effect
                glow_height_factor = 1.0 + (bar_h / max_bar_h) * 0.5
                glow_rect = QRectF(
                    float(x - bar_width * 0.6),
                    float(mid_y - (bar_h / 2.0) - 2.5),
                    float(bar_width * 2.2),
                    float(bar_h * glow_height_factor + 5.0),
                )
                painter.drawRoundedRect(glow_rect, bar_radius + 1.2, bar_radius + 1.2)

        # Draw bars with enhanced gradient based on height
        painter.setPen(Qt.NoPen)

        for x, bar_h in bar_values:
            bar_rect = QRectF(
                float(x),
                float(mid_y - (bar_h / 2.0)),
                float(bar_width),
                float(bar_h),
            )

            # Create gradient from light to dark - intensity based on bar height
            gradient = QLinearGradient(bar_rect.topLeft(), bar_rect.bottomLeft())
            height_intensity = bar_h / max_bar_h if max_bar_h > 0 else 0

            # Lighter colors for taller bars for more dynamic effect
            gradient.setColorAt(0.0, QColor(accent["light"]))
            gradient.setColorAt(0.5 - height_intensity * 0.2, QColor(accent["primary"]))
            gradient.setColorAt(1.0, QColor(accent["dark"]))

            painter.setBrush(gradient)
            painter.drawRoundedRect(bar_rect, bar_radius, bar_radius)

    def _paint_window(self, window):
        painter = QPainter(window)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)

        w = float(window.width())
        h = float(window.height())
        outer_radius = max(14.0, min(24.0, h * 0.48))
        inner_radius = max(12.0, outer_radius - 1.5)

        self._paint_shell(painter, w, h, outer_radius, inner_radius)
        if self._show_close_button:
            self._draw_close_button(painter)
        self._paint_bars(painter, w, h)

        painter.end()

    def show(self, text: str):
        self._queue.put(("show", text))

    def update(self, text: str):
        self._queue.put(("update", text))

    def show_success_feedback(self):
        """Show brief success animation (green flash + bounce)"""
        if (
            self._ui_style == "modern"
            and self._animations_enabled
            and not self._reduced_motion
        ):
            self._queue.put(("feedback", "success"))

    def show_error_feedback(self):
        """Show brief error animation (red flash + shake)"""
        if (
            self._ui_style == "modern"
            and self._animations_enabled
            and not self._reduced_motion
        ):
            self._queue.put(("feedback", "error"))

    def update_amplitude(self, amp: float):
        self._audio_queue.put(amp)

    def set_clipboard_text(self, text: str):
        self._queue.put(("clipboard", text))

    def close(self):
        self._queue.put(("close", None))

    def run(self):
        if not self._window.isVisible():
            self._window.show()
        self._app.exec()

    def quit(self):
        self._app.quit()

    def _show_feedback_animation(self, feedback_type: str):
        """Show brief visual feedback animation"""
        if feedback_type == "success":
            # Store original position
            original_y = self._window.y()
            # Quick bounce animation
            for i in range(3):
                offset = 5 if i % 2 == 0 else -5
                self._window.move(self._window.x(), original_y + offset)
                QApplication.processEvents()
                time.sleep(0.05)
            self._window.move(self._window.x(), original_y)
        elif feedback_type == "error":
            # Store original position
            original_x = self._window.x()
            # Quick shake animation
            for i in range(4):
                offset = 3 if i % 2 == 0 else -3
                self._window.move(original_x + offset, self._window.y())
                QApplication.processEvents()
                time.sleep(0.04)
            self._window.move(original_x, self._window.y())

    # --- Preview Window Methods ---

    def show_preview(self, text: str, status: str = ""):
        """
        Show preview text in overlay window.

        Args:
            text: Preview text to display
            status: Status indicator (e.g., "Streaming...", "Finalizing...")
        """
        now = time.time()
        # Debounce updates
        if now - self._preview_debounce_time < self._preview_debounce_interval:
            return

        self._preview_debounce_time = now
        self._preview_text = text

        if not self._preview_visible:
            self._preview_visible = True
            self._position_preview_window()
            self._preview_window.show()
        else:
            self._preview_window.update()

    def hide_preview(self):
        """Hide the preview window"""
        if self._preview_visible:
            self._preview_visible = False
            self._preview_window.hide()
            self._preview_text = ""

    def update_preview(self, text: str, status: str = ""):
        """
        Update preview text with debouncing.

        Args:
            text: New preview text
            status: Status indicator
        """
        self.show_preview(text, status)

    def _position_preview_window(self):
        """Position preview window below the main floating window"""
        if not self._preview_visible:
            return

        # Calculate preview size based on text
        from PySide6.QtGui import QFontMetrics, QFont

        font = QFont("Sans Serif", 10)
        fm = QFontMetrics(font)

        # Calculate text dimensions
        text_width = min(
            fm.horizontalAdvance(self._preview_text), self._preview_max_width - 20
        )
        text_height = fm.height()

        # Estimate lines needed
        lines = max(1, len(self._preview_text) // 40 + 1)
        preview_height = min(text_height * lines + 30, self._preview_max_height)
        preview_width = min(text_width + 20, self._preview_max_width)

        self._preview_window.setFixedSize(int(preview_width), int(preview_height))

        # Position below main window
        main_x = self._window.x()
        main_y = self._window.y()
        main_h = self._window.height()

        preview_x = main_x + (self._width - preview_width) // 2
        preview_y = main_y + main_h + 5  # 5px gap

        self._preview_window.move(int(preview_x), int(preview_y))

    def _paint_preview(self, window):
        """Paint the preview window"""
        painter = QPainter(window)
        painter.setRenderHint(QPainter.Antialiasing, True)

        w = float(window.width())
        h = float(window.height())

        # Draw background with transparency
        bg_path = QPainterPath()
        radius = 6.0
        bg_path.addRoundedRect(QRectF(0, 0, w, h), radius, radius)

        # Semi-transparent dark background
        painter.fillPath(bg_path, QColor(20, 20, 25, 200))

        # Draw border
        border_pen = painter.pen()
        border_pen.setColor(QColor(100, 100, 120, 180))
        border_pen.setWidthF(1.0)
        painter.setPen(border_pen)
        painter.drawPath(bg_path)

        # Draw text
        from PySide6.QtGui import QFont, QPen

        font = QFont("Sans Serif", 10)
        font.setItalic(True)  # Italic to indicate draft
        painter.setFont(font)

        # Text color - lighter to indicate draft
        text_pen = QPen(QColor(180, 180, 200, 230))
        painter.setPen(text_pen)

        # Truncate text if needed
        display_text = self._preview_text
        if len(display_text) > 100:
            display_text = display_text[:97] + "..."

        # Draw text with padding
        from PySide6.QtCore import Qt

        text_rect = QRectF(8, 5, w - 16, h - 10)
        painter.drawText(text_rect, Qt.TextWordWrap, display_text)

        painter.end()


def main():
    def print_banner(hotkey: str):
        banner = r"""
 ____  _ _      _        ____  _ _       _ _   
|  _ \(_) |    | |      |  _ \(_) |     | | |  
| | | |_| | ___| |_ __ _| |_) || | ___  | | |_ 
| | | | | |/ __| __/ _` |  ___/ | |/ _ \ | | __|
| |_| | | | (__| || (_| | |   | | | (_) || | |_ 
|____/|_|_|\___|\__\__,_|_|   |_|_|\___/ |_|\__|
"""
        print(banner)
        print("DictaPilot")
        print("Developer: Rehan")
        print("License: MIT (see LICENSE file)")
        print("")


def _setup_dictation_pipeline(gui, recorder, processing_event, shutdown_event, config):
    """Setup hotkey listener and recording callbacks for the floating window.
    
    Args:
        gui: GUIManager instance
        recorder: Recorder instance
        processing_event: threading.Event for processing state
        shutdown_event: threading.Event for shutdown coordination
        config: DictaPilotConfig instance
    
    Returns:
        hotkey_manager: HotkeyManager instance (or None if registration failed)
    """
    from smart_editor import is_transform_command, sync_state_to_output, TranscriptState
    
    transcript_state = TranscriptState()
    
    # Load config values
    HOTKEY = config.hotkey
    HOTKEY_BACKEND = config.hotkey_backend
    SMART_EDIT = config.smart_edit
    RESET_TRANSCRIPT_EACH_RECORDING = config.reset_transcript_each_recording
    PASTE_POLICY = config.paste_policy
    PASTE_MODE = config.paste_mode
    PASTE_BACKEND = config.paste_backend
    INSTANT_REFINE = getattr(config, 'instant_refine', True)
    DICTATION_MODE = config.mode
    SMART_MODE = config.smart_mode
    
    def _stop_active_recording():
        if not recorder._running.is_set():
            return
        temp_path = None
        try:
            fd, temp_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            recorder.stop(temp_path)
        except Exception:
            try:
                recorder._running.clear()
            except Exception:
                pass
        finally:
            if temp_path:
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
    
    def _request_shutdown():
        """Shutdown dictation pipeline and quit the application"""
        if shutdown_event.is_set():
            return
        shutdown_event.set()
        try:
            processing_event.clear()
        except Exception:
            pass
        try:
            _stop_active_recording()
        except Exception:
            pass
        try:
            if hotkey_manager is not None:
                hotkey_manager.stop()
        except Exception:
            pass
        
        # Quit the application
        try:
            gui.quit()
        except Exception:
            pass
    
    gui.set_close_callback(_request_shutdown)
    
    def _signal_handler(signum, frame):
        print("\nReceived interrupt, shutting down...")
        _request_shutdown()
    
    signal.signal(signal.SIGINT, _signal_handler)
    try:
        signal.signal(signal.SIGTERM, _signal_handler)
    except Exception:
        pass
    
    def on_press(e):
        if shutdown_event.is_set():
            return
        if recorder._running.is_set():
            return
        if processing_event.is_set():
            try:
                gui.show(("processing", "Still processing previous recording..."))
            except Exception:
                pass
            return
        if SMART_EDIT and RESET_TRANSCRIPT_EACH_RECORDING:
            with transcript_state.lock:
                transcript_state.segments.clear()
                transcript_state.output_text = ""
        print("Start recording")
        
        try:
            gui.show(("record", "Recording..."))
        except Exception:
            pass
        recorder.last_error = None
        recorder.start(amplitude_callback=gui.update_amplitude)
        started = recorder._started_event.wait(timeout=1.0)
        if not started:
            msg = recorder.last_error or "Timeout opening audio input device"
            gui.update(f"Recording error: {msg}")
            time.sleep(1.5)
            gui.close()
            return
    
    def on_release(e):
        if shutdown_event.is_set():
            return
        if not recorder._running.is_set():
            return
        print("Stop recording")
        
        try:
            gui.hide_preview()
            gui.update(("processing", "Processing audio..."))
        except Exception:
            pass
        
        try:
            fd, path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            audio_path = recorder.stop(path)
        except Exception as ex:
            print("Recording error:", ex, file=sys.stderr)
            gui.update(f"Recording error: {ex}")
            time.sleep(2)
            gui.close()
            return
        
        processing_event.set()
        
        def _process():
            try:
                if shutdown_event.is_set():
                    return
                
                gui.update(("processing", "Processing audio..."))
                text = transcribe_with_groq(audio_path)
                
                if not text:
                    text = "(no transcription returned)"
                print("Transcription:\n", text)
                
                prev_out = transcript_state.output_text
                fast_out = text
                fast_action = "append"
                
                if SMART_EDIT:
                    prev_out, fast_out, fast_action = smart_update_state(
                        transcript_state,
                        text,
                        mode="heuristic",
                        allow_llm=False,
                    )
                print(f"Fast action: {fast_action}")
                print("Fast transcript:\n", fast_out if fast_out else "(empty)")
                
                refined_out = fast_out
                refined_action = fast_action
                if (
                    SMART_EDIT
                    and INSTANT_REFINE
                    and DICTATION_MODE != "speed"
                    and not is_transform_command(text)
                ):
                    try:
                        gui.update(("processing", "Refining..."))
                    except Exception:
                        pass
                    llm_result = llm_refine(prev_out, text)
                    if llm_result is not None:
                        refined_out, refined_action = llm_result
                        if refined_out != fast_out:
                            with transcript_state.lock:
                                current_out = transcript_state.output_text
                            if current_out == fast_out:
                                sync_state_to_output(
                                    transcript_state, fast_out, refined_out
                                )
                
                if PASTE_POLICY == "final_only":
                    final_output = refined_out
                    should_paste = (
                        refined_action != "ignore"
                        and refined_action != "clear"
                        and final_output.strip()
                    )
                    
                    if should_paste:
                        try:
                            import pyperclip
                            pyperclip.copy(final_output)
                        except Exception:
                            gui.set_clipboard_text(final_output)
                        
                        paste_error = None
                        try:
                            selected_paste_mode = PASTE_MODE if SMART_EDIT else "delta"
                            paste_text(
                                prev_out,
                                final_output,
                                selected_paste_mode,
                                backend=PASTE_BACKEND,
                            )
                        except Exception as ex:
                            paste_error = ex
                            try:
                                paste_text(
                                    "", final_output, "full", backend=PASTE_BACKEND
                                )
                                paste_error = None
                            except Exception as ex2:
                                paste_error = RuntimeError(
                                    f"{ex}; fallback full paste failed: {ex2}"
                                )
                        
                        if paste_error is not None:
                            print(f"Paste error: {paste_error}", file=sys.stderr)
                            try:
                                gui.update(
                                    "Paste failed. Try normal user mode and PASTE_BACKEND=x11/xdotool."
                                )
                            except Exception:
                                pass
                    else:
                        print(
                            f"Action '{refined_action}' detected - skipping external paste"
                        )
                        try:
                            gui.show(("done", "Command applied"))
                        except Exception:
                            pass
                elif PASTE_POLICY == "live_preview":
                    try:
                        import pyperclip
                        pyperclip.copy(fast_out)
                    except Exception:
                        gui.set_clipboard_text(fast_out)
                    
                    paste_error = None
                    try:
                        selected_paste_mode = PASTE_MODE if SMART_EDIT else "delta"
                        paste_text(
                            prev_out,
                            fast_out,
                            selected_paste_mode,
                            backend=PASTE_BACKEND,
                        )
                    except Exception as ex:
                        paste_error = ex
                        try:
                            paste_text("", fast_out, "full", backend=PASTE_BACKEND)
                            paste_error = None
                        except Exception as ex2:
                            paste_error = RuntimeError(
                                f"{ex}; fallback full paste failed: {ex2}"
                            )
                    
                    if paste_error is not None:
                        print(f"Paste error: {paste_error}", file=sys.stderr)
                        try:
                            gui.update(
                                "Paste failed. Try normal user mode and PASTE_BACKEND=x11/xdotool."
                            )
                        except Exception:
                            pass
                
                try:
                    add_transcription(
                        text,
                        refined_out,
                        refined_action,
                        cleanup_applied=refined_out != text,
                        correction_source="heuristic" if SMART_EDIT else "none",
                        ambiguity_flag=False,
                    )
                    print("Transcription saved to storage")
                except Exception as storage_ex:
                    missing_path = getattr(storage_ex, "filename", None)
                    if missing_path:
                        print(
                            f"Warning: failed to save transcription: {storage_ex} (missing: {missing_path})",
                            file=sys.stderr,
                        )
                    else:
                        print(
                            f"Warning: failed to save transcription: {storage_ex}",
                            file=sys.stderr,
                        )
                
                try:
                    output_for_popup = (
                        refined_out if refined_out else "(empty transcript)"
                    )
                    snippet = (
                        output_for_popup
                        if len(output_for_popup) <= 300
                        else output_for_popup[:300] + "..."
                    )
                    gui.show(("done", snippet))
                except Exception:
                    pass
                
                time.sleep(1.5)
                try:
                    gui.show(("idle", "Ready"))
                except Exception:
                    pass
            
            except Exception as ex:
                missing_path = getattr(ex, "filename", None)
                if missing_path:
                    gui.update(f"Transcription error: {ex} (missing: {missing_path})")
                else:
                    gui.update(f"Transcription error: {ex}")
                print("Transcription error:", ex, file=sys.stderr)
                print(traceback.format_exc(), file=sys.stderr)
            finally:
                processing_event.clear()
                try:
                    os.remove(audio_path)
                except Exception:
                    pass
        
        t = threading.Thread(target=_process, daemon=True)
        t.start()
    
    hotkey_manager = HotkeyManager(HOTKEY, on_press, on_release, backend=HOTKEY_BACKEND)
    try:
        active_backend = hotkey_manager.start()
        print(f"Hotkey listener active: {active_backend}")
    except Exception as ex:
        print(f"Failed to register hotkey '{HOTKEY}': {ex}", file=sys.stderr)
        return None
    
    return hotkey_manager


def main():
    """Main entry point for normal dictation mode (floating window only)."""
    if not sys.stdout.isatty():
        try:
            sys.stdout = open(os.devnull, "w")
            sys.stderr = open(os.devnull, "w")
        except Exception:
            pass
    
    def print_banner(hotkey: str):
        banner = r"""
 ____  _ _      _        ____  _ _       _ _   
|  _ \(_) |    | |      |  _ \(_) |     | | |  
| | | |_| | ___| |_ __ _| |_) || | ___  | | |_ 
| | | | | |/ __| __/ _` |  ___/ | |/ _ \ | | __|
| |_| | | | (__| || (_| | |   | | | (_) || | |_ 
|____/|_|_|\___|\__\__,_|_|   |_|_|\___/ |_|\__|
"""
        print(banner)
        print("DictaPilot")
        print("Developer: Rehan")
        print("License: MIT (see LICENSE file)")
        print("")
        
        # Display server detection
        display_server = detect_display_server()
        print(f"Display server: {display_server}")
        if display_server == "wayland":
            print("Running on Wayland - using pynput backend for hotkeys")
            # Check Wayland dependencies
            try:
                from wayland_backend import (
                    get_wayland_dependencies_status,
                    print_wayland_setup_instructions,
                )

                deps = get_wayland_dependencies_status()
                missing = [
                    k
                    for k, v in deps.items()
                    if not v and k in ("wl_clipboard", "pynput")
                ]
                if missing:
                    print("")
                    print("Warning: Some Wayland dependencies are missing:")
                    for dep in missing:
                        print(f"  - {dep}")
                    print("Run with --wayland-deps for installation instructions.")
            except ImportError:
                pass
        elif display_server == "x11":
            print("Running on X11 - using native X11 backend")
        else:
            print("Display server unknown - using fallback backends")
        print("")

        print(f"Hold '{hotkey}' to record; release to send audio for transcription.")
        print(
            f"Smart dictation: {'on' if SMART_EDIT else 'off'} "
            f"(mode={SMART_MODE}, paste={PASTE_MODE}, paste_backend={PASTE_BACKEND})"
        )
        if SMART_EDIT and SMART_MODE == "llm":
            cleanup_mode = "always" if LLM_ALWAYS_CLEAN else "intent-only"
            print(f"LLM cleanup: {cleanup_mode} (chat_model={GROQ_CHAT_MODEL})")
        print(f"Transcription model: {GROQ_WHISPER_MODEL}")
        print(f"Hotkey backend preference: {HOTKEY_BACKEND}")
        print(f"Dictation mode: {DICTATION_MODE} (cleanup={CLEANUP_LEVEL})")
        print(
            f"Audio: {SR}Hz, channels={CHANNELS}, trim_silence={'on' if TRIM_SILENCE else 'off'}"
        )
        print(f"Instant refine: {'on' if INSTANT_REFINE else 'off'}")
        if SMART_EDIT and RESET_TRANSCRIPT_EACH_RECORDING:
            print("Transcript reset mode: per recording")
        elif SMART_EDIT:
            print("Transcript reset mode: session (keeps previous recordings)")

        try:
            storage_info = get_storage_info()
            print(f"Transcription storage: {storage_info['storage_path']}")
            print(
                f"Total transcriptions: {storage_info['statistics']['total_transcriptions']}"
            )
        except Exception:
            pass
        print("")

    print_banner(HOTKEY)
    recorder = Recorder()
    processing_event = threading.Event()
    shutdown_event = threading.Event()

    try:
        gui = GUIManager()
    except Exception as ex:
        print(f"Failed to initialize GUI: {ex}", file=sys.stderr)
        return
    
    # Load config and setup dictation pipeline
    from config import load_config
    config = load_config()
    
    hotkey_manager = _setup_dictation_pipeline(gui, recorder, processing_event, shutdown_event, config)
    if hotkey_manager is None:
        return

    print("Ready. Press and hold the hotkey to record.")
    try:
        gui.run()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, exiting...")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="DictaPilot - Press-and-hold dictation"
    )
    parser.add_argument(
        "--export",
        type=str,
        metavar="FILE",
        help="Export all transcriptions to a text file",
    )
    parser.add_argument(
        "--list", action="store_true", help="List recent transcriptions"
    )
    parser.add_argument(
        "--stats", action="store_true", help="Show transcription statistics"
    )
    parser.add_argument(
        "--search", type=str, metavar="QUERY", help="Search transcriptions"
    )
    parser.add_argument(
        "--wayland-deps",
        action="store_true",
        help="Show Wayland dependency installation instructions",
    )
    args = parser.parse_args()

    if args.wayland_deps:
        try:
            from wayland_backend import print_wayland_setup_instructions

            print_wayland_setup_instructions()
        except ImportError:
            print("Wayland backend module not available")
        sys.exit(0)

    if args.export:
        from transcription_store import export_all_to_text

        path = Path(args.export)
        content = export_all_to_text(path, include_metadata=True)
        print(f"Exported to: {path}")
        print(f"Content preview:\n{content[:500]}...")
        sys.exit(0)

    if args.list:
        from transcription_store import get_transcriptions

        entries = get_transcriptions(20)
        print("Recent Transcriptions:")
        print("-" * 60)
        for i, entry in enumerate(entries, 1):
            print(f"{i}. [{entry.timestamp[:19]}] {entry.display_text[:80]}")
            if len(entry.display_text) > 80:
                print(f"   ... ({entry.word_count} words, action: {entry.action})")
        sys.exit(0)

    if args.stats:
        from transcription_store import get_storage_info

        info = get_storage_info()
        print("Transcription Storage Statistics")
        print("-" * 40)
        print(f"Storage location: {info['storage_path']}")
        stats = info["statistics"]
        print(f"Total transcriptions: {stats['total_transcriptions']}")
        print(f"Total words: {stats['total_words']}")
        print(f"Total characters: {stats['total_characters']}")
        print(f"Action breakdown: {stats['action_breakdown']}")
        sys.exit(0)

    if args.search:
        from transcription_store import search_transcriptions

        results = search_transcriptions(args.search)
        print(f"Search results for '{args.search}':")
        print("-" * 60)
        for entry in results:
            print(f"[{entry.timestamp[:19]}] {entry.display_text[:100]}")
        print(f"Found {len(results)} matching transcriptions")
        sys.exit(0)

    main()
