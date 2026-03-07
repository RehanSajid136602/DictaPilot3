## 1. Provider and contract setup

- [ ] 1.1 Add Firebase Auth and Firestore dependencies to the desktop workspace and document required environment variables
- [x] 1.2 Define shared TypeScript models for auth state, session payloads, sync preferences, device metadata, and sync record metadata
- [x] 1.3 Add IPC channel contracts for sign-up, sign-in, Google sign-in, sign-out, session status, sync status, and sync preference updates
- [x] 1.4 Create provider configuration validation so the app fails safely when Firebase settings are missing or invalid

## 2. Local storage and migration groundwork

- [x] 2.1 Refactor local storage into explicit domain stores for account profile, settings, snippets, dictionary entries, and sync queue state
- [x] 2.2 Add storage migrations for per-record sync metadata such as `id`, `updatedAt`, `deviceId`, `deletedAt`, and dirty-sync markers
- [x] 2.3 Implement stable device identity generation and local persistence for the current desktop installation
- [x] 2.4 Add local repository helpers that support local-only mode when no authenticated session exists

## 3. Authentication implementation

- [x] 3.1 Create an `authService` for email sign-up, email sign-in, Google sign-in completion, and sign-out
- [x] 3.2 Implement confirm-password validation and user-facing auth error mapping for email registration
- [x] 3.3 Implement the main-process Google OAuth PKCE flow with system-browser launch and loopback callback handling
- [x] 3.4 Exchange successful Google OAuth results for a Firebase-authenticated desktop session

## 4. Session lifecycle implementation

- [x] 4.1 Create a `sessionService` that encrypts persisted session material with Electron `safeStorage`
- [x] 4.2 Restore valid sessions during desktop startup and publish the resulting auth state over IPC
- [x] 4.3 Detect invalid, expired, or revoked sessions and force a clean signed-out recovery path
- [x] 4.4 Ensure sign-out clears persisted encrypted session data and stops account-scoped sync work

## 5. Cloud profile and sync engine

- [x] 5.1 Create Firestore-backed repositories for user profile, sync preferences, settings, snippets, dictionary entries, and registered devices
- [x] 5.2 Provision a cloud account profile on first authentication and load stored sync preferences on subsequent sign-ins
- [x] 5.3 Create a durable `syncQueueService` with retry, backoff, and pending-operation tracking
- [x] 5.4 Implement reconciliation rules for last-write-wins updates and deletion tombstones
- [x] 5.5 Register device metadata on sign-in and update last-seen information during authenticated sessions

## 6. Domain integration

- [x] 6.1 Wire the settings domain into the sync engine with local-first writes and authenticated cloud replication
- [x] 6.2 Add or adapt snippet-library local storage so snippets can participate in the shared sync pipeline
- [x] 6.3 Add or adapt personal-dictionary local storage so dictionary entries can participate in the shared sync pipeline
- [x] 6.4 Ensure signed-out and offline flows preserve full local functionality for settings, snippets, and dictionary entries

## 7. Renderer and preload integration

- [x] 7.1 Extend the preload bridge with typed account and sync APIs
- [x] 7.2 Build renderer auth flows for sign-up, sign-in, Google sign-in, and sign-out
- [x] 7.3 Add an account settings surface that shows auth state, sync status, and the sync enable/disable control
- [x] 7.4 Surface recoverable auth and sync errors in the UI without blocking local-only usage

## 8. Verification and rollout

- [x] 8.1 Add automated tests for email/password auth success and failure paths
- [x] 8.2 Add automated tests for session restore, session invalidation, and sign-out behavior
- [x] 8.3 Add automated tests for offline queue replay, sync merge behavior, and deletion tombstones
- [ ] 8.4 Perform manual verification on two devices for sign-in, initial upload, download, offline edits, and sign-out
- [x] 8.5 Document Firebase project setup, local development configuration, and release rollout steps for the desktop app
