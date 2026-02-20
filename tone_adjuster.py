"""
DictaPilot Context Tone Adjustment Module
Handles automatic tone adjustment based on active application context.

MIT License
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

import json
import os
import platform
import re
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


def get_tone_config_path() -> Path:
    """Get platform-specific tone config path"""
    system = platform.system()
    
    if system == "Windows":
        data_dir = Path(os.environ.get("APPDATA", ""))
        return data_dir / "DictaPilot" / "tone_config.json"
    else:
        data_dir = Path(os.path.expanduser("~/.local/share"))
        return data_dir / "dictapilot" / "tone_config.json"


def get_tone_config_dir() -> Path:
    """Create and return tone config directory"""
    config_path = get_tone_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    return config_path.parent


class AppType(Enum):
    """Application types for context detection"""
    EMAIL = "email"
    CHAT = "chat"
    CODE = "code"
    DOCUMENT = "document"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"
    BROWSER = "browser"
    TERMINAL = "terminal"
    UNKNOWN = "unknown"


class ToneType(Enum):
    """Tone types for text transformation"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    TECHNICAL = "technical"
    NEUTRAL = "neutral"
    CUSTOM = "custom"


# Application classification patterns
APP_PATTERNS: Dict[AppType, List[str]] = {
    AppType.EMAIL: [
        r"thunderbird", r"outlook", r"mail", r"email", r"gmail", 
        r"evolution", r"kmail", r"mailvelope"
    ],
    AppType.CHAT: [
        r"slack", r"discord", r"teams", r"telegram", r"signal",
        r"whatsapp", r"messenger", r"chat", r"signal", r"matrix"
    ],
    AppType.CODE: [
        r"code", r"vscode", r"vscodium", r"sublime", r"atom",
        r"pycharm", r"intellij", r"vim", r"emacs", r"jetbrains",
        r"rider", r"android studio", r"xcode", r"notepad\+\+",
        r"terminal", r"gnome-terminal", r"konsole", r"iterm"
    ],
    AppType.DOCUMENT: [
        r"libreoffice", r"openoffice", r"word", r"pages",
        r"google docs", r"notion", r"obsidian", r"roam"
    ],
    AppType.SPREADSHEET: [
        r"excel", r"sheets", r"calc", r"numbers", r"spreadsheet"
    ],
    AppType.PRESENTATION: [
        r"powerpoint", r"keynote", r"impress", r"slides", r"presentation"
    ],
    AppType.BROWSER: [
        r"firefox", r"chrome", r"chromium", r"brave", r"edge",
        r"safari", r"opera", r"browser", r"epiphany"
    ],
    AppType.TERMINAL: [
        r"terminal", r"konsole", r"gnome-terminal", r"xterm",
        r"iterm", r"powershell", r"cmd", r"alacritty"
    ]
}

# Default tone profiles
TONE_PROFILES: Dict[ToneType, Dict[str, Any]] = {
    ToneType.PROFESSIONAL: {
        "name": "Professional",
        "description": "Formal language suitable for business communication",
        "replacements": {
            r"\bhey\b": "Hello",
            r"\bhi\b": "Hello",
            r"\byeah\b": "yes",
            r"\byep\b": "yes",
            r"\bnope\b": "no",
            r"\bgonna\b": "going to",
            r"\bwanna\b": "want to",
            r"\bgotta\b": "got to",
            r"\bkinda\b": "kind of",
            r"\bsorta\b": "sort of",
            r"\bdunno\b": "do not know",
            r"\bgotta\b": "have to",
            r"\blotta\b": "lot of",
            r"\bwanna\b": "want to"
        },
        "capitalize_sentences": True,
        "add_punctuation": True
    },
    ToneType.CASUAL: {
        "name": "Casual",
        "description": "Relaxed language for informal communication",
        "replacements": {},
        "capitalize_sentences": False,
        "add_punctuation": False
    },
    ToneType.TECHNICAL: {
        "name": "Technical",
        "description": "Precise language for technical documentation",
        "replacements": {},
        "preserve_code": True,
        "preserve_indentation": True,
        "format_code_blocks": True
    },
    ToneType.NEUTRAL: {
        "name": "Neutral",
        "description": "No transformation applied",
        "replacements": {},
        "capitalize_sentences": True,
        "add_punctuation": True
    }
}


