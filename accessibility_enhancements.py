"""
DictaPilot Accessibility Enhancements Module
Handles speech pattern adaptation for users with speech impediments.

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
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum


def get_accessibility_config_path() -> Path:
    """Get platform-specific accessibility config path"""
    system = platform.system()
    
    if system == "Windows":
        data_dir = Path(os.environ.get("APPDATA", ""))
        return data_dir / "DictaPilot" / "accessibility.json"
    else:
        data_dir = Path(os.path.expanduser("~/.local/share"))
        return data_dir / "dictapilot" / "accessibility.json"


def get_accessibility_config_dir() -> Path:
    """Create and return accessibility config directory"""
    config_path = get_accessibility_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    return config_path.parent


class SpeechPatternType(Enum):
    """Types of speech patterns"""
    STUTTER_REPETITION = "stutter_repetition"  # "b-b-b-ball"
    STUTTER_BLOCK = "stutter_block"             # Prolonged sound
    STUTTER_PROLONGATION = "stutter_prolongation"  # "mmmmmilk"
    HESITATION = "hesitation"                   # Filled pauses
    FALSE_START = "false_start"                 # "I I I went"
    SELF_CORRECTION = "self_correction"         # "cat no dog"


@dataclass
class SpeechEvent:
    """Single speech event for pattern analysis"""
    timestamp: float
    event_type: SpeechPatternType
    audio_duration: float
    text_before: str
    text_after: str
    confidence: float


@dataclass
class UserSpeechProfile:
    """User's speech profile for adaptation"""
    user_id: str
    pattern_frequencies: Dict[str, int] = field(default_factory=dict)
    common_mispronunciations: Dict[str, str] = field(default_factory=dict)
    learned_words: Dict[str, str] = field(default_factory=dict)
    adaptation_enabled: bool = True
    sensitivity: float = 0.5  # 0-1, how aggressive the adaptation


