## ADDED Requirements

### Requirement: Recognize real-time edit commands
The system SHALL detect and execute editing commands spoken during dictation without stopping transcription.

#### Scenario: User says "scratch that"
- **WHEN** during dictation user says "scratch that" or similar command
- **THEN** system removes the last spoken phrase
- **AND** continues dictation without interruption

#### Scenario: User says "no I meant [correction]"
- **WHEN** user says "no I meant" followed by correction
- **THEN** system replaces previous phrase with correction
- **AND** maintains transcription continuity

#### Scenario: User says "capitalize that"
- **WHEN** user says "capitalize that" after a word
- **THEN** system capitalizes the last word
- **AND** continues dictation

#### Scenario: User says "new paragraph"
- **WHEN** user says "new paragraph" during dictation
- **THEN** system inserts paragraph break
- **AND** continues dictation on new line

### Requirement: Command parsing during live transcription
The system SHALL parse commands in real-time with minimal latency impact.

#### Scenario: Command detected mid-speech
- **WHEN** command is spoken during continuous speech
- **THEN** system pauses transcription parsing
- **AND** executes command, then resumes

#### Scenario: No matching command
- **WHEN** speech does not match any known command
- **THEN** system treats speech as dictation text
- **AND** continues normal processing

### Requirement: Undo/redo for edit commands
The system SHALL maintain edit history to allow undo and redo of commands.

#### Scenario: User undoes last edit
- **WHEN** user says "undo" or "undo that"
- **THEN** system reverts last edit command
- **AND** restores previous text state

#### Scenario: User redoes undone edit
- **WHEN** user says "redo" after undo
- **THEN** system reapplies previously undone edit
- **AND** maintains edit stack integrity

### Requirement: Command customization
The system SHALL allow users to customize command phrases.

#### Scenario: User adds custom command
- **WHEN** user defines custom command phrase mapping
- **THEN** system adds command to active parser
- **AND** command is available for immediate use

#### Scenario: User removes command
- **WHEN** user deletes a custom command
- **THEN** system removes from parser
- **AND** phrase is treated as dictation if spoken
