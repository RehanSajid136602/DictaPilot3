## ADDED Requirements

### Requirement: Agent mode status display
The system SHALL display current agent mode configuration status including mode state, auto-detect, IDE integration, and output format.

#### Scenario: Display agent mode status
- **WHEN** Agent view is displayed
- **THEN** status section shows current mode, auto-detect state, IDE integration state, and output format

#### Scenario: Toggle agent mode
- **WHEN** user clicks the agent mode toggle
- **THEN** agent mode is enabled/disabled and status updates

### Requirement: Output preview
The system SHALL display a preview of agent output based on current configuration settings.

#### Scenario: Display structured output preview
- **WHEN** output format is set to "structured"
- **THEN** preview shows sample structured output format

#### Scenario: Display markdown output preview
- **WHEN** output format is set to "markdown"
- **THEN** preview shows sample markdown output format

#### Scenario: Display plain output preview
- **WHEN** output format is set to "plain"
- **THEN** preview shows sample plain text output format

### Requirement: Configuration groups
The system SHALL provide configuration groups for output format, IDE integration, webhook, and triggers.

#### Scenario: Configure output format
- **WHEN** user selects an output format option
- **THEN** configuration is saved and preview updates

#### Scenario: Configure IDE integration
- **WHEN** user enables IDE integration and selects IDE type
- **THEN** configuration is saved and status updates

#### Scenario: Configure webhook URL
- **WHEN** user enters a webhook URL
- **THEN** configuration is saved and validated

#### Scenario: Configure auto-detect triggers
- **WHEN** user enables/disables auto-detect
- **THEN** configuration is saved and status updates
