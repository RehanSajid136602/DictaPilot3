## ADDED Requirements

### Requirement: Create categories
The system SHALL allow users to create named categories for organizing transcriptions.

#### Scenario: Create new category
- **WHEN** user calls `create_category('Work Meetings')`
- **THEN** a new category with name 'Work Meetings' is created
- **AND** category has empty list of transcription IDs

#### Scenario: Create category with description
- **WHEN** user calls `create_category('Projects', description='Project-related transcriptions')`
- **THEN** category includes the description field

### Requirement: Assign transcription to category
The system SHALL allow assigning transcriptions to categories.

#### Scenario: Single transcription to category
- **WHEN** user calls `add_to_category(transcription_id, 'Work')`
- **THEN** the transcription ID is added to the 'Work' category's entry list

#### Scenario: Multiple transcriptions to category
- **WHEN** user calls `add_to_category([id1, id2, id3], 'Work')`
- **THEN** all specified transcription IDs are added to the category

### Requirement: Remove transcription from category
The system SHALL allow removing transcriptions from categories.

#### Scenario: Remove from category
- **WHEN** user calls `remove_from_category(transcription_id, 'Work')`
- **THEN** the transcription ID is removed from the 'Work' category

### Requirement: List categories
The system SHALL provide a list of all categories.

#### Scenario: Get all categories
- **WHEN** user calls `get_categories()`
- **THEN** system returns list of all categories with name, description, entry count

### Requirement: Get transcriptions in category
The system SHALL return all transcriptions belonging to a category.

#### Scenario: Get category entries
- **WHEN** user calls `get_category_entries('Work')`
- **THEN** system returns all TranscriptionEntry objects in the 'Work' category

### Requirement: Delete category
The system SHALL allow deleting categories.

#### Scenario: Delete empty category
- **WHEN** user calls `delete_category('Unused')`
- **THEN** category is removed from storage

#### Scenario: Delete category with entries
- **WHEN** user calls `delete_category('Work', keep_entries=True)`
- **THEN** category is removed but transcription entries remain
- **AND** entries are not deleted (just unlinked)

### Requirement: Rename category
The system SHALL allow renaming existing categories.

#### Scenario: Rename category
- **WHEN** user calls `rename_category('Work', 'Work Meetings')`
- **AND** 'Work Meetings' does not already exist
- **THEN** category name is updated to 'Work Meetings'

### Requirement: Category statistics
The system SHALL provide statistics about categories.

#### Scenario: Get category stats
- **WHEN** user calls `get_category_stats()`
- **THEN** system returns dict with each category name mapped to entry count, total word count
