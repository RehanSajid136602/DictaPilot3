## ADDED Requirements

### Requirement: Required email account registration
The system SHALL require unauthenticated desktop users who choose sign up to register with an email address, password, and confirm-password value before entering the app.

#### Scenario: Successful required sign-up
- **WHEN** the user submits a valid email, password, and matching confirm-password value
- **THEN** the system creates an authenticated account session
- **AND** the system admits the user into the main app experience

#### Scenario: Confirm password mismatch during required sign-up
- **WHEN** the user submits a sign-up form where confirm password does not match the password
- **THEN** the system rejects the submission locally
- **AND** the user remains in the onboarding flow until a valid sign-up or sign-in succeeds

### Requirement: Required email account sign-in
The system SHALL require unauthenticated desktop users who choose sign in to complete email/password authentication before entering the app.

#### Scenario: Successful required sign-in
- **WHEN** the user submits valid existing email/password credentials
- **THEN** the system creates an authenticated desktop session
- **AND** the system admits the user into the main app experience

#### Scenario: Invalid credentials in required sign-in
- **WHEN** the user submits an incorrect email or password
- **THEN** the system rejects the sign-in attempt
- **AND** the user remains blocked from the main app until authentication succeeds

### Requirement: Required Google sign-in path
The system SHALL allow unauthenticated desktop users to enter the app through a one-click Google sign-in path.

#### Scenario: Successful required Google sign-in
- **WHEN** the user completes the Google sign-in flow successfully from onboarding
- **THEN** the system creates an authenticated desktop session for the Google-linked account
- **AND** the system admits the user into the main app experience

#### Scenario: Cancelled required Google sign-in
- **WHEN** the user cancels or abandons the Google sign-in flow
- **THEN** the system returns the user to the onboarding state
- **AND** the user remains blocked from the main app until authentication succeeds
