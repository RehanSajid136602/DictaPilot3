import re
import difflib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from transcription_store import TranscriptionEntry, get_store


@dataclass
class SearchResult:
    """Search result with relevance score and highlighting"""
    entry: TranscriptionEntry
    score: float
    highlights: List[str]
    
    def __repr__(self):
        return f"SearchResult(score={self.score:.2f}, entry={self.entry.id})"


class SearchBuilder:
    """Builder for complex search queries with operators"""
    
    def __init__(self, entries: List[TranscriptionEntry]):
        self._entries = entries
        self._results: List[SearchResult] = []
        self._current_query = ""
        self._operator = "AND"  # AND, OR, NOT
    
    def search(self, query: str, highlight: bool = True) -> "SearchBuilder":
        """Start a new search query"""
        self._current_query = query
        self._results = self._basic_search(query, highlight)
        return self
    
    def fuzzy(self, query: str, threshold: float = 0.6, highlight: bool = True) -> "SearchBuilder":
        """Fuzzy search with similarity threshold"""
        self._current_query = query
        self._results = self._fuzzy_search(query, threshold, highlight)
        return self
    
    def phrase(self, phrase: str, highlight: bool = True) -> "SearchBuilder":
        """Exact phrase search"""
        self._current_query = phrase
        self._results = self._phrase_search(phrase, highlight)
        return self
    
    def regex(self, pattern: str, highlight: bool = True) -> "SearchBuilder":
        """Regex pattern search"""
        self._current_query = pattern
        self._results = self._regex_search(pattern, highlight)
        return self
    
    def AND(self, query: str) -> "SearchBuilder":
        """Add AND condition"""
        if not self._results:
            return self.search(query)
        
        new_results = self._basic_search(query)
        entry_ids = set(r.entry.id for r in self._results)
        self._results = [r for r in self._results if r.entry.id in entry_ids]
        return self
    
    def OR(self, query: str) -> "SearchBuilder":
        """Add OR condition"""
        if not self._results:
            return self.search(query)
        
        new_results = self._basic_search(query)
        existing_ids = set(r.entry.id for r in self._results)
        
        for nr in new_results:
            if nr.entry.id not in existing_ids:
                self._results.append(nr)
        
        return self
    
    def NOT(self, query: str) -> "SearchBuilder":
        """Add NOT condition"""
        if not self._results:
            return self
        
        exclude_results = self._basic_search(query)
        exclude_ids = set(r.entry.id for r in exclude_results)
        
        self._results = [r for r in self._results if r.entry.id not in exclude_ids]
        return self
    
    def date_range(self, start: datetime, end: datetime) -> "SearchBuilder":
        """Combine with date range filter"""
        if not self._results:
            return self
        
        start_ts = start.timestamp()
        end_ts = end.timestamp()
        
        self._results = [
            r for r in self._results
            if start_ts <= r.entry.timestamp_unix <= end_ts
        ]
        return self
    
    def execute(self) -> List[SearchResult]:
        """Execute search and return sorted results"""
        # Sort by relevance score
        self._results.sort(key=lambda r: r.score, reverse=True)
        return self._results
    
    def _get_text(self, entry: TranscriptionEntry) -> str:
        """Get searchable text from entry"""
        return f"{entry.original_text} {entry.processed_text}"
    
    def _basic_search(self, query: str, highlight: bool = True) -> List[SearchResult]:
        """Basic substring search"""
        if not query:
            return [SearchResult(e, 1.0, []) for e in self._entries]
        
        query_lower = query.lower()
        results = []
        
        for entry in self._entries:
            text = self._get_text(entry).lower()
            if query_lower in text:
                # Calculate simple relevance score
                score = text.count(query_lower) / (len(text) / len(query))
                highlights = [query] if highlight else []
                results.append(SearchResult(entry, min(score, 1.0), highlights))
        
        return results
    
    def _fuzzy_search(
        self, 
        query: str, 
        threshold: float, 
        highlight: bool = True
    ) -> List[SearchResult]:
        """Fuzzy search using difflib"""
        results = []
        query_lower = query.lower()
        
        # Get all words from query for matching
        query_words = query_lower.split()
        
        for entry in self._entries:
            text = self._get_text(entry).lower()
            
            # Use SequenceMatcher for similarity
            matcher = difflib.SequenceMatcher(None, query_lower, text)
            best_ratio = matcher.ratio()
            
            # Also check individual word matches
            text_words = text.split()
            for qw in query_words:
                for tw in text_words:
                    m = difflib.SequenceMatcher(None, qw, tw)
                    best_ratio = max(best_ratio, m.ratio())
            
            if best_ratio >= threshold:
                highlights = [query] if highlight else []
                results.append(SearchResult(entry, best_ratio, highlights))
        
        return results
    
    def _phrase_search(self, phrase: str, highlight: bool = True) -> List[SearchResult]:
        """Exact phrase search"""
        results = []
        phrase_lower = phrase.lower()
        
        for entry in self._entries:
            text = self._get_text(entry).lower()
            if phrase_lower in text:
                highlights = [phrase] if highlight else []
                results.append(SearchResult(entry, 1.0, highlights))
        
        return results
    
    def _regex_search(self, pattern: str, highlight: bool = True) -> List[SearchResult]:
        """Regex pattern search"""
        results = []
        
        try:
            regex = re.compile(pattern, re.IGNORECASE)
        except re.error:
            return []
        
        for entry in self._entries:
            text = self._get_text(entry)
            match = regex.search(text)
            if match:
                # Extract matched groups for highlighting
                highlights = []
                if highlight and match.groups():
                    highlights = list(match.groups())
                elif highlight:
                    highlights = [match.group()]
                
                results.append(SearchResult(entry, 1.0, highlights))
        
        return results


