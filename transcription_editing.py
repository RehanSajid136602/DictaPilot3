"""
Transcription Editing Module
Provides editing capabilities with version history and rollback.

Supports editing transcriptions with automatic version tracking.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from transcription_store import TranscriptionEntry, get_store, save_store


MAX_EDIT_HISTORY = 5  # Maximum versions to keep


def _validate_text(text: str) -> bool:
    """Validate that text is not empty"""
    if text is None:
        return False
    if isinstance(text, str) and text.strip() == "":
        return False
    return True


def _validate_tags(tags: Any) -> bool:
    """Validate that tags is a list"""
    return isinstance(tags, list)


def _create_history_entry(
    original_text: str = None,
    processed_text: str = None,
    tags: List[str] = None,
    language: str = None
) -> Dict[str, Any]:
    """Create a history entry for edit tracking"""
    return {
        'timestamp': datetime.now().isoformat(),
        'original_text': original_text,
        'processed_text': processed_text,
        'tags': tags,
        'language': language
    }


def edit_transcription(
    entry_id: str,
    original_text: str = None,
    processed_text: str = None,
    tags: List[str] = None,
    language: str = None,
    app_name: str = None,
    save: bool = True
) -> TranscriptionEntry:
    """
    Edit a transcription entry with version history.
    
    Args:
        entry_id: ID of entry to edit
        original_text: New original text (optional)
        processed_text: New processed text (optional)
        tags: New tags list (optional)
        language: New language (optional)
        app_name: New app name (optional)
        save: Whether to save after editing (default True)
    
    Returns:
        Updated TranscriptionEntry
    
    Raises:
        ValueError: If entry not found or validation fails
    """
    store = get_store()
    
    # Find entry
    entry = None
    for e in store.entries:
        if e.id == entry_id:
            entry = e
            break
    
    if entry is None:
        raise ValueError(f"Entry not found: {entry_id}")
    
    # Validate inputs
    if original_text is not None and not _validate_text(original_text):
        raise ValueError("original_text cannot be empty")
    if processed_text is not None and not _validate_text(processed_text):
        raise ValueError("processed_text cannot be empty")
    if tags is not None and not _validate_tags(tags):
        raise ValueError("tags must be a list")
    
    # Create history entry before making changes
    history_entry = _create_history_entry(
        original_text=entry.original_text,
        processed_text=entry.processed_text,
        tags=entry.tags,
        language=entry.language
    )
    
    # Initialize edit_history if needed
    if entry.edit_history is None:
        entry.edit_history = []
    
    # Add to history (keeping only last MAX_EDIT_HISTORY)
    entry.edit_history.append(history_entry)
    if len(entry.edit_history) > MAX_EDIT_HISTORY:
        entry.edit_history = entry.edit_history[-MAX_EDIT_HISTORY:]
    
    # Apply changes
    if original_text is not None:
        entry.original_text = original_text
        # Recalculate word count
        entry.word_count = len(original_text.split())
    
    if processed_text is not None:
        entry.processed_text = processed_text
    
    if tags is not None:
        entry.tags = tags
    
    if language is not None:
        entry.language = language
    
    if app_name is not None:
        entry.app_name = app_name
    
    if save:
        save_store()
    
    return entry


def get_edit_history(entry_id: str) -> List[Dict[str, Any]]:
    """
    Get edit history for a transcription.
    
    Args:
        entry_id: ID of entry
    
    Returns:
        List of history entries (oldest first)
    
    Raises:
        ValueError: If entry not found
    """
    store = get_store()
    
    for e in store.entries:
        if e.id == entry_id:
            return list(e.edit_history or [])
    
    raise ValueError(f"Entry not found: {entry_id}")


def rollback(
    entry_id: str,
    version: int = -1,
    save: bool = True
) -> TranscriptionEntry:
    """
    Rollback to a previous version.
    
    Args:
        entry_id: ID of entry to rollback
        version: Version to rollback to (default -1 = most recent)
        save: Whether to save after rollback (default True)
    
    Returns:
        Updated TranscriptionEntry with new history entry
    
    Raises:
        ValueError: If entry not found or version invalid
    """
    store = get_store()
    
    # Find entry
    entry = None
    for e in store.entries:
        if e.id == entry_id:
            entry = e
            break
    
    if entry is None:
        raise ValueError(f"Entry not found: {entry_id}")
    
    # Get history
    history = entry.edit_history or []
    
    if not history:
        raise ValueError("No edit history available")
    
    # Get target version (handle negative index)
    if version < 0:
        version = len(history) + version
    
    if version < 0 or version >= len(history):
        raise ValueError(f"Invalid version: {version}")
    
    # Get historical state
    historical = history[version]
    
    # Create history entry documenting the rollback
    rollback_entry = _create_history_entry(
        original_text=entry.original_text,
        processed_text=entry.processed_text,
        tags=entry.tags,
        language=entry.language
    )
    rollback_entry['action'] = 'rollback'
    rollback_entry['rolled_back_to'] = version
    
    # Apply historical state
    if historical.get('original_text') is not None:
        entry.original_text = historical['original_text']
        entry.word_count = len(historical['original_text'].split())
    
    if historical.get('processed_text') is not None:
        entry.processed_text = historical['processed_text']
    
    if historical.get('tags') is not None:
        entry.tags = historical['tags']
    
    if historical.get('language') is not None:
        entry.language = historical['language']
    
    # Add rollback to history
    entry.edit_history.append(rollback_entry)
    if len(entry.edit_history) > MAX_EDIT_HISTORY:
        entry.edit_history = entry.edit_history[-MAX_EDIT_HISTORY:]
    
    if save:
        save_store()
    
    return entry


def bulk_edit(
    entry_ids: List[str],
    tags: List[str] = None,
    language: str = None,
    app_name: str = None,
    save: bool = True
) -> Dict[str, Any]:
    """
    Edit multiple transcriptions at once.
    
    Args:
        entry_ids: List of entry IDs to edit
        tags: New tags for all entries (optional)
        language: New language for all entries (optional)
        app_name: New app name for all entries (optional)
        save: Whether to save after editing (default True)
    
    Returns:
        Dict with 'updated' and 'failed' counts
    """
    store = get_store()
    
    updated = 0
    failed = 0
    
    for entry_id in entry_ids:
        try:
            edit_transcription(
                entry_id,
                tags=tags,
                language=language,
                app_name=app_name,
                save=False  # Don't save individually
            )
            updated += 1
        except ValueError:
            failed += 1
    
    if save and updated > 0:
        save_store()
    
    return {
        'updated': updated,
        'failed': failed,
        'total': len(entry_ids)
    }


def bulk_delete(
    entry_ids: List[str],
    save: bool = True
) -> Dict[str, Any]:
    """
    Delete multiple transcriptions at once.
    
    Args:
        entry_ids: List of entry IDs to delete
        save: Whether to save after deleting (default True)
    
    Returns:
        Dict with 'deleted' and 'failed' counts
    """
    store = get_store()
    
    deleted = 0
    failed = 0
    
    for entry_id in entry_ids:
        original_count = len(store.entries)
        store.entries = [e for e in store.entries if e.id != entry_id]
        
        if len(store.entries) < original_count:
            deleted += 1
        else:
            failed += 1
    
    if save and deleted > 0:
        save_store()
    
    return {
        'deleted': deleted,
        'failed': failed,
        'total': len(entry_ids)
    }


if __name__ == "__main__":
    # Demo
    print("Editing Module Demo")
    store = get_store()
    print(f"Total entries: {len(store.entries)}")
    
    # Demo editing
    if store.entries:
        entry = store.entries[0]
        print(f"\nEditing entry: {entry.id}")
        
        # Show current state
        print(f"Original: {entry.original_text[:50]}...")
        print(f"Tags: {entry.tags}")
        
        # Make an edit
        edited = edit_transcription(
            entry.id,
            processed_text=entry.processed_text + " [edited]"
        )
        print(f"After edit: {edited.processed_text[-20:]}")
        
        # Get history
        history = get_edit_history(entry.id)
        print(f"History entries: {len(history)}")
