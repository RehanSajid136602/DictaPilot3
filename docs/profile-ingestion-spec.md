# Profile Ingestion Spec (Website → DictaPilot)

## Purpose
Define a stable contract for collecting profile information on a website and importing it into DictaPilot with high consistency and low risk.

## Transport Model
- Website exports a JSON bundle.
- App imports bundle via local file placement or explicit import flow.
- Default local path: `~/.config/dictapilot/profile_bundle.json` (or `%APPDATA%/DictaPilot/profile_bundle.json` on Windows via existing config dir logic).
- Override path supported with `PROFILE_BUNDLE_PATH`.

## Bundle Schema (v1)
```json
{
  "version": 1,
  "default_profile": "default",
  "source_url": "https://your-site.example/profiles/abc",
  "profiles": [
    {
      "id": "default",
      "name": "Default",
      "tone": "polite",
      "language": "english",
      "role": "general assistant",
      "domain": "general",
      "glossary": {
        "SLA": "service level agreement"
      }
    }
  ]
}
```

## Validation Rules
- `profiles` must contain at least one profile.
- Profile `id` is required (case-insensitive, normalized to lowercase in app).
- `glossary` must be an object of non-empty string key/value pairs.
- Unknown fields are ignored (forward compatibility).

## Runtime Resolution
1. App loads legacy app profiles (`profiles.json`) for per-app tone/language overrides.
2. App loads website profile bundle (`profile_bundle.json`).
3. Active profile is selected from:
   - `ACTIVE_PROFILE` env var, else
   - `default_profile` in bundle, else
   - `default`.
4. Final context merge order:
   - Legacy defaults → Active profile → Per-app overrides.

## Security/Privacy
- No remote fetch in runtime path by default.
- Bundle import is local-first.
- Avoid storing secrets in profile bundle.
- Keep profile data limited to dictation behavior fields only.

## Observability (recommended next)
- Track active profile ID in debug logs.
- Track ingestion validation errors with actionable messages.
- Track profile usage counters locally.
