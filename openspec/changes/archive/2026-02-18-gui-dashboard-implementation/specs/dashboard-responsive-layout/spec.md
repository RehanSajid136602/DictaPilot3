## ADDED Requirements

### Requirement: Desktop layout
The system SHALL display full sidebar and 2-column content grid when window width is 1024px or greater.

#### Scenario: Desktop sidebar width
- **WHEN** window width is 1024px or greater
- **THEN** sidebar displays at 220px width with icons and labels

#### Scenario: Desktop content grid
- **WHEN** window width is 1024px or greater
- **THEN** main content uses 2-column grid layout with 16px gap

### Requirement: Tablet layout
The system SHALL collapse sidebar to icon-only mode and use single-column layout when window width is between 768px and 1023px.

#### Scenario: Tablet sidebar width
- **WHEN** window width is between 768px and 1023px
- **THEN** sidebar collapses to 56px width showing only icons

#### Scenario: Tablet content grid
- **WHEN** window width is between 768px and 1023px
- **THEN** main content uses single-column layout with cards stacked vertically

### Requirement: Compact layout
The system SHALL hide sidebar and use mobile-optimized layout when window width is less than 768px.

#### Scenario: Compact sidebar hidden
- **WHEN** window width is less than 768px
- **THEN** sidebar is hidden and hamburger menu icon appears in toolbar

#### Scenario: Compact hamburger menu
- **WHEN** user clicks hamburger menu icon
- **THEN** sidebar appears as overlay drawer at 280px width

#### Scenario: Compact content layout
- **WHEN** window width is less than 768px
- **THEN** all cards stack vertically in single column

### Requirement: Minimum window size
The system SHALL enforce a minimum window size of 900x700 pixels.

#### Scenario: Enforce minimum width
- **WHEN** user attempts to resize window below 900px width
- **THEN** window width stops at 900px minimum

#### Scenario: Enforce minimum height
- **WHEN** user attempts to resize window below 700px height
- **THEN** window height stops at 700px minimum

### Requirement: Responsive chart sizing
The system SHALL adjust chart dimensions based on available space while maintaining minimum readable size.

#### Scenario: Chart width adjustment
- **WHEN** content area width changes
- **THEN** charts resize to fit available width with minimum 320px

#### Scenario: Chart height preservation
- **WHEN** content area width changes
- **THEN** chart heights remain fixed at specified values
