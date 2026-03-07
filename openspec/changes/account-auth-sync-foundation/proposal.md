## Why

DictaPilot needs account-backed sync to become a credible multi-device dictation product instead of a single-device utility. Users should be able to sign in with Google or email/password, keep their account session across app restarts, and bring core personalization data like settings, snippets, and personal dictionary entries to a new device without manual export/import.

## What Changes

- Add account authentication for desktop users with:
  - email sign-up
  - email sign-in
  - password confirmation during sign-up
  - Google sign-in
- Add secure session persistence so authenticated users remain signed in across app restarts until they explicitly sign out or the session is revoked.
- Add account profile and sync preferences so users can enable or disable sync and understand their current account state.
- Extend sync from a local-only feature into an authenticated cloud-backed feature for user-owned settings, snippets, and personal dictionary entries.
- Add local-first sync behavior so DictaPilot remains usable offline and reconciles cloud changes when connectivity returns.
- Add a conflict resolution baseline for synced records using last-write-wins plus deletion tombstones for safe merges.
- Keep transcript history, billing, teams, and organization management out of scope for this foundation change.

## Capabilities

### New Capabilities
- `user-authentication`: Desktop account authentication with email/password and Google sign-in, including sign-up validation and sign-out behavior.
- `session-management`: Secure persistence, restoration, and revocation handling for authenticated desktop sessions.
- `cloud-account-profile`: User account profile state, sync preferences, and account-linked device metadata needed to support cloud sync.

### Modified Capabilities
- `cross-device-sync`: Change sync from an optional generic backup concept into authenticated, account-scoped sync with offline queueing and conflict handling.
- `personal-dictionary`: Extend dictionary entries from local-only management to user-owned data that can sync across authenticated devices.
- `snippet-library`: Extend snippet storage from local-only management to user-owned data that can sync across authenticated devices.

## Impact

**Affected code and systems:**
- `desktop/renderer/*` for auth screens, account settings, sync status, and account-linked UX states
- `desktop/preload/*` for typed auth and sync IPC surface
- `desktop/main/*` for secure OAuth/session bootstrap and desktop auth orchestration
- `desktop/backend/services/*` for auth, session, sync queue, and cloud data coordination
- local storage model for account-aware ownership and sync metadata
- cloud backend and auth provider configuration

**Dependencies and external systems:**
- Firebase Auth for Google sign-in and email/password authentication
- Firestore (or equivalent document database) for account-scoped sync data
- secure OS-backed credential/session storage for desktop session material

**User impact:**
- users gain optional sign-in and multi-device continuity
- authenticated users can restore key personalization data on a new device
- unauthenticated or offline users can continue local-first usage without forced cloud dependency

**Out of scope for this change:**
- transcript history cloud sync by default
- billing and subscription management
- shared workspaces or enterprise administration
- mobile client implementation
