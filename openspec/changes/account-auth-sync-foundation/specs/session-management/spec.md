## ADDED Requirements

### Requirement: Secure authenticated session persistence
The system SHALL persist authenticated session state securely across desktop app restarts.

#### Scenario: Session stored after authentication
- **WHEN** the user successfully authenticates with email/password or Google
- **THEN** the system stores the session material in encrypted local storage
- **AND** the system does not store the user's plaintext password

#### Scenario: Session restored on app restart
- **WHEN** the app is restarted while a valid authenticated session exists
- **THEN** the system restores the authenticated user state automatically
- **AND** the system resumes account-aware behavior without requiring the user to sign in again

### Requirement: Invalid or revoked session handling
The system SHALL detect invalid, expired, or revoked sessions and recover safely.

#### Scenario: Session refresh fails on startup
- **WHEN** the app attempts to restore a persisted session that is no longer valid
- **THEN** the system clears the invalid session state
- **AND** the system returns the user to a signed-out state with a re-authentication prompt

#### Scenario: Session becomes invalid during use
- **WHEN** an authenticated API or sync request fails because the session is revoked or expired
- **THEN** the system stops account-scoped sync operations
- **AND** the system requires the user to sign in again before cloud operations continue

### Requirement: Sign-out clears local session secrets
The system SHALL remove persisted authenticated session state when the user signs out.

#### Scenario: User signs out
- **WHEN** the user signs out from an authenticated session
- **THEN** the system deletes the locally persisted encrypted session data
- **AND** subsequent app launches start in a signed-out state unless the user authenticates again
