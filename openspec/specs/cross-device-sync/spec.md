## ADDED Requirements

### Requirement: Cross-device data sync
The system SHALL synchronize personal dictionary, snippets, and preferences across devices.

#### Scenario: User enables sync
- **WHEN** user enables cross-device sync
- **THEN** system establishes connection to sync service
- **AND** uploads local data to cloud

#### Scenario: New device joins sync
- **WHEN** user signs in on new device
- **THEN** system downloads existing data
- **AND** merges with local storage

#### Scenario: Conflict resolution
- **WHEN** same entry modified on multiple devices
- **THEN** system applies last-write-wins
- **AND** logs conflict for user review if needed

### Requirement: Optional cloud storage
The system SHALL offer optional cloud backup for local data.

#### Scenario: User enables cloud backup
- **WHEN** user enables cloud backup
- **THEN** system regularly backs up data to cloud
- **AND** allows restoration from any device
