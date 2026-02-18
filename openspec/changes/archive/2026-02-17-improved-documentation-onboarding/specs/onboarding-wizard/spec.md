## ADDED Requirements

### Requirement: Onboarding wizard launches on first run
The system SHALL automatically launch an onboarding wizard when the application is run for the first time.

#### Scenario: First-time user starts application
- **WHEN** user runs the application for the first time
- **THEN** the onboarding wizard appears before the main application starts

#### Scenario: Returning user starts application
- **WHEN** user has completed setup previously
- **THEN** the application starts normally without showing the wizard

### Requirement: Wizard guides through essential configuration
The onboarding wizard SHALL guide users through configuring API key, hotkey, and audio device.

#### Scenario: User configures API key
- **WHEN** user reaches the API key page
- **THEN** they can enter their Groq API key and the wizard validates it

#### Scenario: User configures hotkey
- **WHEN** user reaches the hotkey page
- **THEN** they can press a key to set it as the dictation hotkey

#### Scenario: User selects audio device
- **WHEN** user reaches the audio device page
- **THEN** they see a list of available microphones and can select one

### Requirement: Wizard can be skipped or cancelled
Users SHALL be able to skip the wizard and configure manually.

#### Scenario: User skips wizard
- **WHEN** user clicks "Skip Setup" button
- **THEN** the wizard closes and the application starts with default settings

#### Scenario: User cancels wizard
- **WHEN** user clicks "Cancel" or closes the wizard window
- **THEN** the application exits gracefully

### Requirement: Wizard validates configuration
The wizard SHALL validate each configuration step before allowing progression.

#### Scenario: User enters invalid API key
- **WHEN** user enters an API key that fails validation
- **THEN** the wizard shows an error message and prevents moving to the next step

#### Scenario: User tests configuration
- **WHEN** user completes configuration
- **THEN** the wizard offers a "Test Dictation" button to verify setup

### Requirement: Wizard can be re-run from settings
Users SHALL be able to re-run the onboarding wizard from the application settings.

#### Scenario: User re-runs setup wizard
- **WHEN** user selects "Re-run Setup Wizard" from settings
- **THEN** the wizard launches with current configuration pre-filled

#### Scenario: User resets to defaults
- **WHEN** user re-runs wizard and completes it
- **THEN** configuration is updated with new values
