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
from paste_utils import paste_text
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

try:
    from PySide6.QtCore import QPoint, QRectF, Qt, QTimer
    from PySide6.QtGui import QColor, QGuiApplication, QImage, QLinearGradient, QPainter, QPainterPath, QPixmap
    from PySide6.QtWidgets import QApplication, QWidget

    PYSIDE6_AVAILABLE = True
except Exception:
    QPoint = QRectF = Qt = QTimer = None
    QColor = QGuiApplication = QImage = QLinearGradient = QPainter = QPainterPath = QPixmap = None
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
GROQ_WHISPER_MODEL = os.getenv("GROQ_WHISPER_MODEL", "whisper-large-v3-turbo").strip() or "whisper-large-v3-turbo"
GROQ_CHAT_MODEL = os.getenv("GROQ_CHAT_MODEL", "openai/gpt-oss-120b").strip() or "openai/gpt-oss-120b"


def _env_flag(name: str, default: str = "1") -> bool:
    value = os.getenv(name, default).strip().lower()
    return value not in {"0", "false", "no", "off"}


SMART_EDIT = _env_flag("SMART_EDIT", "1")
SMART_MODE = os.getenv("SMART_MODE", "llm").strip().lower()
PASTE_MODE = os.getenv("PASTE_MODE", "delta").strip().lower()
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