class StutterDetector:
    """Detects stuttering patterns in speech"""
    
    # Patterns for different stutter types
    REPETITION_PATTERNS = [
        r'(\w)\1{2,}',  # "b-b-b-ball"
        r'(\w{1,3})\1{1,}\b',  # "go-go-go"
    ]
    
    PROLONGATION_PATTERNS = [
        r'(\w)\1{2,}',  # "mmmmmilk"
    ]
    
    BLOCK_PATTERNS = [
        r'[\w]{2,}-{2,}',  # "te-a" (blocked)
    ]
    
    def __init__(self):
        self.sensitivity = 0.5
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns"""
        self.repetition_re = [re.compile(p, re.IGNORECASE) for p in self.REPETITION_PATTERNS]
        self.prolongation_re = [re.compile(p, re.IGNORECASE) for p in self.PROLONGATION_PATTERNS]
        self.block_re = [re.compile(p) for p in self.BLOCK_PATTERNS]
    
    def set_sensitivity(self, sensitivity: float):
        """Set detection sensitivity (0-1)"""
        self.sensitivity = max(0, min(1, sensitivity))
    
    def detect_patterns(self, text: str) -> List[Tuple[SpeechPatternType, str, int]]:
        """Detect stuttering patterns in text"""
        detections = []
        
        # Check repetitions
        if self.sensitivity > 0.3:
            for pattern in self.repetition_re:
                for match in pattern.finditer(text):
                    detections.append((
                        SpeechPatternType.STUTTER_REPETITION,
                        match.group(),
                        match.start()
                    ))
        
        # Check prolongations
        if self.sensitivity > 0.4:
            for pattern in self.prolongation_re:
                for match in pattern.finditer(text):
                    detections.append((
                        SpeechPatternType.STUTTER_PROLONGATION,
                        match.group(),
                        match.start()
                    ))
        
        # Check blocks
        if self.sensitivity > 0.5:
            for pattern in self.block_re:
                for match in pattern.finditer(text):
                    detections.append((
                        SpeechPatternType.STUTTER_BLOCK,
                        match.group(),
                        match.start()
                    ))
        
        return detections
    
    def is_stutter_event(self, text: str, duration: float) -> bool:
        """Determine if a speech event is a stutter"""
        patterns = self.detect_patterns(text)
        
        if not patterns:
            return False
        
        # Duration check - stutters are typically short
        if duration > 2.0:  # More than 2 seconds
            return False
        
        # Check confidence based on patterns found
        confidence = len(patterns) * self.sensitivity
        
        return confidence > 0.3


class SpeechPatternAnalyzer:
    """Analyzes user's speech patterns over time"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.events: deque = deque(maxlen=window_size)
        self.pattern_counts: Dict[SpeechPatternType, int] = defaultdict(int)
        self.total_events = 0
        self.stutter_rate = 0.0
    
    def add_event(self, event: SpeechEvent):
        """Add a speech event"""
        self.events.append(event)
        self.total_events += 1
        
        if event.event_type in [
            SpeechPatternType.STUTTER_REPETITION,
            SpeechPatternType.STUTTER_BLOCK,
            SpeechPatternType.STUTTER_PROLONGATION
        ]:
            self.pattern_counts[event.event_type] += 1
        
        # Calculate stutter rate
        speech_events = sum(1 for e in self.events 
                          if e.event_type in [
                              SpeechPatternType.STUTTER_REPETITION,
                              SpeechPatternType.STUTTER_BLOCK,
                              SpeechPatternType.STUTTER_PROLONGATION
                          ])
        
        if self.total_events > 0:
            self.stutter_rate = speech_events / self.total_events
    
    def get_pattern_analysis(self) -> Dict[str, Any]:
        """Get analysis of speech patterns"""
        return {
            "total_events": self.total_events,
            "stutter_rate": round(self.stutter_rate, 3),
            "pattern_counts": {
                k.value: v for k, v in self.pattern_counts.items()
            },
            "recommendations": self._get_recommendations()
        }
    
    def _get_recommendations(self) -> List[str]:
        """Get recommendations based on patterns"""
        recommendations = []
        
        if self.stutter_rate > 0.3:
            recommendations.append("High stutter rate detected. Consider enabling aggressive adaptation.")
        elif self.stutter_rate > 0.1:
            recommendations.append("Moderate stutter rate. Standard adaptation recommended.")
        
        if self.pattern_counts.get(SpeechPatternType.STUTTER_REPETITION, 0) > 10:
            recommendations.append("Frequent word repetitions detected.")
        
        if self.pattern_counts.get(SpeechPatternType.STUTTER_PROLONGATION, 0) > 5:
            recommendations.append("Frequent sound prolongations detected.")
        
        return recommendations


class AccentAdapter:
    """Adapts to user accent over time"""
    
    def __init__(self):
        self.common_substitutions: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.total_adaptations = 0
    
    def learn_substitution(self, wrong: str, correct: str):
        """Learn a pronunciation substitution"""
        self.common_substitutions[wrong][correct] += 1
        self.total_adaptations += 1
    
    def get_corrections(self) -> Dict[str, str]:
        """Get learned corrections"""
        corrections = {}
        
        for wrong, corrections_dict in self.common_substitutions.items():
            if corrections_dict:
                # Get most common correction
                correct = max(corrections_dict, key=corrections_dict.get)
                corrections[wrong] = correct
        
        return corrections
    
    def apply_corrections(self, text: str) -> str:
        """Apply learned corrections to text"""
        corrections = self.get_corrections()
        
        for wrong, correct in corrections.items():
            # Word boundary matching
            pattern = r'\b' + re.escape(wrong) + r'\b'
            text = re.sub(pattern, correct, text, flags=re.IGNORECASE)
        
        return text
    
    def clear_learning(self):
        """Clear all learned substitutions"""
        self.common_substitutions.clear()
        self.total_adaptations = 0