@dataclass
class ToneProfile:
    """Tone transformation profile"""
    name: str
    description: str
    replacements: Dict[str, str] = field(default_factory=dict)
    capitalize_sentences: bool = True
    add_punctuation: bool = True
    preserve_code: bool = False
    preserve_indentation: bool = False
    format_code_blocks: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToneProfile":
        return cls(**data)


class AppContextDetector:
    """Detects application type from window title/app name"""
    
    def __init__(self):
        self.custom_mappings: Dict[str, AppType] = {}
        self._load_custom_mappings()
    
    def _load_custom_mappings(self):
        """Load custom app mappings from config"""
        config_path = get_tone_config_path()
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    mappings = data.get('app_mappings', {})
                    self.custom_mappings = {
                        k.lower(): AppType(v) for k, v in mappings.items()
                    }
            except (json.JSONDecodeError, IOError):
                self.custom_mappings = {}
    
    def _save_custom_mappings(self):
        """Save custom app mappings to config"""
        get_tone_config_dir()
        config_path = get_tone_config_path()
        
        # Load existing config
        data = {}
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, IOError):
                data = {}
        
        data['app_mappings'] = {k: v.value for k, v in self.custom_mappings.items()}
        
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def detect_app_type(self, app_name: str, window_title: str = "") -> AppType:
        """Detect application type from app name and window title"""
        search_text = f"{app_name} {window_title}".lower()
        
        # Check custom mappings first
        for pattern, app_type in self.custom_mappings.items():
            if pattern in search_text:
                return app_type
        
        # Check built-in patterns
        for app_type, patterns in APP_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, search_text):
                    return app_type
        
        return AppType.UNKNOWN
    
    def add_custom_mapping(self, pattern: str, app_type: AppType):
        """Add custom app type mapping"""
        self.custom_mappings[pattern.lower()] = app_type
        self._save_custom_mappings()
    
    def remove_custom_mapping(self, pattern: str):
        """Remove custom app type mapping"""
        pattern_lower = pattern.lower()
        if pattern_lower in self.custom_mappings:
            del self.custom_mappings[pattern_lower]
            self._save_custom_mappings()


class ToneAdjuster:
    """Applies tone transformations to text"""
    
    def __init__(self):
        self.profiles: Dict[ToneType, ToneProfile] = {}
        self.custom_profiles: Dict[str, ToneProfile] = {}
        self._load_profiles()
    
    def _load_profiles(self):
        """Load tone profiles"""
        # Load default profiles
        for tone_type, profile_data in TONE_PROFILES.items():
            self.profiles[tone_type] = ToneProfile.from_dict(profile_data)
        
        # Load custom profiles from config
        config_path = get_tone_config_path()
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    custom = data.get('custom_profiles', {})
                    for name, profile_data in custom.items():
                        self.custom_profiles[name] = ToneProfile.from_dict(profile_data)
            except (json.JSONDecodeError, IOError):
                pass
    
    def _save_profiles(self):
        """Save custom profiles to config"""
        get_tone_config_dir()
        config_path = get_tone_config_path()
        
        # Load existing config
        data = {}
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, IOError):
                data = {}
        
        data['custom_profiles'] = {
            name: profile.to_dict() 
            for name, profile in self.custom_profiles.items()
        }
        
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_profile(self, tone_type: ToneType) -> ToneProfile:
        """Get tone profile by type"""
        return self.profiles.get(tone_type, self.profiles[ToneType.NEUTRAL])
    
    def get_custom_profile(self, name: str) -> Optional[ToneProfile]:
        """Get custom profile by name"""
        return self.custom_profiles.get(name)
    
    def add_custom_profile(self, name: str, profile: ToneProfile):
        """Add custom tone profile"""
        self.custom_profiles[name] = profile
        self._save_profiles()
    
    def transform_text(self, text: str, tone_type: ToneType) -> str:
        """Transform text according to tone profile"""
        profile = self.get_profile(tone_type)
        
        result = text
        
        # Apply replacements
        for pattern, replacement in profile.replacements.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        # Capitalize sentences if needed
        if profile.capitalize_sentences:
            result = self._capitalize_sentences(result)
        
        # Add punctuation if needed
        if profile.add_punctuation:
            result = self._fix_punctuation(result)
        
        return result
    
    def _capitalize_sentences(self, text: str) -> str:
        """Capitalize first letter of each sentence"""
        # Split into sentences
        sentences = re.split(r'([.!?]\s+)', text)
        
        result = []
        for i, part in enumerate(sentences):
            if i % 2 == 0 and part:  # Text part, not punctuation
                result.append(part[0].upper() + part[1:] if len(part) > 0 else part)
            else:
                result.append(part)
        
        return ''.join(result)
    
    def _fix_punctuation(self, text: str) -> str:
        """Fix common punctuation issues"""
        # Ensure space after punctuation
        text = re.sub(r'([.!?])([A-Za-z])', r'\1 \2', text)
        
        # Remove double spaces
        text = re.sub(r'  +', ' ', text)
        
        return text


