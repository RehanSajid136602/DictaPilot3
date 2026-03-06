## Why

DictaPilot needs a Windows desktop app with modern UI quality, smooth interactions, and smaller runtime overhead than Electron. Tauri with a React frontend provides native-feeling performance, lower memory footprint, and a cleaner security model while still enabling rapid UI development.

## What Changes

- Introduce a new desktop stack based on **Tauri + React + TypeScript + Rust backend commands**.
- Build the core dictation desktop UX (recording states, streaming preview, history, settings) in React.
- Implement backend orchestration in Tauri/Rust commands for secure desktop capabilities and system integrations.
- Define typed frontend-to-backend contracts for transcription flow, smart-edit processing, and settings/history persistence.
- Add Windows packaging pipeline for `.exe` installer output via Tauri bundling.
- Keep existing OpenSpec changes intact; this is a separate implementation track.

## Capabilities

### New Capabilities

- `tauri-shell-runtime`: Secure Tauri runtime with native window lifecycle, tray support, and command bridge.
- `react-desktop-ui`: React renderer for modern dictation workflow and dashboard views.
- `rust-command-backend`: Rust command layer for desktop operations, pipeline orchestration, and typed errors.
- `tauri-command-contracts`: Shared command payload/response types across frontend and backend.
- `windows-tauri-packaging`: Build and bundle Windows installer/executable artifacts.

### Modified Capabilities

- `live-preview-ui`: Reimplemented in React while preserving behavior semantics from current app.
- `dashboard-home-view`: Recreated for Tauri desktop with high-performance visual states.
- `dashboard-history-view`: Recreated with search/filter and quick actions.

## Impact

**Code Changes:**
- New `tauri-desktop/` workspace (React app, `src-tauri`, shared types).
- New packaging scripts and CI workflow for Tauri Windows bundles.
- Documentation updates for local dev/build/package commands.

**Dependencies:**
- Rust toolchain (`rustup`, stable toolchain)
- Tauri CLI and build prerequisites
- React + TypeScript frontend toolchain
- Optional audio/transcription integrations chosen during implementation

**User Experience:**
- Faster startup and lower memory use vs Electron baseline
- High-quality, smooth UI transitions for dictation states
- Installer-based Windows onboarding

**Risk Areas:**
- Global hotkey/audio capture parity with current implementation
- Rust command surface design and migration complexity
- Windows bundling/signing setup and native dependency edges
