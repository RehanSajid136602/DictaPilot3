## ADDED Requirements

### Requirement: Account-scoped snippet sync
The system SHALL sync user-owned snippets across authenticated devices.

#### Scenario: Signed-in user creates or edits snippet
- **WHEN** an authenticated user creates, updates, or deletes a snippet
- **THEN** the system applies the change to the local snippet store immediately
- **AND** the system marks the snippet record for account-scoped cloud synchronization

#### Scenario: Authenticated user restores snippets on another device
- **WHEN** the same authenticated user signs in on another device with sync enabled
- **THEN** the system downloads that user's synced snippets
- **AND** the snippets become available for normal snippet activation on that device

### Requirement: Local-only snippet behavior without sync
The system SHALL preserve snippet-library behavior when no authenticated sync session exists.

#### Scenario: User is signed out
- **WHEN** the user manages snippets while signed out
- **THEN** the system stores and uses snippets locally
- **AND** the system does not require cloud connectivity for snippet functionality
