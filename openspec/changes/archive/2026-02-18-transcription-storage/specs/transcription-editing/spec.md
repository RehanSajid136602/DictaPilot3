## ADDED Requirements

### Requirement: Edit transcription text
The system SHALL allow users to modify transcription text.

#### Scenario: Edit processed text
- **WHEN** user calls `edit_transcription(id, processed_text='corrected text')`
- **THEN** the processed_text field is updated
- **AND** a version history entry is created

#### Scenario: Edit original text
- **WHEN** user calls `edit_transcription(id, original_text='fixed original')`
- **THEN** the original_text field is updated
- **AND** word_count is recalculated

### Requirement: Version history tracking
The system SHALL maintain a history of edits for each transcription.

#### Scenario: Track edit history
- **WHEN** user edits a transcription multiple times
- **THEN** system stores up to 5 previous versions
- **AND** each version includes timestamp and previous text content

#### Scenario: View edit history
- **WHEN** user calls `get_edit_history(id)`
- **THEN** system returns list of previous versions with timestamps

### Requirement: Rollback to previous version
The system SHALL allow rolling back to a previous version.

#### Scenario: Rollback to specific version
- **WHEN** user calls `rollback(id, version=2)`
- **THEN** current text is replaced with content from version 2
- **AND** a new version is created documenting the rollback

#### Scenario: Rollback to most recent
- **WHEN** user calls `rollback(id)`
- **THEN** system reverts to the most recent previous version

### Requirement: Edit metadata
The system SHALL allow editing transcription metadata fields.

#### Scenario: Update tags
- **WHEN** user calls `edit_transcription(id, tags=['new', 'tags'])`
- **THEN** tags are replaced with new list

#### Scenario: Update language
- **WHEN** user calls `edit_transcription(id, language='es')`
- **THEN** language field is updated

### Requirement: Batch editing
The system SHALL support editing multiple transcriptions at once.

#### Scenario: Bulk tag update
- **WHEN** user calls `bulk_edit(ids, tags=['archived'])`
- **THEN** all specified transcriptions receive the new tags

#### Scenario: Bulk delete
- **WHEN** user calls `bulk_delete(ids)`
- **THEN** all specified transcriptions are removed from storage

### Requirement: Edit validation
The system SHALL validate edits before applying.

#### Scenario: Reject empty text
- **WHEN** user attempts to edit text to empty string
- **THEN** system raises `ValueError` with validation message

#### Scenario: Reject invalid tags
- **WHEN** user provides non-list tags
- **THEN** system raises `TypeError` indicating expected list
