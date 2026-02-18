## ADDED Requirements

### Requirement: Automatic fallback to batch mode
The system SHALL automatically fall back to batch transcription if streaming fails.

#### Scenario: Fallback on API error
- **WHEN** a streaming chunk transcription fails with an API error
- **THEN** the system falls back to batch mode for the remaining recording

#### Scenario: Fallback on network timeout
- **WHEN** streaming requests timeout multiple times
- **THEN** the system switches to batch mode

#### Scenario: Fallback indication to user
- **WHEN** fallback occurs
- **THEN** the user is notified that streaming is unavailable

### Requirement: Graceful error handling
The system SHALL handle streaming errors without interrupting the recording.

#### Scenario: Recording continues on chunk error
- **WHEN** a chunk transcription fails
- **THEN** recording continues and subsequent chunks are processed normally

#### Scenario: Partial results preserved on error
- **WHEN** streaming fails after some partial results
- **THEN** already-received partial results are preserved and displayed

### Requirement: Streaming health monitoring
The system SHALL monitor streaming health and proactively switch modes.

#### Scenario: Track consecutive failures
- **WHEN** multiple consecutive chunk transcriptions fail
- **THEN** streaming is temporarily disabled and batch mode is used

#### Scenario: Automatic recovery
- **WHEN** streaming was disabled due to failures
- **THEN** the system attempts to re-enable streaming for subsequent recordings

### Requirement: Configuration-based fallback
The system SHALL respect configuration settings for fallback behavior.

#### Scenario: User disables final pass
- **WHEN** `streaming_final_pass` is disabled and streaming fails
- **THEN** the system uses available streaming results only

#### Scenario: User forces batch mode
- **WHEN** `streaming_enabled` is set to `false`
- **THEN** the system always uses batch mode without attempting streaming
