## ADDED Requirements

### Requirement: React UI provides low-latency dictation feedback
The renderer SHALL display idle, recording, processing, success, and error states with smooth, responsive transitions.

#### Scenario: Recording starts
- **WHEN** backend reports recording started
- **THEN** UI reflects recording state within 100ms and displays animated activity indicator

#### Scenario: Processing completes
- **WHEN** backend returns final edited text
- **THEN** UI updates output panel and state badge without blocking user actions

### Requirement: React UI includes core views and accessibility
The renderer SHALL include Home, History, and Settings views with keyboard navigation and readable status messages.

#### Scenario: History search interaction
- **WHEN** user types query in History view
- **THEN** list filters by text and metadata and supports keyboard selection

#### Scenario: Settings update interaction
- **WHEN** user changes hotkey or dictation mode settings
- **THEN** changes persist through backend API and are reflected immediately in UI state
