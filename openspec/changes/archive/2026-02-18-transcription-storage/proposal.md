## Why

DictaPilot currently stores transcriptions locally in JSON format, but lacks advanced organization, export, and data management capabilities. Users need better ways to filter, categorize, export, and manage their transcription history beyond simple text search. As users accumulate more transcriptions over time, the current flat-list approach becomes increasingly difficult to navigate.

## What Changes

- Add multi-format export capabilities (CSV, Markdown, HTML)
- Implement advanced filtering by date range, tags, language, and quality metrics
- Add import functionality to merge external transcription data
- Introduce transcription categories/folders for organization
- Add fuzzy search for typo-tolerant matching
- Enable transcription editing and correction with version history
- Add data backup and restore functionality
- Implement bulk operations (delete, tag, export multiple entries)

## Capabilities

### New Capabilities

- **transcription-export**: Multi-format export system supporting CSV, Markdown documents, and HTML reports with customizable templates
- **transcription-filtering**: Advanced query system with filters for date ranges, tags, language, app name, quality score, and word count thresholds
- **transcription-import**: Import functionality to merge transcriptions from external JSON files, supporting deduplication and conflict resolution
- **transcription-categories**: Folder/category system allowing users to organize transcriptions beyond tags
- **transcription-search**: Enhanced search with fuzzy matching, exact phrase search, and regex support
- **transcription-editing**: In-place editing with automatic version history and rollback capability

### Modified Capabilities

- None - this is a net-new capability set

## Impact

- Primary: `transcription_store.py` - core storage module will be extended
- New modules: `transcription_export.py`, `transcription_import.py`, `transcription_categories.py`
- Configuration: May need new settings in `config.py` for export defaults, backup paths
- UI Impact: Dashboard views for managing transcriptions, export dialogs, category management
