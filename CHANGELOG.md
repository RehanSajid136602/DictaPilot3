# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### Wayland Support for Linux
- **Native Wayland display server support** - DictaPilot now works natively on Wayland-based Linux desktops (GNOME, KDE Plasma, Sway, Hyprland)
- `display_server.py` module with automatic display server detection using `XDG_SESSION_TYPE`, `WAYLAND_DISPLAY`, and `DISPLAY` environment variables
- `wayland_backend.py` module with `WaylandPasteBackend` and `WaylandHotkeyBackend` classes
- `wl-clipboard` integration for clipboard operations on Wayland
- `wtype` integration for keyboard simulation on Wayland
- Automatic backend selection based on detected display server
- Manual override via `DISPLAY_SERVER` environment variable
- `--wayland-deps` CLI flag to check and display Wayland dependency status
- New configuration options: `DISPLAY_SERVER`, `WAYLAND_COMPOSITOR`
- Wayland-specific error messages with troubleshooting hints

### Changed

- `HOTKEY_BACKEND` now supports `wayland` option
- `PASTE_BACKEND` now supports `wayland` option
- Backend selection now considers display server type automatically
- Startup banner now shows detected display server type
- `paste_utils.py` updated with Wayland clipboard support
- `config.py` updated with Wayland configuration options
- Updated Linux platform guide with comprehensive Wayland documentation
- Updated README.md with Wayland support information
- Updated FAQ with Wayland troubleshooting

### Dependencies

- Optional: `wl-clipboard` system package for Wayland clipboard support
- Optional: `wtype` system package for Wayland keyboard simulation
- Optional: `PyGObject` for XDG desktop portal integration (future)

### Testing

- Added unit tests for display server detection (`tests/test_display_server.py`)

## [1.0.0] - 2026-01-15

### Added
- Initial release of DictaPilot3
- Press-and-hold dictation workflow
- Smart editing with LLM integration
- Voice commands for text manipulation
- Delta paste for efficient text insertion
- Context-aware profiles
- Cross-platform support (Linux X11, macOS, Windows)
- Groq Whisper integration for transcription
- Floating window GUI with audio visualization
- Transcription storage and search
- Agent mode for developer workflows

[Unreleased]: https://github.com/RehanSajid136602/DictaPilot/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/RehanSajid136602/DictaPilot/releases/tag/v1.0.0
