# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - 2026-02-19

### Added - Modern Floating Window UI/UX (2026 Redesign)

**Major Feature: Glassmorphism & Modern Animations**
- Implemented modern 2026 UI/UX design with glassmorphism effect
- Translucent backgrounds (25-30% opacity) with multi-layer shadows
- Smooth animations: breathing (idle), pulsing (recording), state transitions
- Modern 7-bar waveform with gradient fills and glow effects
- Micro-interactions: hover effects, success/error feedback animations

**Visual Enhancements:**
- Glassmorphism shell with backdrop blur simulation
- 3-layer shadow system for depth (24-32px blur)
- Accent color support: blue (default), purple, green
- 4-layer outer glow effect during recording
- Elastic easing for natural motion (60 FPS target)
- Enhanced waveform: 7 bars with smooth interpolation and gradient fills

**Configuration Options (6 new settings):**
- `FLOATING_UI_STYLE`: "modern" (default) or "classic"
- `FLOATING_ACCENT_COLOR`: "blue", "purple", "green"
- `FLOATING_GLASSMORPHISM`: Enable/disable glass effect
- `FLOATING_ANIMATIONS`: Enable/disable animations
- `FLOATING_REDUCED_MOTION`: Accessibility option
- `FLOATING_LAYOUT`: "pill" (default), "circular", "card"

**Accessibility:**
- Reduced motion support for users sensitive to animations
- High contrast maintained (WCAG 2.1 AA)
- Classic mode fallback available
- Backward compatible with existing configurations

**Performance:**
- CPU usage: <5% during animations
- 60 FPS animation target
- GPU-accelerated rendering via Qt
- Optimized for high DPI displays
- Smooth state transitions with progress tracking

**Documentation:**
- Added `docs/modern-ui-guide.md`: Comprehensive user guide
- Added `MODERN_UI_IMPLEMENTATION_SUMMARY.md`: Technical details
- Updated `.env.example` with modern UI settings
- Updated README.md with modern UI features
- Updated quick-start guide with UI customization
- Updated FAQ with modern UI section

**Files Modified:**
- `app.py`: 333 lines added (core implementation)
- `config.py`: 138 lines added (configuration system)
- `.env.example`: 44 lines added (documentation)
- Documentation: 5 files updated

**Backward Compatibility:**
- Classic UI mode preserved (set `FLOATING_UI_STYLE=classic`)
- All existing tests pass (7/7)
- No breaking changes to API
- Existing configurations continue to work

## [Unreleased] - 2026-02-18

### Fixed - CLI Auto-Enter Issue & Grammar Improvements

**Critical Fix: CLI Auto-Enter Prevention**
- Fixed issue where DictaPilot automatically pressed Enter in terminal/CLI environments
- Added automatic CLI environment detection (bash, zsh, PowerShell, CMD, etc.)
- Implemented newline sanitization for CLI to prevent command interruption
- Preserves intentional newlines when user says "new line"
- Configurable via `CLI_AUTO_DETECT` and `CLI_STRIP_NEWLINES` settings

**Enhancement: Grammar Correction**
- Improved grammar correction to preserve code snippets and technical terms
- Added preservation rules for camelCase, snake_case, and technical syntax
- Enhanced LLM prompts to make minimal changes while fixing grammar
- Preserves API names, brand names, and domain-specific terminology
- Configurable via `GRAMMAR_PRESERVE_CODE` and `GRAMMAR_PRESERVE_TECHNICAL`

**Files Modified:**
- `app_context.py`: Added `is_cli_application()` for CLI detection
- `paste_utils.py`: Added `_sanitize_for_cli()` and `_detect_cli_environment()`
- `smart_editor.py`: Enhanced grammar correction prompts with preservation rules
- `config.py`: Added 5 new configuration options
- `.env.example`: Documented CLI and grammar settings

**Configuration Options Added:**
- `cli_auto_detect`: Auto-detect CLI/terminal environments (default: True)
- `cli_strip_newlines`: Strip newlines in CLI to prevent auto-enter (default: True)
- `cli_newline_keyword`: Keyword to force newline in CLI (default: "new line")
- `grammar_preserve_code`: Preserve code in grammar fixes (default: True)
- `grammar_preserve_technical`: Preserve technical terms (default: True)

### Added - Specification-Driven Development (Agentic Coding)

