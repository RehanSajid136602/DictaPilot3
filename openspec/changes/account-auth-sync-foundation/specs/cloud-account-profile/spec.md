## ADDED Requirements

### Requirement: Account profile provisioning
The system SHALL provision an account profile for each authenticated user.

#### Scenario: First authenticated sign-in
- **WHEN** a user successfully authenticates for the first time
- **THEN** the system creates a cloud account profile for that user
- **AND** the profile contains the default sync preferences needed by the app

#### Scenario: Returning authenticated user
- **WHEN** a previously authenticated user signs in on any device
- **THEN** the system loads the existing account profile
- **AND** the system applies the stored sync preferences to the current session

### Requirement: Sync preference management
The system SHALL let an authenticated user manage whether account-scoped sync is enabled.

#### Scenario: User enables sync
- **WHEN** an authenticated user enables sync in the app
- **THEN** the system stores that preference in the user's cloud account profile
- **AND** the system allows eligible local data domains to participate in cloud sync

#### Scenario: User disables sync
- **WHEN** an authenticated user disables sync in the app
- **THEN** the system updates the user's cloud account profile to reflect that preference
- **AND** the system stops future cloud sync activity while preserving local data

### Requirement: Device registration metadata
The system SHALL track authenticated device metadata for the user account.

#### Scenario: Device joins an authenticated account
- **WHEN** a user signs in on a device that is not yet registered for that account
- **THEN** the system creates a device metadata record linked to the user
- **AND** the record includes a device identifier, platform, and last-seen timestamp

#### Scenario: Device reuses an authenticated account
- **WHEN** an already registered device restores a valid session
- **THEN** the system updates the device metadata last-seen timestamp
- **AND** the system keeps the device associated with the authenticated account
