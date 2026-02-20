"""
DictaPilot Speed Metrics Module
Tracks real-time WPM and productivity statistics.

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
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from collections import deque


def get_metrics_path() -> Path:
    """Get platform-specific metrics file path"""
    system = platform.system()
    
    if system == "Windows":
        data_dir = Path(os.environ.get("APPDATA", ""))
        return data_dir / "DictaPilot" / "metrics.json"
    else:
        data_dir = Path(os.path.expanduser("~/.local/share"))
        return data_dir / "dictapilot" / "metrics.json"


def get_metrics_dir() -> Path:
    """Create and return metrics directory"""
    metrics_path = get_metrics_path()
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    return metrics_path.parent


@dataclass
class SessionMetrics:
    """Metrics for a single dictation session"""
    session_id: str
    start_time: str
    end_time: Optional[str] = None
    total_words: int = 0
    total_characters: int = 0
    total_duration: float = 0.0  # seconds
    total_transcriptions: int = 0
    avg_wpm: float = 0.0
    peak_wpm: float = 0.0
    min_wpm: float = 0.0
    pause_count: int = 0
    pause_duration: float = 0.0
    corrections_made: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionMetrics":
        return cls(**data)


@dataclass
class TranscriptionEvent:
    """Single transcription event with timing"""
    timestamp: str
    word_count: int
    character_count: int
    duration: float  # seconds since session start
    is_correction: bool = False


class SpeedTracker:
    """Real-time speed tracking during dictation"""
    
    def __init__(self, window_size: int = 5):
        """
        Initialize speed tracker
        
        Args:
            window_size: Number of recent events to use for WPM calculation
        """
        self.window_size = window_size
        self.events: deque = deque(maxlen=window_size)
        self.session_start: Optional[float] = None
        self.current_wpm: float = 0.0
        self.peak_wpm: float = 0.0
        self.total_words: int = 0
    
    def start_session(self):
        """Start a new tracking session"""
        self.session_start = time.time()
        self.events.clear()
        self.current_wpm = 0.0
        self.peak_wpm = 0.0
        self.total_words = 0
    
    def record_transcription(self, text: str, is_correction: bool = False):
        """Record a transcription event"""
        if self.session_start is None:
            self.start_session()
        
        now = time.time()
        duration = now - self.session_start
        
        word_count = len(text.split())
        char_count = len(text)
        
        event = TranscriptionEvent(
            timestamp=datetime.now().isoformat(),
            word_count=word_count,
            character_count=char_count,
            duration=duration,
            is_correction=is_correction
        )
        
        self.events.append(event)
        self.total_words += word_count
        
        # Calculate current WPM
        self._calculate_wpm()
    
    def _calculate_wpm(self):
        """Calculate current WPM from recent events"""
        if len(self.events) < 2:
            self.current_wpm = 0.0
            return
        
        # Use linear regression on recent events for more accurate WPM
        durations = [e.duration for e in self.events]
        word_counts = [e.word_count for e in self.events]
        
        if not durations or durations[-1] == durations[0]:
            self.current_wpm = 0.0
            return
        
        # Calculate words per minute
        time_span = durations[-1] - durations[0]
        words_in_span = sum(word_counts)
        
        if time_span > 0:
            self.current_wpm = (words_in_span / time_span) * 60
        
        # Update peak
        if self.current_wpm > self.peak_wpm:
            self.peak_wpm = self.current_wpm
    
    def get_current_wpm(self) -> float:
        """Get current WPM"""
        return round(self.current_wpm, 1)
    
    def get_peak_wpm(self) -> float:
        """Get peak WPM"""
        return round(self.peak_wpm, 1)
    
    def get_average_wpm(self) -> float:
        """Get average WPM for the session"""
        if self.session_start is None:
            return 0.0
        
        duration = time.time() - self.session_start
        if duration > 0:
            return round((self.total_words / duration) * 60, 1)
        return 0.0
    
    def get_session_duration(self) -> float:
        """Get current session duration in seconds"""
        if self.session_start is None:
            return 0.0
        return time.time() - self.session_start
    
    def get_word_count(self) -> int:
        """Get total words in session"""
        return self.total_words


class MetricsTracker:
    """Tracks and persists session metrics"""
    
    def __init__(self):
        self.current_session: Optional[SessionMetrics] = None
        self.speed_tracker = SpeedTracker()
        self.sessions: List[SessionMetrics] = []
        self._load_sessions()
    
    def _load_sessions(self):
        """Load historical sessions from file"""
        metrics_path = get_metrics_path()
        if metrics_path.exists():
            try:
                with open(metrics_path, 'r') as f:
                    data = json.load(f)
                    sessions_list = data.get('sessions', [])
                    self.sessions = [
                        SessionMetrics.from_dict(s) for s in sessions_list
                    ]
            except (json.JSONDecodeError, IOError):
                self.sessions = []
        else:
            self.sessions = []
    
    def _save_sessions(self):
        """Save sessions to file"""
        get_metrics_dir()
        metrics_path = get_metrics_path()
        
        data = {
            'last_updated': datetime.now().isoformat(),
            'sessions': [s.to_dict() for s in self.sessions]
        }
        
        with open(metrics_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def start_session(self, session_id: Optional[str] = None):
        """Start a new metrics session"""
        if session_id is None:
            session_id = f"session_{int(time.time())}"
        
        self.current_session = SessionMetrics(
            session_id=session_id,
            start_time=datetime.now().isoformat()
        )
        self.speed_tracker.start_session()
    
    def end_session(self):
        """End current session and save metrics"""
        if self.current_session is None:
            return
        
        self.current_session.end_time = datetime.now().isoformat()
        
        # Get final statistics
        self.current_session.total_words = self.speed_tracker.get_word_count()
        self.current_session.avg_wpm = self.speed_tracker.get_average_wpm()
        self.current_session.peak_wpm = self.speed_tracker.get_peak_wpm()
        
        duration = self.speed_tracker.get_session_duration()
        self.current_session.total_duration = duration
        
        if duration > 0:
            self.current_session.min_wpm = self.speed_tracker.get_current_wpm()
        
        self.sessions.append(self.current_session)
        self._save_sessions()
        
        self.current_session = None
    
    def record_transcription(self, text: str, is_correction: bool = False):
        """Record a transcription"""
        if self.current_session is None:
            self.start_session()
        
        # Update speed tracker
        self.speed_tracker.record_transcription(text, is_correction)
        
        # Update session metrics
        if self.current_session:
            self.current_session.total_words = self.speed_tracker.get_word_count()
            self.current_session.total_characters += len(text)
            self.current_session.total_transcriptions += 1
            
            if is_correction:
                self.current_session.corrections_made += 1
    
    def record_pause(self, duration: float):
        """Record a pause in dictation"""
        if self.current_session:
            self.current_session.pause_count += 1
            self.current_session.pause_duration += duration
    
    def get_current_wpm(self) -> float:
        """Get current real-time WPM"""
        return self.speed_tracker.get_current_wpm()
    
    def get_peak_wpm(self) -> float:
        """Get peak WPM for current session"""
        return self.speed_tracker.get_peak_wpm()
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        if self.current_session is None:
            return {
                "active": False,
                "words": 0,
                "wpm": 0.0,
                "peak_wpm": 0.0,
                "duration": 0.0
            }
        
        return {
            "active": True,
            "session_id": self.current_session.session_id,
            "words": self.speed_tracker.get_word_count(),
            "wpm": self.get_current_wpm(),
            "peak_wpm": self.speed_tracker.get_peak_wpm(),
            "avg_wpm": self.speed_tracker.get_average_wpm(),
            "duration": self.speed_tracker.get_session_duration(),
            "transcriptions": self.current_session.total_transcriptions,
            "corrections": self.current_session.corrections_made
        }
    
    def get_historical_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get historical statistics"""
        cutoff = datetime.now() - timedelta(days=days)
        
        recent_sessions = [
            s for s in self.sessions 
            if datetime.fromisoformat(s.start_time) >= cutoff
        ]
        
        if not recent_sessions:
            return {
                "period_days": days,
                "total_sessions": 0,
                "total_words": 0,
                "total_duration": 0.0,
                "avg_wpm": 0.0,
                "best_wpm": 0.0,
                "avg_session_words": 0.0,
                "avg_session_duration": 0.0
            }
        
        total_words = sum(s.total_words for s in recent_sessions)
        total_duration = sum(s.total_duration for s in recent_sessions)
        avg_wpm = sum(s.avg_wpm for s in recent_sessions) / len(recent_sessions)
        best_wpm = max(s.peak_wpm for s in recent_sessions)
        
        return {
            "period_days": days,
            "total_sessions": len(recent_sessions),
            "total_words": total_words,
            "total_duration": round(total_duration, 1),
            "avg_wpm": round(avg_wpm, 1),
            "best_wpm": round(best_wpm, 1),
            "avg_session_words": round(total_words / len(recent_sessions), 1),
            "avg_session_duration": round(total_duration / len(recent_sessions), 1)
        }
    
    def get_daily_stats(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get statistics for a specific date"""
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime("%Y-%m-%d")
        
        day_sessions = [
            s for s in self.sessions
            if s.start_time.startswith(date_str)
        ]
        
        if not day_sessions:
            return {
                "date": date_str,
                "sessions": 0,
                "words": 0,
                "duration": 0.0,
                "wpm": 0.0
            }
        
        total_words = sum(s.total_words for s in day_sessions)
        total_duration = sum(s.total_duration for s in day_sessions)
        
        return {
            "date": date_str,
            "sessions": len(day_sessions),
            "words": total_words,
            "duration": round(total_duration, 1),
            "wpm": round(total_words / (total_duration / 60), 1) if total_duration > 0 else 0
        }
    
    def get_weekly_trends(self) -> List[Dict[str, Any]]:
        """Get weekly trend data for the past 8 weeks"""
        trends = []
        
        for i in range(8):
            date = datetime.now() - timedelta(weeks=i)
            stats = self.get_daily_stats(date)
            trends.append(stats)
        
        return list(reversed(trends))
    
    def compare_to_typing(self, avg_typing_wpm: float = 40.0) -> Dict[str, Any]:
        """Compare dictation speed to average typing speed"""
        current_wpm = self.get_current_wpm()
        avg_wpm = self.speed_tracker.get_average_wpm()
        
        return {
            "current_wpm": current_wpm,
            "avg_wpm": avg_wpm,
            "typing_wpm": avg_typing_wpm,
            "speed_improvement_current": round(((current_wpm / avg_typing_wpm) - 1) * 100, 1),
            "speed_improvement_avg": round(((avg_wpm / avg_typing_wpm) - 1) * 100, 1),
            "times_faster_current": round(current_wpm / avg_typing_wpm, 2),
            "times_faster_avg": round(avg_wpm / avg_typing_wpm, 2)
        }
    
    def clear_history(self, before_date: Optional[datetime] = None):
        """Clear session history"""
        if before_date is None:
            self.sessions.clear()
        else:
            self.sessions = [
                s for s in self.sessions
                if datetime.fromisoformat(s.start_time) >= before_date
            ]
        
        self._save_sessions()


# Global instance
_metrics_instance: Optional[MetricsTracker] = None


def get_metrics_tracker() -> MetricsTracker:
    """Get or create the global metrics tracker instance"""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = MetricsTracker()
    return _metrics_instance
