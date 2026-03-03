## ADDED Requirements

### Requirement: Theme system provides Wispr Flow color tokens
The theme system SHALL provide a complete set of Wispr Flow color tokens including backgrounds, text colors, accent colors (blues and purples), state colors (cyan, magenta), semantic colors (success, warning, error), and glassmorphism values.

#### Scenario: Accessing background colors
- **WHEN** a component requests a background color token
- **THEN** the theme system returns the appropriate Wispr Flow background color (bg-base: #0f1419, bg-elevated: #1a1f2e, bg-surface: #242938, bg-overlay: #2d3548)

#### Scenario: Accessing accent colors
- **WHEN** a component requests an accent color token
- **THEN** the theme system returns the appropriate blue or purple shade (accent-blue: #3b82f6, accent-purple: #8b5cf6, etc.)

#### Scenario: Accessing state colors
- **WHEN** a component requests a state-specific color
- **THEN** the theme system returns cyan (#06b6d4) for recording state or magenta (#d946ef) for processing state

### Requirement: Theme system provides typography scale
The theme system SHALL provide a typography scale with font sizes, weights, and line heights for display, headings, body text, captions, and monospace text.

#### Scenario: Applying display typography
- **WHEN** a component applies display typography
- **THEN** the text renders at 32px size, 700 weight, with 40px line height

#### Scenario: Applying body typography
- **WHEN** a component applies body typography
- **THEN** the text renders at 15px size, 400 weight, with 24px line height

### Requirement: Theme system provides spacing scale
The theme system SHALL provide a spacing scale based on 8px increments (xs: 4px, sm: 8px, md: 16px, lg: 24px, xl: 32px, 2xl: 48px, 3xl: 64px).

#### Scenario: Applying medium spacing
- **WHEN** a component requests medium spacing
- **THEN** the theme system returns 16px

#### Scenario: Applying extra large spacing
- **WHEN** a component requests extra large spacing
- **THEN** the theme system returns 32px

### Requirement: Theme system provides border radius values
The theme system SHALL provide border radius values for small (6px), medium (12px), large (16px), and pill (9999px) shapes.

#### Scenario: Applying pill border radius
- **WHEN** a component requests pill border radius
- **THEN** the theme system returns 9999px for fully rounded edges

### Requirement: Theme system provides gradient definitions
The theme system SHALL provide gradient definitions for blue-purple (135deg, #3b82f6 to #8b5cf6) and cyan-blue (135deg, #06b6d4 to #3b82f6) gradients.

#### Scenario: Applying blue-purple gradient
- **WHEN** a component requests the blue-purple gradient
- **THEN** the theme system returns a linear gradient from #3b82f6 to #8b5cf6 at 135 degrees

### Requirement: Theme system supports color contrast validation
The theme system SHALL validate that all text/background color combinations meet WCAG 2.1 AA contrast ratio requirements (minimum 4.5:1 for normal text).

#### Scenario: Validating text on background
- **WHEN** text-primary (#e8eaed) is placed on bg-base (#0f1419)
- **THEN** the contrast ratio is at least 4.5:1 and passes WCAG 2.1 AA

#### Scenario: Rejecting insufficient contrast
- **WHEN** a color combination has contrast ratio below 4.5:1
- **THEN** the theme system logs a warning and suggests alternative colors

### Requirement: Theme system provides stylesheet generation
The theme system SHALL generate complete QSS (Qt Style Sheet) with all Wispr Flow tokens applied to Qt widgets.

#### Scenario: Generating stylesheet for buttons
- **WHEN** the theme system generates a stylesheet
- **THEN** QPushButton styles include Wispr Flow colors, border radius, and hover states

#### Scenario: Generating stylesheet for inputs
- **WHEN** the theme system generates a stylesheet
- **THEN** QLineEdit styles include bg-surface background, bottom border focus state, and text colors
