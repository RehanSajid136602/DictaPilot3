## ADDED Requirements

### Requirement: System health checks display
The system SHALL display results from HealthChecker including API key, microphone, display server, paste backend, dependencies, and hotkey backend status.

#### Scenario: Display all health checks
- **WHEN** Diagnostics view is displayed
- **THEN** all diagnostic results are shown with icons, names, messages, and severity

#### Scenario: Passed check display
- **WHEN** a diagnostic check passes
- **THEN** row shows green checkmark icon and green left border

#### Scenario: Warning check display
- **WHEN** a diagnostic check has warnings
- **THEN** row shows yellow warning icon and yellow left border

#### Scenario: Failed check display
- **WHEN** a diagnostic check fails
- **THEN** row shows red X icon and red left border

### Requirement: Run diagnostics action
The system SHALL provide a button to manually run all diagnostic checks.

#### Scenario: Run all checks
- **WHEN** user clicks "Run All Checks" button
- **THEN** system executes all diagnostic checks and updates display

#### Scenario: Display last checked timestamp
- **WHEN** diagnostics have been run
- **THEN** view shows "Last checked: X minutes ago" timestamp

### Requirement: Detailed logs
The system SHALL provide expandable detailed logs for diagnostic output.

#### Scenario: Expand logs
- **WHEN** user clicks "Detailed Logs" section
- **THEN** section expands to show full diagnostic output

#### Scenario: Collapse logs
- **WHEN** user clicks expanded "Detailed Logs" section
- **THEN** section collapses to hide diagnostic output

### Requirement: Auto-refresh on view open
The system SHALL automatically run diagnostics when the Diagnostics view is opened if last check was more than 5 minutes ago.

#### Scenario: Auto-run stale diagnostics
- **WHEN** user navigates to Diagnostics view and last check was over 5 minutes ago
- **THEN** system automatically runs all diagnostic checks
