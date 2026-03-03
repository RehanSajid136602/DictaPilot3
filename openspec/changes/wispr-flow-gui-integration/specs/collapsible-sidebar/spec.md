## ADDED Requirements

### Requirement: Sidebar displays in collapsed or expanded state
The sidebar SHALL display in either collapsed state (64px width, icons only) or expanded state (240px width, icons with labels).

#### Scenario: Collapsed state
- **WHEN** sidebar is in collapsed state
- **THEN** it displays at 64px width showing only icons

#### Scenario: Expanded state
- **WHEN** sidebar is in expanded state
- **THEN** it displays at 240px width showing icons with text labels

### Requirement: Sidebar toggle button switches state
The sidebar SHALL include a toggle button that switches between collapsed and expanded states with smooth animation.

#### Scenario: Expanding sidebar
- **WHEN** user clicks toggle button in collapsed state
- **THEN** sidebar animates to 240px width over 250ms showing text labels

#### Scenario: Collapsing sidebar
- **WHEN** user clicks toggle button in expanded state
- **THEN** sidebar animates to 64px width over 250ms hiding text labels

### Requirement: Active sidebar item shows left border
The active sidebar item SHALL display a 3px left border in accent-blue color (#3b82f6) and bg-surface background.

#### Scenario: Home item active
- **WHEN** Home view is displayed
- **THEN** Home sidebar item shows 3px blue left border and bg-surface background

### Requirement: Sidebar items have hover state
Sidebar items SHALL display hover state with bg-surface background.

#### Scenario: Hovering over item
- **WHEN** user hovers over a sidebar item
- **THEN** the item background changes to bg-surface with smooth transition

### Requirement: Sidebar auto-collapses on small screens
The sidebar SHALL automatically collapse when window width is less than 1280px.

#### Scenario: Resizing to small screen
- **WHEN** window width becomes less than 1280px
- **THEN** sidebar automatically collapses to 64px width
