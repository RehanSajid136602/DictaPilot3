"""
Transcription Export Module
Provides multi-format export capabilities for transcriptions.

Supports CSV, Markdown, and HTML export formats with customizable options.
"""

import csv
import io
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime

from transcription_store import TranscriptionEntry, TranscriptionStore, get_store


# Default CSV columns
DEFAULT_CSV_COLUMNS = [
    'id', 'timestamp', 'original_text', 'processed_text', 'action',
    'word_count', 'tags', 'app_name', 'language', 'model_used',
    'duration', 'wpm', 'quality_score'
]


def export_to_csv(
    entries: List[TranscriptionEntry],
    path: Optional[Path] = None,
    columns: List[str] = None,
    filters: Dict[str, Any] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> str:
    """
    Export transcriptions to CSV format.
    
    Args:
        entries: List of TranscriptionEntry objects to export
        path: Optional path to save CSV file
        columns: List of column names to include (default: DEFAULT_CSV_COLUMNS)
        filters: Optional filters to apply before export
        progress_callback: Optional callback(completed, total) for progress
    
    Returns:
        CSV string content
    """
    if columns is None:
        columns = DEFAULT_CSV_COLUMNS
    
    # Apply filters if provided
    if filters:
        store = get_store()
        fb = store.filter()
        
        if 'date_range' in filters:
            fb = fb.date_range(filters['date_range'][0], filters['date_range'][1])
        if 'tags' in filters:
            fb = fb.tags(filters['tags'], match_any=filters.get('match_any', False))
        if 'language' in filters:
            fb = fb.language(filters['language'])
        if 'quality_above' in filters:
            fb = fb.quality_above(filters['quality_above'])
        if 'min_words' in filters:
            fb = fb.min_words(filters['min_words'])
        if 'app' in filters:
            fb = fb.app(filters['app'])
        
        entries = fb.execute()
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=columns, extrasaction='ignore')
    writer.writeheader()
    
    total = len(entries)
    for i, entry in enumerate(entries):
        row = {
            'id': entry.id,
            'timestamp': entry.timestamp,
            'original_text': entry.original_text,
            'processed_text': entry.processed_text,
            'action': entry.action,
            'word_count': entry.word_count,
            'tags': ','.join(entry.tags or []),
            'app_name': entry.app_name,
            'language': entry.language,
            'model_used': entry.model_used,
            'duration': entry.duration,
            'wpm': entry.wpm,
            'quality_score': entry.quality_score,
        }
        writer.writerow(row)
        
        # Progress callback every 100 entries
        if progress_callback and (i + 1) % 100 == 0:
            progress_callback(i + 1, total)
    
    csv_content = output.getvalue()
    
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(csv_content)
    
    return csv_content


def export_to_markdown(
    entries: List[TranscriptionEntry],
    path: Optional[Path] = None,
    include_metadata: bool = False,
    separator: str = '\n\n',
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> str:
    """
    Export transcriptions to Markdown format.
    
    Args:
        entries: List of TranscriptionEntry objects to export
        path: Optional path to save Markdown file
        include_metadata: Whether to include YAML frontmatter
        separator: String to separate entries (default: double newline)
        progress_callback: Optional callback(completed, total) for progress
    
    Returns:
        Markdown string content
    """
    lines = []
    total = len(entries)
    
    for i, entry in enumerate(entries):
        if include_metadata:
            # Add YAML frontmatter
            lines.append(f"---")
            lines.append(f"id: {entry.id}")
            lines.append(f"timestamp: {entry.timestamp}")
            lines.append(f"word_count: {entry.word_count}")
            lines.append(f"tags: {', '.join(entry.tags or []) or 'none'}")
            lines.append(f"language: {entry.language or 'unknown'}")
            lines.append(f"---")
            lines.append("")
        
        # Add the transcription text
        lines.append(entry.display_text)
        
        if i < total - 1:
            lines.append(separator)
        
        # Progress callback every 100 entries
        if progress_callback and (i + 1) % 100 == 0:
            progress_callback(i + 1, total)
    
    markdown_content = "\n".join(lines)
    
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
    
    return markdown_content


# Default HTML template
DEFAULT_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transcriptions Export</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .entry {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .entry-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            color: #666;
            font-size: 0.9em;
        }}
        .entry-text {{
            line-height: 1.6;
            white-space: pre-wrap;
        }}
        .tags {{
            margin-top: 12px;
        }}
        .tag {{
            display: inline-block;
            background: #e0e7ff;
            color: #3730a3;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            margin-right: 4px;
        }}
        .metadata {{
            font-size: 0.85em;
            color: #888;
            margin-top: 8px;
        }}
        .highlight {{
            background: #fef08a;
            padding: 0 2px;
        }}
    </style>
