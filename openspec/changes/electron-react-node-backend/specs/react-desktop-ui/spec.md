## ADDED Requirements

### Requirement: React UI delivers low-latency dictation experience
The renderer SHALL provide real-time visual feedback for idle, recording, processing, and error states with smooth transitions and responsive controls.

#### Scenario: Recording state transition
- **WHEN** recording starts
- **THEN** UI transitions to recording state within 100ms and displays animated waveform/indicator

#### Scenario: Streaming text preview
- **WHEN** partial transcription chunks arrive
- **THEN** preview text updates incrementally without blocking controls

### Requirement: React UI provides core desktop views
The renderer SHALL include Home, History, and Settings views with keyboard-accessible interactions.

#### Scenario: User searches history
- **WHEN** the user enters a query in History
- **THEN** results filter in-place and show timestamp, preview, and quick actions

#### Scenario: User updates settings
- **WHEN** the user changes hotkey or mode settings
- **THEN** values persist via backend settings API and are applied on next relevant action
