## ADDED Requirements

### Requirement: Automatic language detection
The system SHALL detect the language being spoken and switch transcription appropriately.

#### Scenario: Single language dictation
- **WHEN** user speaks in a consistent language
- **THEN** system detects language via NVIDIA NIM API
- **AND** transcribes with correct language model

#### Scenario: Language switch during dictation
- **WHEN** user switches to different language mid-dictation
- **THEN** system detects language change
- **AND** seamlessly switches transcription model
- **AND** maintains context across language boundary

### Requirement: Support 100+ languages
The system SHALL support transcription for over 100 languages.

#### Scenario: Language selection
- **WHEN** user selects target language
- **THEN** system uses appropriate transcription model
- **AND** applies language-specific rules

#### Scenario: Language preference per application
- **WHEN** user sets language preference for specific app
- **THEN** system applies preference when that app is active
- **AND** overrides default language setting
