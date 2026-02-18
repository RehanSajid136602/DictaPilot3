## ADDED Requirements

### Requirement: Real-time partial transcription results
The system SHALL provide partial transcription results while the user is recording audio, without requiring the user to release the hotkey.

#### Scenario: User receives partial results during recording
- **WHEN** user holds the hotkey and speaks for more than 2 seconds
- **THEN** system displays partial transcription text within 500ms of the first chunk being processed

#### Scenario: Partial results update as recording continues
- **WHEN** user continues speaking while partial results are displayed
- **THEN** system updates the preview text with new transcription content as additional chunks are processed

#### Scenario: Streaming disabled by configuration
- **WHEN** streaming is disabled in configuration
- **THEN** system falls back to batch transcription mode without streaming preview

### Requirement: Configurable streaming mode
The system SHALL allow users to enable or disable streaming transcription via configuration.

#### Scenario: Streaming enabled by default
- **WHEN** no streaming configuration is set
- **THEN** streaming mode is enabled by default

#### Scenario: User disables streaming
- **WHEN** user sets `streaming_enabled` to `false` in configuration
- **THEN** system uses batch transcription only without streaming preview

### Requirement: Streaming transcription callback interface
The system SHALL provide a callback interface for receiving partial transcription results.

#### Scenario: Callback receives partial text
- **WHEN** a chunk transcription completes
- **THEN** the registered callback is invoked with the partial transcription text

#### Scenario: Callback handles errors gracefully
- **WHEN** a chunk transcription fails
- **THEN** the callback is invoked with an error indicator and the system continues processing subsequent chunks
