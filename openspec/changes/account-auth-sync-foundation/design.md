## Context

DictaPilot's desktop stack is currently an Electron application with a React renderer, a preload bridge, a main process, and backend-style Node services. User data today is primarily local and stored through `electron-store`, with no authenticated identity, no secure session lifecycle, and no cloud-backed ownership model for settings or future personalization domains.

This change introduces the identity and sync foundation needed to support multi-device continuity. The design must cover multiple modules at once: renderer account UX, preload IPC, main-process OAuth orchestration, backend auth/session/sync services, local storage migration, and cloud data ownership. It also adds an external dependency for authentication and storage.

**Current state**
- Desktop configuration and history are stored locally.
- The renderer talks to Electron through a typed preload bridge and IPC channels.
- There is no authenticated user model, account profile, or sync queue.
- Existing cross-device-sync, personal-dictionary, and snippet-library specs describe product requirements, but the desktop architecture does not yet implement authenticated cloud sync.

**Constraints**
- The desktop app must remain usable when offline.
- Passwords must never be stored by DictaPilot outside the auth provider flow.
- The cloud design must be account-scoped; one user cannot access another user's data.
- Google sign-in must work reliably in a packaged desktop app.
- The architecture should not lock the product into transcript-history sync or team features in this phase.

**Stakeholders**
- End users who want their setup and personalization to follow them across devices
- Developers who need a maintainable desktop auth and sync architecture
- Privacy-conscious users who want local-first behavior and clear sync boundaries

## Goals / Non-Goals

**Goals:**
- Add email/password sign-up and sign-in for the desktop app
- Add Google sign-in for the desktop app
- Persist authenticated sessions securely across app restarts
- Provision an account profile and sync preferences for each authenticated user
- Add authenticated sync for settings, snippets, and personal dictionary entries
- Preserve local-only behavior when the user is signed out or offline
- Provide conflict-safe sync behavior using deterministic rules that are simple enough for an MVP

**Non-Goals:**
- Billing, subscriptions, or entitlement checks
- Team workspaces, shared dictionaries, or organization administration
- Cloud transcript-history sync by default
- Mobile client implementation
- A custom hosted auth backend owned by DictaPilot

## Decisions

### Decision 1: Use Firebase Auth and Firestore for the MVP foundation

**Choice:** Use Firebase Auth for identity and Firestore for account-scoped sync storage.

**Rationale:**
- Firebase gives the fastest path to both email/password auth and Google sign-in.
- Firestore fits the document-heavy nature of settings, snippets, and dictionary entries.
- The product needs a low-ops MVP more than deep SQL querying.
- Firebase Auth removes the need for DictaPilot to handle raw password storage or a custom auth service.

**Alternatives considered:**
- Supabase: stronger SQL ergonomics, but less direct for the desktop Google-auth MVP and adds more backend-shape decisions up front.
- Custom backend: too much surface area, security risk, and operational burden for this phase.

### Decision 2: Keep auth and sync orchestration in the desktop backend/main layers, not the renderer

**Choice:** The renderer will remain a UI client. Auth initiation, token exchange, session persistence, and sync orchestration will live behind IPC in main/backend services.

**Rationale:**
- It keeps the renderer free of direct credential/session handling logic.
- It aligns with the existing Electron split in this repo.
- It makes it easier to change providers later without rewriting UI flows.
- It centralizes audit-sensitive behavior in a smaller part of the app.

**Alternatives considered:**
- Put Firebase SDK logic directly in the renderer: faster to prototype but weaker separation and harder to reason about securely.
- Move everything into Electron main only: workable, but it overloads main-process responsibilities and makes testing harder.

### Decision 3: Use system-browser Google OAuth with PKCE and a loopback callback

**Choice:** Launch Google sign-in in the user's default browser, complete OAuth with PKCE, receive the callback on a loopback listener, then exchange the result for a Firebase-authenticated session.

**Rationale:**
- System browser auth is more robust and less fragile than an embedded BrowserWindow popup.
- PKCE is the right pattern for a public desktop client.
- This approach works better in a packaged desktop environment where popup/redirect semantics can be inconsistent.

**Alternatives considered:**
- Embedded Electron auth window: easier to wire initially, but less reliable and less aligned with modern OAuth guidance.
- Custom URI scheme callback: viable, but loopback is simpler to debug and adopt in the MVP.

### Decision 4: Store session state locally using Electron `safeStorage` with `electron-store`

