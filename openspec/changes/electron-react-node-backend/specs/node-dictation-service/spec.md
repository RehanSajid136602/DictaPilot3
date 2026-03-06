## ADDED Requirements

### Requirement: Node backend orchestrates dictation and editing pipeline
The backend SHALL expose typed APIs to start/stop recording, run transcription, apply smart editing, and return structured results.

#### Scenario: End-to-end dictation request
- **WHEN** renderer requests dictation stop
- **THEN** backend finalizes audio, runs transcription + smart editing pipeline, and returns output text with action metadata

#### Scenario: Backend failure handling
- **WHEN** transcription service returns an error
- **THEN** backend returns typed error codes and user-safe messages without crashing the app

### Requirement: Backend persists local app data
The backend SHALL persist settings and history in a local storage layer with schema versioning.

#### Scenario: Fresh install launch
- **WHEN** app launches with no existing data
- **THEN** backend creates required storage structures with default settings

#### Scenario: Version upgrade
- **WHEN** storage schema version is behind expected version
- **THEN** backend runs idempotent migration steps before serving requests
