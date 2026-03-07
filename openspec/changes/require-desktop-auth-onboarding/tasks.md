## 1. Startup and auth-state gating

- [x] 1.1 Audit the current desktop startup path and identify every renderer surface still reachable while signed out
- [x] 1.2 Add a dedicated onboarding-gate state in the renderer so only authenticated users can access the main app shell
- [x] 1.3 Update main-process auth bootstrap and invalid-session recovery to route missing or failed sessions into onboarding-required state

## 2. Onboarding experience

- [x] 2.1 Extract or build a dedicated onboarding/auth container from the current account UI
- [x] 2.2 Add separate `Sign up` and `Sign in` entry paths with email, password, and confirm-password form behavior
- [x] 2.3 Keep `Continue with Google` as a one-click onboarding action wired to the existing Google OAuth flow
- [x] 2.4 Add clear signed-out, invalid-session, and configuration error messaging in the onboarding flow

## 3. Session and sign-out behavior

- [x] 3.1 Change sign-out behavior so it clears the session and always returns the user to onboarding instead of local-only access
- [x] 3.2 Ensure restored valid sessions bypass onboarding and enter the main app directly
- [x] 3.3 Ensure expired or revoked sessions force re-authentication without leaving partially usable signed-out app state

## 4. Account-scoped product expectations

- [x] 4.1 Update sync copy and account messaging to reflect that desktop usage is account-first rather than anonymous local-first
- [x] 4.2 Remove or disable any remaining signed-out dictation/settings actions that contradict mandatory authentication
- [x] 4.3 Verify authenticated sync preference controls still work correctly once onboarding is required

## 5. Verification

- [x] 5.1 Add automated tests for first launch without a session, valid session restore, sign-out redirect, and invalid-session redirect
- [x] 5.2 Add renderer tests for onboarding path switching between sign-up, sign-in, and Google entry
- [ ] 5.3 Perform manual packaged-app verification for sign-up, sign-in, Google sign-in, session restore, sign-out, and revoked-session recovery
