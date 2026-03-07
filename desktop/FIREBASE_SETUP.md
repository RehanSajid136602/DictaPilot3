# Firebase Setup For DictaPilot Desktop

## Required Firebase services

Create or reuse a Firebase project with:

- Authentication
- Cloud Firestore

Enable these sign-in providers in Firebase Authentication:

- Email/Password
- Google

Use a Google OAuth client of type `Desktop app` and copy its client ID into `GOOGLE_OAUTH_CLIENT_ID`.

## Firestore layout

DictaPilot stores account-scoped records under:

- `users/{uid}`
- `users/{uid}/settings/default`
- `users/{uid}/snippets/{snippetId}`
- `users/{uid}/dictionary/{entryId}`
- `users/{uid}/devices/{deviceId}`

Each synced record includes metadata for:

- `id`
- `updatedAt`
- `deviceId`
- `deletedAt`
- `version`

## Local development

1. Copy [`.env.example`](/C:/Users/Admin/Documents/Dictapilot3/desktop/.env.example) to `desktop/.env`.
2. Fill in:
   - `FIREBASE_API_KEY`
   - `FIREBASE_PROJECT_ID`
   - `FIREBASE_AUTH_DOMAIN`
   - `GOOGLE_OAUTH_CLIENT_ID`
   - `GROQ_API_KEY`
3. Run `npm run build` from [desktop](/C:/Users/Admin/Documents/Dictapilot3/desktop).
4. Run `npm run dev` from [desktop](/C:/Users/Admin/Documents/Dictapilot3/desktop).

## Firestore security baseline

Restrict documents to the authenticated user:

- only allow reads and writes when `request.auth.uid == userId`
- deny anonymous access to every `users/*` path

## Release rollout checklist

1. Confirm email/password and Google sign-in work in a packaged Windows build.
2. Verify session restore after restart.
3. Verify enabling sync uploads local settings, snippets, and dictionary data.
4. Verify a second device downloads the same account data.
5. Verify offline edits remain local and sync after reconnect.
6. Verify sign-out clears the saved session and stops account-scoped sync.

## Notes

- DictaPilot uses Electron main/backend services plus Firebase REST APIs for auth and Firestore access.
- Passwords are never stored by DictaPilot outside Firebase Authentication.
- Session material is persisted locally through Electron `safeStorage`.
