# Specification-Driven Development Guide

## Overview

DictaPilot's Spec Mode transforms voice dictation into structured specifications that can be sent directly to IDE agents and AI coding assistants. This enables a voice-first, specification-driven workflow inspired by Luna Drive and modern agentic coding patterns.

## Quick Start

### 1. Enable Spec Mode

Add to your `.env` file:
```bash
SPEC_MODE_ENABLED=1
SPEC_AUTO_DETECT_INTENT=1
SPEC_TEMPLATE=standard
```

### 2. Start a New Spec

Press your hotkey (F9) and say:
```
"Start new spec: Add dark mode to settings dashboard"
```

### 3. Add Details

Continue speaking to add context and criteria:
```
"Context: Users need dark mode for late-night coding sessions. 
Acceptance criteria: Toggle in settings, persists across sessions, applies to all views.
Constraint: Must support system theme detection."
```

### 4. Send to IDE

```
"Send to Cursor"
```

## Voice Commands

### Creating Specs

- **"Start new spec: [title]"** - Create a new specification
- **"Create feature spec: [title]"** - Create a feature specification
- **"Create bugfix spec: [title]"** - Create a bug fix specification
- **"Create refactor spec: [title]"** - Create a refactoring specification

### Adding Content

- **"Goal: [description]"** - Set the goal/objective
- **"Context: [description]"** - Add background context
- **"Acceptance criteria: [criterion]"** - Add acceptance criterion
- **"Constraint: [constraint]"** - Add a constraint
- **"File: [path]"** - Reference a file location
- **"Non-goal: [description]"** - Add a non-goal

### Managing Specs

- **"Save spec"** - Save current specification
- **"Export as [format]"** - Export spec (formats: standard, openspec, luna, github)
- **"Send to [agent]"** - Send to IDE agent (cursor, windsurf, cline, luna)
- **"List specs"** - List saved specifications
- **"Load spec: [title]"** - Load a saved specification

## Spec Templates

### Standard Template
General-purpose specification with all sections.

### Feature Template
Optimized for new feature development:
- Goal
- Context
- Acceptance Criteria
- Constraints
- Files/Locations

### Bugfix Template
Optimized for bug fixes:
- Bug Description
- Steps to Reproduce
- Expected Behavior
- Acceptance Criteria

### Refactor Template
Optimized for refactoring:
- Current State
- Target State
- Acceptance Criteria
- Non-Goals (what not to change)

### Minimal Template
Quick specs with just goal and acceptance criteria.

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

## Constraints
- [Constraint 1]
```

### OpenSpec Format
Compatible with OpenSpec workflow tools:
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
Compatible with Luna Drive:
```markdown
# Specification: Feature Title

## Intent
[Description]

## Success Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]

## Boundaries
- [Constraint 1]
```

### GitHub Format
Compatible with GitHub issues/PRs:
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
Specs are saved to `~/.cursor/dictapilot_input.md` and Cursor is triggered to open them.

### Windsurf
Specs are saved to `~/.windsurf/dictapilot_input.md`.

### Cline
Specs are saved to `~/.vscode/cline/dictapilot_input.md`.

### Luna Drive
Specs are sent via API to Luna Drive endpoint (requires API key).

### Custom Webhooks
Configure custom endpoints in `AGENT_ENDPOINTS`:
```bash
AGENT_ENDPOINTS='{"myagent": "https://api.example.com/spec"}'
```

## Configuration

### Environment Variables

```bash
# Enable spec mode
SPEC_MODE_ENABLED=1

# Default template (standard, minimal, detailed, openspec, luna, github)
SPEC_TEMPLATE=standard

# Auto-detect intent (spec vs code vs docs)
SPEC_AUTO_DETECT_INTENT=1

# Default export format
SPEC_FORMAT=standard

# Enable spec versioning
SPEC_STORAGE_ENABLED=1

# Agent endpoints (JSON)
AGENT_ENDPOINTS='{"cursor": "http://localhost:9333"}'

