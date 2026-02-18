## ADDED Requirements

### Requirement: Architecture documentation explains system design
The system SHALL provide architecture documentation explaining the overall design and component interactions.

#### Scenario: Developer understands audio pipeline
- **WHEN** developer reads architecture docs
- **THEN** they understand the flow from audio capture through transcription to paste

#### Scenario: Developer understands smart editor
- **WHEN** developer reads architecture docs
- **THEN** they understand how heuristic and LLM modes work and when each is used

### Requirement: API reference documents public interfaces
The system SHALL provide API reference documentation for public modules and functions.

#### Scenario: Developer uses transcription API
- **WHEN** developer wants to integrate transcription
- **THEN** they find documented functions with parameters, return values, and examples

#### Scenario: Developer extends smart editor
- **WHEN** developer wants to add custom commands
- **THEN** they find documented extension points and examples

### Requirement: Contributing guide explains development workflow
The system SHALL provide a contributing guide explaining how to set up development environment and submit changes.

#### Scenario: New contributor sets up environment
- **WHEN** new contributor wants to contribute
- **THEN** they find step-by-step instructions for cloning, installing dependencies, and running tests

#### Scenario: Contributor submits pull request
- **WHEN** contributor completes a change
- **THEN** the guide explains PR requirements: tests, documentation, code style

### Requirement: Developer docs include code examples
Developer documentation SHALL include working code examples for common integration scenarios.

#### Scenario: Developer adds custom backend
- **WHEN** developer wants to add a new paste backend
- **THEN** they find example code showing the required interface and implementation

#### Scenario: Developer adds custom profile
- **WHEN** developer wants to create a profile bundle
- **THEN** they find example JSON with all available options documented
