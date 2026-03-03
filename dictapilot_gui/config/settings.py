"""
DictaPilot GUI Settings Module
Handles configuration persistence and settings management
"""

import json
import os
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, List


def get_config_dir() -> Path:
    """Get platform-specific config directory"""
    if os.name == 'nt':  # Windows
        config_dir = Path(os.environ.get('APPDATA', ''))
        path = config_dir / 'DictaPilot'
    else:  # Linux/macOS
        path = Path.home() / '.config' / 'dictapilot'
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_config_file() -> Path:
    """Get the config file path"""
    return get_config_dir() / 'gui_config.json'


def get_models_dir() -> Path:
    """Get directory for storing downloaded models"""
    path = get_config_dir() / 'models'
    path.mkdir(parents=True, exist_ok=True)
    return path


@dataclass
class Settings:
    """Application settings with defaults"""
    # Model settings
    model: str = "base"  # tiny, base, small, medium
    language: str = "auto"  # auto, en, ur, etc.
    translate_to_english: bool = False
    device: str = "cpu"  # cpu, cuda
    
    # Audio settings
    sample_rate: int = 16000
    channels: int = 1
    
    # UI settings
    window_width: int = 900
    window_height: int = 700
    monospace_font: bool = True
    
    # Paths
    last_save_dir: str = str(Path.home())
    
    def to_dict(self) -> dict:
        """Convert settings to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Settings':
        """Create settings from dictionary, ignoring unknown keys"""
        if not data:
            return cls()
        # Filter only valid fields
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)
    
    def save(self) -> None:
        """Save settings to config file"""
        config_file = get_config_file()
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Failed to save settings: {e}")
    
    @classmethod
    def load(cls) -> 'Settings':
        """Load settings from config file"""
        config_file = get_config_file()
        if not config_file.exists():
            return cls()
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Failed to load settings: {e}")
            return cls()
    
    def get_available_models(self) -> List[str]:
        """Get list of available whisper models"""
        return ["tiny", "base", "small", "medium"]
    
    def get_available_languages(self) -> List[tuple]:
        """Get list of available languages as (code, name) tuples"""
        return [
            ("auto", "Auto-detect"),
            ("en", "English"),
            ("es", "Spanish"),
            ("fr", "French"),
            ("de", "German"),
            ("it", "Italian"),
            ("pt", "Portuguese"),
            ("nl", "Dutch"),
            ("ru", "Russian"),
            ("zh", "Chinese"),
            ("ja", "Japanese"),
            ("ko", "Korean"),
            ("ar", "Arabic"),
            ("hi", "Hindi"),
            ("ur", "Urdu"),
        ]
    
    def get_available_devices(self) -> List[tuple]:
        """Get list of available compute devices"""
        devices = [("cpu", "CPU")]
        try:
            import torch
            if torch.cuda.is_available():
                for i in range(torch.cuda.device_count()):
                    name = torch.cuda.get_device_name(i)
                    devices.append((f"cuda:{i}", f"CUDA: {name}"))
        except ImportError:
            pass
        return devices


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get global settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings.load()
    return _settings