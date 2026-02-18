# DictaPilot

![DictaPilot](Dictepilot.png)

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Platform: Windows | macOS | Linux](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgray.svg)

Cross-platform press-and-hold dictation with smart editing. Hold a hotkey, speak, release, and DictaPilot transcribes and pastes into the currently focused text field.

## What You Get

- Hold-to-record workflow (`f9` by default)
- Smart voice commands like `delete that`, `clear all`, `ignore`, `replace X with Y`
- Delta paste mode to update only changed text
- Persistent transcription history with search/export CLI
- Linux, macOS, and Windows startup scripts included

## Current Status

DictaPilot is currently terminal-first.

- No full desktop GUI yet (no settings dashboard or manager app).
- No Dory assistant integration yet.
- No visual onboarding wizard yet.

What exists today:
- CLI + global hotkey workflow.
- Optional lightweight floating status overlay and tray flow.

UI and Dory-related features are planned and will be added in future releases.

## 5-Minute Setup

1. Clone the repo:

```bash
git clone https://github.com/RehanSajid136602/DictaPilot.git
cd DictaPilot
```

2. Run your OS setup script:

- Windows: `setup\setup_windows.bat`
- Linux: `./setup/setup_linux.sh`
- macOS: `./setup/setup_macos.command`

3. Set your Groq API key:

- Open `.env`
- Set `GROQ_API_KEY=your_real_key`

4. Start DictaPilot:

```bash
python app.py
```

5. Use it:

- Focus any text input field
- Hold `F9` to record
- Release `F9` to transcribe and paste

## One-Click Start (Portable Scripts)

If setup is already done, use:

- Windows: `portable-start/start_windows.bat`
- Linux: `portable-start/start_linux.sh`
- macOS: `portable-start/start_macos.command`

Details: `portable-start/README.txt`

## Start at Login (Optional)

Use these scripts to register auto-start and launch now:

- Windows: `auto_start/autostart_windows.bat`
- Linux: `auto_start/autostart_linux.sh`
- macOS: `auto_start/autostart_macos.command`

Details: `auto_start/README.txt`

## CLI Commands

```bash
# List recent transcriptions
python app.py --list

# View storage statistics
python app.py --stats

# Search transcriptions
python app.py --search "meeting notes"

# Export transcriptions to a text file
python app.py --export my_transcriptions.txt
```

## Smart Dictation Commands

| Spoken Command | Action |
|---|---|
| `delete that`, `undo`, `scratch that` | Remove last segment |
| `clear all`, `reset`, `start over` | Clear full transcript |
| `ignore`, `skip`, `don't include` | Ignore this utterance |
| `replace X with Y` | Replace phrase in transcript |

## Environment Variables

`GROQ_API_KEY` is the only required variable. Everything else is optional.

### Core

| Variable | Default | Notes |
|---|---|---|
| `GROQ_API_KEY` | _(required)_ | Groq API key |
| `HOTKEY` | `f9` | Hold-to-record key |
| `SMART_EDIT` | `1` | Smart editing on/off (`1`/`0`) |
| `SMART_MODE` | `llm` | `llm` or `heuristic` |
| `LLM_ALWAYS_CLEAN` | `1` | In `llm` mode: always clean vs intent-only |
| `GROQ_WHISPER_MODEL` | `whisper-large-v3-turbo` | Transcription model |
| `GROQ_CHAT_MODEL` | `openai/gpt-oss-120b` | Cleanup model in `llm` mode |

### Paste and Input Backends

| Variable | Default | Notes |
|---|---|---|
| `PASTE_MODE` | `delta` | `delta` or `full` |
| `PASTE_POLICY` | `final_only` | `final_only` or `live_preview` |
| `PASTE_BACKEND` | `auto` | `auto`, `keyboard`, `pynput`, `xdotool`, `x11`, `osascript` |
| `HOTKEY_BACKEND` | `auto` | `auto`, `keyboard`, `pynput`, `x11` |

### Audio and Processing

| Variable | Default | Notes |
|---|---|---|
| `SAMPLE_RATE` | `16000` | Recording sample rate |
| `CHANNELS` | `1` | Number of channels |
| `TRIM_SILENCE` | `1` | Trim silence before transcription |
| `SILENCE_THRESHOLD` | `0.02` | Trim sensitivity |
| `INSTANT_REFINE` | `1` | Fast first paste then refinement |
| `DICTATION_MODE` | `accurate` | `speed`, `balanced`, `accurate` |
| `CLEANUP_LEVEL` | `aggressive` | `basic`, `balanced`, `aggressive` |
| `CLEANUP_STRICTNESS` | `balanced` | `conservative`, `balanced`, `aggressive` |
| `CONFIDENCE_THRESHOLD` | `0.65` | Used by cleanup guardrails |

