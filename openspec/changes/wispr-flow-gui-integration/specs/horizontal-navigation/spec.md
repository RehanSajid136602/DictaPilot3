## ADDED Requirements

### Requirement: Top navigation bar displays horizontally
The top navigation bar SHALL display horizontally at the top of the dashboard with 56px height, spanning the full width.

#### Scenario: Rendering navigation bar
- **WHEN** the dashboard is displayed
- **THEN** the top navigation bar renders at 56px height with bg-elevated background

#### Scenario: Full width layout
- **WHEN** the window is resized
- **THEN** the navigation bar spans the full width of the window

### Requirement: Navigation bar contains logo and menu items
The navigation bar SHALL contain the DictaPilot logo on the left, navigation menu items in the center, and action buttons on the right.

#### Scenario: Logo placement
- **WHEN** the navigation bar is rendered
- **THEN** the DictaPilot logo appears on the left side with 16px padding

#### Scenario: Menu items placement
- **WHEN** the navigation bar is rendered
- **THEN** menu items (Home, Settings, Statistics, History, Dictionary, Profiles, Help) appear in the center

#### Scenario: Action buttons placement
- **WHEN** the navigation bar is rendered
- **THEN** theme toggle, notifications, and user menu appear on the right side

### Requirement: Active navigation item shows bottom border
The active navigation item SHALL display a 3px bottom border in accent-blue color (#3b82f6).

#### Scenario: Home is active
- **WHEN** the Home view is displayed
- **THEN** the Home navigation item shows a 3px blue bottom border

#### Scenario: Settings is active
- **WHEN** the Settings view is displayed
- **THEN** the Settings navigation item shows a 3px blue bottom border

### Requirement: Navigation items have hover state
Navigation items SHALL display hover state with text color changing to text-primary (#e8eaed).

#### Scenario: Hovering over inactive item
- **WHEN** user hovers over an inactive navigation item
- **THEN** the text color changes to text-primary with smooth transition

### Requirement: Navigation supports keyboard navigation
The navigation bar SHALL support keyboard navigation with Tab key to move between items and Enter/Space to activate.

#### Scenario: Tab navigation
- **WHEN** user presses Tab key
- **THEN** focus moves to the next navigation item with visible focus indicator

#### Scenario: Activating with keyboard
- **WHEN** user presses Enter or Space on a focused navigation item
- **THEN** the corresponding view is displayed
