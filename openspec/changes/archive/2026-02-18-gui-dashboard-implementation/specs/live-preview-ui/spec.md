## MODIFIED Requirements

### Requirement: Dashboard integration
The floating indicator bar SHALL remain as the minimal recording UI while the dashboard serves as the control center.

#### Scenario: Independent operation
- **WHEN** dashboard is closed
- **THEN** floating indicator bar continues to function independently

#### Scenario: Dashboard reflects recording state
- **WHEN** recording starts via floating indicator bar
- **THEN** dashboard status card updates to show "Recording" state

#### Scenario: Dashboard controls recording
- **WHEN** user starts recording from dashboard
- **THEN** floating indicator bar updates to show recording state

#### Scenario: Synchronized state
- **WHEN** recording state changes in either UI
- **THEN** both dashboard and floating indicator bar reflect the same state