### Profiles and Personalization

| Variable | Default | Notes |
|---|---|---|
| `ACTIVE_PROFILE` | `default` | Active profile ID |
| `PROFILE_BUNDLE_PATH` | platform path | Custom profile bundle path |
| `ACTIVE_APP` | _(unset)_ | Force app context |
| `DEFAULT_TONE` | `polite` | Fallback tone |
| `DEFAULT_LANGUAGE` | `english` | Fallback language |
| `PERSONAL_DICTIONARY_PATH` | platform path | Custom dictionary path |
| `SNIPPETS_PATH` | platform path | Custom snippets path |
| `USER_ADAPTATION` | `1` | Enable adaptive correction memory |

### Floating Overlay / Behavior

These variables tune the lightweight floating overlay and runtime behavior, not a full GUI application.

| Variable | Default | Notes |
|---|---|---|
| `RESET_TRANSCRIPT_EACH_RECORDING` | `1` | Reset transcript on each hold/release |
| `FLOATING_WIDTH` | `148` | Floating widget width |
| `FLOATING_HEIGHT` | `36` | Floating widget height |
| `FLOATING_BAR_COUNT` | `5` | Number of level bars (clamped to 3-6) |
| `FLOATING_CLOSE_BUTTON` | `1` | Show floating close button |
| `FLOATING_THEME` | `professional_minimal` | `professional_minimal` or `high_contrast` |
| `FLOATING_MOTION_PROFILE` | `expressive` | `expressive`, `balanced`, or `reduced` |
| `FLOATING_GLOW_INTENSITY` | `1.0` | Glow strength multiplier (`0.0` to `1.6`) |
| `FLOATING_BAR_RADIUS` | `1.0` | Bar roundness multiplier (`0.5` to `1.5`) |
| `FLOATING_BORDER_ALPHA` | `72` | Floating shell border opacity (`8` to `255`) |

Profile bundle reference: `docs/profile-ingestion-spec.md`

## Storage Paths

| Data | Linux/macOS | Windows |
|---|---|---|
| Transcriptions | `~/.local/share/dictapilot/transcriptions.json` | `%APPDATA%\DictaPilot\transcriptions.json` |
| Config | `~/.config/dictapilot/config.json` | `%APPDATA%\DictaPilot\config.json` |
| Profiles | `~/.config/dictapilot/profile_bundle.json` | `%APPDATA%\DictaPilot\profile_bundle.json` |

## Troubleshooting

### Linux

- Install `xdotool` if needed: `sudo apt install xdotool`
- If global hotkey fails, try `HOTKEY_BACKEND=x11` or `HOTKEY_BACKEND=pynput`
- If paste fails, try `PASTE_BACKEND=x11` or `PASTE_BACKEND=xdotool`

### macOS

- Grant Accessibility permission to Terminal/iTerm
- If paste/hotkey fails, test `PASTE_BACKEND=osascript`

### Windows

- Run terminal as normal user (not admin unless required by keyboard hook behavior)
- If hotkey behavior is inconsistent, try `HOTKEY_BACKEND=pynput`

### General

- API error: check `GROQ_API_KEY`
- No audio: confirm microphone permissions and selected input device
- Quick health check:

```bash
python app.py --stats
```

## Roadmap Snapshot

Planned milestones:

- Full desktop UI for settings and profile management.
- Dory integration and related assistant workflows.
- Guided onboarding flow for first-time setup.

Current releases remain focused on stable terminal-first dictation.

## Build Packages

```bash
# Linux AppImage
./packaging/build_linux.sh

# Linux .deb
./packaging/build_deb.sh

# macOS zip
./packaging/build_macos.sh

# Windows zip (PowerShell)
.\packaging\build_windows.ps1
```

## Testing

```bash
pytest -q tests/test_smart_editor.py
python3 scripts/eval_smart_editor.py
```

## About This Fork

This is a maintained fork of DictaPilot by [Rohan Sharvesh](https://github.com/RohanSharvesh), with additional reliability and usability improvements by Rehan.

Original project: https://github.com/rohansharvesh/WhisperGroq

## License

MIT. See `LICENSE`.
