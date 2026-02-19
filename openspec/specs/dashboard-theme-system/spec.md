## ADDED Requirements

### Requirement: Color token system
The system SHALL provide a token-based color system with semantic names for consistent theming.

#### Scenario: Access color tokens
- **WHEN** a component needs a color value
- **THEN** it retrieves the color from the token system by semantic name

#### Scenario: Dark theme tokens
- **WHEN** dark theme is active
- **THEN** token system returns Catppuccin Mocha color values

#### Scenario: Light theme tokens
- **WHEN** light theme is active
- **THEN** token system returns light theme color values

### Requirement: Typography scale
The system SHALL provide a typography scale with consistent font sizes, weights, and line heights.

#### Scenario: Apply typography tokens
- **WHEN** a component needs text styling
- **THEN** it uses typography tokens for size, weight, and line height

#### Scenario: Font stack fallback
- **WHEN** system font is not available
- **THEN** typography system falls back to next font in stack

### Requirement: Spacing system
The system SHALL provide a base-4 spacing scale for consistent layout spacing.

#### Scenario: Apply spacing tokens
- **WHEN** a component needs padding or margin
- **THEN** it uses spacing tokens (xs, sm, md, lg, xl, 2xl)

### Requirement: Theme switching
The system SHALL allow users to switch between dark and light themes.

#### Scenario: Switch to light theme
- **WHEN** user selects light theme
- **THEN** all components update to use light theme colors

#### Scenario: Switch to dark theme
- **WHEN** user selects dark theme
- **THEN** all components update to use dark theme colors

#### Scenario: Persist theme preference
- **WHEN** user switches theme
- **THEN** preference is saved to config and applied on next launch

### Requirement: System theme detection
The system SHALL detect system theme preference on startup.

#### Scenario: Detect dark system theme
- **WHEN** application starts and system theme is dark
- **THEN** dashboard uses dark theme by default

#### Scenario: Detect light system theme
- **WHEN** application starts and system theme is light
- **THEN** dashboard uses light theme by default

#### Scenario: Override system theme
- **WHEN** user has manually selected a theme
- **THEN** manual selection overrides system theme detection
