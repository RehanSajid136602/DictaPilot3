## MODIFIED Requirements

### Requirement: Cross-device data sync
The system SHALL synchronize authenticated user-owned settings, snippets, and personal dictionary entries across devices for the same account.

#### Scenario: Authenticated user enables sync
- **WHEN** an authenticated user enables cross-device sync
- **THEN** the system establishes a connection to the user's sync service scope
- **AND** the system uploads eligible local account-owned data to the cloud

#### Scenario: New device joins sync
- **WHEN** the same authenticated user signs in on a new device with sync enabled
- **THEN** the system downloads the user's existing synced data
- **AND** the system merges that data with the local store for the supported domains

#### Scenario: Signed-out user remains local-only
- **WHEN** no authenticated user session exists
- **THEN** the system does not attempt account-scoped cloud sync
- **AND** the system keeps supported domains available in local-only mode

### Requirement: Optional cloud storage
The system SHALL keep cloud backup and sync optional for authenticated users.

#### Scenario: User enables cloud backup
- **WHEN** an authenticated user enables cloud backup or sync
- **THEN** the system regularly persists eligible account-owned data to the cloud
- **AND** the data can be restored by that same account on another device

#### Scenario: User disables cloud sync
- **WHEN** an authenticated user disables cloud sync
- **THEN** the system stops future background cloud synchronization
- **AND** the system preserves existing local data on the device

## ADDED Requirements

### Requirement: Offline-first sync reconciliation
The system SHALL support offline changes for synced domains and reconcile them when connectivity returns.

#### Scenario: User changes synced data while offline
- **WHEN** the user modifies a synced domain while the device cannot reach the sync service
- **THEN** the system writes the change to the local store immediately
- **AND** the system queues the change for later synchronization

#### Scenario: Connectivity returns after offline changes
- **WHEN** queued sync work exists and the device reconnects to the sync service
- **THEN** the system retries the queued cloud operations
- **AND** successful operations are removed from the pending sync queue

### Requirement: Deterministic conflict handling
The system SHALL reconcile conflicting sync updates with last-write-wins semantics and deletion tombstones.

#### Scenario: Same record changes on multiple devices
- **WHEN** the same synced record is modified on more than one device before reconciliation
- **THEN** the system applies the version with the latest update timestamp
- **AND** the system preserves enough metadata to avoid resurrecting stale values

#### Scenario: Record is deleted on one device and edited on another
- **WHEN** a synced record has a deletion tombstone from one device and a stale update from another
- **THEN** the system honors the newest timestamp across the delete and update operations
- **AND** the system prevents deleted records from reappearing unless a newer explicit recreation occurs