# Workflow format
WORKFLOW_FORMAT=openspec
```

### Dashboard Configuration

Access spec mode settings in the Agent View of the dashboard:
- Enable/disable spec mode
- Select default template
- Configure agent connections
- View spec history

## Workflow Examples

### Example 1: Voice-Driven Feature Development

1. **Start Spec**
   ```
   "Start new spec: Add user authentication"
   ```

2. **Add Details**
   ```
   "Goal: Implement secure user authentication with JWT tokens.
   Context: Currently no authentication, need to protect API endpoints.
   Acceptance criteria: Users can register, login, logout, JWT tokens expire after 24 hours.
   Constraint: Must use bcrypt for password hashing.
   File: app.py, auth.py"
   ```

3. **Save and Send**
   ```
   "Save spec. Send to Cursor."
   ```

### Example 2: Quick Bug Fix

1. **Start Bugfix Spec**
   ```
   "Create bugfix spec: Fix login redirect loop"
   ```

2. **Describe Bug**
   ```
   "Context: Users get stuck in redirect loop after login.
   Acceptance criteria: Login redirects to dashboard once, no loops."
   ```

3. **Send to Agent**
   ```
   "Send to Windsurf"
   ```

### Example 3: Refactoring

1. **Start Refactor Spec**
   ```
   "Create refactor spec: Extract database logic to repository pattern"
   ```

2. **Add Details**
   ```
   "Goal: Separate database logic from business logic.
   Context: Current code has SQL queries mixed with business logic.
   Acceptance criteria: All database access through repository classes, tests pass.
   Non-goal: Don't change the API interface."
   ```

3. **Export for Review**
   ```
   "Export as GitHub format"
   ```

## Intent Detection

Spec mode automatically detects your intent:

### Spec Intent
Triggered by keywords: "spec", "requirement", "goal", "acceptance criteria", "we need to"

### Code Intent
Triggered by keywords: "function", "class", "method", "implement", "write code"

### Documentation Intent
Triggered by keywords: "document", "readme", "guide", "comment", "docstring"

### Review Intent
Triggered by keywords: "review", "feedback", "issue", "bug", "refactor"

## Storage and Versioning

Specs are stored in:
- **Linux/macOS**: `~/.local/share/dictapilot/specs/`
- **Windows**: `%APPDATA%\DictaPilot\specs\`

Each spec includes:
- `spec.md` - Markdown version
- `spec.json` - JSON version for parsing
- `versions/` - Version history

## Best Practices

1. **Be Specific**: Clear goals and acceptance criteria lead to better implementations
2. **Use Templates**: Choose the right template for your task
3. **Add Context**: Background information helps agents understand the problem
4. **Define Constraints**: Specify what must/must not be done
5. **Reference Files**: Mention specific files that need changes
6. **Version Specs**: Save specs before major changes
7. **Review Before Sending**: Export and review before sending to agents

## Troubleshooting

### Spec Mode Not Activating
- Check `SPEC_MODE_ENABLED=1` in `.env`
- Verify `SPEC_AUTO_DETECT_INTENT=1`
- Use explicit trigger: "Start new spec"

### Agent Not Receiving Specs
- Check agent connection in dashboard
- Verify agent endpoint configuration
- Test connection with "Test connection to [agent]"

### Intent Misclassified
- Use explicit commands: "Start new spec", "Write code", etc.
- Adjust `SPEC_AUTO_DETECT_INTENT` if needed
- Check intent confidence in dashboard

## Advanced Usage

### Custom Templates

Create custom templates by extending `SpecTemplate` class in `spec_generator.py`.

### Custom Agents

Add custom agents in `agent_orchestrator.py` or via webhook configuration.

### Workflow Automation

Use `workflow_engine.py` to create custom workflows that chain spec creation, agent handoff, and implementation.

## API Reference

See `spec_generator.py`, `intent_classifier.py`, `spec_store.py`, `agent_orchestrator.py`, and `workflow_engine.py` for detailed API documentation.
