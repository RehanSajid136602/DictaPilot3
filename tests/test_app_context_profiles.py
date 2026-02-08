import json

import app_context


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def _reset_profile_caches():
    app_context._PROFILE_CACHE.update({"path": None, "mtime": None, "data": {}})
    app_context._PROFILE_BUNDLE_CACHE.update({"path": None, "mtime": None, "data": {}})


def test_context_uses_active_profile_bundle(monkeypatch, tmp_path):
    profiles_path = tmp_path / "profiles.json"
    bundle_path = tmp_path / "profile_bundle.json"

    monkeypatch.setattr(app_context, "_profiles_path", lambda: profiles_path)
    monkeypatch.setattr(app_context, "_profile_bundle_path", lambda: bundle_path)
    monkeypatch.setattr(app_context, "_active_app_id", lambda: None)
    monkeypatch.setenv("ACTIVE_PROFILE", "legal_writer")

    _write_json(
        profiles_path,
        {"default": {"tone": "polite", "language": "english"}, "apps": {}},
    )
    _write_json(
        bundle_path,
        {
            "version": 1,
            "default_profile": "default",
            "source_url": "https://example.com/profiles/legal_writer",
            "profiles": [
                {
                    "id": "default",
                    "name": "Default",
                    "tone": "polite",
                    "language": "english",
                },
                {
                    "id": "legal_writer",
                    "name": "Legal Writer",
                    "tone": "formal",
                    "language": "english",
                    "role": "legal analyst",
                    "domain": "compliance",
                    "glossary": {"SLA": "service level agreement"},
                },
            ],
        },
    )
    _reset_profile_caches()

    ctx = app_context.get_context()
    assert ctx.profile_id == "legal_writer"
    assert ctx.profile_name == "Legal Writer"
    assert ctx.tone == "formal"
    assert ctx.language == "english"
    assert ctx.role == "legal analyst"
    assert ctx.domain == "compliance"
    assert ctx.glossary.get("SLA") == "service level agreement"
    assert ctx.profile_source == "https://example.com/profiles/legal_writer"


def test_app_override_wins_over_bundle_tone_language(monkeypatch, tmp_path):
    profiles_path = tmp_path / "profiles.json"
    bundle_path = tmp_path / "profile_bundle.json"

    monkeypatch.setattr(app_context, "_profiles_path", lambda: profiles_path)
    monkeypatch.setattr(app_context, "_profile_bundle_path", lambda: bundle_path)
    monkeypatch.setattr(app_context, "_active_app_id", lambda: "Slack")
    monkeypatch.delenv("ACTIVE_PROFILE", raising=False)

    _write_json(
        profiles_path,
        {
            "default": {"tone": "polite", "language": "english"},
            "apps": {"Slack": {"tone": "casual", "language": "english"}},
        },
    )
    _write_json(
        bundle_path,
        {
            "version": 1,
            "default_profile": "support_agent",
            "profiles": [
                {
                    "id": "support_agent",
                    "name": "Support Agent",
                    "tone": "professional",
                    "language": "english",
                    "role": "support specialist",
                }
            ],
        },
    )
    _reset_profile_caches()

    ctx = app_context.get_context()
    assert ctx.profile_id == "support_agent"
    assert ctx.tone == "casual"
    assert ctx.language == "english"
    assert ctx.role == "support specialist"


def test_list_available_profiles_handles_object_shape(monkeypatch, tmp_path):
    bundle_path = tmp_path / "profile_bundle.json"
    monkeypatch.setattr(app_context, "_profile_bundle_path", lambda: bundle_path)

    _write_json(
        bundle_path,
        {
            "version": 1,
            "profiles": {
                "engineering_writer": {
                    "name": "Engineering Writer",
                    "tone": "concise",
                    "language": "english",
                },
                "product_writer": {
                    "name": "Product Writer",
                    "tone": "friendly",
                    "language": "english",
                },
            },
        },
    )
    _reset_profile_caches()

    profiles = app_context.list_available_profiles()
    assert [item["id"] for item in profiles] == ["engineering_writer", "product_writer"]