SR = _env_int("SAMPLE_RATE", 16000)
CHANNELS = _env_int("CHANNELS", 1)
TRIM_SILENCE = _env_flag("TRIM_SILENCE", "1")
SILENCE_THRESHOLD = float(os.getenv("SILENCE_THRESHOLD", "0.02"))


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
    if key_name.startswith("f") and key_name[1:].isdigit() and hasattr(pynput_keyboard.Key, key_name):
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
        release_hook = keyboard.on_release_key(self.hotkey, lambda _: self._handle_release())

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
                    return getattr(key_obj, "char", None) and key_obj.char.lower() == token.char.lower()
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
            # Linux avoids keyboard backend by default due /dev/input instability on many systems.
            if sys.platform.startswith("linux"):
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
                    with sd.InputStream(samplerate=candidate, channels=self.channels, callback=self._callback):
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
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
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
        self._manager._set_close_button_hover(False)
        super().leaveEvent(event)

    def paintEvent(self, event):
        self._manager._paint_window(self)


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
        self._bar_count = 5
        self._amplitudes = [0.0] * self._bar_count
        self._current_heights = [0.0] * self._bar_count
        self._level_env = 0.0
        self._level_peak = 0.12
        self._logo_image = None
        self._logo_mtime = None
        self._last_logo_check = 0.0
        self._width = 85
        self._height = 72
        self._platform_name = platform.system()
        self._show_close_button = (os.getenv("FLOATING_CLOSE_BUTTON", "1").strip().lower() not in {"0", "false", "no", "off"})
        self._close_button_hover = False
        self._close_button_pressed = False
        self._on_close_requested = on_close_requested

        self._window = _QtFloatingWindow(self)
        self._setup_window()
        self._load_logo_image()

        self._timer = QTimer()
        self._timer.timeout.connect(self._poll)
        self._timer.start(16)

    def _logo_path(self) -> Path:
        return Path(__file__).resolve().parent / "public" / "asset" / "logo.png"

    def _setup_window(self):
        self._window.setFixedSize(self._width, self._height)
        screen = QGuiApplication.primaryScreen()
        if screen is not None:
            geometry = screen.availableGeometry()
            x = geometry.x() + (geometry.width() - self._width) // 2
            y = geometry.y() + 26
            self._window.move(x, y)
        self._window.show()

    def set_close_callback(self, callback):
        self._on_close_requested = callback

    def _close_button_rect(self) -> QRectF:
        if not self._show_close_button:
            return QRectF(0.0, 0.0, 0.0, 0.0)
        size = 16.0
        margin_x = 8.0
        margin_y = 6.0
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

                rgba = np.ascontiguousarray(np.array(logo.convert("RGBA"), dtype=np.uint8))
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
                elif cmd == "clipboard":
                    try:
                        self._app.clipboard().setText(str(arg))
                    except Exception:
                        pass
        except queue.Empty:
            pass

        try:
            while True:
                amp = float(self._audio_queue.get_nowait())
                amp = max(0.0, min(1.0, amp))
                self._amplitudes.pop(0)
                self._amplitudes.append(amp)
                self._level_env = (self._level_env * 0.72) + (amp * 0.28)
        except queue.Empty:
            pass
        except Exception:
            pass

        decay = 0.24
        rise = 0.82
        self._level_peak = max(self._level_peak * 0.985, self._level_env, 0.10)
        scaled_level = min(1.0, self._level_env / max(0.12, self._level_peak))
        expressive_level = scaled_level ** 0.55
        half = max(1, (self._bar_count - 1) / 2)

        for i in range(self._bar_count):
            center_bias = 1.2 - (abs(i - half) / half) * 0.4
            if self._mode == "record":
                amp_idx = min(i, len(self._amplitudes) - 1)
                local = min(1.0, self._amplitudes[amp_idx] / max(0.12, self._level_peak))
                local_drive = local ** 0.50
                rhythm = 0.86 + 0.22 * np.sin(time.time() * 11.0 + i * 0.9)
                drive = (0.62 * local_drive) + (0.38 * expressive_level)
                target = min(1.0, 0.05 + drive * center_bias * rhythm)
            elif self._mode == "processing":
                target = 0.18 + (np.sin(time.time() * 4.5 + i * 0.45) + 1.0) * 0.12
            elif self._mode == "done":
                target = 0.16 + (np.sin(time.time() * 3.2 + i * 0.45) + 1.0) * 0.09
            elif self._mode == "idle":
                target = 0.10 + (np.sin(time.time() * 2.4 + i * 0.5) + 1.0) * 0.06
            else:
                target = 0.10

            diff = target - self._current_heights[i]
            if diff > 0:
                self._current_heights[i] += diff * rise
            else:
                self._current_heights[i] += diff * decay

        self._window.update()

    def _draw_rounded_rect(self, painter, x, y, w, h, color, r):
        rect = QRectF(float(x), float(y), float(w), float(h))
        path = QPainterPath()
        radius = max(1.0, min(float(r), rect.width() / 2.0, rect.height() / 2.0))
        path.addRoundedRect(rect, radius, radius)
        painter.fillPath(path, QColor(color))

    def _draw_capsule(self, painter, cx, cy, width, height):
        width = max(2.0, float(width))
        height = max(width + 1.0, float(height))
        rect = QRectF(cx - width / 2.0, cy - height / 2.0, width, height)
        painter.drawRoundedRect(rect, width / 2.0, width / 2.0)

    def _draw_close_button(self, painter):
        if not self._show_close_button:
            return

        rect = self._close_button_rect()
        halo = QColor(255, 255, 255, 44 if (self._close_button_hover or self._close_button_pressed) else 24)
        painter.setPen(Qt.NoPen)
        painter.setBrush(halo)
        painter.drawRoundedRect(rect.adjusted(-1.2, -1.2, 1.2, 1.2), 5.2, 5.2)

        if self._close_button_pressed:
            fill = QColor("#991b1b")
        elif self._close_button_hover:
            fill = QColor("#ef4444")
        else:
            fill = QColor("#dc2626")

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

    def _paint_window(self, window):
        painter = QPainter(window)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)

        w = float(window.width())
        h = float(window.height())
        mid_y = h / 2.0

        self._draw_rounded_rect(painter, 0, 0, w, h, "#0b1324", 24)
        self._draw_rounded_rect(painter, 1, 1, w - 2, h - 2, "#0f1b33", 23)
        self._draw_close_button(painter)

        # Logo removed - minimal GUI with audio bars only
        start_x = 12.0

        if self._mode == "record":
            top_color = QColor("#f8fafc")
            bottom_color = QColor("#94a3b8")
            glow_color = QColor(241, 245, 249, 88)
        elif self._mode == "processing":
            top_color = QColor("#e2e8f0")
            bottom_color = QColor("#64748b")
            glow_color = QColor(226, 232, 240, 64)
        elif self._mode == "done":
            top_color = QColor("#ffffff")
            bottom_color = QColor("#a3b3c8")
            glow_color = QColor(248, 250, 252, 76)
        else:
            top_color = QColor("#cbd5e1")
            bottom_color = QColor("#475569")
            glow_color = QColor(203, 213, 225, 56)

        bar_w = 5.0
        gap = 4.0
        max_h = h - 16.0
        right_pad = 32.0 if self._show_close_button else 8.0
        available_w = max(0.0, w - start_x - right_pad)
        stride = bar_w + gap
        bars_to_draw = min(self._bar_count, max(1, int(available_w // stride)))

        for i in range(bars_to_draw):
            idx = int(i * self._bar_count / bars_to_draw)
            mirror_idx = self._bar_count - 1 - idx
            raw_level = (self._current_heights[idx] * 0.7) + (self._current_heights[mirror_idx] * 0.3)
            height_factor = max(0.0, min(1.0, raw_level))
            center_dist = 0.0 if bars_to_draw <= 1 else abs((i / (bars_to_draw - 1)) - 0.5) * 2.0
            arch = 1.0 - (center_dist ** 1.35) * 0.35
            hv = max(5.0, height_factor * max_h * arch)
            x = start_x + i * stride + bar_w / 2.0
            edge_weight = 1.0 - center_dist

            local_glow = QColor(
                glow_color.red(),
                glow_color.green(),
                glow_color.blue(),
                int(glow_color.alpha() * (0.62 + 0.38 * edge_weight)),
            )
            painter.setBrush(local_glow)
            self._draw_capsule(painter, x, mid_y, bar_w + 4.8, hv + 6.2)

            grad = QLinearGradient(x, mid_y - hv / 2.0, x, mid_y + hv / 2.0)
            grad.setColorAt(0.0, top_color)
            grad.setColorAt(0.58, QColor(176, 188, 206))
            grad.setColorAt(1.0, bottom_color)
            painter.setBrush(grad)
            self._draw_capsule(painter, x, mid_y, bar_w, hv)

            painter.setBrush(QColor(255, 255, 255, 56 if self._mode == "record" else 36))
            self._draw_capsule(
                painter,
                x + 0.3,
                mid_y - hv * 0.18,
                max(1.8, bar_w - 2.7),
                max(4.0, hv * 0.30),
            )

        painter.end()

    def show(self, text: str):
        self._queue.put(("show", text))

    def update(self, text: str):
        self._queue.put(("update", text))

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
        print(f"Audio: {SR}Hz, channels={CHANNELS}, trim_silence={'on' if TRIM_SILENCE else 'off'}")
        print(f"Instant refine: {'on' if INSTANT_REFINE else 'off'}")
        if SMART_EDIT and RESET_TRANSCRIPT_EACH_RECORDING:
            print("Transcript reset mode: per recording")
        elif SMART_EDIT:
            print("Transcript reset mode: session (keeps previous recordings)")

        try:
            storage_info = get_storage_info()
            print(f"Transcription storage: {storage_info['storage_path']}")
            print(f"Total transcriptions: {storage_info['statistics']['total_transcriptions']}")
        except Exception:
            pass
        print("")

    print_banner(HOTKEY)
    recorder = Recorder()
    processing_event = threading.Event()
    shutdown_event = threading.Event()
    hotkey_manager = None

    try:
        gui = GUIManager()
    except Exception as ex:
        print(f"Failed to initialize GUI: {ex}", file=sys.stderr)
        return
    transcript_state = TranscriptState()

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
        # start only if not already recording
        if shutdown_event.is_set():
            return
        if recorder._running.is_set():
            return
        # avoid overlapping transcription workers that can mix state across recordings
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
        # wait for the input stream to open or error
        started = recorder._started_event.wait(timeout=1.0)
        if not started:
            # if there was an error, show it; otherwise show a timeout message
            msg = recorder.last_error or "Timeout opening audio input device"
            gui.update(f"Recording error: {msg}")
            time.sleep(1.5)
            gui.close()
            return

    def on_release(e):
        # ignore if we never started recording
        if shutdown_event.is_set():
            return
        if not recorder._running.is_set():
            return
        print("Stop recording")
        try:
            # save to temp file
            fd, path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            gui.update("Stopping... saving audio")
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

                # Check mode - if in agent mode, format differently
                mode = os.getenv("MODE", "dictation").strip().lower()

                # Determine final output after all processing
                if mode == "agent":
                    # Format for agent consumption
                    from agent_formatter import AgentFormatter
                    formatter = AgentFormatter()
                    refined_out = formatter.format_for_agent(fast_out, mode="structured")

                    # Copy to clipboard as formatted agent prompt
                    try:
                        import pyperclip
                        pyperclip.copy(refined_out)
                    except Exception:
                        gui.set_clipboard_text(refined_out)

                    # Optionally post to webhook if configured
                    webhook_url = os.getenv("AGENT_WEBHOOK_URL")
                    if webhook_url:
                        import threading
                        def send_webhook():
                            try:
                                import urllib.request
                                import urllib.parse
                                import json

                                data = {
                                    'prompt': refined_out,
                                    'timestamp': time.time(),
                                    'source': 'dictapilot'
                                }

                                req = urllib.request.Request(
                                    webhook_url,
                                    data=json.dumps(data).encode('utf-8'),
                                    headers={'Content-Type': 'application/json'}
                                )

                                with urllib.request.urlopen(req, timeout=10) as response:
                                    if response.status == 200:
                                        print("Successfully sent to agent webhook")
                                    else:
                                        print(f"Webhook responded with status {response.status}")
                            except Exception as e:
                                print(f"Failed to send to webhook: {e}", file=sys.stderr)

                        # Send webhook in background thread
                        threading.Thread(target=send_webhook, daemon=True).start()

                    # For agent mode, use the formatted output
                    refined_action = "append"
                else:
                    # Original dictation mode behavior
                    refined_out = fast_out
                    refined_action = fast_action
                    if SMART_EDIT and INSTANT_REFINE and DICTATION_MODE != "speed" and not is_transform_command(text):
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
                                    sync_state_to_output(transcript_state, fast_out, refined_out)

                # Only paste the final refined text according to the paste policy
                if PASTE_POLICY == "final_only":
                    # For "final_only" policy, only paste the final refined output
                    final_output = refined_out

                    # Only paste if the action is not ignore/clear and output is not empty
                    should_paste = (refined_action != "ignore" and
                                  refined_action != "clear" and
                                  final_output.strip())

                    if should_paste:
                        # copy to clipboard (prefer pyperclip, fallback to GUI clipboard)
                        try:
                            import pyperclip
                            pyperclip.copy(final_output)
                        except Exception:
                            gui.set_clipboard_text(final_output)

                        # Keep floating window visible to avoid hide/show flicker glitch.
                        paste_error = None
                        try:
                            selected_paste_mode = PASTE_MODE if SMART_EDIT else "delta"
                            paste_text(prev_out, final_output, selected_paste_mode, backend=PASTE_BACKEND)
                        except Exception as ex:
                            paste_error = ex
                            try:
                                # fallback: force full replace for better compatibility
                                paste_text("", final_output, "full", backend=PASTE_BACKEND)
                                paste_error = None
                            except Exception as ex2:
                                paste_error = RuntimeError(f"{ex}; fallback full paste failed: {ex2}")

                        if paste_error is not None:
                            print(f"Paste error: {paste_error}", file=sys.stderr)
                            try:
                                gui.update("Paste failed. Try normal user mode and PASTE_BACKEND=x11/xdotool.")
                            except Exception:
                                pass
                    else:
                        # For ignore/clear actions, still update the GUI but don't paste to external apps
                        print(f"Action '{refined_action}' detected - skipping external paste")
                        try:
                            gui.show(("done", "Command applied"))
                        except Exception:
                            pass
                elif PASTE_POLICY == "live_preview":
                    # Original behavior for backward compatibility
                    # copy to clipboard (prefer pyperclip, fallback to GUI clipboard)
                    try:
                        import pyperclip
                        pyperclip.copy(fast_out)
                    except Exception:
                        gui.set_clipboard_text(fast_out)

                    # Keep floating window visible to avoid hide/show flicker glitch.
                    paste_error = None
                    try:
                        selected_paste_mode = PASTE_MODE if SMART_EDIT else "delta"
                        paste_text(prev_out, fast_out, selected_paste_mode, backend=PASTE_BACKEND)
                    except Exception as ex:
                        paste_error = ex
                        try:
                            # fallback: force full replace for better compatibility
                            paste_text("", fast_out, "full", backend=PASTE_BACKEND)
                            paste_error = None
                        except Exception as ex2:
                            paste_error = RuntimeError(f"{ex}; fallback full paste failed: {ex2}")

                    if paste_error is not None:
                        print(f"Paste error: {paste_error}", file=sys.stderr)
                        try:
                            gui.update("Paste failed. Try normal user mode and PASTE_BACKEND=x11/xdotool.")
                        except Exception:
                            pass

                # Save transcription to storage (final output).
                # Storage failures should not break the dictation pipeline.
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
                        print(f"Warning: failed to save transcription: {storage_ex}", file=sys.stderr)

                # show done text briefly after paste
                try:
                    output_for_popup = refined_out if refined_out else "(empty transcript)"
                    snippet = output_for_popup if len(output_for_popup) <= 300 else output_for_popup[:300] + "..."
                    gui.show(("done", snippet))
                except Exception:
                    pass

                # keep the done window visible briefly then return to idle
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

    # register hotkey handlers
    hotkey_manager = HotkeyManager(HOTKEY, on_press, on_release, backend=HOTKEY_BACKEND)
    try:
        active_backend = hotkey_manager.start()
        print(f"Hotkey listener active: {active_backend}")
    except Exception as ex:
        print(f"Failed to register hotkey '{HOTKEY}': {ex}", file=sys.stderr)
        return

    print("Ready. Press and hold the hotkey to record.")
    try:
        gui.run()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, exiting...")
        _request_shutdown()
    finally:
        _request_shutdown()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="DictaPilot - Press-and-hold dictation")
    parser.add_argument("--tray", action="store_true", help="Run with system tray")
    parser.add_argument("--export", type=str, metavar="FILE", help="Export all transcriptions to a text file")
    parser.add_argument("--list", action="store_true", help="List recent transcriptions")
    parser.add_argument("--stats", action="store_true", help="Show transcription statistics")
    parser.add_argument("--search", type=str, metavar="QUERY", help="Search transcriptions")
    args = parser.parse_args()

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
        stats = info['statistics']
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
