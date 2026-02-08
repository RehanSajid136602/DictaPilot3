"""
DictaPilot app context, per-app profiles, and profile bundle ingestion.

Original by: Rohan Sharvesh
Fork maintained by: Rehan

MIT License
Copyright (c) 2026 Rohan Sharvesh
Copyright (c) 2026 Rehan

Legacy profiles file format (JSON):
{
  "default": {"tone": "polite", "language": "english"},
  "apps": {
    "Slack": {"tone": "casual"},
    "Gmail": {"tone": "formal", "language": "english"}
  }
}

Profile bundle file format (JSON):
{
  "version": 1,
  "default_profile": "default",
  "source_url": "https://example.com/profile/abc",
  "profiles": [
    {
      "id": "default",
      "name": "Default",
      "tone": "polite",
      "language": "english",
      "role": "general assistant",
      "domain": "general",
      "glossary": {"sla": "service level agreement"}
    }
  ]
}
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class DictationContext:
    app_id: Optional[str]
    tone: str
    language: str
    profile_id: str = "default"
    profile_name: str = "Default"
    role: str = ""
    domain: str = ""
    glossary: Dict[str, str] = field(default_factory=dict)
    profile_source: Optional[str] = None


DEFAULT_TONE = (os.getenv("DEFAULT_TONE") or "polite").strip().lower()
DEFAULT_LANGUAGE = (os.getenv("DEFAULT_LANGUAGE") or "english").strip().lower()
DEFAULT_PROFILE_ID = (os.getenv("ACTIVE_PROFILE") or "default").strip().lower() or "default"


def _profiles_path() -> Path:
    system = platform.system()
    if system == "Windows":
        base = os.environ.get("APPDATA") or ""
        return Path(base) / "DictaPilot" / "profiles.json"
    return Path.home() / ".config" / "dictapilot" / "profiles.json"


def _profile_bundle_path() -> Path:
    explicit = (os.getenv("PROFILE_BUNDLE_PATH") or "").strip()
    if explicit:
        return Path(os.path.expanduser(explicit))
    return _profiles_path().parent / "profile_bundle.json"


_PROFILE_CACHE = {"path": None, "mtime": None, "data": {}}
_PROFILE_BUNDLE_CACHE = {"path": None, "mtime": None, "data": {}}


def _load_cached_json(path: Path, cache: dict) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    path_str = str(path)
    try:
        mtime = path.stat().st_mtime
    except FileNotFoundError:
        cache.update({"path": path_str, "mtime": None, "data": {}})
        return {}

    if cache.get("path") == path_str and cache.get("mtime") == mtime:
        data = cache.get("data", {})
        return data if isinstance(data, dict) else {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}

    if not isinstance(data, dict):
        data = {}
    cache.update({"path": path_str, "mtime": mtime, "data": data})
    return data


def _load_profiles() -> dict:
    return _load_cached_json(_profiles_path(), _PROFILE_CACHE)


def _load_profile_bundle() -> dict:
    return _load_cached_json(_profile_bundle_path(), _PROFILE_BUNDLE_CACHE)


def _save_profiles(data: dict) -> None:
    path = _profiles_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    _PROFILE_CACHE.update({"path": str(path), "mtime": path.stat().st_mtime, "data": data})


def _save_profile_bundle(data: dict, path: Optional[Path] = None) -> Path:
    target = path or _profile_bundle_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    _PROFILE_BUNDLE_CACHE.update({"path": str(target), "mtime": target.stat().st_mtime, "data": data})
    return target


def _normalize_glossary(raw: Any) -> Dict[str, str]:
    if not isinstance(raw, dict):
        return {}
    normalized: Dict[str, str] = {}
    for key, value in raw.items():
        clean_key = str(key).strip()
        clean_value = str(value).strip()
        if clean_key and clean_value:
            normalized[clean_key] = clean_value
    return normalized


def _coerce_profile_entry(raw: Any, fallback_id: str) -> Dict[str, Any]:
    if not isinstance(raw, dict):
        raw = {}
    profile_id = (str(raw.get("id") or fallback_id).strip().lower() or DEFAULT_PROFILE_ID)
    name = str(raw.get("name") or profile_id).strip() or profile_id
    return {
        "id": profile_id,
        "name": name,
        "tone": str(raw.get("tone") or "").strip().lower(),
        "language": str(raw.get("language") or "").strip().lower(),
        "role": str(raw.get("role") or "").strip(),
        "domain": str(raw.get("domain") or "").strip(),
        "glossary": _normalize_glossary(raw.get("glossary")),
    }


def _profile_mapping(bundle: dict) -> Dict[str, Dict[str, Any]]:
    profiles = bundle.get("profiles")
    mapping: Dict[str, Dict[str, Any]] = {}

    if isinstance(profiles, list):
        for item in profiles:
            if not isinstance(item, dict):
                continue
            profile = _coerce_profile_entry(item, str(item.get("id") or ""))
            if profile["id"]:
                mapping[profile["id"]] = profile
        return mapping

    if isinstance(profiles, dict):
        for key, item in profiles.items():
            profile = _coerce_profile_entry(item, str(key))
            if profile["id"]:
                mapping[profile["id"]] = profile
    return mapping


def list_available_profiles() -> List[Dict[str, Any]]:
    bundle = _load_profile_bundle()
    mapping = _profile_mapping(bundle)
    return sorted(mapping.values(), key=lambda item: item["id"])


def validate_profile_bundle(bundle: dict) -> Tuple[bool, str]:
    if not isinstance(bundle, dict):
        return False, "Profile bundle must be a JSON object"
    mapping = _profile_mapping(bundle)
    if not mapping:
        return False, "Bundle must contain at least one profile in 'profiles'"
    return True, ""


def import_profile_bundle(bundle: dict, path: Optional[Path] = None) -> Path:
    ok, reason = validate_profile_bundle(bundle)
    if not ok:
        raise ValueError(reason)
    return _save_profile_bundle(bundle, path=path)


def _resolve_active_profile(bundle: dict) -> Tuple[str, Optional[Dict[str, Any]]]:
    mapping = _profile_mapping(bundle)
    if not mapping:
        return DEFAULT_PROFILE_ID, None

    env_profile = (os.getenv("ACTIVE_PROFILE") or "").strip().lower()
    configured_default = (str(bundle.get("default_profile") or "").strip().lower())
    selected = env_profile or configured_default or DEFAULT_PROFILE_ID

    if selected in mapping:
        return selected, mapping[selected]

    first_key = next(iter(mapping.keys()))
    return first_key, mapping[first_key]


def update_profile(app_id: Optional[str], tone: Optional[str] = None, language: Optional[str] = None) -> None:
    data = _load_profiles()
    if app_id:
        apps = data.setdefault("apps", {})
        profile = apps.setdefault(app_id, {})
    else:
        profile = data.setdefault("default", {})
    if tone:
        profile["tone"] = tone
    if language:
        profile["language"] = language
    _save_profiles(data)


def get_context() -> DictationContext:
    app_id = _active_app_id()
    data = _load_profiles()
    bundle = _load_profile_bundle()
    default = data.get("default") or {}
    tone = (default.get("tone") or DEFAULT_TONE).strip().lower()
    language = (default.get("language") or DEFAULT_LANGUAGE).strip().lower()
    profile_id, active_profile = _resolve_active_profile(bundle)
    profile_name = "Default"
    role = ""
    domain = ""
    glossary: Dict[str, str] = {}
    profile_source = str(bundle.get("source_url") or bundle.get("source") or "").strip() or None

    if active_profile:
        tone = (active_profile.get("tone") or tone).strip().lower()
        language = (active_profile.get("language") or language).strip().lower()
        profile_name = str(active_profile.get("name") or profile_id).strip() or profile_id
        role = str(active_profile.get("role") or "").strip()
        domain = str(active_profile.get("domain") or "").strip()
        glossary = dict(active_profile.get("glossary") or {})

    if app_id:
        app_cfg = _match_profile(app_id, data.get("apps") or {})
        if app_cfg:
            tone = (app_cfg.get("tone") or tone).strip().lower()
            language = (app_cfg.get("language") or language).strip().lower()

    return DictationContext(
        app_id=app_id,
        tone=tone,
        language=language,
        profile_id=profile_id,
        profile_name=profile_name,
        role=role,
        domain=domain,
        glossary=glossary,
        profile_source=profile_source,
    )


def _match_profile(app_id: str, apps: dict) -> Optional[dict]:
    if not app_id:
        return None
    lower = app_id.lower()
    for key, profile in apps.items():
        if key and key.lower() in lower:
            return profile
    return None


def _active_app_id() -> Optional[str]:
    override = os.getenv("ACTIVE_APP")
    if override:
        return override.strip()

    system = platform.system()
    if system == "Windows":
        return _active_app_windows()
    if system == "Darwin":
        return _active_app_macos()
    if system == "Linux":
        return _active_app_linux()
    return None


def _active_app_macos() -> Optional[str]:
    script = 'tell application "System Events" to get name of first application process whose frontmost is true'
    try:
        result = subprocess.check_output(["osascript", "-e", script], timeout=0.5)
        return result.decode("utf-8", "ignore").strip() or None
    except Exception:
        return None


def _active_app_linux() -> Optional[str]:
    if shutil.which("xdotool"):
        try:
            result = subprocess.check_output(
                ["xdotool", "getactivewindow", "getwindowname"],
                timeout=0.5,
            )
            return result.decode("utf-8", "ignore").strip() or None
        except Exception:
            return None
    return None


def _active_app_windows() -> Optional[str]:
    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        psapi = ctypes.windll.psapi

        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return None

        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        process = kernel32.OpenProcess(0x0410, False, pid.value)
        if not process:
            return None

        buf = (wintypes.WCHAR * 260)()
        psapi.GetModuleBaseNameW(process, None, buf, 260)
        kernel32.CloseHandle(process)
        name = buf.value.strip()
        return name or None
    except Exception:
        return None