**Choice:** Persist the refreshable session payload in local app storage, encrypted using Electron `safeStorage` before it is written.

**Rationale:**
- It avoids plaintext session tokens in the local store.
- It fits the current local storage pattern already used in the app.
- It avoids bringing in a native credential dependency unless later testing shows a need for OS keychain integration.

**Alternatives considered:**
- Plain `electron-store`: rejected because it leaves session material readable on disk.
- `keytar`: stronger OS integration, but adds native packaging complexity for a first-pass foundation.

### Decision 5: Use a local-first sync engine with per-record metadata and a durable queue

**Choice:** Local stores remain the source of immediate UX. Cloud sync runs asynchronously with per-record metadata and a retryable queue.

**Rationale:**
- The app must continue working offline.
- Local-first avoids blocking common actions on network availability.
- A queue-based model is easier to reason about than whole-database snapshots and reduces data loss risk.

**Alternatives considered:**
- Cloud-first writes: too brittle for a dictation desktop app.
- Full snapshot uploads: simpler conceptually, but poor for conflict handling and inefficient as synced domains grow.

### Decision 6: Represent synced data as user-scoped Firestore documents and subcollections

**Choice:** Use a user root with scoped documents/subcollections such as:
- `users/{uid}` for account profile metadata
- `users/{uid}/settings/default`
- `users/{uid}/snippets/{snippetId}`
- `users/{uid}/dictionary/{entryId}`
- `users/{uid}/devices/{deviceId}`

Each synced record will carry shared metadata:
- `id`
- `updatedAt`
- `deviceId`
- `deletedAt` nullable
- `version`

**Rationale:**
- It keeps ownership boundaries explicit.
- It matches the product domains being synced.
- It supports incremental sync and tombstones without bloating a single document.

**Alternatives considered:**
- One large user document: simpler initially, but poor for merge granularity and document size limits.
- Top-level collections keyed by uid: workable, but less cohesive than user-root grouping for this product.

### Decision 7: Limit this foundation to settings, snippets, and personal dictionary

**Choice:** Only settings, snippets, and personal dictionary entries are in scope for cloud sync in this change.

**Rationale:**
- These are the highest-value personalization domains for a multi-device experience.
- Transcript history is larger, more privacy-sensitive, and harder to reconcile cleanly.
- The foundation should be useful without expanding into a full cloud product immediately.

**Alternatives considered:**
- Sync all local data, including history: too risky and too large for the first authenticated release.

## Risks / Trade-offs

- **Google OAuth complexity in a packaged desktop app** → Mitigation: keep the flow in main/backend, use system browser + PKCE, and test against packaged builds early.
- **Session persistence bugs causing false sign-outs or stale sessions** → Mitigation: isolate session storage behind a dedicated service, validate on startup, and force clean sign-out on invalid refresh flows.
- **Firestore conflict handling is intentionally simple** → Mitigation: use last-write-wins with tombstones in the MVP and log enough metadata to support a future conflict-review UI.
- **Sync metadata may require local schema changes across multiple stores** → Mitigation: introduce shared sync metadata helpers and storage migrations before connecting cloud writes.
- **Users may expect transcript history sync once account sign-in exists** → Mitigation: keep history explicitly out of scope in the UX and spec language for this phase.
- **Firebase introduces provider lock-in** → Mitigation: hide provider specifics behind `authService`, `cloudStoreService`, and `syncService` interfaces so the app can migrate later.

## Migration Plan

1. Add environment and provider configuration for Firebase Auth and Firestore.
2. Introduce shared auth/session/sync IPC contracts and backend services behind feature flags or no-op fallbacks.
3. Add local schema extensions for sync metadata and device identity without requiring sign-in.
4. Ship account UI and authentication flows.
5. Enable account profile provisioning and session restore on startup.
6. Enable sync for settings first, then snippets and personal dictionary through the shared queue/reconciliation path.
7. Roll forward only after verifying offline recovery, sign-out behavior, and two-device sync.

**Rollback strategy**
- Disable account UI entry points and sync startup hooks.
- Keep local data untouched in current stores.
- Ignore persisted encrypted session payloads if the auth foundation must be temporarily turned off.

## Open Questions

- Should email verification be required before cloud sync begins, or can it be deferred to a later phase?
- Do we want password reset in this same change, or is sign-up/sign-in/sign-out sufficient for the first implementation pass?
- Should sync be opt-in after authentication, or auto-enabled on first sign-in with a one-time consent screen?
