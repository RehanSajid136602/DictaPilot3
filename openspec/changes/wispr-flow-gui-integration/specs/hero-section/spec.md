## ADDED Requirements

### Requirement: Hero section displays with gradient background
The hero section SHALL display with blue-purple gradient background (135deg, #3b82f6 to #8b5cf6) and glassmorphism overlay.

#### Scenario: Rendering hero background
- **WHEN** the home view is displayed
- **THEN** the hero section displays with blue-purple gradient background

### Requirement: Hero section contains title and subtitle
The hero section SHALL contain a title in display typography (32px, 700 weight) and subtitle in body typography (15px, 400 weight).

#### Scenario: Title rendering
- **WHEN** the hero section is rendered
- **THEN** the title "Welcome to DictaPilot" displays in 32px bold text

#### Scenario: Subtitle rendering
- **WHEN** the hero section is rendered
- **THEN** the subtitle "Press F9 to start dictating" displays in 15px regular text

### Requirement: Hero section contains primary action button
The hero section SHALL contain a large primary action button (48px height, 150px minimum width) with "Start Dictating" text.

#### Scenario: Action button rendering
- **WHEN** the hero section is rendered
- **THEN** a primary button displays with "▶ Start Dictating" text at 48px height

#### Scenario: Action button click
- **WHEN** user clicks the "Start Dictating" button
- **THEN** the recording starts and floating window appears

### Requirement: Hero section has minimum height
The hero section SHALL have a minimum height of 80px with 16px vertical padding.

#### Scenario: Hero section height
- **WHEN** the hero section is rendered
- **THEN** it displays with at least 80px height plus padding
