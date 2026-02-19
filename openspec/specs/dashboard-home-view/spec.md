## ADDED Requirements

### Requirement: Status card display
The system SHALL display a status card showing recording state, API connection, microphone, and active profile.

#### Scenario: Display system status
- **WHEN** Home view is displayed
- **THEN** status card shows four rows with colored indicators and current values

#### Scenario: Recording idle state
- **WHEN** recording is not active
- **THEN** status card shows "Recording: Idle" with gray indicator

#### Scenario: Recording active state
- **WHEN** recording is active
- **THEN** status card shows "Recording: Recording" with green indicator

#### Scenario: API connected state
- **WHEN** API connection is successful
- **THEN** status card shows "API: Connected" with green indicator

#### Scenario: API error state
- **WHEN** API connection fails
- **THEN** status card shows "API: Error" with red indicator

### Requirement: Quick stats display
The system SHALL display quick statistics including transcriptions today, total words, average WPM, and average quality.

#### Scenario: Display today's stats
- **WHEN** Home view is displayed
- **THEN** quick stats card shows count of transcriptions created today

#### Scenario: Display total words
- **WHEN** Home view is displayed
- **THEN** quick stats card shows sum of word counts for today

#### Scenario: Display average WPM
- **WHEN** Home view is displayed
- **THEN** quick stats card shows mean WPM across all transcriptions

#### Scenario: Display average quality
- **WHEN** Home view is displayed
- **THEN** quick stats card shows mean quality score as percentage

### Requirement: Recent transcriptions list
The system SHALL display the 5 most recent transcriptions with timestamp and truncated text.

#### Scenario: Display recent items
- **WHEN** Home view is displayed and transcriptions exist
- **THEN** recent transcriptions list shows up to 5 items with relative timestamps

#### Scenario: Navigate to full history
- **WHEN** user clicks "View All History" link
- **THEN** system navigates to History view

#### Scenario: Open transcription detail
- **WHEN** user clicks a transcription in recent list
- **THEN** system navigates to History view with that transcription selected

#### Scenario: Empty state
- **WHEN** no transcriptions exist
- **THEN** recent list shows "No transcriptions yet" message with "Start Dictating" button

### Requirement: Audio waveform preview
The system SHALL display a real-time audio waveform when recording is active.

#### Scenario: Idle waveform
- **WHEN** recording is not active
- **THEN** waveform shows flat line with subtle breathing animation

#### Scenario: Recording waveform
- **WHEN** recording is active
- **THEN** waveform shows live amplitude bars in green

#### Scenario: Processing waveform
- **WHEN** transcription is processing
- **THEN** waveform shows pulsing yellow wave

### Requirement: Activity bar chart
The system SHALL display a bar chart showing transcription count for the last 7 days.

#### Scenario: Display 7-day activity
- **WHEN** Home view is displayed
- **THEN** activity chart shows 7 bars representing last 7 days

#### Scenario: Chart hover tooltip
- **WHEN** user hovers over a bar
- **THEN** tooltip shows day name and transcription count

### Requirement: Start dictating action
The system SHALL provide a prominent button to start dictating from the Home view.

#### Scenario: Start recording
- **WHEN** user clicks "Start Dictating" button
- **THEN** system begins recording and status card updates to "Recording"
