## ADDED Requirements

### Requirement: Windows packaging produces installer artifacts
Build system SHALL generate Windows installer/executable bundles using Tauri bundling configuration.

#### Scenario: Local package build
- **WHEN** developer runs package command
- **THEN** output artifacts are generated in documented dist path with versioned naming

#### Scenario: CI release build
- **WHEN** release workflow runs on Windows
- **THEN** workflow publishes installer executable and checksum metadata

### Requirement: Packaged runtime is parity-checked
Packaged builds SHALL be smoke-tested for startup and core dictation controls.

#### Scenario: Packaged app startup smoke test
- **WHEN** user launches packaged app
- **THEN** app opens, backend commands are reachable, and basic dictation start/stop path works