class ContextToneManager:
    """Main manager combining app detection and tone adjustment"""
    
    def __init__(self):
        self.detector = AppContextDetector()
        self.adjuster = ToneAdjuster()
        self.current_app_type = AppType.UNKNOWN
        self.current_tone = ToneType.NEUTRAL
        self.enabled = True
        self.voice_override: Optional[ToneType] = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration"""
        config_path = get_tone_config_path()
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    self.enabled = data.get('enabled', True)
                    
                    # Load app-type to tone mappings
                    app_tone_map = data.get('app_tone_mapping', {})
                    self.app_tone_mapping = {
                        AppType(k): ToneType(v) for k, v in app_tone_map.items()
                    }
            except (json.JSONDecodeError, IOError):
                self.app_tone_mapping = self._get_default_mapping()
        else:
            self.app_tone_mapping = self._get_default_mapping()
    
    def _get_default_mapping(self) -> Dict[AppType, ToneType]:
        """Get default app-type to tone mapping"""
        return {
            AppType.EMAIL: ToneType.PROFESSIONAL,
            AppType.CHAT: ToneType.CASUAL,
            AppType.CODE: ToneType.TECHNICAL,
            AppType.DOCUMENT: ToneType.PROFESSIONAL,
            AppType.SPREADSHEET: ToneType.PROFESSIONAL,
            AppType.PRESENTATION: ToneType.PROFESSIONAL,
            AppType.BROWSER: ToneType.NEUTRAL,
            AppType.TERMINAL: ToneType.TECHNICAL,
            AppType.UNKNOWN: ToneType.NEUTRAL
        }
    
    def _save_config(self):
        """Save configuration"""
        get_tone_config_dir()
        config_path = get_tone_config_path()
        
        data = {
            'enabled': self.enabled,
            'app_tone_mapping': {
                k.value: v.value for k, v in self.app_tone_mapping.items()
            }
        }
        
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def update_context(self, app_name: str, window_title: str = ""):
        """Update context with new app info"""
        self.current_app_type = self.detector.detect_app_type(app_name, window_title)
        self.current_tone = self.app_tone_mapping.get(
            self.current_app_type, 
            ToneType.NEUTRAL
        )
        # Clear voice override when context changes
        self.voice_override = None
    
    def transform_text(self, text: str) -> str:
        """Transform text based on current context"""
        if not self.enabled:
            return text
        
        # Use voice override if set
        tone = self.voice_override if self.voice_override else self.current_tone
        
        return self.adjuster.transform_text(text, tone)
    
    def set_voice_override(self, tone: ToneType):
        """Set temporary tone override via voice command"""
        self.voice_override = tone
    
    def clear_voice_override(self):
        """Clear voice override"""
        self.voice_override = None
    
    def set_enabled(self, enabled: bool):
        """Enable or disable tone adjustment"""
        self.enabled = enabled
        self._save_config()
    
    def set_app_tone_mapping(self, app_type: AppType, tone: ToneType):
        """Set tone for specific app type"""
        self.app_tone_mapping[app_type] = tone
        self._save_config()
    
    def get_current_context(self) -> Dict[str, Any]:
        """Get current context info"""
        return {
            "app_type": self.current_app_type.value,
            "tone": self.current_tone.value,
            "voice_override": self.voice_override.value if self.voice_override else None,
            "enabled": self.enabled
        }


# Global instance
_tone_manager_instance: Optional[ContextToneManager] = None


def get_tone_manager() -> ContextToneManager:
    """Get or create the global tone manager instance"""
    global _tone_manager_instance
    if _tone_manager_instance is None:
        _tone_manager_instance = ContextToneManager()
    return _tone_manager_instance
