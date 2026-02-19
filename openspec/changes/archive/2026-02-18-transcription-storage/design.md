## Context

The current transcription storage system (`transcription_store.py`) provides basic JSON-based persistence with simple search and export capabilities. It stores transcriptions as a flat list with metadata fields (tags, language, quality score, etc.) but lacks:

- Multi-format export beyond basic text/JSON
- Advanced filtering beyond simple text search
- Organizational structures like categories/folders
- Import/merge capabilities
- Version history for edits
- Bulk operations

The system is used by the main DictaPilot application and potentially a dashboard UI. Any changes must maintain backward compatibility with existing stored data.

## Goals / Non-Goals

**Goals:**
- Add multi-format export (CSV, Markdown, HTML) with customizable templates
- Implement advanced filtering by date range, tags, language, quality score, word count
- Add import functionality with deduplication
- Introduce category/folder system for organizing transcriptions
- Enhance search with fuzzy matching and regex support
- Add transcription editing with version history

**Non-Goals:**
- Cloud sync or remote backup (out of scope for this change)
- Real-time collaboration features
- OCR or document import (scanned PDFs, images)
- Audio file management
- User authentication/permissions

## Decisions

### 1. Export Format Architecture

**Decision:** Create a plugin-based export system using strategy pattern

**Rationale:** Allows adding new export formats without modifying core storage code. Each exporter is a separate class implementing a common interface.

**Alternatives Considered:**
- Single monolithic export function with format parameter: Rejected - becomes unwieldy as formats grow
- Template-based only: Rejected - some formats (CSV) need structured data handling not suitable for templates

### 2. Filtering Implementation

**Decision:** Chainable filter builder pattern with method chaining

**Rationale:** Python's method chaining allows intuitive filter construction: `store.filter().date_range(start, end).tags(['work']).quality_above(0.7).execute()`

**Alternatives Considered:**
- SQL-like query string: Rejected - adds dependency and complexity
- Config dict filters: Rejected - less readable, no type safety

### 3. Category Storage

**Decision:** Embed categories in existing JSON as a separate section, not modifying individual entries

**Rationale:** Categories are many-to-many relationships. Storing as separate index avoids duplicating data and simplifies migrations.

**Alternatives Considered:**
- Category field on each entry: Rejected - requires schema migration
- Separate category files: Rejected - complicates atomic saves

### 4. Search Enhancement

**Decision:** Use `difflib` (standard library) for fuzzy matching

**Rationale:** No external dependencies, adequate performance for typical transcription volumes (<10,000 entries)

**Alternatives Considered:**
- Whoosh/Elasticsearch: Rejected - overkill for local desktop app
- SQLite FTS: Rejected - adds database dependency

### 5. Version History

**Decision:** Store edit history as separate array in each entry, limited to last 5 edits

**Rationale:** Prevents unbounded growth while providing useful rollback capability

**Alternatives Considered:**
- Full diff storage: Rejected - complex to implement
- Unlimited history: Rejected - storage bloat risk

## Risks / Trade-offs

- **[Risk]** Schema migration for existing users  
  → **[Mitigation]** Version field in JSON schema, migrate on load if version < current

- **[Risk]** Performance degradation with large transcription history  
  → **[Mitigation]** Add indexing for common filters, cache filter results

- **[Risk]** Export template injection  
  → **[Mitigation]** Sanitize user content in templates, use Jinja2's autoescape

- **[Risk]** Import conflicts with duplicate IDs  
  → **[Mitigation]** Generate new IDs on import, optionally match by timestamp+content hash

## Migration Plan

1. Add version field to schema (v2.0 → v3.0)
2. Load existing data, auto-migrate if needed
3. New features degrade gracefully if categories/versions not present
4. No breaking changes to existing API signatures
5. Rollback: Previous version of transcription_store.py still works with v3.0 data (read-only)

## Open Questions

- Should categories support nested hierarchy (folders within folders)?
- What's the max file size for import? Need to set reasonable limits.
- Should export be asynchronous for large datasets?
