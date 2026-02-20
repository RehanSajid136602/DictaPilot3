"""
DictaPilot Filler Word Detection Module
Handles detection and removal of filler words during transcription.

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

import re
import json
import os
import platform
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, field


def get_filler_config_path() -> Path:
    """Get platform-specific filler config path"""
    system = platform.system()
    
    if system == "Windows":
        data_dir = Path(os.environ.get("APPDATA", ""))
        return data_dir / "DictaPilot" / "fillers.json"
    else:
        data_dir = Path(os.path.expanduser("~/.local/share"))
        return data_dir / "dictapilot" / "fillers.json"


def get_filler_config_dir() -> Path:
    """Create and return filler config directory"""
    config_path = get_filler_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    return config_path.parent


# Default filler words by language
DEFAULT_FILLERS: Dict[str, Set[str]] = {
    "en": {
        # English fillers
        "um", "uh", "er", "ah", "like", "you know", "I mean", 
        "sort of", "kind of", "basically", "actually", "literally",
        "so", "yeah", "yep", "nope", "okay", "ok", "right",
        "i guess", "i suppose", "i think", "you see", "i see",
        "let me think", "how do you say", "what's it called",
        "anyway", "as i said", "as i was saying",
        "well", "i suppose", "i believe", "i suppose"
    },
    "es": {
        # Spanish fillers
        "eh", "um", "bueno", "este", "o sea", "como", "más o menos",
        "básicamente", "en fin", "bueno pues", "pues"
    },
    "fr": {
        # French fillers
        "euh", "ben", "bah", "voilà", "donc", "enfin", "bon",
        "vous savez", "comment dire", "euh"
    },
    "de": {
        # German fillers
        "ähm", "eh", "na ja", "also", "irgendwie", "eigentlich",
        "weißt du", "ich meine", "oder so"
    },
    "it": {
        # Italian fillers
        "ehm", "mah", "insomma", "praticamente", "cioè", "vabbè"
    },
    "zh": {
        # Chinese fillers
        "嗯", "啊", "这个", "那个", "就是", "其实", "基本上"
    },
    "ja": {
        # Japanese fillers
        "あの", "えーと", "ちょっと", "つまり", "いわゆる"
    }
}


@dataclass
class FillerConfig:
    """Configuration for filler word detection"""
    enabled: bool = True
    replacement: str = ""  # Empty = remove entirely
    preserve_punctuation: bool = True
    context_aware: bool = True
    languages: List[str] = field(default_factory=lambda: ["en"])
    custom_fillers: Set[str] = field(default_factory=set)
    excluded_phrases: Set[str] = field(default_factory=set)


class FillerWordDetector:
    """Detects and filters filler words from text"""
    
    def __init__(self):
        self.config = FillerConfig()
        self.fillers: Set[str] = set()
        self.filler_patterns: List[Tuple[str, re.Pattern]] = []
        self._load_config()
        self._build_patterns()
    
    def _load_config(self):
        """Load filler configuration"""
        config_path = get_filler_config_path()
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    self.config.enabled = data.get('enabled', True)
                    self.config.replacement = data.get('replacement', "")
                    self.config.preserve_punctuation = data.get('preserve_punctuation', True)
                    self.config.context_aware = data.get('context_aware', True)
                    self.config.languages = data.get('languages', ["en"])
                    
                    custom = data.get('custom_fillers', [])
                    self.config.custom_fillers = set(custom)
                    
                    excluded = data.get('excluded_phrases', [])
                    self.config.excluded_phrases = set(excluded)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Build filler set from enabled languages
        self._build_filler_set()
    
    def _save_config(self):
        """Save filler configuration"""
        get_filler_config_dir()
        config_path = get_filler_config_path()
        
        data = {
            'enabled': self.config.enabled,
            'replacement': self.config.replacement,
            'preserve_punctuation': self.config.preserve_punctuation,
            'context_aware': self.config.context_aware,
            'languages': self.config.languages,
            'custom_fillers': list(self.config.custom_fillers),
            'excluded_phrases': list(self.config.excluded_phrases)
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _build_filler_set(self):
        """Build filler set from enabled languages"""
        self.fillers = set()
        
        for lang in self.config.languages:
            if lang in DEFAULT_FILLERS:
                self.fillers.update(DEFAULT_FILLERS[lang])
        
        # Add custom fillers
        self.fillers.update(self.config.custom_fillers)
        
        self._build_patterns()
    
    def _build_patterns(self):
        """Build regex patterns for filler detection"""
        self.filler_patterns = []
        
        # Sort by length (longest first) to match longer phrases
        sorted_fillers = sorted(self.fillers, key=len, reverse=True)
        
        for filler in sorted_fillers:
            # Escape special regex characters
            pattern_str = re.escape(filler)
            # Word boundary at start and end
            pattern = re.compile(r'\b' + pattern_str + r'\b', re.IGNORECASE)
            self.filler_patterns.append((filler, pattern))
    
    def set_enabled(self, enabled: bool):
        """Enable or disable filler detection"""
        self.config.enabled = enabled
        self._save_config()
    
    def set_replacement(self, replacement: str):
        """Set replacement text for fillers"""
        self.config.replacement = replacement
        self._save_config()
    
    def set_languages(self, languages: List[str]):
        """Set enabled languages"""
        self.config.languages = languages
        self._build_filler_set()
        self._save_config()
    
    def add_custom_filler(self, filler: str):
        """Add a custom filler word"""
        self.config.custom_fillers.add(filler.lower())
        self._build_filler_set()
        self._save_config()
    
    def remove_custom_filler(self, filler: str):
        """Remove a custom filler word"""
        self.config.custom_fillers.discard(filler.lower())
        self._build_filler_set()
        self._save_config()
    
    def add_excluded_phrase(self, phrase: str):
        """Add a phrase to exclude from filler detection"""
        self.config.excluded_phrases.add(phrase.lower())
        self._save_config()
    
    def remove_excluded_phrase(self, phrase: str):
        """Remove an excluded phrase"""
        self.config.excluded_phrases.discard(phrase.lower())
        self._save_config()
    
    def detect_fillers(self, text: str) -> List[Dict[str, any]]:
        """Detect filler words in text"""
        if not self.config.enabled:
            return []
        
        detections = []
        
        for filler, pattern in self.filler_patterns:
            for match in pattern.finditer(text):
                # Check if in excluded phrase
                context_start = max(0, match.start() - 20)
                context_end = min(len(text), match.end() + 20)
                context = text[context_start:context_end].lower()
                
                excluded = False
                for excl_phrase in self.config.excluded_phrases:
                    if excl_phrase in context:
                        excluded = True
                        break
                
                if not excluded:
                    detections.append({
                        'filler': filler,
                        'start': match.start(),
                        'end': match.end(),
                        'text': match.group()
                    })
        
        # Sort by position
        detections.sort(key=lambda x: x['start'])
        return detections
    
    def filter_text(self, text: str) -> Tuple[str, List[Dict[str, any]]]:
        """Filter filler words from text"""
        if not self.config.enabled:
            return text, []
        
        detections = self.detect_fillers(text)
        
        if not detections:
            return text, []
        
        # Build result by removing/replacing fillers
        result = text
        offset = 0
        
        for detection in detections:
            start = detection['start'] + offset
            end = detection['end'] + offset
            filler = detection['filler']
            
            if self.config.replacement:
                # Replace with custom text
                replacement = self.config.replacement
                if self.config.preserve_punctuation:
                    # Check if original had punctuation after
                    if end < len(result) and result[end] in '.,!?;:)':
                        replacement += result[end]
                        end += 1
                result = result[:start] + replacement + result[end:]
                offset += len(replacement) - (end - start)
            else:
                # Remove entirely
                result = result[:start] + result[end:]
                offset -= (end - start)
        
        # Clean up extra spaces
        result = re.sub(r'\s+', ' ', result).strip()
        
        return result, detections
    
    def filter_sentence(self, sentence: str) -> str:
        """Filter fillers from a single sentence"""
        result, _ = self.filter_text(sentence)
        return result
    
    def get_statistics(self) -> Dict[str, any]:
        """Get filler detection statistics"""
        return {
            'enabled': self.config.enabled,
            'languages': self.config.languages,
            'total_fillers': len(self.fillers),
            'custom_fillers': len(self.config.custom_fillers),
            'excluded_phrases': len(self.config.excluded_phrases),
            'replacement': self.config.replacement if self.config.replacement else "(remove)"
        }
    
    def get_available_languages(self) -> List[str]:
        """Get list of available languages"""
        return list(DEFAULT_FILLERS.keys())


# Global instance
_filler_detector_instance: Optional[FillerWordDetector] = None


def get_filler_detector() -> FillerWordDetector:
    """Get or create the global filler detector instance"""
    global _filler_detector_instance
    if _filler_detector_instance is None:
        _filler_detector_instance = FillerWordDetector()
    return _filler_detector_instance
