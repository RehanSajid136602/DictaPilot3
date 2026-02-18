## ADDED Requirements

### Requirement: Live preview display
The system SHALL display partial transcription results in a preview overlay during recording.

#### Scenario: Preview appears during recording
- **WHEN** user is recording and streaming is enabled
- **THEN** a preview overlay displays partial transcription text

#### Scenario: Preview updates in real-time
- **WHEN** new partial results arrive
- **THEN** the preview text updates within 100ms of receiving the result

#### Scenario: Preview hidden when not recording
- **WHEN** recording stops or streaming is disabled
- **THEN** the preview overlay is hidden

### Requirement: Preview visual distinction
The system SHALL visually distinguish preview text from final transcription.

#### Scenario: Preview has draft styling
- **WHEN** preview text is displayed
- **THEN** it is styled differently (e.g., italic, lighter color) to indicate draft status

#### Scenario: Preview shows streaming indicator
- **WHEN** streaming is in progress
- **THEN** a visual indicator shows the streaming status

### Requirement: Preview positioning
The system SHALL position the preview overlay relative to the recording window.

#### Scenario: Preview positioned below recording window
- **WHEN** preview is displayed
- **THEN** it appears below the floating recording window, anchored to its position

#### Scenario: Preview follows recording window
- **WHEN** user moves the recording window
- **THEN** the preview overlay follows to maintain relative positioning

### Requirement: Preview debouncing
The system SHALL debounce preview updates to prevent visual flicker.

#### Scenario: Rapid updates are smoothed
- **WHEN** multiple partial results arrive in quick succession
- **THEN** the preview is updated at most every 100ms

#### Scenario: Final update is immediate
- **WHEN** recording stops and final result is ready
- **THEN** the preview immediately updates to show final result
