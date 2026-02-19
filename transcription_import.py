"""
Transcription Import Module
Provides import capabilities for transcriptions from external JSON files.

Supports deduplication, conflict resolution, and merge modes.
"""

import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from transcription_store import (
    TranscriptionEntry, 
    TranscriptionStore, 
    get_store, 
    save_store
)


def _compute_content_hash(entry_data: Dict[str, Any]) -> str:
    """Compute hash from timestamp and content for deduplication"""
    content = f"{entry_data.get('timestamp', '')}:{entry_data.get('original_text', '')}:{entry_data.get('processed_text', '')}"
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def _validate_entry(entry_data: Dict[str, Any]) -> bool:
    """Validate entry has required fields"""
    required = ['id', 'timestamp', 'original_text']
    for field in required:
        if field not in entry_data:
            return False
    return True


def import_from_json(
    path: Path,
    generate_new_ids: bool = False,
    deduplicate: bool = True,
    on_conflict: str = 'skip',  # 'skip', 'overwrite', 'keep_both'
    merge: bool = True,
    validate: bool = True
) -> Dict[str, Any]:
    """
    Import transcriptions from a JSON file.
    
    Args:
        path: Path to JSON file to import
        generate_new_ids: If True, generate new UUIDs for all entries
        deduplicate: If True, skip entries with same timestamp+content hash
        on_conflict: Strategy for handling conflicts ('skip', 'overwrite', 'keep_both')
        merge: If True, append to existing entries; if False, replace all
        validate: If True, validate entries before importing
    
    Returns:
        Dict with 'imported', 'skipped', 'errors' counts and details
    
    Raises:
        ValueError: If file is invalid or validation fails
    """
    # Load and parse JSON
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON file: {e}")
    except FileNotFoundError:
        raise ValueError(f"File not found: {path}")
    
    # Handle different JSON formats
    if isinstance(data, dict):
        if 'entries' in data:
            entries_data = data['entries']
        else:
            entries_data = [data]
    elif isinstance(data, list):
        entries_data = data
    else:
        raise ValueError("Invalid JSON format: expected dict or list")
    
    # Validate entries
    if validate:
        invalid_entries = [i for i, e in enumerate(entries_data) if not _validate_entry(e)]
        if invalid_entries:
            raise ValueError(f"Invalid entries at indices: {invalid_entries}")
    
    # Get store
    store = get_store()
    
    # Clear existing if not merging
    if not merge:
        store.entries = []
    
    # Track stats
    imported = 0
    skipped = 0
    errors = 0
    seen_hashes = set() if deduplicate else None
    
    # Build existing entry lookup for conflict resolution
    existing_by_id = {e.id: e for e in store.entries} if on_conflict != 'keep_both' else {}
    
    # Import entries
    new_entries = []
    for entry_data in entries_data:
        try:
            entry_id = entry_data.get('id', '')
            
            # Handle deduplication
            if deduplicate:
                content_hash = _compute_content_hash(entry_data)
                if content_hash in seen_hashes:
                    skipped += 1
                    continue
                seen_hashes.add(content_hash)
            
            # Handle ID conflicts
            if entry_id in existing_by_id:
                if on_conflict == 'skip':
                    skipped += 1
                    continue
                elif on_conflict == 'overwrite':
                    # Remove existing entry
                    store.entries = [e for e in store.entries if e.id != entry_id]
                elif on_conflict == 'keep_both':
                    # Generate new ID
                    entry_data['id'] = str(uuid.uuid4())[:8]
            
            # Generate new ID if needed
            if generate_new_ids:
                entry_data['id'] = str(uuid.uuid4())[:8]
            
            # Create entry
            entry = TranscriptionEntry.from_dict(entry_data)
            new_entries.append(entry)
            imported += 1
            
        except Exception as e:
            errors += 1
    
    # Add new entries to store
    store.entries.extend(new_entries)
    
    # Save store
    save_store()
    
    return {
        'imported': imported,
        'skipped': skipped,
        'errors': errors,
        'total': len(entries_data)
    }


def import_from_json_string(
    json_string: str,
    generate_new_ids: bool = False,
    deduplicate: bool = True,
    on_conflict: str = 'skip',
    merge: bool = True,
    validate: bool = True
) -> Dict[str, Any]:
    """
    Import transcriptions from a JSON string.
    
    Args:
        json_string: JSON string to import
        generate_new_ids: If True, generate new UUIDs for all entries
        deduplicate: If True, skip entries with same timestamp+content hash
        on_conflict: Strategy for handling conflicts ('skip', 'overwrite', 'keep_both')
        merge: If True, append to existing entries; if False, replace all
        validate: If True, validate entries before importing
    
    Returns:
        Dict with 'imported', 'skipped', 'errors' counts and details
    
    Raises:
        ValueError: If JSON is invalid or validation fails
    """
    try:
        data = json.loads(json_string)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON string: {e}")
    
    # Handle different JSON formats
    if isinstance(data, dict):
        if 'entries' in data:
            entries_data = data['entries']
        else:
            entries_data = [data]
    elif isinstance(data, list):
        entries_data = data
    else:
        raise ValueError("Invalid JSON format: expected dict or list")
    
    # Write to temp file and use import_from_json
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(json_string)
        temp_path = Path(f.name)
    
    try:
        result = import_from_json(
            temp_path,
            generate_new_ids=generate_new_ids,
            deduplicate=deduplicate,
            on_conflict=on_conflict,
            merge=merge,
            validate=validate
        )
    finally:
        temp_path.unlink()
    
    return result


def export_and_reimport(
    source_path: Path,
    backup_path: Optional[Path] = None,
    **import_kwargs
) -> Dict[str, Any]:
    """
    Export current store, then import from source, creating a backup.
    
    This is useful for testing import functionality.
    
    Args:
        source_path: Path to import from
        backup_path: Optional path for backup (default: backup.json in same dir)
        **import_kwargs: Additional arguments passed to import_from_json
    
    Returns:
        Import result dict
    """
    store = get_store()
    
    # Create backup
    if backup_path is None:
        backup_path = source_path.parent / 'backup.json'
    
    backup_data = store.export_to_json()
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(backup_data)
    
    # Import
    return import_from_json(source_path, **import_kwargs)


if __name__ == "__main__":
    # Demo
    print("Import Module Demo")
    store = get_store()
    print(f"Current entries: {len(store.entries)}")
    
    # Show sample import result structure
    print("\nImport result structure:")
    print("{'imported': 0, 'skipped': 0, 'errors': 0, 'total': 0}")