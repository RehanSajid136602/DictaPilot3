## ADDED Requirements

### Requirement: Sidebar navigation system
The system SHALL provide a left sidebar with icon-based navigation that allows users to switch between dashboard views.

#### Scenario: Navigate to view via sidebar
- **WHEN** user clicks a sidebar navigation item
- **THEN** the main content area displays the corresponding view

#### Scenario: Sidebar shows active view
- **WHEN** a view is active
- **THEN** the corresponding sidebar item displays a 3px blue left border and surface1 background

### Requirement: Collapsible sidebar
The system SHALL allow users to collapse the sidebar to icon-only mode to save screen space.

#### Scenario: Collapse sidebar
- **WHEN** user clicks the collapse button or window width is below 1024px
- **THEN** sidebar width changes from 220px to 56px showing only icons

#### Scenario: Expand sidebar
- **WHEN** user clicks the expand button or window width is above 1024px
- **THEN** sidebar width changes from 56px to 220px showing icons and labels

#### Scenario: Icon tooltips in collapsed mode
- **WHEN** sidebar is collapsed and user hovers over an icon
- **THEN** a tooltip displays the view name

### Requirement: Breadcrumb navigation
The system SHALL display a breadcrumb bar showing the current navigation path.

#### Scenario: Display current path
- **WHEN** user navigates to Settings > Audio
- **THEN** breadcrumb bar displays "Home > Settings > Audio"

#### Scenario: Navigate via breadcrumb
- **WHEN** user clicks "Settings" in breadcrumb "Home > Settings > Audio"
- **THEN** system navigates to Settings view

### Requirement: Keyboard shortcuts
The system SHALL provide keyboard shortcuts for quick navigation between views.

#### Scenario: Navigate with Ctrl+H
- **WHEN** user presses Ctrl+H
- **THEN** system navigates to Home view

#### Scenario: Navigate with Ctrl+comma
- **WHEN** user presses Ctrl+,
- **THEN** system navigates to Settings view

#### Scenario: Focus search with Ctrl+F
- **WHEN** user presses Ctrl+F
- **THEN** global search bar receives focus

#### Scenario: Navigate with arrow keys
- **WHEN** sidebar has focus and user presses up/down arrows
- **THEN** focus moves between navigation items

#### Scenario: Collapse sidebar with Escape
- **WHEN** user presses Escape
- **THEN** sidebar collapses to icon-only mode if expanded
