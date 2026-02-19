## ADDED Requirements

### Requirement: Keyboard navigation
The system SHALL support full keyboard navigation for all interactive elements.

#### Scenario: Tab navigation
- **WHEN** user presses Tab key
- **THEN** focus moves to next focusable element in logical order

#### Scenario: Shift+Tab navigation
- **WHEN** user presses Shift+Tab
- **THEN** focus moves to previous focusable element

#### Scenario: Focus indicators
- **WHEN** an element receives keyboard focus
- **THEN** 2px accent-blue outline appears with 2px offset

#### Scenario: Arrow key navigation in lists
- **WHEN** list has focus and user presses up/down arrows
- **THEN** focus moves between list items

### Requirement: Screen reader support
The system SHALL provide accessible names and descriptions for all interactive widgets.

#### Scenario: Widget accessible names
- **WHEN** screen reader encounters a widget
- **THEN** accessible name is announced via setAccessibleName()

#### Scenario: Widget accessible descriptions
- **WHEN** screen reader needs context for a widget
- **THEN** accessible description is available via setAccessibleDescription()

#### Scenario: Status updates
- **WHEN** status changes (e.g., recording starts)
- **THEN** screen reader announces the status change

### Requirement: Color contrast compliance
The system SHALL maintain WCAG 2.1 AA color contrast ratios for all text and UI elements.

#### Scenario: Text contrast
- **WHEN** text is displayed
- **THEN** contrast ratio is at least 4.5:1 against background

#### Scenario: Large text contrast
- **WHEN** large text (18px+ or 14px+ bold) is displayed
- **THEN** contrast ratio is at least 3:1 against background

#### Scenario: UI component contrast
- **WHEN** interactive UI component is displayed
- **THEN** contrast ratio is at least 3:1 against adjacent colors

### Requirement: Non-color information
The system SHALL not rely solely on color to convey information.

#### Scenario: Status indicators
- **WHEN** status is displayed
- **THEN** it combines color with icon and text label

#### Scenario: Chart data
- **WHEN** chart displays multiple series
- **THEN** series are distinguished by pattern fills and labels in addition to color

### Requirement: Focus management
The system SHALL manage focus appropriately for modals and dynamic content.

#### Scenario: Modal focus trap
- **WHEN** modal is open
- **THEN** Tab key cycles focus only within modal

#### Scenario: Modal close focus return
- **WHEN** modal closes
- **THEN** focus returns to element that triggered modal

#### Scenario: Dynamic content focus
- **WHEN** new content appears dynamically
- **THEN** focus moves to new content if appropriate

### Requirement: Reduced motion support
The system SHALL respect user preference for reduced motion.

#### Scenario: Detect reduced motion preference
- **WHEN** system has reduced motion preference enabled
- **THEN** dashboard disables animations and transitions

#### Scenario: Disable waveform animation
- **WHEN** reduced motion is enabled
- **THEN** waveform shows static bars without animation

#### Scenario: Disable toast slide animation
- **WHEN** reduced motion is enabled
- **THEN** toasts appear instantly without slide-in animation

### Requirement: Resizable text
The system SHALL remain usable when text is scaled up to 200%.

#### Scenario: Text scaling
- **WHEN** user scales text to 200%
- **THEN** layout remains functional and readable without horizontal scrolling

### Requirement: Error identification
The system SHALL identify errors with icon, text, and color.

#### Scenario: Form error display
- **WHEN** form field has error
- **THEN** error is indicated by red border, warning icon, and error text message
