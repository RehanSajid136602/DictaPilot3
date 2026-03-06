## ADDED Requirements

### Requirement: Tauri shell provides secure desktop runtime
The application SHALL run in Tauri with secure defaults, exposing only an allowlisted command surface to the frontend.

#### Scenario: App launch initializes runtime
- **WHEN** user starts DictaPilot Desktop on Windows
- **THEN** Tauri initializes main window, tray integration, and restored window state

#### Scenario: Unapproved backend invocation is attempted
- **WHEN** frontend attempts to invoke a command outside the allowlist
- **THEN** invocation is rejected and an error is returned without app crash

### Requirement: Tauri shell supports dictation lifecycle controls
The shell SHALL support application-level hotkey registration, start/stop lifecycle hooks, and graceful shutdown cleanup.

#### Scenario: Global hotkey triggers recording
- **WHEN** configured hotkey is pressed
- **THEN** runtime forwards event to backend command path and transitions UI to recording state

#### Scenario: App closes during active recording
- **WHEN** user exits while recording
- **THEN** runtime stops capture, flushes pending state, and exits cleanly
