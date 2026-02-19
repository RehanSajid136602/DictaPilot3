"""
DictaPilot Transcription Store
Handles persistent storage of all transcriptions in JSON format for easy access and reuse.

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

import json
import os
import platform
from pathlib import Path
from datetime import datetime
from datetime import timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
import time
import time


def get_transcriptions_path() -> Path:
    """Get platform-specific transcriptions file path"""
    system = platform.system()
    
    if system == "Windows":
        data_dir = Path(os.environ.get("APPDATA", ""))
        return data_dir / "DictaPilot" / "transcriptions.json"
    else:
        data_dir = Path(os.path.expanduser("~/.local/share"))
        return data_dir / "dictapilot" / "transcriptions.json"


def get_transcriptions_dir() -> Path:
    """Create and return transcriptions directory"""
    transcriptions_path = get_transcriptions_path()
    transcriptions_path.parent.mkdir(parents=True, exist_ok=True)
    return transcriptions_path.parent


@dataclass
class TranscriptionEntry:
    """Single transcription entry"""
    id: str
    timestamp: str
    timestamp_unix: float
    original_text: str
    processed_text: str
    action: str
    session_id: str
    word_count: int
    # Enhanced tagging fields
    tags: List[str] = None  # Custom tags
    app_name: str = ""      # Name of app where dictation occurred
    language: str = ""      # Detected language
    model_used: str = ""    # Model used for transcription
    duration: float = 0.0   # Duration of recording in seconds
    wpm: float = 0.0        # Words per minute
    quality_score: float = 0.0  # Estimated quality score (0-1)
    cleanup_applied: bool = False
    correction_source: str = ""  # heuristic, llm, adaptive
    ambiguity_flag: bool = False
    transcription_confidence: float = 0.0
    # Version history for edits
    edit_history: List[Dict[str, Any]] = None  # List of previous versions
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        # Convert None tags to empty list for JSON serialization
        if result['tags'] is None:
            result['tags'] = []
        # Convert None edit_history to empty list
        if result['edit_history'] is None:
            result['edit_history'] = []
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TranscriptionEntry":
        # Handle missing fields in older data
        kwargs = {
            'id': data.get('id', ''),
            'timestamp': data.get('timestamp', ''),
            'timestamp_unix': data.get('timestamp_unix', 0.0),
            'original_text': data.get('original_text', ''),
            'processed_text': data.get('processed_text', ''),
            'action': data.get('action', 'append'),
            'session_id': data.get('session_id', ''),
            'word_count': data.get('word_count', 0),
            'tags': data.get('tags', []),
            'app_name': data.get('app_name', ''),
            'language': data.get('language', ''),
            'model_used': data.get('model_used', ''),
            'duration': data.get('duration', 0.0),
            'wpm': data.get('wpm', 0.0),
            'quality_score': data.get('quality_score', 0.0),
            'cleanup_applied': data.get('cleanup_applied', False),
            'correction_source': data.get('correction_source', ''),
            'ambiguity_flag': data.get('ambiguity_flag', False),
            'transcription_confidence': data.get('transcription_confidence', 0.0),
            'edit_history': data.get('edit_history', []),
        }
        return cls(**kwargs)
    
    @property
    def display_text(self) -> str:
        """Get the best text for display/reuse (processed if available)"""
        return self.processed_text if self.processed_text else self.original_text


@dataclass
class TranscriptionStore:
    """Manages transcription storage and retrieval"""
    entries: List[TranscriptionEntry]
    session_start: str
    
    def __init__(self):
        self.entries = []
        self.session_start = datetime.now().isoformat()
        self.categories: Dict[str, Dict[str, Any]] = {}  # category_name -> {description, entry_ids, created_at}
        self.edit_history: Dict[str, List[Dict[str, Any]]] = {}  # entry_id -> list of edits
    
    @staticmethod
    def _migrate_schema(data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate older schema versions to current version"""
        schema_version = data.get("schema_version", "1.0")
        
        # Migrate from 1.0/2.0 to 3.0
        if schema_version in ("1.0", "2.0"):
            # Add categories section if missing
            if "categories" not in data:
                data["categories"] = {}
            # Add edit_history section if missing
            if "edit_history" not in data:
                data["edit_history"] = {}
            # Add edit_history to each entry if missing
            if "entries" in data:
                for entry in data["entries"]:
                    if "edit_history" not in entry:
                        entry["edit_history"] = []
            data["schema_version"] = "3.0"
        
        return data
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": "3.0",  # Updated schema version
            "created_version": "1.0",  # Original version when store was created
            "session_start": self.session_start,
            "last_updated": datetime.now().isoformat(),
            "total_entries": len(self.entries),
            "entries": [e.to_dict() for e in self.entries],
            "categories": self.categories,
            "edit_history": self.edit_history,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TranscriptionStore":
        # Apply schema migration
        data = cls._migrate_schema(data)
        
        store = cls()
        store.session_start = data.get("session_start", datetime.now().isoformat())
        store.categories = data.get("categories", {})
        store.edit_history = data.get("edit_history", {})
        
        if "entries" in data:
            store.entries = [TranscriptionEntry.from_dict(e) for e in data["entries"]]
        return store
    
    def save(self, path: Optional[Path] = None) -> None:
        """Save all transcriptions to JSON file"""
        path = path or get_transcriptions_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls, path: Optional[Path] = None) -> "TranscriptionStore":
        """Load transcriptions from JSON file"""
        path = path or get_transcriptions_path()
        if not path.exists():
            return cls()
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except (json.JSONDecodeError, KeyError, TypeError):
            return cls()
    
    def add_entry(
        self,
        original_text: str,
        processed_text: str = "",
        action: str = "append",
        tags: List[str] = None,
        app_name: str = "",
        language: str = "",
        model_used: str = "",
        duration: float = 0.0,
        wpm: float = 0.0,
        quality_score: float = 0.0,
        cleanup_applied: bool = False,
        correction_source: str = "",
        ambiguity_flag: bool = False,
        transcription_confidence: float = 0.0,
    ) -> TranscriptionEntry:
        """Add a new transcription entry"""
        import uuid

        timestamp = datetime.now()
        entry = TranscriptionEntry(
            id=str(uuid.uuid4())[:8],
            timestamp=timestamp.isoformat(),
            timestamp_unix=timestamp.timestamp(),
            original_text=original_text,
            processed_text=processed_text,
            action=action,
            session_id=self.session_start,
            word_count=len(original_text.split()),
            tags=tags or [],
            app_name=app_name,
            language=language,
            model_used=model_used,
            duration=duration,
            wpm=wpm,
            quality_score=quality_score,
            cleanup_applied=cleanup_applied,
            correction_source=correction_source,
            ambiguity_flag=ambiguity_flag,
            transcription_confidence=transcription_confidence,
        )
        self.entries.append(entry)
        return entry
    
    def get_recent(self, count: int = 10) -> List[TranscriptionEntry]:
        """Get the most recent transcriptions"""
        return self.entries[-count:] if count > 0 else self.entries
    
    def get_all(self) -> List[TranscriptionEntry]:
        """Get all transcriptions"""
        return self.entries
    
    def search(self, query: str, case_sensitive: bool = False) -> List[TranscriptionEntry]:
        """Search transcriptions by text content"""
        if not query:
            return self.entries
        
        if case_sensitive:
            return [e for e in self.entries 
                    if query in e.original_text or query in e.processed_text]
        else:
            query_lower = query.lower()
            return [e for e in self.entries 
                    if query_lower in e.original_text.lower() or 
                       query_lower in e.processed_text.lower()]
    
    def get_by_date(self, date_str: str) -> List[TranscriptionEntry]:
        """Get transcriptions from a specific date (YYYY-MM-DD)"""
        return [e for e in self.entries if e.timestamp.startswith(date_str)]
    
    def clear_session(self) -> None:
        """Clear all entries and start a new session"""
        self.entries = []
        self.session_start = datetime.now().isoformat()
    
    def export_to_text(self, path: Optional[Path] = None, 
                       include_metadata: bool = False) -> str:
        """Export all transcriptions to a plain text format"""
        lines = []
        for entry in self.entries:
            if include_metadata:
                lines.append(f"[{entry.timestamp}]")
            lines.append(entry.display_text)
            lines.append("")  # Empty line between entries
        text = "\n".join(lines).strip()
        
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
        return text
    
    def export_to_json(self, path: Optional[Path] = None) -> str:
        """Export to JSON string"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get storage statistics"""
        total_words = sum(e.word_count for e in self.entries)
        total_chars = sum(len(e.display_text) for e in self.entries)
        actions = {}
        for e in self.entries:
            actions[e.action] = actions.get(e.action, 0) + 1
        
        return {
            "total_transcriptions": len(self.entries),
            "total_words": total_words,
            "total_characters": total_chars,
            "action_breakdown": actions,
            "session_start": self.session_start
        }
    
    def filter(self) -> "FilterBuilder":
        """Create a new filter builder for chainable filtering"""
        return FilterBuilder(self.entries)


