## ADDED Requirements

### Requirement: Import from JSON file
The system SHALL allow importing transcriptions from external JSON files.

#### Scenario: Import valid JSON file
- **WHEN** user calls `import_from_json('transcriptions.json')`
- **AND** the file contains valid transcription data in expected format
- **THEN** system imports all entries and returns count of imported items

#### Scenario: Import with schema mismatch
- **WHEN** user imports a JSON file with missing fields
- **THEN** system uses default values for missing fields (empty string, 0, empty list)

### Requirement: Deduplication on import
The system SHALL detect and handle duplicate entries during import.

#### Scenario: Import with timestamp-content duplicate
- **WHEN** user imports entries with same timestamp and content hash
- **AND** deduplication is enabled
- **THEN** system skips duplicate entries and reports count of skipped items

#### Scenario: Import with new IDs for duplicates
- **WHEN** user imports with `generate_new_ids=True`
- **THEN** system assigns new UUIDs to all imported entries regardless of duplicates

### Requirement: Conflict resolution
The system SHALL provide strategies for handling conflicts during import.

#### Scenario: Skip existing on conflict
- **WHEN** user imports with `on_conflict='skip'`
- **AND** an entry with same ID already exists
- **THEN** system skips that entry

#### Scenario: Overwrite on conflict
- **WHEN** user imports with `on_conflict='overwrite'`
- **AND** an entry with same ID already exists
- **THEN** system replaces the existing entry with imported data

#### Scenario: Keep both on conflict
- **WHEN** user imports with `on_conflict='keep_both'`
- **AND** an entry with same ID already exists
- **THEN** system assigns a new ID to the imported entry

### Requirement: Import validation
The system SHALL validate imported data before adding to storage.

#### Scenario: Import invalid data
- **WHEN** user imports a file with malformed data
- **THEN** system raises `ValueError` with descriptive message
- **AND** no partial imports occur (transaction semantics)

### Requirement: Merge mode
The system SHALL support merging imported data with existing storage.

#### Scenario: Merge with existing entries
- **WHEN** user calls `import_from_json(file, merge=True)`
- **THEN** system appends new entries to existing storage
- **AND** existing entries remain unchanged
