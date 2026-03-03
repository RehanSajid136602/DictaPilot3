## ADDED Requirements

### Requirement: Floating window has pill shape with glassmorphism
The floating window SHALL render as a pill-shaped rectangle (320px × 80px) with glassmorphism effects including background blur (20px), semi-transparent background (rgba(36, 41, 56, 0.7)), and subtle border (1px solid rgba(96, 165, 250, 0.2)).

#### Scenario: Rendering floating window
- **WHEN** the floating window is displayed
- **THEN** it appears as a 320px × 80px pill shape with rounded corners and glassmorphism effects

#### Scenario: Positioning floating window
- **WHEN** the floating window is shown
- **THEN** it positions itself at center-bottom of screen, 40px from the bottom edge

### Requirement: Floating window displays state-based colors
The floating window SHALL display different colors based on recording state: gray (#6b7280) for idle, cyan (#06b6d4) for recording, purple (#8b5cf6) for processing, green (#10b981) for done, and red (#ef4444) for error.

#### Scenario: Recording state color
- **WHEN** recording state is "recording"
- **THEN** the floating window displays cyan (#06b6d4) accent color

#### Scenario: Processing state color
- **WHEN** recording state is "processing"
- **THEN** the floating window displays purple (#8b5cf6) accent color

#### Scenario: Idle state color
- **WHEN** recording state is "idle"
- **THEN** the floating window displays gray (#6b7280) with minimal presence

### Requirement: Floating window contains waveform visualization
The floating window SHALL contain a gradient waveform visualization component displaying 11 bars with real-time amplitude updates.

#### Scenario: Displaying waveform
- **WHEN** the floating window is in recording state
- **THEN** it displays an 11-bar waveform with gradient colors matching the current state

### Requirement: Floating window shows status text
The floating window SHALL display status text indicating current state (e.g., "Listening...", "Processing...", "Done").

#### Scenario: Recording status text
- **WHEN** recording state is "recording"
- **THEN** the status text displays "Listening..."

#### Scenario: Processing status text
- **WHEN** recording state is "processing"
- **THEN** the status text displays "Processing..."

### Requirement: Floating window has close button
The floating window SHALL include a close button (×) that dismisses the window when clicked or when Escape key is pressed.

#### Scenario: Closing with button
- **WHEN** user clicks the close button
- **THEN** the floating window dismisses with fade-out animation

#### Scenario: Closing with keyboard
- **WHEN** user presses Escape key while floating window has focus
- **THEN** the floating window dismisses with fade-out animation

### Requirement: Floating window animates appearance and disappearance
The floating window SHALL animate its appearance with fade-in and slide-up (300ms ease-out) and disappearance with fade-out and slide-down (200ms ease-in).

#### Scenario: Appearing animation
- **WHEN** the floating window is shown
- **THEN** it fades in and slides up from bottom over 300ms with ease-out easing

#### Scenario: Disappearing animation
- **WHEN** the floating window is dismissed
- **THEN** it fades out and slides down over 200ms with ease-in easing

### Requirement: Floating window announces state changes to screen readers
The floating window SHALL use ARIA live regions to announce state changes to screen readers.

#### Scenario: Announcing recording start
- **WHEN** recording state changes to "recording"
- **THEN** screen reader announces "Recording started, listening"

#### Scenario: Announcing processing
- **WHEN** recording state changes to "processing"
- **THEN** screen reader announces "Processing transcription"
