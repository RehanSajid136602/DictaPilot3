## ADDED Requirements

### Requirement: Detect application type
The system SHALL classify active application by type for formatting decisions.

#### Scenario: Email application detected
- **WHEN** user switches to email client
- **THEN** system sets format profile to email standards
- **AND** applies proper capitalization, punctuation

#### Scenario: IDE detected
- **WHEN** user switches to code editor
- **THEN** system enables code syntax mode
- **AND** preserves indentation, applies code formatting

#### Scenario: Document editor detected
- **WHEN** user switches to word processor
- **THEN** system applies document formatting rules
- **AND** enables smart punctuation

### Requirement: Apply code syntax awareness
The system SHALL recognize and properly format code elements.

#### Scenario: Code dictation detected
- **WHEN** transcribed text contains code-like patterns
- **THEN** system applies appropriate syntax formatting
- **AND** preserves code structure in output
