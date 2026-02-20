## ADDED Requirements

### Requirement: Create and store text snippets
The system SHALL allow users to create, store, and manage text snippets with optional variable placeholders.

#### Scenario: User creates text snippet
- **WHEN** user creates a new snippet with trigger phrase and content
- **THEN** system stores snippet in JSON format with unique ID
- **AND** snippet is immediately available for voice activation

#### Scenario: User creates template snippet
- **WHEN** user creates snippet with Jinja2 template variables
- **THEN** system stores template with variable syntax intact
- **AND** variables are parsed and prompted when snippet is activated

#### Scenario: User organizes snippets by category
- **WHEN** user assigns category to snippet
- **THEN** system groups snippets by category
- **AND** user can filter view by category

### Requirement: Voice-activated snippet insertion
The system SHALL recognize voice commands to insert pre-defined snippets into active application.

#### Scenario: User activates snippet by name
- **WHEN** user speaks trigger phrase matching a snippet
- **THEN** system inserts snippet content at cursor position
- **AND** template variables are resolved (with prompts if needed)

#### Scenario: No matching snippet found
- **WHEN** user speaks phrase that doesn't match any snippet
- **THEN** system continues normal transcription
- **AND** no snippet insertion occurs

### Requirement: Snippet library management
The system SHALL provide UI for viewing, editing, and deleting snippets.

#### Scenario: User views snippet library
- **WHEN** user opens snippet library view
- **THEN** system displays all snippets in searchable list
- **AND** shows trigger phrase, preview, and category for each

#### Scenario: User edits snippet
- **WHEN** user modifies existing snippet
- **THEN** system updates JSON storage
- **AND** changes take effect immediately

#### Scenario: User deletes snippet
- **WHEN** user removes a snippet
- **THEN** system deletes from storage
- **AND** trigger phrase is no longer recognized

### Requirement: Import/export snippet library
The system SHALL support backup and transfer of snippet collections.

#### Scenario: User exports snippets
- **WHEN** user requests to export snippet library
- **THEN** system generates JSON file with all snippets
- **AND** file includes templates and categories

#### Scenario: User imports snippets
- **WHEN** user provides snippet JSON to import
- **THEN** system validates and merges with existing snippets
- **AND** duplicate trigger phrases prompt for resolution