# Convenience functions

def search(query: str) -> List[SearchResult]:
    """Basic search for transcriptions"""
    store = get_store()
    return SearchBuilder(store.entries).search(query).execute()


def fuzzy_search(query: str, threshold: float = 0.6) -> List[SearchResult]:
    """Fuzzy search with similarity threshold"""
    store = get_store()
    return SearchBuilder(store.entries).fuzzy(query, threshold).execute()


def phrase_search(phrase: str) -> List[SearchResult]:
    """Exact phrase search"""
    store = get_store()
    return SearchBuilder(store.entries).phrase(phrase).execute()


def regex_search(pattern: str) -> List[SearchResult]:
    """Regex pattern search"""
    store = get_store()
    return SearchBuilder(store.entries).regex(pattern).execute()


def advanced_search(
    query: str = None,
    fuzzy: bool = False,
    threshold: float = 0.6,
    phrase: bool = False,
    regex: bool = False,
    date_start: datetime = None,
    date_end: datetime = None
) -> List[SearchResult]:
    """
    Advanced search with multiple options.
    
    Args:
        query: Search query
        fuzzy: Use fuzzy matching
        threshold: Similarity threshold for fuzzy (default 0.6)
        phrase: Treat as exact phrase
        regex: Treat as regex pattern
        date_start: Filter by start date
        date_end: Filter by end date
    
    Returns:
        List of SearchResult sorted by relevance
    """
    store = get_store()
    builder = SearchBuilder(store.entries)
    
    if regex:
        builder = builder.regex(query)
    elif phrase:
        builder = builder.phrase(query)
    elif fuzzy:
        builder = builder.fuzzy(query, threshold)
    elif query:
        builder = builder.search(query)
    
    if date_start and date_end:
        builder = builder.date_range(date_start, date_end)
    
    return builder.execute()


if __name__ == "__main__":
    # Demo
    print("Search Module Demo")
    store = get_store()
    print(f"Total entries: {len(store.entries)}")
    
    # Basic search
    if store.entries:
        results = search("hello")
        print(f"\nBasic search 'hello': {len(results)} results")
        if results:
            print(f"Top result score: {results[0].score}")
    
    # Fuzzy search
    if store.entries:
        results = fuzzy_search("helo", threshold=0.6)
        print(f"\nFuzzy search 'helo': {len(results)} results")