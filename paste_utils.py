"""
DictaPilot Paste Utilities (Windows Only)
Text injection for pasting transcribed text on Windows.

Original by: Rohan Sharvesh
Fork maintained by: Rehan
"""

import os
import time
import threading
from typing import Tuple

def longest_common_prefix(a: str, b: str) -> int:
    limit = min(len(a), len(b))
    idx = 0
    while idx < limit and a[idx] == b[idx]:
        idx += 1
    return idx

def compute_delta(prev_text: str, new_text: str) -> Tuple[int, str]:
    lcp = longest_common_prefix(prev_text or "", new_text or "")
    to_delete = len(prev_text or "") - lcp
    to_insert = (new_text or "")[lcp:]
    return to_delete, to_insert

def _keyboard_module():
    import keyboard
    return keyboard

def _pynput_controller():
    from pynput.keyboard import Controller, Key, KeyCode
    return Controller(), Key, KeyCode

def _pynput_key_from_name(name: str):
    key_name = (name or "").strip().lower()
    _, Key, KeyCode = _pynput_controller()
    mapping = {
        "ctrl": Key.ctrl,
        "control": Key.ctrl,
        "alt": Key.alt,
        "shift": Key.shift,
        "tab": Key.tab,
        "enter": Key.enter,
        "return": Key.enter,
        "esc": Key.esc,
        "escape": Key.esc,
        "space": Key.space,
        "backspace": Key.backspace,
        "delete": Key.delete,
    }
    if key_name in mapping:
        return mapping[key_name]
    if key_name.startswith("f") and key_name[1:].isdigit() and hasattr(Key, key_name):
        return getattr(Key, key_name)
    if len(key_name) == 1:
        return KeyCode.from_char(key_name)
    return None

def _pynput_key(combo: str) -> bool:
    try:
        controller, _, _ = _pynput_controller()
        keys = [_pynput_key_from_name(part) for part in combo.split("+")]
        if any(key is None for key in keys):
            return False
        for key in keys:
            controller.press(key)
        for key in reversed(keys):
            controller.release(key)
        return True
    except Exception:
        return False

def _pynput_backspace(count: int) -> bool:
    if count <= 0:
        return True
    try:
        controller, Key, _ = _pynput_controller()
        for _ in range(count):
            controller.press(Key.backspace)
            controller.release(Key.backspace)
        return True
    except Exception:
        return False

def _pynput_type(text: str) -> bool:
    if not text:
        return True
    try:
        controller, _, _ = _pynput_controller()
        controller.type(text)
        return True
    except Exception:
        return False

def _copy_to_clipboard(text: str) -> bool:
    if not text:
        return True
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception:
        return False

def _send_hotkey(combo: str, backend: str = "auto") -> None:
    # Try keyboard module first, then fallback to pynput
    try:
        keyboard = _keyboard_module()
        keyboard.press_and_release(combo)
        return
    except Exception:
        pass

    if _pynput_key(combo):
        return

    raise RuntimeError(f"Failed to send hotkey '{combo}'. Check permissions.")

def _send_backspaces(count: int, backend: str = "auto") -> None:
    if count <= 0:
        return
    
    # Try keyboard module first
    try:
        keyboard = _keyboard_module()
        for _ in range(count):
            keyboard.press_and_release("backspace")
        return
    except Exception:
        pass

    if _pynput_backspace(count):
        return

    raise RuntimeError("Failed to send backspace events. Check permissions.")

def _type_text(text: str, backend: str = "auto") -> None:
    if not text:
        return

    # Try keyboard module first
    try:
        keyboard = _keyboard_module()
        keyboard.write(text)
        return
    except Exception:
        pass

    if _pynput_type(text):
        return

    raise RuntimeError("Failed to type text. Check permissions.")

def _paste_insert(text: str, backend: str = "auto") -> None:
    if not text:
        return
    if _copy_to_clipboard(text):
        _send_hotkey("ctrl+v", backend=backend)
        return
    _type_text(text, backend=backend)

def paste_delta(prev_text: str, new_text: str, backend: str = "auto") -> None:
    to_delete, to_insert = compute_delta(prev_text, new_text)
    _send_backspaces(max(0, to_delete), backend=backend)
    _paste_insert(to_insert, backend=backend)

def paste_full_replace(new_text: str, backend: str = "auto") -> None:
    _send_hotkey("ctrl+a", backend=backend)
    _paste_insert(new_text, backend=backend)

def _detect_cli_environment() -> bool:
    cli_auto_detect = os.getenv("CLI_AUTO_DETECT", "1").strip()
    if cli_auto_detect.lower() in ("0", "false", "no", "off"):
        return False

    try:
        from app_context import is_cli_application, get_context
        context = get_context()
        if context and context.app_id:
            return is_cli_application(context.app_id)
    except Exception:
        pass

    active_app = os.getenv("ACTIVE_APP", "").lower()
    if active_app:
        cli_keywords = ["terminal", "cmd", "powershell", "pwsh", "console"]
        return any(keyword in active_app for keyword in cli_keywords)
    return False

def _sanitize_for_cli(text: str) -> str:
    if not text:
        return text
    newline_keyword = os.getenv("CLI_NEWLINE_KEYWORD", "new line").lower()
    if newline_keyword in text.lower():
        return text
    sanitized = text.replace("\n", " ").replace("\r", " ")
    import re
    sanitized = re.sub(r"\s+", " ", sanitized)
    return sanitized.strip()

def _sanitize_text_for_environment(text: str, preserve_newlines: bool = False) -> str:
    if not text or preserve_newlines:
        return text
    cli_strip_newlines = os.getenv("CLI_STRIP_NEWLINES", "1").strip()
    if cli_strip_newlines.lower() in ("0", "false", "no", "off"):
        return text
    if _detect_cli_environment():
        return _sanitize_for_cli(text)
    return text

def paste_text(
    prev_text: str,
    new_text: str,
    mode: str = "delta",
    backend: str = "auto",
    preserve_newlines: bool = False,
) -> None:
    sanitized_text = _sanitize_text_for_environment(
        new_text or "", preserve_newlines=preserve_newlines
    )
    selected_mode = (mode or "delta").strip().lower()
    if selected_mode == "full":
        paste_full_replace(sanitized_text, backend=backend)
        return
    paste_delta(prev_text or "", sanitized_text, backend=backend)

class PasteWorker:
    def __init__(self):
        self.task_queue = []
        self.worker_thread = None
        self.running = False

    def start_worker(self):
        if self.running:
            return
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    def stop_worker(self):
        self.running = False

    def _worker_loop(self):
        while self.running:
            if self.task_queue:
                task = self.task_queue.pop(0)
                prev_text, new_text, mode, backend, callback = task
                try:
                    paste_text(prev_text, new_text, mode, backend)
                    if callback:
                        callback(success=True)
                except Exception as e:
                    if callback:
                        callback(success=False, error=e)
            else:
                time.sleep(0.01)

    def paste_async(
        self,
        prev_text: str,
        new_text: str,
        mode: str = "delta",
        backend: str = "auto",
        callback=None,
    ):
        if not self.running:
            self.start_worker()
        self.task_queue.append((prev_text, new_text, mode, backend, callback))

_global_paste_worker = PasteWorker()

def paste_text_async(
    prev_text: str,
    new_text: str,
    mode: str = "delta",
    backend: str = "auto",
    callback=None,
) -> None:
    _global_paste_worker.paste_async(prev_text, new_text, mode, backend, callback)
