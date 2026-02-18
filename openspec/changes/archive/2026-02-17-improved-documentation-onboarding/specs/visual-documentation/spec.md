## ADDED Requirements

### Requirement: Documentation includes screenshots of key features
The system SHALL provide screenshots demonstrating all major features and UI components.

#### Scenario: User views feature screenshots
- **WHEN** user reads feature documentation
- **THEN** they see relevant screenshots showing the feature in action

#### Scenario: Screenshots show current UI state
- **WHEN** screenshots are added or updated
- **THEN** they SHALL accurately reflect the current version of the application

### Requirement: Documentation includes animated GIFs for workflows
The system SHALL provide animated GIFs demonstrating common workflows and interactions.

#### Scenario: User learns voice command workflow
- **WHEN** user reads about voice commands
- **THEN** they see an animated GIF showing the complete workflow from hotkey press to text paste

#### Scenario: GIF demonstrates real-time behavior
- **WHEN** user views a workflow GIF
- **THEN** the GIF shows actual timing and behavior of the feature

### Requirement: Video tutorials cover essential features
The system SHALL provide video tutorials covering installation, basic usage, and key features.

#### Scenario: New user watches quick start video
- **WHEN** a new user wants to learn the basics
- **THEN** they can watch a 3-5 minute video covering installation to first dictation

#### Scenario: User learns advanced features
- **WHEN** user wants to learn about smart editing or profiles
- **THEN** dedicated video tutorials are available for each major feature

### Requirement: Visual assets are properly organized
Visual assets SHALL be organized in a structured directory with clear naming conventions.

#### Scenario: Developer adds new screenshot
- **WHEN** a developer adds a new screenshot
- **THEN** it is placed in docs/assets/screenshots/ with a descriptive filename

#### Scenario: Assets are referenced in documentation
- **WHEN** documentation references a visual asset
- **THEN** the path is relative and works in both local and web documentation

### Requirement: Videos are hosted externally with embeds
Video tutorials SHALL be hosted on YouTube and embedded in documentation.

#### Scenario: User watches embedded video
- **WHEN** user views documentation with video
- **THEN** the video plays inline without leaving the documentation page

#### Scenario: Video is accessible without JavaScript
- **WHEN** user has JavaScript disabled
- **THEN** they see a direct link to the video on YouTube
