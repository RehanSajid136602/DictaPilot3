## ADDED Requirements

### Requirement: Electron shell provides secure desktop runtime
The desktop application SHALL run inside Electron with hardened defaults, including `contextIsolation: true`, `nodeIntegration: false`, and a preload-only IPC bridge.

#### Scenario: App launches from executable
- **WHEN** the user starts DictaPilot Desktop on Windows
- **THEN** Electron creates the main window, initializes tray support, and restores last known window state

#### Scenario: Renderer attempts Node access
- **WHEN** renderer code attempts direct Node.js access
- **THEN** access is blocked and only preload-exposed APIs are available

### Requirement: Electron shell supports global dictation lifecycle controls
The desktop shell SHALL expose start/stop dictation controls, app-level hotkey registration, and shutdown-safe cleanup.

#### Scenario: User triggers global hotkey
- **WHEN** the configured hotkey is pressed
- **THEN** shell dispatches a typed IPC event to backend service to start recording

#### Scenario: App exits while recording
- **WHEN** the user quits app during active recording
- **THEN** shell stops recording, flushes pending state, and exits without orphan worker processes
