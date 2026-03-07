## MODIFIED Requirements

### Requirement: Cross-device data sync
The system SHALL synchronize authenticated user-owned settings, snippets, and personal dictionary entries across devices for the same account.

#### Scenario: Authenticated user reaches the desktop app
- **WHEN** a desktop user completes authentication and enters the app
- **THEN** the system treats supported synced domains as account-scoped data
- **AND** the system prepares authenticated sync state for that account

#### Scenario: New device joins sync
- **WHEN** the same authenticated user signs in on a new device
- **THEN** the system downloads the user's existing data
- **AND** merges it with the device's local storage for supported domains

#### Scenario: Conflict resolution
- **WHEN** the same entry is modified on multiple authenticated devices
- **THEN** the system applies last-write-wins
- **AND** logs or preserves metadata needed for deterministic reconciliation

### Requirement: Optional cloud storage
The system SHALL offer account-scoped cloud backup and sync controls within the authenticated desktop experience.

#### Scenario: Authenticated user enables cloud backup
- **WHEN** an authenticated user enables cloud backup or sync
- **THEN** the system regularly backs up eligible account-owned data to the cloud
- **AND** allows restoration by that same account on another device

#### Scenario: User signs out of the desktop app
- **WHEN** the current authenticated user signs out
- **THEN** the system stops future account-scoped cloud synchronization
- **AND** returns the user to required authentication onboarding instead of local-only app usage
