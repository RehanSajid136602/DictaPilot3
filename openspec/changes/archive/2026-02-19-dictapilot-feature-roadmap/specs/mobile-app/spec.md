## ADDED Requirements

### Requirement: iOS mobile app
The system SHALL provide native iOS app with full dictation capabilities.

#### Scenario: iOS app available
- **WHEN** user downloads iOS app
- **THEN** app provides full transcription features
- **AND** syncs with desktop application

#### Scenario: Mobile dictation
- **WHEN** user dictates on mobile
- **THEN** system processes audio using mobile-optimized pipeline
- **AND** outputs text to active mobile app

### Requirement: Android mobile app
The system SHALL provide native Android app with full dictation capabilities.

#### Scenario: Android app available
- **WHEN** user downloads Android app
- **THEN** app provides full transcription features
- **AND** syncs with desktop application

#### Scenario: Mobile-desktop sync
- **WHEN** transcription completes on mobile
- **THEN** data syncs to desktop application
- **AND** available across all devices
