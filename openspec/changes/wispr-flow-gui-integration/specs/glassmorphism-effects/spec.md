## ADDED Requirements

### Requirement: Glassmorphism effect applies blur and transparency
The glassmorphism effect SHALL apply background blur (20px default) and semi-transparent background (0.7 opacity default) to components.

#### Scenario: Applying glassmorphism to card
- **WHEN** glassmorphism effect is applied to a card component
- **THEN** the card displays with 20px background blur and 70% opacity

#### Scenario: Custom blur radius
- **WHEN** glassmorphism effect is applied with custom blur radius of 15px
- **THEN** the component displays with 15px background blur

### Requirement: Glassmorphism effect adds glass border
The glassmorphism effect SHALL add a 1px border with glass-border color (rgba(96, 165, 250, 0.2)).

#### Scenario: Glass border rendering
- **WHEN** glassmorphism effect is applied
- **THEN** the component displays a 1px border with rgba(96, 165, 250, 0.2) color

### Requirement: Glassmorphism detects performance capabilities
The glassmorphism utility SHALL detect GPU capabilities and disable effects on low-end hardware.

#### Scenario: High-end hardware
- **WHEN** glassmorphism is initialized on hardware with GPU acceleration
- **THEN** blur effects are enabled

#### Scenario: Low-end hardware
- **WHEN** glassmorphism is initialized on hardware without GPU acceleration
- **THEN** blur effects are disabled and fallback to solid background

### Requirement: Glassmorphism respects disable flag
The glassmorphism utility SHALL respect DISABLE_GLASSMORPHISM environment variable.

#### Scenario: Glassmorphism disabled
- **WHEN** DISABLE_GLASSMORPHISM environment variable is set to true
- **THEN** all glassmorphism effects are disabled and components use solid backgrounds

### Requirement: Glassmorphism caches blur effects
The glassmorphism utility SHALL cache QGraphicsBlurEffect objects to improve performance.

#### Scenario: Reusing blur effect
- **WHEN** multiple components request the same blur radius
- **THEN** the same cached QGraphicsBlurEffect object is reused
