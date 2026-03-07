## ADDED Requirements

### Requirement: Email account registration
The system SHALL allow a desktop user to create an account with an email address, password, and password confirmation.

#### Scenario: Successful email sign-up
- **WHEN** the user submits a valid email, password, and matching confirm-password value
- **THEN** the system creates an authenticated account session
- **AND** the system associates the session with the newly created user identity

#### Scenario: Confirm password mismatch
- **WHEN** the user submits a sign-up form where confirm password does not match the password
- **THEN** the system rejects the submission locally
- **AND** the system shows a validation error without attempting account creation

#### Scenario: Email address already in use
- **WHEN** the user submits a valid sign-up form for an email address that already belongs to an account
- **THEN** the system rejects the sign-up attempt
- **AND** the system shows an actionable error that the user can use to switch to sign-in

### Requirement: Email account sign-in
The system SHALL allow a desktop user to sign in with an existing email address and password.

#### Scenario: Successful email sign-in
- **WHEN** the user submits valid existing email/password credentials
- **THEN** the system creates an authenticated desktop session
- **AND** the system loads the user-owned account state needed for sync

#### Scenario: Invalid email credentials
- **WHEN** the user submits an incorrect email or password
- **THEN** the system rejects the sign-in attempt
- **AND** the system shows an authentication error without altering local signed-out state

### Requirement: Google sign-in
The system SHALL allow a desktop user to authenticate with Google.

#### Scenario: Successful Google sign-in
- **WHEN** the user completes the Google sign-in flow successfully
- **THEN** the system creates an authenticated desktop session for the Google-linked account
- **AND** the system returns the user to DictaPilot with the authenticated state available

#### Scenario: User cancels Google sign-in
- **WHEN** the user abandons or cancels the Google sign-in flow before completion
- **THEN** the system leaves the app in a signed-out state
- **AND** the system does not create or persist a partial authenticated session

### Requirement: User sign-out
The system SHALL allow an authenticated user to sign out from the desktop app.

#### Scenario: Standard sign-out
- **WHEN** an authenticated user chooses sign out
- **THEN** the system clears the active authenticated session
- **AND** the system stops account-scoped sync activity until the user signs in again
