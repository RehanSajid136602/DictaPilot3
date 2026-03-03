## ADDED Requirements

### Requirement: FAB displays as circular button
The floating action button (FAB) SHALL display as a circular button with 56px diameter in the bottom-right corner of the view.

#### Scenario: FAB rendering
- **WHEN** a view with FAB is displayed
- **THEN** the FAB appears as a 56px circular button in the bottom-right corner

#### Scenario: FAB positioning
- **WHEN** the view is scrolled
- **THEN** the FAB remains fixed in the bottom-right corner with 24px margin

### Requirement: FAB has primary accent color
The FAB SHALL display with accent-blue background (#3b82f6) and white icon/text.

#### Scenario: FAB color
- **WHEN** the FAB is rendered
- **THEN** it displays with #3b82f6 background and white foreground

### Requirement: FAB has hover and pressed states
The FAB SHALL display hover state (lighter blue #60a5fa) and pressed state (darker blue #2563eb).

#### Scenario: Hovering over FAB
- **WHEN** user hovers over the FAB
- **THEN** the background color transitions to #60a5fa

#### Scenario: Pressing FAB
- **WHEN** user presses the FAB
- **THEN** the background color changes to #2563eb

### Requirement: FAB displays icon or text
The FAB SHALL display either an icon (e.g., + symbol) or short text (e.g., "Add").

#### Scenario: Icon display
- **WHEN** FAB is configured with icon
- **THEN** it displays the icon centered in the circle

### Requirement: FAB has elevation shadow
The FAB SHALL display with elevation shadow (8px blur, 40% opacity) to appear floating above content.

#### Scenario: Shadow rendering
- **WHEN** the FAB is rendered
- **THEN** it displays with 8px blur shadow at 40% opacity

### Requirement: FAB is keyboard accessible
The FAB SHALL be focusable and activatable with keyboard (Tab to focus, Enter/Space to activate).

#### Scenario: Keyboard focus
- **WHEN** user presses Tab to reach FAB
- **THEN** the FAB displays focus indicator (2px outline in accent-blue)

#### Scenario: Keyboard activation
- **WHEN** user presses Enter or Space on focused FAB
- **THEN** the FAB action is triggered
