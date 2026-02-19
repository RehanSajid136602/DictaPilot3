## ADDED Requirements

### Requirement: Button variants
The system SHALL provide four button variants: primary, secondary, destructive, and ghost.

#### Scenario: Primary button styling
- **WHEN** primary button is rendered
- **THEN** it displays with accent-blue background and white text

#### Scenario: Secondary button styling
- **WHEN** secondary button is rendered
- **THEN** it displays with surface1 background and primary text color

#### Scenario: Destructive button styling
- **WHEN** destructive button is rendered
- **THEN** it displays with accent-red background and white text

#### Scenario: Ghost button styling
- **WHEN** ghost button is rendered
- **THEN** it displays with transparent background and secondary text color

#### Scenario: Button hover state
- **WHEN** user hovers over a button
- **THEN** background color changes to hover variant

#### Scenario: Button disabled state
- **WHEN** button is disabled
- **THEN** it displays at 50% opacity and does not respond to clicks

### Requirement: Dropdown components
The system SHALL provide styled dropdown/combobox components matching the theme.

#### Scenario: Dropdown display
- **WHEN** dropdown is rendered
- **THEN** it displays with surface0 background and surface1 border

#### Scenario: Dropdown focus
- **WHEN** dropdown receives focus
- **THEN** border changes to accent-blue

#### Scenario: Dropdown list
- **WHEN** user clicks dropdown
- **THEN** list appears with max 8 visible items and scrollbar if needed

### Requirement: Search bar component
The system SHALL provide a search bar with debouncing and clear button.

#### Scenario: Search input
- **WHEN** user types in search bar
- **THEN** input is debounced with 200ms delay before triggering search

#### Scenario: Clear button appearance
- **WHEN** search bar contains text
- **THEN** X clear button appears on the right

#### Scenario: Clear search
- **WHEN** user clicks X clear button
- **THEN** search text is cleared and search resets

### Requirement: Toggle and checkbox components
The system SHALL provide styled toggle switches and checkboxes.

#### Scenario: Checkbox checked state
- **WHEN** checkbox is checked
- **THEN** it displays with accent-blue background and white checkmark

#### Scenario: Checkbox unchecked state
- **WHEN** checkbox is unchecked
- **THEN** it displays with surface0 background and surface1 border

### Requirement: Modal dialogs
The system SHALL provide modal dialogs with backdrop, header, content, and footer.

#### Scenario: Display modal
- **WHEN** modal is shown
- **THEN** backdrop appears with 40% opacity and modal fades in with scale animation

#### Scenario: Close modal with X
- **WHEN** user clicks X button in modal header
- **THEN** modal closes with fade-out animation

#### Scenario: Close modal with Escape
- **WHEN** user presses Escape key while modal is open
- **THEN** modal closes

#### Scenario: Focus trap
- **WHEN** modal is open
- **THEN** Tab key cycles focus only within modal elements

### Requirement: Tooltip component
The system SHALL provide tooltips with 500ms show delay and 100ms hide delay.

#### Scenario: Show tooltip on hover
- **WHEN** user hovers over element with tooltip for 500ms
- **THEN** tooltip appears above element with 8px offset

#### Scenario: Hide tooltip
- **WHEN** user moves mouse away from element
- **THEN** tooltip hides after 100ms delay

### Requirement: Context menu component
The system SHALL provide context menus with keyboard navigation.

#### Scenario: Show context menu
- **WHEN** user right-clicks on element with context menu
- **THEN** menu appears at cursor position

#### Scenario: Navigate with keyboard
- **WHEN** context menu is open and user presses up/down arrows
- **THEN** focus moves between menu items

#### Scenario: Select menu item
- **WHEN** user clicks or presses Enter on menu item
- **THEN** action executes and menu closes
