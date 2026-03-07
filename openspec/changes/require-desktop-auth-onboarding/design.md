## Context

DictaPilot already has desktop authentication, session restore, Google OAuth, and account-scoped sync, but the current product flow still allows signed-out usage and local-only behavior. The requested change is not just a UI tweak; it changes the entry contract for the desktop app so authentication becomes a required prerequisite for access. This affects startup behavior, renderer routing, session recovery, sign-out handling, sync assumptions, and packaged-build readiness.

The desktop stack is split across Electron main, preload, renderer, and backend services. Authentication state is already owned in the main process and published to the renderer. That existing structure should remain the source of truth, but the renderer and startup flow need a stronger gating model so users cannot interact with dictation features until a valid authenticated session exists.

## Goals / Non-Goals

**Goals:**
- Require a valid authenticated session before the desktop app exposes its main product surfaces.
- Present a dedicated auth onboarding experience with clear `Sign up`, `Sign in`, and `Continue with Google` paths.
- Restore users directly into the app only when a persisted session is valid.
- Return users to the auth onboarding gate when the session is missing, expired, revoked, or explicitly cleared.
- Keep the implementation aligned with the existing Firebase-backed auth stack instead of introducing a second auth architecture.

**Non-Goals:**
- Redesign the underlying Firebase provider implementation.
- Add billing, subscriptions, team workspaces, or role-based access control.
- Change transcript sync scope or introduce additional cloud domains beyond the existing account-backed foundation.
- Build mobile onboarding or web account management flows.

## Decisions

### Gate the renderer on authenticated auth state
The renderer will treat `authenticated` as the only state that unlocks the main app shell. Any other state, including startup restore failure, missing session, sign-out, or revoked session, will render the auth onboarding screen instead.

Why:
- It centralizes enforcement in the UI layer users actually interact with.
- It avoids partial access bugs where signed-out users can still reach settings or dictation controls.
- It reuses the existing main-process auth state publication model.

Alternative considered:
- Gating only specific actions while leaving the main shell visible. Rejected because it creates confusing half-signed-in states and more surface area for accidental anonymous usage.

### Keep auth state authoritative in Electron main
The main process remains responsible for bootstrapping session restore, validating saved sessions, performing sign-in flows, and emitting auth-state changes. The renderer only reacts to that state and invokes typed IPC actions.

Why:
- Session material is already persisted securely in the desktop process using `safeStorage`.
- Google OAuth and Firebase session exchange already live in trusted main/backend code.
- It keeps secrets and refresh tokens out of renderer-owned logic.

Alternative considered:
- Moving startup auth logic into the renderer. Rejected for security and because it would duplicate state orchestration already present in main.

### Convert sign-out from “local-only fallback” to “return to onboarding”
When a user signs out, the app will clear the session, stop sync, and immediately return to the onboarding/auth screen. The signed-out mode remains a transient auth state, not a usable operating mode.

Why:
- It matches the new product requirement that authentication is mandatory.
- It simplifies sync expectations because every active user session is account-scoped.
- It prevents a confusing split where sign-out appears to keep the product fully usable.

Alternative considered:
- Preserve existing local-only access after sign-out. Rejected because it contradicts the requirement that all users must log in or sign up before using the app.

### Keep onboarding in-app rather than forcing browser-only account creation
Email sign-up/sign-in remain native in the desktop auth screen, while Google sign-in continues to use the system-browser OAuth flow.

Why:
- Email onboarding is faster and clearer when it happens directly in the app.
- Google on desktop still benefits from the safer browser-based PKCE flow already implemented.
- This combination minimizes changes while satisfying the required one-click Google path.

Alternative considered:
- Move all auth into an external hosted page. Rejected because it adds infrastructure and weakens the desktop onboarding experience.

### Treat sync as an authenticated feature by definition
The app will no longer describe sync as an add-on for users who may remain local-only forever. Once authenticated, account-linked sync remains part of the desktop identity model, with the existing enabled/disabled preference controlling whether replication is active.

Why:
- It keeps the current sync preference behavior without preserving anonymous product access.
- It aligns product messaging: account first, then sync preference within the account.

Alternative considered:
- Automatically force sync on for every authenticated user. Rejected because the current design already includes a user-controlled sync preference, and removing it would be a separate product decision.

## Risks / Trade-offs

- [Firebase misconfiguration blocks the entire app] → Add startup-safe error messaging in the onboarding screen so configuration failures are visible and actionable instead of leaving a blank or broken shell.
- [Signed-out recovery loops or flicker on launch] → Distinguish `bootstrapping` from `signed-out` in the renderer and only render onboarding after main has resolved session restore.
- [Existing users are surprised by the removal of local-only mode] → Update onboarding copy, release notes, and sign-out messaging to explain that an account is now required.
- [Session expiry during active use interrupts workflows] → On invalid session detection, preserve a clear error reason and route the user back to onboarding with a re-auth prompt.
- [Auth screen becomes too tightly coupled to the existing settings/account panel] → Extract a dedicated onboarding container instead of layering more conditions into the current settings-only account section.

## Migration Plan

1. Add a dedicated onboarding/auth state in the renderer and route startup through it until auth bootstrap completes.
2. Update main-process startup and sign-out flows to treat missing or invalid sessions as onboarding-required states rather than local-only fallbacks.
3. Refactor the existing account UI into reusable sign-up/sign-in components that can be shown as the first-run experience and as signed-out recovery.
4. Update sync and copy expectations so the authenticated flow is the default desktop model.
5. Validate packaged builds with email sign-up, email sign-in, Google sign-in, session restore, sign-out, and invalid-session recovery.

Rollback:
- Re-enable the current signed-out local-only renderer path and restore the previous sign-out behavior while keeping the underlying auth infrastructure unchanged.

## Open Questions

- Should there be any guest/demo path for internal testing builds, or is the auth gate universal across all packaged variants?
- Should the app block all renderer content until Firebase config is valid, or should it render onboarding with an explicit configuration error panel for developer builds?
- Do we want to require email verification before entering the app, or is authenticated account creation sufficient for the first release of mandatory onboarding?
