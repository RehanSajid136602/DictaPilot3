"""
Transcription Categories Module
Provides category/folder organization for transcriptions.

Categories allow organizing transcriptions beyond simple tags.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from transcription_store import TranscriptionEntry, get_store, save_store


@dataclass
class Category:
    """Category for organizing transcriptions"""
    name: str
    description: str = ""
    entry_ids: List[str] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.entry_ids is None:
            self.entry_ids = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'entry_ids': self.entry_ids,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Category":
        return cls(
            name=data.get('name', ''),
            description=data.get('description', ''),
            entry_ids=data.get('entry_ids', []),
            created_at=data.get('created_at')
        )
    
    @property
    def entry_count(self) -> int:
        return len(self.entry_ids)


def _ensure_categories() -> Dict[str, Dict[str, Any]]:
    """Ensure categories dict exists in store"""
    store = get_store()
    if not hasattr(store, 'categories') or store.categories is None:
        store.categories = {}
    return store.categories


def create_category(name: str, description: str = "") -> Category:
    """
    Create a new category.
    
    Args:
        name: Category name
        description: Optional description
    
    Returns:
        Created Category
    
    Raises:
        ValueError: If category already exists
    """
    categories = _ensure_categories()
    
    if name in categories:
        raise ValueError(f"Category '{name}' already exists")
    
    category = Category(name=name, description=description)
    categories[name] = category.to_dict()
    save_store()
    
    return category


def get_category(name: str) -> Optional[Category]:
    """Get a category by name"""
    categories = _ensure_categories()
    if name in categories:
        return Category.from_dict(categories[name])
    return None


def get_all_categories() -> List[Category]:
    """Get all categories"""
    categories = _ensure_categories()
    return [Category.from_dict(c) for c in categories.values()]


def add_to_category(
    transcription_ids: List[str],
    category_name: str
) -> int:
    """
    Add transcriptions to a category.
    
    Args:
        transcription_ids: Single ID or list of IDs to add
        category_name: Name of category
    
    Returns:
        Number of entries added
    
    Raises:
        ValueError: If category doesn't exist or entry not found
    """
    categories = _ensure_categories()
    
    if category_name not in categories:
        raise ValueError(f"Category '{category_name}' does not exist")
    
    # Handle single ID
    if isinstance(transcription_ids, str):
        transcription_ids = [transcription_ids]
    
    store = get_store()
    entry_ids = set(categories[category_name]['entry_ids'])
    added = 0
    
    for tid in transcription_ids:
        # Verify entry exists
        if any(e.id == tid for e in store.entries):
            if tid not in entry_ids:
                entry_ids.add(tid)
                added += 1
    
    categories[category_name]['entry_ids'] = list(entry_ids)
    save_store()
    
    return added


def remove_from_category(
    transcription_ids: List[str],
    category_name: str
) -> int:
    """
    Remove transcriptions from a category.
    
    Args:
        transcription_ids: Single ID or list of IDs to remove
        category_name: Name of category
    
    Returns:
        Number of entries removed
    
    Raises:
        ValueError: If category doesn't exist
    """
    categories = _ensure_categories()
    
    if category_name not in categories:
        raise ValueError(f"Category '{category_name}' does not exist")
    
    # Handle single ID
    if isinstance(transcription_ids, str):
        transcription_ids = [transcription_ids]
    
    entry_ids = set(categories[category_name]['entry_ids'])
    removed = 0
    
    for tid in transcription_ids:
        if tid in entry_ids:
            entry_ids.remove(tid)
            removed += 1
    
    categories[category_name]['entry_ids'] = list(entry_ids)
    save_store()
    
    return removed


def get_category_entries(category_name: str) -> List[TranscriptionEntry]:
    """
    Get all transcriptions in a category.
    
    Args:
        category_name: Name of category
    
    Returns:
        List of TranscriptionEntry objects in the category
    
    Raises:
        ValueError: If category doesn't exist
    """
    categories = _ensure_categories()
    
    if category_name not in categories:
        raise ValueError(f"Category '{category_name}' does not exist")
    
    entry_ids = set(categories[category_name]['entry_ids'])
    store = get_store()
    
    return [e for e in store.entries if e.id in entry_ids]


def delete_category(name: str, keep_entries: bool = True) -> bool:
    """
    Delete a category.
    
    Args:
        name: Category name
        keep_entries: If True, keep transcription entries (just unlink)
    
    Returns:
        True if deleted, False if not found
    """
    categories = _ensure_categories()
    
    if name not in categories:
        return False
    
    del categories[name]
    save_store()
    
    return True


def rename_category(old_name: str, new_name: str) -> bool:
    """
    Rename a category.
    
    Args:
        old_name: Current category name
        new_name: New category name
    
    Returns:
        True if renamed, False if old doesn't exist or new already exists
    
    Raises:
        ValueError: If new_name already exists
    """
    categories = _ensure_categories()
    
    if old_name not in categories:
        return False
    
    if new_name in categories:
        raise ValueError(f"Category '{new_name}' already exists")
    
    categories[new_name] = categories.pop(old_name)
    categories[new_name]['name'] = new_name
    save_store()
    
    return True


def get_category_stats() -> Dict[str, Dict[str, Any]]:
    """
    Get statistics for all categories.
    
    Returns:
        Dict mapping category name to stats (entry_count, total_words)
    """
    categories = _ensure_categories()
    store = get_store()
    
    stats = {}
    for name, cat_data in categories.items():
        entry_ids = set(cat_data['entry_ids'])
        entries = [e for e in store.entries if e.id in entry_ids]
        
        stats[name] = {
            'entry_count': len(entries),
            'total_words': sum(e.word_count for e in entries),
            'description': cat_data.get('description', ''),
            'created_at': cat_data.get('created_at', '')
        }
    
    return stats


# Convenience functions

def list_categories() -> List[str]:
    """List all category names"""
    categories = _ensure_categories()
    return list(categories.keys())


def category_exists(name: str) -> bool:
    """Check if category exists"""
    categories = _ensure_categories()
    return name in categories


if __name__ == "__main__":
    # Demo
    print("Categories Demo")
    
    # Create a test category
    try:
        cat = create_category("Work", "Work-related transcriptions")
        print(f"Created category: {cat.name}")
    except ValueError as e:
        print(f"Category creation: {e}")
    
    # List categories
    print(f"Categories: {list_categories()}")
    
    # Get stats
    stats = get_category_stats()
    print(f"Stats: {stats}")
