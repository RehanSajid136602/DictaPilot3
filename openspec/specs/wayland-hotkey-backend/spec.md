## ADDED Requirements

### Requirement: System registers global hotkeys on Wayland
The system SHALL register global hotkeys using XDG desktop portal on Wayland systems.

#### Scenario: Register hotkey via portal
- **WHEN** user configures a hotkey on Wayland
- **THEN** system registers the hotkey using XDG desktop portal API

#### Scenario: Hotkey triggers callback
- **WHEN** user presses registered hotkey on Wayland
- **THEN** system invokes the registered callback function

### Requirement: System falls back to pynput if portal unavailable
The system SHALL use pynput backend if XDG desktop portal is not available.

#### Scenario: Portal not available
- **WHEN** XDG desktop portal is not available on Wayland
- **THEN** system falls back to pynput hotkey backend

#### Scenario: PyGObject not installed
- **WHEN** PyGObject is not installed
- **THEN** system falls back to pynput hotkey backend

### Requirement: System handles portal permissions
The system SHALL handle permission requests from XDG desktop portal.

#### Scenario: Permission granted
- **WHEN** user grants permission in portal dialog
- **THEN** system successfully registers hotkey

#### Scenario: Permission denied
- **WHEN** user denies permission in portal dialog
- **THEN** system logs error and falls back to pynput

### Requirement: System unregisters hotkeys on cleanup
The system SHALL properly unregister hotkeys when application exits.

#### Scenario: Application exits normally
- **WHEN** application exits
- **THEN** system unregisters all hotkeys via portal

#### Scenario: Application crashes
- **WHEN** application crashes
- **THEN** portal automatically cleans up hotkey registrations