class FilterBuilder:
    """Chainable filter builder for transcriptions"""
    
    def __init__(self, entries: List[TranscriptionEntry]):
        self._entries = entries
        self._filters: List[callable] = []
    
    def date_range(self, start: datetime, end: datetime) -> "FilterBuilder":
        """Filter by date range (inclusive)"""
        start_ts = start.timestamp()
        end_ts = end.timestamp()
        self._filters.append(lambda e: start_ts <= e.timestamp_unix <= end_ts)
        return self
    
    def last_n_days(self, days: int) -> "FilterBuilder":
        """Filter by last N days"""
        end = datetime.now()
        start = end - timedelta(days=days)
        return self.date_range(start, end)
    
    def tags(self, tags: List[str], match_any: bool = False) -> "FilterBuilder":
        """Filter by tags (AND by default, OR if match_any=True)"""
        if match_any:
            self._filters.append(lambda e: any(t in (e.tags or []) for t in tags))
        else:
            self._filters.append(lambda e: all(t in (e.tags or []) for t in tags))
        return self
    
    def language(self, language: str) -> "FilterBuilder":
        """Filter by language code"""
        self._filters.append(lambda e: e.language == language)
        return self
    
    def quality_above(self, threshold: float) -> "FilterBuilder":
        """Filter by minimum quality score"""
        self._filters.append(lambda e: e.quality_score >= threshold)
        return self
    
    def quality_range(self, min_q: float, max_q: float) -> "FilterBuilder":
        """Filter by quality score range (inclusive)"""
        self._filters.append(lambda e: min_q <= e.quality_score <= max_q)
        return self
    
    def min_words(self, count: int) -> "FilterBuilder":
        """Filter by minimum word count"""
        self._filters.append(lambda e: e.word_count >= count)
        return self
    
    def word_count_range(self, min_w: int, max_w: int) -> "FilterBuilder":
        """Filter by word count range (inclusive)"""
        self._filters.append(lambda e: min_w <= e.word_count <= max_w)
        return self
    
    def app(self, app_name: str) -> "FilterBuilder":
        """Filter by source application name"""
        self._filters.append(lambda e: e.app_name == app_name)
        return self
    
    def execute(self) -> List[TranscriptionEntry]:
        """Apply all filters and return matching entries"""
        result = self._entries
        for f in self._filters:
            result = [e for e in result if f(e)]
        return result
    
    def count(self) -> int:
        """Return count of matching entries"""
        return len(self.execute())


