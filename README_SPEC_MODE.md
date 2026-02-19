# 🎯 Spec Mode - Voice-Driven Development

> Transform your voice into structured specifications that AI agents can implement.

## What is Spec Mode?

Spec Mode enables you to dictate software specifications naturally and have them automatically structured into formats compatible with modern IDE agents like Cursor, Windsurf, Cline, and Luna Drive.

**Voice → Structured Spec → AI Implementation**

## Quick Example

```
You: "Start new spec: Add user authentication"

You: "Goal: Implement secure JWT-based authentication.
      Context: Currently no authentication, need to protect API endpoints.
      Acceptance criteria: Users can register, login, logout, tokens expire in 24 hours.
      Constraint: Must use bcrypt for password hashing.
      Files: app.py, auth.py"

You: "Send to Cursor"

✓ Spec created, structured, and sent to Cursor IDE!
```

## Features

### 🎤 Voice-First Workflow
- Natural language input
- Automatic structuring
- Real-time parsing
- No typing required

### 📋 Multiple Templates
- **Feature**: New functionality
- **Bugfix**: Issue resolution
- **Refactor**: Code improvement
- **Minimal**: Quick specs

### 🔄 Multi-Format Export
- **Standard**: General markdown
- **OpenSpec**: OpenSpec workflow format
- **Luna**: Luna Drive format
- **GitHub**: GitHub issue/PR format

### 🔌 IDE Integration
- **Cursor**: Direct integration
- **Windsurf**: Direct integration
- **Cline**: VS Code extension
- **Luna Drive**: API integration
- **Custom**: Webhook support

### 💾 Storage & Versioning
- Automatic saving
- Version history
- Search capabilities
- Cross-platform storage

### 🤖 Intent Detection
- Auto-detect spec vs code
- Confidence scoring
- Context-aware routing
- Smart mode switching

## Installation

### 1. Enable Spec Mode

Add to your `.env` file:

```bash
SPEC_MODE_ENABLED=1
SPEC_AUTO_DETECT_INTENT=1
SPEC_TEMPLATE=standard
```

### 2. Configure Agent (Optional)

For Luna Drive or custom agents:

```bash
AGENT_ENDPOINTS='{"luna": "https://api.luna.ai/v1/spec"}'
```

### 3. Start Using

Press F9 and start dictating!

## Voice Commands

### Creating Specs

| Command | Action |
|---------|--------|
| "Start new spec: [title]" | Create new specification |
| "Create feature spec: [title]" | Create feature spec |
| "Create bugfix spec: [title]" | Create bugfix spec |
| "Create refactor spec: [title]" | Create refactor spec |

### Adding Content

| Command | Action |
|---------|--------|
| "Goal: [description]" | Set the goal/objective |
| "Context: [info]" | Add background context |
| "Acceptance criteria: [criterion]" | Add success criterion |
| "Constraint: [limit]" | Add constraint |
| "File: [path]" | Reference file location |
| "Non-goal: [description]" | Add non-goal |

### Managing Specs

| Command | Action |
|---------|--------|
| "Save spec" | Save current spec |
| "Export as [format]" | Export (standard/openspec/luna/github) |
| "Send to [agent]" | Send to IDE (cursor/windsurf/cline/luna) |
| "List specs" | List saved specs |

## Workflow Examples

### Example 1: Feature Development

```
"Start new spec: Add dark mode toggle"

"Goal: Allow users to switch between light and dark themes.
Context: Users requested dark mode for late-night coding.
Acceptance criteria: Toggle in settings, persists across sessions, applies to all views.
Constraint: Must support system theme detection."

"Send to Cursor"
```

### Example 2: Bug Fix

```
"Create bugfix spec: Fix login redirect loop"

"Context: Users get stuck in redirect loop after successful login.
Acceptance criteria: Login redirects to dashboard once, no loops, works on all browsers."

"Send to Windsurf"
```

### Example 3: Refactoring

```
"Create refactor spec: Extract database logic to repository pattern"

"Goal: Separate database access from business logic.
Context: SQL queries mixed with business logic, hard to test.
Acceptance criteria: All DB access through repositories, tests pass, no API changes.
Non-goal: Don't change the API interface."

"Export as OpenSpec"
```

## Export Formats

### Standard Format
```markdown
# Feature Title

## Goal
[Description]

## Context
[Background]

## Acceptance Criteria
- [Criterion 1]
- [Criterion 2]
```

