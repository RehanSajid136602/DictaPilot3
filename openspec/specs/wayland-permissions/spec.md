## ADDED Requirements

### Requirement: System requests permissions appropriately
The system SHALL request necessary permissions from Wayland compositor.

#### Scenario: Request global shortcut permission
- **WHEN** system needs to register global hotkey
- **THEN** XDG portal shows permission dialog to user

#### Scenario: Permission dialog appears
- **WHEN** permission dialog is shown
- **THEN** system displays console message explaining the dialog

### Requirement: System handles permission responses
The system SHALL handle both granted and denied permissions gracefully.

#### Scenario: User grants permission
- **WHEN** user clicks "Allow" in permission dialog
- **THEN** system proceeds with hotkey registration

#### Scenario: User denies permission
- **WHEN** user clicks "Deny" in permission dialog
- **THEN** system logs warning and uses fallback backend

#### Scenario: User closes dialog
- **WHEN** user closes permission dialog without responding
- **THEN** system treats it as denied and uses fallback

### Requirement: System provides permission troubleshooting
The system SHALL provide clear guidance when permissions are denied.

#### Scenario: Permission denied message
- **WHEN** permission is denied
- **THEN** system shows message with troubleshooting steps

#### Scenario: Re-request permission
- **WHEN** user wants to grant permission after denying
- **THEN** system provides way to re-request permission

### Requirement: System logs permission events
The system SHALL log all permission-related events for debugging.

#### Scenario: Log permission request
- **WHEN** system requests permission
- **THEN** event is logged with timestamp

#### Scenario: Log permission response
- **WHEN** user responds to permission dialog
- **THEN** response is logged with result (granted/denied)