</head>
<body>
    <h1>Transcriptions Export</h1>
    <p>Exported on: {export_date}</p>
    <p>Total entries: {total_count}</p>
    
    {entries_html}
</body>
</html>"""


def _format_entry_html(
    entry: TranscriptionEntry,
    highlight_terms: List[str] = None
) -> str:
    """Format a single entry as HTML"""
    text = entry.display_text
    
    # Apply highlighting if terms provided
    if highlight_terms:
        for term in highlight_terms:
            text = text.replace(
                term,
                f'<span class="highlight">{term}</span>'
            )
    
    tags_html = ''
    if entry.tags:
        tags_html = '<div class="tags">' + ''.join(
            f'<span class="tag">{tag}</span>' for tag in entry.tags
        ) + '</div>'
    
    metadata_parts = []
    if entry.language:
        metadata_parts.append(f"Language: {entry.language}")
    if entry.app_name:
        metadata_parts.append(f"App: {entry.app_name}")
    if entry.word_count:
        metadata_parts.append(f"Words: {entry.word_count}")
    
    metadata_html = ''
    if metadata_parts:
        metadata_html = f'<div class="metadata">{" | ".join(metadata_parts)}</div>'
    
    return f'''    <div class="entry">
        <div class="entry-header">
            <span>{entry.timestamp}</span>
            <span>{entry.action}</span>
        </div>
        <div class="entry-text">{text}</div>
        {tags_html}
        {metadata_html}
    </div>'''


def export_to_html(
    entries: List[TranscriptionEntry],
    path: Optional[Path] = None,
    template: str = None,
    highlight_terms: List[str] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> str:
    """
    Export transcriptions to HTML format.
    
    Args:
        entries: List of TranscriptionEntry objects to export
        path: Optional path to save HTML file
        template: Optional custom template string (uses DEFAULT_HTML_TEMPLATE if None)
        highlight_terms: Optional list of terms to highlight
        progress_callback: Optional callback(completed, total) for progress
    
    Returns:
        HTML string content
    """
    template_str = template or DEFAULT_HTML_TEMPLATE
    
    entries_html_parts = []
    total = len(entries)
    
    for i, entry in enumerate(entries):
        entries_html_parts.append(_format_entry_html(entry, highlight_terms))
        
        if progress_callback and (i + 1) % 100 == 0:
            progress_callback(i + 1, total)
    
    entries_html = '\n'.join(entries_html_parts)
    
    html_content = template_str.format(
        export_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        total_count=total,
        entries_html=entries_html
    )
    
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    return html_content


# Convenience functions that work with the global store

def export_all_csv(
    path: Optional[Path] = None,
    columns: List[str] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> str:
    """Export all transcriptions to CSV"""
    store = get_store()
    return export_to_csv(
        store.entries,
        path=path,
        columns=columns,
        progress_callback=progress_callback
    )


def export_all_markdown(
    path: Optional[Path] = None,
    include_metadata: bool = False,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> str:
    """Export all transcriptions to Markdown"""
    store = get_store()
    return export_to_markdown(
        store.entries,
        path=path,
        include_metadata=include_metadata,
        progress_callback=progress_callback
    )


def export_all_html(
    path: Optional[Path] = None,
    template: str = None,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> str:
    """Export all transcriptions to HTML"""
    store = get_store()
    return export_to_html(
        store.entries,
        path=path,
        template=template,
        progress_callback=progress_callback
    )


if __name__ == "__main__":
    # Demo export
    print("Export Demo")
    store = get_store()
    print(f"Total entries: {len(store.entries)}")
    
    # Export to each format
    csv_out = export_to_csv(store.entries[:5])
    print(f"\nCSV (first 5):\n{csv_out[:500]}...")
    
    md_out = export_to_markdown(store.entries[:3], include_metadata=True)
    print(f"\nMarkdown (first 3):\n{md_out[:500]}...")
    
    html_out = export_to_html(store.entries[:3])
    print(f"\nHTML (first 3):\n{html_out[:500]}...")
