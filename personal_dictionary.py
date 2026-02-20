"""
DictaPilot Personal Dictionary Module
Handles persistent storage of user-specific words with frequency tracking.

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
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict


def get_dictionary_path() -> Path:
    """Get platform-specific personal dictionary database path"""
    system = platform.system()
    
    if system == "Windows":
        data_dir = Path(os.environ.get("APPDATA", ""))
        return data_dir / "DictaPilot" / "personal_dictionary.db"
    else:
        data_dir = Path(os.path.expanduser("~/.local/share"))
        return data_dir / "dictapilot" / "personal_dictionary.db"


def get_dictionary_dir() -> Path:
    """Create and return dictionary directory"""
    dictionary_path = get_dictionary_path()
    dictionary_path.parent.mkdir(parents=True, exist_ok=True)
    return dictionary_path.parent


@dataclass
class DictionaryEntry:
    """Single personal dictionary entry"""
    word: str
    frequency: int
    source: str  # "auto_learned" or "manual"
    created_at: str
    last_used: str
    tags: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        if result['tags'] is None:
            result['tags'] = []
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DictionaryEntry":
        if data.get('tags') is None:
            data['tags'] = []
        return cls(**data)


class PersonalDictionary:
    """Personal dictionary with auto-learning and frequency tracking"""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or get_dictionary_path()
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Create database and table if they don't exist"""
        get_dictionary_dir()
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS personal_dictionary (
                word TEXT PRIMARY KEY,
                frequency INTEGER DEFAULT 1,
                source TEXT DEFAULT 'manual',
                created_at TEXT NOT NULL,
                last_used TEXT NOT NULL,
                tags TEXT DEFAULT '[]'
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_frequency 
            ON personal_dictionary(frequency DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_last_used 
            ON personal_dictionary(last_used DESC)
        """)
        
        conn.commit()
        conn.close()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        return sqlite3.connect(str(self.db_path))
    
    def add_word(self, word: str, source: str = "manual", 
                 frequency: int = 1, tags: Optional[List[str]] = None) -> bool:
        """Add a word to the personal dictionary"""
        word = word.strip().lower()
        if not word:
            return False
        
        now = datetime.now().isoformat()
        tags_json = json.dumps(tags or [])
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO personal_dictionary (word, frequency, source, created_at, last_used, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (word, frequency, source, now, now, tags_json))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Word already exists, update frequency
            cursor.execute("""
                UPDATE personal_dictionary 
                SET frequency = frequency + 1, last_used = ?
                WHERE word = ?
            """, (now, word))
            conn.commit()
            return False
        finally:
            conn.close()
    
    def add_words_bulk(self, words: List[Dict[str, Any]]) -> int:
        """Add multiple words at once"""
        now = datetime.now().isoformat()
        conn = self._get_connection()
        cursor = conn.cursor()
        
        added = 0
        for item in words:
            word = item.get('word', '').strip().lower()
            if not word:
                continue
            
            frequency = item.get('frequency', 1)
            source = item.get('source', 'manual')
            tags = json.dumps(item.get('tags', []))
            
            try:
                cursor.execute("""
                    INSERT INTO personal_dictionary (word, frequency, source, created_at, last_used, tags)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (word, frequency, source, now, now, tags))
                added += 1
            except sqlite3.IntegrityError:
                # Update existing
                cursor.execute("""
                    UPDATE personal_dictionary 
                    SET frequency = MAX(frequency, ?), last_used = ?
                    WHERE word = ? AND frequency < ?
                """, (frequency, now, word, frequency))
        
        conn.commit()
        conn.close()
        return added
    
    def get_word(self, word: str) -> Optional[DictionaryEntry]:
        """Get a specific word from the dictionary"""
        word = word.strip().lower()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT word, frequency, source, created_at, last_used, tags
            FROM personal_dictionary
            WHERE word = ?
        """, (word,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return DictionaryEntry(
                word=row[0],
                frequency=row[1],
                source=row[2],
                created_at=row[3],
                last_used=row[4],
                tags=json.loads(row[5])
            )
        return None
    
    def get_all_words(self, sort_by: str = "frequency") -> List[DictionaryEntry]:
        """Get all words from the dictionary"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        order = "frequency DESC" if sort_by == "frequency" else "last_used DESC"
        
        cursor.execute(f"""
            SELECT word, frequency, source, created_at, last_used, tags
            FROM personal_dictionary
            ORDER BY {order}
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            DictionaryEntry(
                word=row[0],
                frequency=row[1],
                source=row[2],
                created_at=row[3],
                last_used=row[4],
                tags=json.loads(row[5])
            )
            for row in rows
        ]
    
    def update_word(self, word: str, frequency: Optional[int] = None,
                   tags: Optional[List[str]] = None) -> bool:
        """Update a word in the dictionary"""
        word = word.strip().lower()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if frequency is not None:
            updates.append("frequency = ?")
            params.append(frequency)
        
        if tags is not None:
            updates.append("tags = ?")
            params.append(json.dumps(tags))
        
        if not updates:
            return False
        
        updates.append("last_used = ?")
        params.append(datetime.now().isoformat())
        params.append(word)
        
        cursor.execute(f"""
            UPDATE personal_dictionary 
            SET {', '.join(updates)}
            WHERE word = ?
        """, params)
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def delete_word(self, word: str) -> bool:
        """Delete a word from the dictionary"""
        word = word.strip().lower()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM personal_dictionary WHERE word = ?", (word,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def increment_frequency(self, word: str) -> bool:
        """Increment usage frequency for a word"""
        word = word.strip().lower()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE personal_dictionary 
            SET frequency = frequency + 1, last_used = ?
            WHERE word = ?
        """, (datetime.now().isoformat(), word))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def search_words(self, query: str, limit: int = 20) -> List[DictionaryEntry]:
        """Search words in the dictionary"""
        query = query.strip().lower()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT word, frequency, source, created_at, last_used, tags
            FROM personal_dictionary
            WHERE word LIKE ?
            ORDER BY frequency DESC
            LIMIT ?
        """, (f"%{query}%", limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            DictionaryEntry(
                word=row[0],
                frequency=row[1],
                source=row[2],
                created_at=row[3],
                last_used=row[4],
                tags=json.loads(row[5])
            )
            for row in rows
        ]
    
    def word_exists(self, word: str) -> bool:
        """Check if a word exists in the dictionary"""
        word = word.strip().lower()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM personal_dictionary WHERE word = ?", (word,))
        exists = cursor.fetchone() is not None
        conn.close()
        
        return exists
    
    def get_all_words_set(self) -> set:
        """Get all words as a set for fast lookup"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT word FROM personal_dictionary")
        words = {row[0] for row in cursor.fetchall()}
        conn.close()
        
        return words
    
    def export_to_json(self, filepath: Optional[Path] = None) -> Dict[str, Any]:
        """Export dictionary to JSON format"""
        words = self.get_all_words()
        
        export_data = {
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "word_count": len(words),
            "words": [word.to_dict() for word in words]
        }
        
        if filepath:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return export_data
    
    def import_from_json(self, filepath: Path) -> Dict[str, int]:
        """Import dictionary from JSON file"""
        filepath = Path(filepath)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        words = import_data.get('words', [])
        
        added = 0
        updated = 0
        
        for word_data in words:
            word = word_data.get('word', '').strip().lower()
            if not word:
                continue
            
            existing = self.get_word(word)
            
            if existing:
                # Update if imported frequency is higher
                if word_data.get('frequency', 0) > existing.frequency:
                    self.update_word(word, frequency=word_data['frequency'])
                    updated += 1
            else:
                self.add_word(
                    word=word,
                    source=word_data.get('source', 'manual'),
                    frequency=word_data.get('frequency', 1),
                    tags=word_data.get('tags', [])
                )
                added += 1
        
        return {"added": added, "updated": updated, "total": len(words)}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get dictionary statistics"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*), SUM(frequency), AVG(frequency) FROM personal_dictionary")
        row = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) FROM personal_dictionary WHERE source = 'auto_learned'")
        auto_learned = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM personal_dictionary WHERE source = 'manual'")
        manual = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_words": row[0] or 0,
            "total_uses": row[1] or 0,
            "average_frequency": round(row[2] or 0, 2),
            "auto_learned": auto_learned,
            "manual": manual
        }
    
    def clear_all(self) -> bool:
        """Clear all words from dictionary (use with caution)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM personal_dictionary")
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success


# Global instance for easy access
_dictionary_instance: Optional[PersonalDictionary] = None


def get_personal_dictionary() -> PersonalDictionary:
    """Get or create the global personal dictionary instance"""
    global _dictionary_instance
    if _dictionary_instance is None:
        _dictionary_instance = PersonalDictionary()
    return _dictionary_instance
