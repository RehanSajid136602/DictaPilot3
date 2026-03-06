## Why

DictaPilot currently runs as a Python app with PySide UI. The target is a Windows-first desktop product that feels modern, smooth, and app-like while keeping existing dictation value. Moving to an Electron shell with a React frontend and Node backend gives faster UI iteration, richer motion/visual capability, and simpler Windows `.exe` distribution.

## What Changes

- Add a new desktop application stack: Electron + React + Node/TypeScript.
- Build a native-feeling React interface with real-time recording states, streaming transcript preview, and command-aware editing controls.
- Implement a Node backend service layer for transcription orchestration, smart editing pipeline calls, settings/profile management, and local persistence.
- Define secure IPC contracts between renderer and main process (no direct Node in renderer).
- Add Windows packaging and release flow producing installable `.exe` artifacts.
- Keep migration-safe boundaries so existing Python implementation can remain available during transition.

## Capabilities

### New Capabilities

- `electron-shell-runtime`: Desktop runtime with app lifecycle, tray, window management, auto-update hooks, and secure preload bridge.
- `react-desktop-ui`: Modern React UI for dictation workflow, history, profiles, and settings.
- `node-dictation-service`: Node orchestration layer for transcription pipeline, smart editing, and local data operations.
- `desktop-ipc-contracts`: Typed request/response IPC APIs for renderer-main communication.
- `windows-installer-packaging`: Build and package Windows installer/executable output.

### Modified Capabilities

- `live-preview-ui`: Move from PySide rendering to React renderer while preserving behavior and state semantics.
- `dashboard-home-view`: Reimplemented in React with richer animation and responsive layouts.
- `dashboard-history-view`: Reimplemented in React with search/filter and clipboard actions.

## Impact

**Code Changes:**
- New: `desktop/` workspace (Electron main/preload, React renderer, Node services, shared types)
- Modified: documentation and setup flow for desktop build/run/package
- Optional transitional integration points for existing Python modules

**Dependencies:**
- Electron runtime and packaging toolchain
- React + TypeScript UI stack
- Node audio/transcription related libraries (final selection during implementation)

**User Experience:**
- Cleaner, faster-feeling desktop UX with modern motion
- Windows installer-based onboarding
- Better visual continuity for streaming dictation states

**Risk Areas:**
- Audio capture and global hotkey parity with current Python behavior
- IPC security and process isolation
- Packaging/signing and Windows permission edge cases
