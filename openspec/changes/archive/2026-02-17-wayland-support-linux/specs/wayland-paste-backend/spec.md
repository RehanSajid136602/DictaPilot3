## ADDED Requirements

### Requirement: System pastes text on Wayland
The system SHALL paste text using wl-clipboard on Wayland systems.

#### Scenario: Paste text successfully
- **WHEN** system needs to paste text on Wayland
- **THEN** text is copied to clipboard via wl-copy and pasted via keyboard simulation

#### Scenario: wl-clipboard available
- **WHEN** wl-clipboard is installed
- **THEN** system uses wl-copy for clipboard operations

### Requirement: System falls back if wl-clipboard unavailable
The system SHALL use pynput backend if wl-clipboard is not available.

#### Scenario: wl-clipboard not installed
- **WHEN** wl-clipboard is not installed
- **THEN** system falls back to pynput paste backend

#### Scenario: wl-copy command fails
- **WHEN** wl-copy command fails
- **THEN** system falls back to pynput paste backend

### Requirement: System simulates keyboard for paste
The system SHALL simulate Ctrl+V keyboard shortcut to trigger paste.

#### Scenario: Simulate paste shortcut
- **WHEN** text is in clipboard
- **THEN** system simulates Ctrl+V to paste text

#### Scenario: Use wtype for simulation
- **WHEN** wtype is available
- **THEN** system uses wtype for keyboard simulation

#### Scenario: Fallback to pynput simulation
- **WHEN** wtype is not available
- **THEN** system uses pynput for keyboard simulation

### Requirement: System handles paste timing
The system SHALL add appropriate delays for reliable pasting.

#### Scenario: Delay after clipboard copy
- **WHEN** text is copied to clipboard
- **THEN** system waits 50ms before simulating paste

#### Scenario: Verify clipboard content
- **WHEN** paste operation completes
- **THEN** system can verify text was copied correctly