### OpenSpec Format
```markdown
# Feature Title

**Created:** 2026-02-18T16:55:00Z
**Updated:** 2026-02-18T16:55:00Z

## Overview
[Description]

## Requirements
1. [Requirement 1]
2. [Requirement 2]
```

### Luna Format
```markdown
# Specification: Feature Title

## Intent
[Description]

## Success Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]
```

### GitHub Format
```markdown
## Feature Title

### Description
[Description]

### Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]
```

## IDE Integration

### Cursor
Specs saved to: `~/.cursor/dictapilot_input.md`

### Windsurf
Specs saved to: `~/.windsurf/dictapilot_input.md`

### Cline
Specs saved to: `~/.vscode/cline/dictapilot_input.md`

### Luna Drive
Sent via API (requires API key in `AGENT_ENDPOINTS`)

### Custom Webhooks
Configure in `AGENT_ENDPOINTS`:
```bash
AGENT_ENDPOINTS='{"myagent": "https://api.example.com/spec"}'
```

## Configuration Reference

### Environment Variables

```bash
# Enable spec mode
SPEC_MODE_ENABLED=1

# Default template (standard, minimal, detailed, openspec, luna, github)
SPEC_TEMPLATE=standard

# Auto-detect intent (1=on, 0=off)
SPEC_AUTO_DETECT_INTENT=1

# Default export format
SPEC_FORMAT=standard

# Enable spec versioning (1=on, 0=off)
SPEC_STORAGE_ENABLED=1

# Agent endpoints (JSON)
AGENT_ENDPOINTS='{"cursor": "http://localhost:9333"}'

# Workflow format (openspec, luna, github-spec-kit)
WORKFLOW_FORMAT=openspec
```

## Storage Locations

### Linux/macOS
```
~/.local/share/dictapilot/specs/
├── index.json
├── spec-1_20260218_165500/
│   ├── spec.md
│   ├── spec.json
│   └── versions/
└── spec-2_20260218_170500/
    ├── spec.md
    └── spec.json
```

### Windows
```
%APPDATA%\DictaPilot\specs\
├── index.json
├── spec-1_20260218_165500\
│   ├── spec.md
│   ├── spec.json
│   └── versions\
└── spec-2_20260218_170500\
    ├── spec.md
    └── spec.json
```

## Best Practices

1. **Be Specific**: Clear goals lead to better implementations
2. **Use Templates**: Choose the right template for your task
3. **Add Context**: Help agents understand the problem
4. **Define Constraints**: Specify what must/must not be done
5. **Reference Files**: Mention specific files that need changes
6. **Version Specs**: Save before major changes
7. **Review Before Sending**: Export and review first

## Troubleshooting

### Spec Mode Not Activating
- ✓ Check `SPEC_MODE_ENABLED=1` in `.env`
- ✓ Verify `SPEC_AUTO_DETECT_INTENT=1`
- ✓ Use explicit trigger: "Start new spec"

### Agent Not Receiving Specs
- ✓ Check agent is running
- ✓ Verify endpoint configuration
- ✓ Test with "Test connection to [agent]"

### Intent Misclassified
- ✓ Use explicit commands
- ✓ Check confidence in logs
- ✓ Adjust detection settings if needed

## Documentation

- **[Comprehensive Guide](docs/spec-mode-guide.md)** - Full documentation
- **[Quick Start](docs/spec-mode-quickstart.md)** - 5-minute setup
- **[Implementation Summary](SPEC_MODE_SUMMARY.md)** - Technical details

## Architecture

```
Voice Input
    ↓
Intent Classifier (detect spec/code/doc/review)
    ↓
Workflow Engine (route to handler)
    ↓
Spec Generator (parse and structure)
    ↓
Spec Store (save and version)
    ↓
Agent Orchestrator (send to IDE/agent)
```

## API Reference

### Python Modules

- `spec_generator.py` - Specification generation
- `intent_classifier.py` - Intent detection
- `spec_store.py` - Storage and versioning
- `agent_orchestrator.py` - Agent integration
- `workflow_engine.py` - Workflow orchestration

See module docstrings for detailed API documentation.

## Contributing

Contributions welcome! Areas for enhancement:

- Additional IDE integrations
- New spec templates
- Enhanced intent detection
- Workflow templates
- Dashboard visualization

## License

MIT License - See [LICENSE](LICENSE) file.

## Credits

Inspired by:
- Luna Drive specification-driven workflows
- OpenSpec methodology
- GitHub Spec Kit patterns
- Modern agentic coding practices (2026)

---

**Made with ❤️ for developers who prefer speaking to typing.**
