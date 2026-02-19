# Spec Mode Quick Start

Transform your voice into structured specifications that AI agents can implement.

## 5-Minute Setup

### 1. Enable Spec Mode

Add to `.env`:
```bash
SPEC_MODE_ENABLED=1
SPEC_AUTO_DETECT_INTENT=1
```

### 2. Try It Out

Press F9 and say:
```
"Start new spec: Add dark mode toggle to settings"
```

Continue:
```
"Context: Users want dark mode for night coding.
Acceptance criteria: Toggle button in settings, persists on reload, applies to all views.
Constraint: Must support system theme detection."
```

### 3. Send to Your IDE

```
"Send to Cursor"
```

Done! Your spec is now in Cursor ready for implementation.

## Voice Commands Cheat Sheet

| Say This | Result |
|----------|--------|
| "Start new spec: [title]" | Create new specification |
| "Goal: [description]" | Set the goal |
| "Context: [info]" | Add background |
| "Acceptance criteria: [criterion]" | Add success criterion |
| "Constraint: [limit]" | Add constraint |
| "Save spec" | Save to storage |
| "Send to Cursor" | Send to Cursor IDE |
| "Export as Luna" | Export Luna format |

## Supported IDEs

- **Cursor** - Saved to `~/.cursor/dictapilot_input.md`
- **Windsurf** - Saved to `~/.windsurf/dictapilot_input.md`
- **Cline** - Saved to `~/.vscode/cline/dictapilot_input.md`
- **Luna Drive** - Sent via API (requires API key)
- **Custom** - Configure webhook endpoints

## Export Formats

- **standard** - General markdown format
- **openspec** - OpenSpec workflow format
- **luna** - Luna Drive format
- **github** - GitHub issue/PR format

## Example Workflow

```
You: "Start new spec: User authentication with JWT"

You: "Goal: Implement secure authentication.
      Context: No auth currently, need to protect API.
      Acceptance criteria: Register, login, logout, JWT expires in 24h.
      Constraint: Use bcrypt for passwords.
      Files: app.py, auth.py"

You: "Save spec. Send to Cursor."

✓ Spec saved and sent to Cursor!
```

## Next Steps

- Read the [full guide](spec-mode-guide.md)
- Configure [agent connections](spec-mode-guide.md#ide-integration)
- Explore [templates](spec-mode-guide.md#spec-templates)
- Learn [best practices](spec-mode-guide.md#best-practices)

## Troubleshooting

**Spec mode not working?**
- Check `SPEC_MODE_ENABLED=1` in `.env`
- Use explicit trigger: "Start new spec"

**Agent not receiving specs?**
- Verify agent is running
- Check dashboard Agent View for connection status

**Need help?**
- See [full documentation](spec-mode-guide.md)
- Check [FAQ](../faq.md)
