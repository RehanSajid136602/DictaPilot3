## ADDED Requirements

### Requirement: Voice commands reference lists all available commands
The system SHALL provide a comprehensive reference listing all voice commands with descriptions and examples.

#### Scenario: User finds command for deleting text
- **WHEN** user searches for deletion commands
- **THEN** they find all variants: "delete that", "undo", "scratch that", "remove last"

#### Scenario: User learns command syntax
- **WHEN** user views a command entry
- **THEN** they see the command phrase, description, and usage example

### Requirement: Commands are organized by category
Voice commands SHALL be organized into logical categories for easy navigation.

#### Scenario: User browses editing commands
- **WHEN** user views the commands reference
- **THEN** commands are grouped into categories: Editing, Formatting, Navigation, Control

#### Scenario: User finds formatting commands
- **WHEN** user looks for text formatting
- **THEN** they find all formatting commands grouped together: capitalize, bold, italic, heading

### Requirement: Each command includes working examples
Each command entry SHALL include at least one working example showing input and expected output.

#### Scenario: User learns replace command
- **WHEN** user views "replace X with Y" command
- **THEN** they see example: "replace hello with goodbye" transforms "hello world" to "goodbye world"

#### Scenario: User understands command variations
- **WHEN** a command has multiple variations
- **THEN** all variations are listed with examples showing they produce the same result

### Requirement: Commands reference is searchable
The commands reference SHALL be searchable by command name, category, or keyword.

#### Scenario: User searches for undo functionality
- **WHEN** user searches for "undo"
- **THEN** they find all commands related to undoing: "delete that", "undo", "scratch that"

#### Scenario: User searches by action
- **WHEN** user searches for "remove"
- **THEN** they find all removal-related commands regardless of exact phrasing
