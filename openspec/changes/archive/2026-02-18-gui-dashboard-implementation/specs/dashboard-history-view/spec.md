## ADDED Requirements

### Requirement: Master-detail layout
The system SHALL display transcriptions in a master-detail layout with list on left and detail panel on right.

#### Scenario: Display transcription list
- **WHEN** History view is displayed
- **THEN** left panel shows list of transcriptions with timestamp and truncated text

#### Scenario: Select transcription
- **WHEN** user clicks a transcription in the list
- **THEN** right panel displays full original text, processed text, and metadata

#### Scenario: Resizable splitter
- **WHEN** user drags the splitter between panels
- **THEN** panel widths adjust proportionally

### Requirement: Advanced filtering
The system SHALL provide filters for tags, quality range, source app, and date range.

#### Scenario: Filter by tag
- **WHEN** user selects a tag from the tags dropdown
- **THEN** list shows only transcriptions with that tag

#### Scenario: Filter by quality
- **WHEN** user selects a quality range
- **THEN** list shows only transcriptions within that quality score range

#### Scenario: Filter by app
- **WHEN** user selects an app from the app dropdown
- **THEN** list shows only transcriptions from that source app

#### Scenario: Filter by date range
- **WHEN** user selects a date range
- **THEN** list shows only transcriptions within that date range

#### Scenario: Clear filters
- **WHEN** user clicks "Clear filters" button
- **THEN** all filters reset and full list is displayed

### Requirement: Search functionality
The system SHALL provide full-text search across transcription content.

#### Scenario: Search transcriptions
- **WHEN** user types in search bar
- **THEN** list filters to show only transcriptions containing the search term

#### Scenario: Search debouncing
- **WHEN** user types in search bar
- **THEN** search executes after 200ms of no typing

#### Scenario: Clear search
- **WHEN** user clicks X button in search bar
- **THEN** search clears and full list is displayed

### Requirement: Pagination
The system SHALL paginate transcription list with 25 items per page.

#### Scenario: Display page controls
- **WHEN** more than 25 transcriptions exist
- **THEN** pagination controls show at bottom with page numbers and prev/next buttons

#### Scenario: Navigate to next page
- **WHEN** user clicks "Next" button
- **THEN** list displays next 25 transcriptions

#### Scenario: Navigate to specific page
- **WHEN** user clicks a page number
- **THEN** list displays transcriptions for that page

### Requirement: Transcription actions
The system SHALL provide actions to copy, delete, and tag transcriptions.

#### Scenario: Copy transcription
- **WHEN** user clicks "Copy" button in detail panel
- **THEN** processed text is copied to clipboard

#### Scenario: Delete transcription
- **WHEN** user clicks "Delete" button and confirms
- **THEN** transcription is removed from store and list updates

#### Scenario: Add tag
- **WHEN** user clicks "Tag" button and enters tag name
- **THEN** tag is added to transcription and displayed in detail panel

### Requirement: Export functionality
The system SHALL provide export functionality for filtered transcriptions.

#### Scenario: Export to CSV
- **WHEN** user clicks "Export" button
- **THEN** system downloads CSV file with all filtered transcriptions
