## ADDED Requirements

### Requirement: Detect active application context
The system SHALL detect the currently active application and classify its type for tone adjustment.

#### Scenario: User switches to email client
- **WHEN** active window changes to email application
- **THEN** system detects application type as "email"
- **AND** sets tone profile to "professional"

#### Scenario: User switches to chat application
- **WHEN** active window changes to messaging/chat app
- **THEN** system detects application type as "chat"
- **AND** sets tone profile to "casual"

#### Scenario: User switches to IDE
- **WHEN** active window changes to code editor/IDE
- **THEN** system detects application type as "code"
- **AND** sets tone profile to "technical"

#### Scenario: Unknown application
- **WHEN** active window is unrecognized application
- **THEN** system uses default neutral tone
- **AND** logs application for future recognition learning

### Requirement: Apply tone-based text transformation
The system SHALL transform transcribed text based on detected context tone.

#### Scenario: Professional tone for email
- **WHEN** context is "email" and user dictates casual text
- **THEN** system transforms text to more professional language
- **AND** preserves original meaning while improving formality

#### Scenario: Casual tone for chat
- **WHEN** context is "chat" and user dictates formal text
- **THEN** system relaxes language to casual tone
- **AND** maintains readability

#### Scenario: Technical tone for code
- **WHEN** context is "IDE" and user dictates natural language
- **THEN** system maintains technical precision
- **AND** applies appropriate code syntax when applicable

### Requirement: User tone preferences
The system SHALL allow users to customize tone profiles and per-application settings.

#### Scenario: User customizes tone profile
- **WHEN** user modifies tone transformation settings
- **THEN** system saves preferences to configuration
- **AND** applies custom settings to future transcriptions

#### Scenario: User disables tone adjustment
- **WHEN** user disables tone adjustment globally
- **THEN** system passes through text unchanged
- **AND** tone adjustment is skipped for all applications

### Requirement: Tone adjustment via voice command
The system SHALL allow temporary tone override via voice command.

#### Scenario: User requests tone change
- **WHEN** user says "make this professional" or "be casual"
- **THEN** system applies requested tone to next passage
- **AND** returns to auto-detected tone after passage ends
