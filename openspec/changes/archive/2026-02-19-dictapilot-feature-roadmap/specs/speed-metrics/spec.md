## ADDED Requirements

### Requirement: Real-time WPM calculation
The system SHALL calculate and display words per minute during active transcription.

#### Scenario: Active transcription displays WPM
- **WHEN** user is actively dictating
- **THEN** system calculates WPM from words transcribed per minute
- **AND** displays current speed in floating window or dashboard

#### Scenario: WPM updates in real-time
- **WHEN** transcription continues beyond initial minute
- **THEN** WPM is recalculated using rolling average
- **AND** display updates every second

### Requirement: Session speed statistics
The system SHALL track and display transcription speed statistics per session.

#### Scenario: Session summary shows average WPM
- **WHEN** dictation session ends
- **THEN** system calculates average WPM for session
- **AND** stores statistics for historical review

#### Scenario: User views speed history
- **WHEN** user opens statistics dashboard
- **THEN** system displays WPM trends over time
- **AND** shows comparison to previous sessions

### Requirement: Speed comparison display
The system SHALL compare dictation speed to average typing speed.

#### Scenario: Display speed comparison
- **WHEN** WPM is calculated during transcription
- **THEN** system compares to baseline typing speed (40 WPM)
- **AND** shows improvement percentage