# Global store instance
_store: Optional[TranscriptionStore] = None


def get_store() -> TranscriptionStore:
    """Get or create the global transcription store"""
    global _store
    if _store is None:
        _store = TranscriptionStore.load()
    return _store


def save_store() -> None:
    """Save the global store to disk"""
    global _store
    if _store is not None:
        _store.save()


def add_transcription(original_text: str, processed_text: str = "",
                      action: str = "append", tags: List[str] = None,
                      app_name: str = "", language: str = "",
                      model_used: str = "", duration: float = 0.0,
                      wpm: float = 0.0, quality_score: float = 0.0,
                      cleanup_applied: bool = False, correction_source: str = "",
                      ambiguity_flag: bool = False,
                      transcription_confidence: float = 0.0) -> TranscriptionEntry:
    """Convenience function to add a transcription"""
    store = get_store()
    entry = store.add_entry(
        original_text, processed_text, action,
        tags=tags, app_name=app_name, language=language,
        model_used=model_used, duration=duration,
        wpm=wpm, quality_score=quality_score,
        cleanup_applied=cleanup_applied,
        correction_source=correction_source,
        ambiguity_flag=ambiguity_flag,
        transcription_confidence=transcription_confidence,
    )
    save_store()
    return entry


def get_transcriptions(count: int = 10) -> List[TranscriptionEntry]:
    """Get recent transcriptions"""
    return get_store().get_recent(count)


def search_transcriptions(query: str) -> List[TranscriptionEntry]:
    """Search transcriptions"""
    return get_store().search(query)


def export_all_to_text(path: Optional[Path] = None, 
                       include_metadata: bool = False) -> str:
    """Export all transcriptions to text file"""
    return get_store().export_to_text(path, include_metadata)


def clear_all_transcriptions() -> None:
    """Clear all transcriptions"""
    store = get_store()
    store.clear_session()
    save_store()