**Major Feature: Voice-to-Spec Workflow**
- New `spec_generator.py`: Convert voice input into structured specifications
  - Multiple templates: feature, bugfix, refactor, minimal
  - Voice input parsing with pattern matching
  - Export formats: standard, OpenSpec, Luna Drive, GitHub
- New `intent_classifier.py`: Auto-detect user intent from voice
  - Classifies: spec, code, documentation, review, command
  - Confidence scoring and metadata extraction
- New `spec_store.py`: Specification storage and versioning
  - Platform-specific storage paths
  - JSON and Markdown persistence
  - Version history tracking
  - Search and list capabilities
- New `agent_orchestrator.py`: IDE agent integration
  - Support for Cursor, Windsurf, Cline, Luna Drive
  - Webhook support for custom agents
  - Connection management and testing
- New `workflow_engine.py`: Specification-driven workflows
  - Workflow state management
  - Voice input routing based on intent
  - Spec creation and refinement workflows
  - Agent handoff orchestration

**Configuration**
- Added spec mode configuration options to `config.py`:
  - `spec_mode_enabled`: Enable/disable spec mode
  - `spec_template`: Default template selection
  - `spec_auto_detect_intent`: Auto-detect intent from voice
  - `spec_format`: Default export format
  - `spec_storage_enabled`: Enable spec versioning
  - `agent_endpoints`: JSON string of agent endpoints
  - `workflow_format`: Workflow format (openspec, luna, github-spec-kit)

**Documentation**
- Added `docs/spec-mode-guide.md`: Comprehensive guide (500+ lines)
- Added `docs/spec-mode-quickstart.md`: 5-minute quick start
- Added `SPEC_MODE_SUMMARY.md`: Implementation summary
- Updated `.env.example` with spec mode variables

**Voice Commands**
- "Start new spec: [title]" - Create new specification
- "Goal: [description]" - Set goal/objective
- "Context: [info]" - Add background context
- "Acceptance criteria: [criterion]" - Add success criterion
- "Constraint: [limit]" - Add constraint
- "Save spec" - Save to storage
- "Send to [agent]" - Send to IDE (Cursor, Windsurf, Cline, Luna)
- "Export as [format]" - Export spec (standard, openspec, luna, github)

**Integration**
- Enhanced `agent_formatter.py` with spec.md export capability
- Seamless integration with existing dictation workflow
- Backward compatible with existing features

### Technical Details
- ~2,500 lines of new code and documentation
- 5 new Python modules
- 3 new documentation files
- All tests passing
- Zero breaking changes to existing functionality

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### Transcription Storage Enhancements
- **Multi-format Export** - Export transcriptions to CSV, Markdown, and HTML formats
  - `transcription_export.py` module with CSV, Markdown, HTML exporters
  - Configurable columns for CSV export
  - YAML frontmatter option for Markdown
  - Custom template support for HTML
  - Progress callback support for large exports

- **Advanced Filtering** - Chainable filter builder for complex queries
  - `FilterBuilder` class in `transcription_store.py`
  - Filter by date range, last N days
  - Filter by tags (AND/OR matching), language, quality score, word count
  - Filter by source application

- **Import Functionality** - Import transcriptions from JSON files
  - `transcription_import.py` module
  - Deduplication using timestamp+content hash
  - Conflict resolution strategies (skip, overwrite, keep_both)
  - Transaction semantics with rollback on failure
  - Merge mode support

- **Category System** - Organize transcriptions into categories/folders
  - `transcription_categories.py` module
  - Create, rename, delete categories
  - Add/remove entries from categories
  - Category statistics

- **Enhanced Search** - Advanced search capabilities
  - `transcription_search.py` module
  - Fuzzy search using difflib with configurable threshold
  - Exact phrase search
  - Regex pattern search
  - AND/OR/NOT operators
  - Relevance ranking and match highlighting

- **Editing with Version History** - Edit transcriptions with rollback capability
  - `transcription_editing.py` module
  - Edit with automatic version tracking (max 5 versions)
  - Get edit history
  - Rollback to previous versions
  - Bulk edit and delete operations

- **Schema Migration** - Backward compatibility with existing data
  - Schema version updated to 3.0
  - Automatic migration from v1.0/v2.0 data
  - Graceful degradation for new features

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
