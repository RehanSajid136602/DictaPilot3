## ADDED Requirements

### Requirement: Account-scoped personal dictionary sync
The system SHALL sync user-owned personal dictionary entries across authenticated devices.

#### Scenario: Signed-in user adds dictionary entry
- **WHEN** an authenticated user creates or updates a personal dictionary entry
- **THEN** the system writes the change to the local dictionary store immediately
- **AND** the system marks the entry for account-scoped cloud synchronization

#### Scenario: Authenticated user signs in on another device
- **WHEN** the same authenticated user signs in on a second device with sync enabled
- **THEN** the system downloads that user's synced personal dictionary entries
- **AND** the entries become available to future transcription on that device

### Requirement: Local-only dictionary behavior without sync
The system SHALL preserve personal dictionary behavior when no authenticated sync session exists.

#### Scenario: User is signed out
- **WHEN** the user manages personal dictionary entries while signed out
- **THEN** the system stores and uses those entries locally
- **AND** the system does not require cloud connectivity for dictionary functionality