def get_storage_info() -> Dict[str, Any]:
    """Get storage location and statistics"""
    store = get_store()
    return {
        "storage_path": str(get_transcriptions_path()),
        "statistics": store.get_statistics()
    }


# ============================================================================
# Dashboard Aggregation Methods with Caching
# ============================================================================

# Simple cache with 5-minute TTL
_aggregation_cache: Dict[str, tuple] = {}
_CACHE_TTL = 300  # 5 minutes in seconds


def _get_cached(key: str) -> Optional[Any]:
    """Get cached value if not expired"""
    if key in _aggregation_cache:
        value, timestamp = _aggregation_cache[key]
        if time.time() - timestamp < _CACHE_TTL:
            return value
    return None


def _set_cached(key: str, value: Any):
    """Set cached value with current timestamp"""
    _aggregation_cache[key] = (value, time.time())


def invalidate_cache():
    """Invalidate all cached aggregation results"""
    global _aggregation_cache
    _aggregation_cache = {}


def get_transcription_count_by_date(start_date: datetime, end_date: datetime) -> int:
    """Get count of transcriptions within date range"""
    cache_key = f"count_{start_date.isoformat()}_{end_date.isoformat()}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached
    
    store = get_store()
    count = sum(
        1 for entry in store.entries
        if start_date.timestamp() <= entry.timestamp_unix <= end_date.timestamp()
    )
    
    _set_cached(cache_key, count)
    return count


def get_total_word_count(start_date: datetime, end_date: datetime) -> int:
    """Get total word count within date range"""
    cache_key = f"words_{start_date.isoformat()}_{end_date.isoformat()}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached
    
    store = get_store()
    total = sum(
        entry.word_count for entry in store.entries
        if start_date.timestamp() <= entry.timestamp_unix <= end_date.timestamp()
    )
    
    _set_cached(cache_key, total)
    return total


def get_average_wpm(start_date: datetime, end_date: datetime) -> float:
    """Get average words per minute within date range"""
    cache_key = f"wpm_{start_date.isoformat()}_{end_date.isoformat()}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached
    
    store = get_store()
    entries_in_range = [
        entry for entry in store.entries
        if start_date.timestamp() <= entry.timestamp_unix <= end_date.timestamp()
        and entry.wpm > 0
    ]
    
    if not entries_in_range:
        return 0.0
    
    avg = sum(entry.wpm for entry in entries_in_range) / len(entries_in_range)
    _set_cached(cache_key, avg)
    return avg


def get_quality_distribution() -> Dict[str, int]:
    """Get distribution of quality scores (Excellent, Good, Fair, Poor)"""
    cache_key = "quality_dist"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached
    
    store = get_store()
    distribution = {
        "excellent": 0,  # > 0.9
        "good": 0,       # 0.7 - 0.9
        "fair": 0,       # 0.5 - 0.7
        "poor": 0,       # < 0.5
    }
    
    for entry in store.entries:
        score = entry.quality_score
        if score > 0.9:
            distribution["excellent"] += 1
        elif score >= 0.7:
            distribution["good"] += 1
        elif score >= 0.5:
            distribution["fair"] += 1
        else:
            distribution["poor"] += 1
    
    _set_cached(cache_key, distribution)
    return distribution


def get_recent_transcriptions(limit: int = 5) -> List[TranscriptionEntry]:
    """Get most recent transcriptions"""
    store = get_store()
    sorted_entries = sorted(store.entries, key=lambda e: e.timestamp_unix, reverse=True)
    return sorted_entries[:limit]


def get_transcriptions_by_day(days: int = 7) -> Dict[str, int]:
    """Get transcription count per day for last N days"""
    cache_key = f"by_day_{days}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached
    
    store = get_store()
    now = datetime.now()
    result = {}
    
    for i in range(days):
        day = now - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        count = sum(
            1 for entry in store.entries
            if day_start.timestamp() <= entry.timestamp_unix <= day_end.timestamp()
        )
        
        result[day.strftime("%Y-%m-%d")] = count
    
    _set_cached(cache_key, result)
    return result


if __name__ == "__main__":
    # Demo/test of the transcription store
    store = get_store()
    print(f"Transcription Store Demo")
    print(f"Storage location: {get_transcriptions_path()}")
    print(f"Current entries: {len(store.entries)}")
    
    # Add a demo entry
    add_transcription("Hello world", "Hello world", "append")
    print(f"After adding demo: {len(store.entries)} entries")
    
    # Show statistics
    stats = store.get_statistics()
    print(f"Stats: {stats}")
