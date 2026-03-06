## ADDED Requirements

### Requirement: Rust backend orchestrates dictation pipeline
The backend SHALL expose command handlers for start/stop recording, transcription execution, smart editing, and structured output response.

#### Scenario: End-to-end dictation flow
- **WHEN** user stops recording
- **THEN** backend finalizes audio, executes transcription + smart edit pipeline, and returns text plus action metadata

#### Scenario: Transcription provider failure
- **WHEN** provider request fails or times out
- **THEN** backend returns typed error code and user-safe message without process termination

### Requirement: Backend persists local settings and history
The backend SHALL persist configuration and dictation history with schema versioning and migration support.

#### Scenario: First launch initialization
- **WHEN** app starts with no prior storage
- **THEN** backend creates storage structures with default settings

#### Scenario: Data schema upgrade
- **WHEN** stored schema version is behind current backend version
- **THEN** migrations run idempotently before serving commands
