## ADDED Requirements

### Requirement: Mandatory desktop authentication gate
The system SHALL require a valid authenticated account session before a desktop user can access DictaPilot's main application surfaces.

#### Scenario: First launch without a saved session
- **WHEN** the desktop app starts and no valid persisted session exists
- **THEN** the system displays the authentication onboarding flow
- **AND** the system does not expose the main dictation interface before authentication succeeds

#### Scenario: Valid session restores on launch
- **WHEN** the desktop app starts and a valid persisted authenticated session is restored
- **THEN** the system bypasses the onboarding flow
- **AND** the system opens directly into the main authenticated app experience

### Requirement: Dedicated authentication onboarding entry
The system SHALL present a dedicated onboarding entry that offers separate `Sign up`, `Sign in`, and `Continue with Google` actions.

#### Scenario: User selects sign-up path
- **WHEN** a signed-out user chooses the sign-up action from onboarding
- **THEN** the system displays the email registration form
- **AND** the flow includes fields for email, password, and confirm password

#### Scenario: User selects sign-in path
- **WHEN** a signed-out user chooses the sign-in action from onboarding
- **THEN** the system displays the email sign-in form
- **AND** the flow allows the user to submit existing email/password credentials

#### Scenario: User selects Google sign-in
- **WHEN** a signed-out user activates `Continue with Google`
- **THEN** the system starts the Google sign-in flow immediately
- **AND** the system returns the user to the authenticated app when the flow completes successfully

### Requirement: Signed-out recovery returns to onboarding
The system SHALL route the desktop app back to the authentication onboarding flow whenever an active session is cleared or becomes invalid.

#### Scenario: User signs out
- **WHEN** an authenticated desktop user signs out
- **THEN** the system clears the active session
- **AND** the system returns the user to the authentication onboarding flow

#### Scenario: Session becomes invalid
- **WHEN** the current authenticated session expires, is revoked, or fails restoration
- **THEN** the system ends the active session
- **AND** the system requires the user to authenticate again through onboarding
