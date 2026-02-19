## ADDED Requirements

### Requirement: Export to CSV format
The system SHALL allow users to export transcriptions to CSV format with configurable columns.

#### Scenario: Export all transcriptions to CSV
- **WHEN** user calls `export_to_csv()` with no filters
- **THEN** system exports all stored transcriptions as CSV with columns: id, timestamp, original_text, processed_text, action, word_count, tags, app_name, language, model_used, duration, wpm, quality_score

#### Scenario: Export filtered transcriptions to CSV
- **WHEN** user calls `export_to_csv(filters={'tags': ['work']})`
- **THEN** system exports only transcriptions matching the filter criteria

### Requirement: Export to Markdown format
The system SHALL allow users to export transcriptions as formatted Markdown documents.

#### Scenario: Export with metadata headers
- **WHEN** user calls `export_to_markdown(include_metadata=True)`
- **THEN** each transcription is preceded by YAML frontmatter containing timestamp, word_count, tags, and language

#### Scenario: Export as continuous document
- **WHEN** user calls `export_to_markdown(separator='\n\n')`
- **THEN** transcriptions are concatenated with double-newline separators into a single document

### Requirement: Export to HTML format
The system SHALL allow users to export transcriptions as styled HTML pages.

#### Scenario: Export with default styling
- **WHEN** user calls `export_to_html()`
- **THEN** system generates an HTML document with basic responsive CSS styling

#### Scenario: Export with custom template
- **WHEN** user calls `export_to_html(template='custom.html')`
- **THEN** system uses the provided template file, injecting transcription data into template variables

### Requirement: Batch export with progress
The system SHALL support exporting large datasets with progress callbacks.

#### Scenario: Large export with progress
- **WHEN** user exports 1000+ transcriptions with progress_callback
- **THEN** callback is invoked every 100 entries with progress percentage
- **AND** export can be cancelled by raising an exception in callback