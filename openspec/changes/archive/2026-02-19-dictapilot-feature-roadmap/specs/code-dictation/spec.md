## ADDED Requirements

### Requirement: Programming language detection
The system SHALL detect when user is dictating code and apply appropriate formatting.

#### Scenario: Code dictation mode
- **WHEN** user opens IDE or starts dictating code
- **THEN** system detects programming context
- **AND** applies code-specific formatting rules

#### Scenario: Language-specific syntax
- **WHEN** user dictates code in specific language
- **THEN** system applies language syntax rules
- **AND** handles indentation, brackets, keywords appropriately

### Requirement: IDE integration for code dictation
The system SHALL integrate with IDEs for enhanced code dictation.

#### Scenario: IDE context available
- **WHEN** dictating in connected IDE
- **THEN** system uses IDE context (imports, types, variables)
- **AND** provides accurate code completion suggestions
