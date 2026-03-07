## Why

DictaPilot now has account-backed sync, but authentication is still optional. That creates an inconsistent product model, weakens cross-device continuity, and leaves the desktop app without a clear first-run identity flow. We need a mandatory onboarding gate so every desktop user signs up or logs in before using the app.

## What Changes

- Add a required first-run authentication gate in the desktop app.
- Require every user to complete one of these paths before reaching the main product:
  - sign up with email, password, and confirm password
  - sign in with email and password
  - continue with Google in one click
- Add a dedicated onboarding/auth entry experience that clearly separates `Sign up` and `Sign in`.
- Enforce authenticated session restoration on app launch so returning users skip onboarding only when a valid saved session exists.
- Add signed-out recovery handling that returns the user to the auth gate when the session is missing, expired, revoked, or cleared.
- Remove local-only anonymous access from the desktop product flow. **BREAKING**
- Update account and sync expectations so sync is no longer an optional enhancement layered on top of anonymous usage; it becomes part of the authenticated desktop experience.

## Capabilities

### New Capabilities
- `desktop-auth-onboarding`: First-run and signed-out desktop entry flow that requires account creation or login before the main app is accessible.
- `user-authentication`: Required desktop authentication with email sign-up, email sign-in, confirm-password validation, Google sign-in, and sign-out recovery.

### Modified Capabilities
- `cross-device-sync`: Sync assumptions change from optional authenticated usage to required account-scoped usage for all desktop users.

## Impact

- `desktop/renderer/*` for the onboarding gate, auth screens, empty/signed-out states, and blocking navigation into the main app until authentication succeeds
- `desktop/preload/*` for required auth state bootstrapping and typed auth actions exposed to the renderer
- `desktop/main/*` for startup gating, session restore enforcement, sign-out handling, and auth-failure redirects
- `desktop/backend/services/*` for mandatory session lifecycle handling and startup auth checks
- onboarding copy, first-run UX, and release behavior for packaged desktop builds
- Firebase Auth configuration remains required for email/password and Google sign-in

User impact:
- every desktop user must authenticate before using DictaPilot
- returning users with a valid saved session continue directly into the app
- users with invalid or missing sessions are returned to the login/sign-up screen instead of using local-only mode