class AccessibilityManager:
    """Main accessibility manager combining all features"""
    
    def __init__(self):
        self.stutter_detector = StutterDetector()
        self.pattern_analyzer = SpeechPatternAnalyzer()
        self.accent_adapter = AccentAdapter()
        self.enabled = False
        self.sensitivity = 0.5
        self.profile: Optional[UserSpeechProfile] = None
        self._load_config()
        self._load_profile()
    
    def _load_config(self):
        """Load configuration"""
        config_path = get_accessibility_config_path()
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.enabled = data.get('enabled', False)
                    self.sensitivity = data.get('sensitivity', 0.5)
                    self.stutter_detector.set_sensitivity(self.sensitivity)
            except (json.JSONDecodeError, IOError):
                pass
    
    def _save_config(self):
        """Save configuration"""
        get_accessibility_config_dir()
        config_path = get_accessibility_config_path()
        
        data = {
            'enabled': self.enabled,
            'sensitivity': self.sensitivity
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def _load_profile(self):
        """Load user speech profile"""
        profile_path = get_accessibility_config_path().parent / "speech_profile.json"
        
        if profile_path.exists():
            try:
                with open(profile_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.profile = UserSpeechProfile(
                        user_id=data.get('user_id', 'default'),
                        pattern_frequencies=data.get('pattern_frequencies', {}),
                        common_mispronunciations=data.get('common_mispronunciations', {}),
                        learned_words=data.get('learned_words', {}),
                        adaptation_enabled=data.get('adaptation_enabled', True),
                        sensitivity=data.get('sensitivity', 0.5)
                    )
            except (json.JSONDecodeError, IOError):
                self.profile = UserSpeechProfile(user_id='default')
        else:
            self.profile = UserSpeechProfile(user_id='default')
    
    def _save_profile(self):
        """Save user speech profile"""
        if self.profile is None:
            return
        
        profile_path = get_accessibility_config_path().parent / "speech_profile.json"
        
        data = {
            'user_id': self.profile.user_id,
            'pattern_frequencies': self.profile.pattern_frequencies,
            'common_mispronunciations': self.profile.common_mispronunciations,
            'learned_words': self.profile.learned_words,
            'adaptation_enabled': self.profile.adaptation_enabled,
            'sensitivity': self.profile.sensitivity
        }
        
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def set_enabled(self, enabled: bool):
        """Enable or disable accessibility features"""
        self.enabled = enabled
        self._save_config()
    
    def set_sensitivity(self, sensitivity: float):
        """Set detection sensitivity"""
        self.sensitivity = max(0, min(1, sensitivity))
        self.stutter_detector.set_sensitivity(self.sensitivity)
        if self.profile:
            self.profile.sensitivity = sensitivity
        self._save_config()
    
    def process_text(self, text: str, audio_duration: float = 0.0) -> str:
        """Process text with accessibility adaptations"""
        if not self.enabled:
            return text
        
        # Detect stuttering patterns
        patterns = self.stutter_detector.detect_patterns(text)
        
        # Add events to analyzer
        for pattern_type, matched_text, position in patterns:
            event = SpeechEvent(
                timestamp=0,  # Would come from audio
                event_type=pattern_type,
                audio_duration=audio_duration,
                text_before=matched_text,
                text_after="",
                confidence=0.8
            )
            self.pattern_analyzer.add_event(event)
        
        # Apply accent corrections
        text = self.accent_adapter.apply_corrections(text)
        
        return text
    
    def learn_correction(self, wrong: str, correct: str):
        """Learn a pronunciation correction"""
        self.accent_adapter.learn_substitution(wrong, correct)
        
        # Update profile
        if self.profile:
            self.profile.common_mispronunciations[wrong] = correct
            self._save_profile()
    
    def get_analysis(self) -> Dict[str, Any]:
        """Get speech pattern analysis"""
        return {
            "enabled": self.enabled,
            "sensitivity": self.sensitivity,
            "pattern_analysis": self.pattern_analyzer.get_pattern_analysis(),
            "learned_corrections": len(self.accent_adapter.get_corrections()),
            "profile": {
                "user_id": self.profile.user_id if self.profile else "none",
                "adaptation_enabled": self.profile.adaptation_enabled if self.profile else False
            }
        }
    
    def clear_learning(self):
        """Clear all learned patterns"""
        self.accent_adapter.clear_learning()
        if self.profile:
            self.profile.common_mispronunciations.clear()
            self.profile.learned_words.clear()
            self._save_profile()


# Global instance
_accessibility_instance: Optional[AccessibilityManager] = None


def get_accessibility_manager() -> AccessibilityManager:
    """Get or create the global accessibility manager instance"""
    global _accessibility_instance
    if _accessibility_instance is None:
        _accessibility_instance = AccessibilityManager()
    return _accessibility_instance
