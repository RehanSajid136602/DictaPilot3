## 1. Workspace and Tooling Foundation

- [x] 1.1 Create `desktop/` workspace structure for `main`, `preload`, `renderer`, `backend`, `shared`
- [x] 1.2 Add package manager/workspace config and scripts for dev, build, package
- [x] 1.3 Configure TypeScript projects and path aliases for shared contracts
- [x] 1.4 Add lint/format/test baseline for desktop workspace

## 2. Electron Shell and Security

- [x] 2.1 Create Electron main process bootstrap with window lifecycle + tray integration
- [x] 2.2 Configure BrowserWindow security flags (`contextIsolation`, `nodeIntegration`, `sandbox` as applicable)
- [x] 2.3 Implement preload bridge exposing typed IPC client only
- [x] 2.4 Add global hotkey registration with lifecycle-safe cleanup
- [x] 2.5 Add app state persistence for window bounds and last-opened view

## 3. IPC Contracts and Main Handlers

- [x] 3.1 Define shared IPC channel contracts in `desktop/shared`
- [x] 3.2 Implement main-process IPC handlers with validation and typed responses
- [x] 3.3 Add structured error model (`code`, `message`, `details?`) across IPC replies
- [x] 3.4 Add tests for IPC contract conformance and disallowed channels

## 4. Node Backend Services

- [x] 4.1 Implement `audioService` start/stop/finalize interfaces
- [x] 4.2 Implement `transcriptionService` interface and provider abstraction
- [x] 4.3 Implement `editingService` for command-aware post-processing
- [x] 4.4 Implement `settingsService` and `historyService` with local persistence
- [x] 4.5 Add storage schema versioning + migration runner

## 5. React Renderer Core Experience

- [x] 5.1 Build root app shell with route/state container
- [x] 5.2 Implement dictation status panel (idle/recording/processing/error)
- [x] 5.3 Implement streaming preview component with incremental text updates
- [x] 5.4 Implement Home, History, Settings views with keyboard-accessible interactions
- [x] 5.5 Add motion system tuned for smooth transitions with reduced-motion fallback

## 6. End-to-End Dictation Flow

- [x] 6.1 Wire renderer actions to IPC for start/stop dictation
- [x] 6.2 Wire backend pipeline response to output/preview UI
- [x] 6.3 Add retry + timeout handling for transcription failures
- [x] 6.4 Add telemetry/logging hooks for latency and error analysis

## 7. Windows Packaging and Release

- [x] 7.1 Configure Electron Builder for Windows `.exe` output
- [x] 7.2 Add app metadata, icons, and installer defaults
- [x] 7.3 Add CI build job for desktop package artifacts
- [x] 7.4 Add package smoke test verifying app startup and basic dictation controls

## 8. Verification

- [x] 8.1 Verify all scenarios in `electron-shell-runtime` spec
- [x] 8.2 Verify all scenarios in `react-desktop-ui` spec
- [x] 8.3 Verify all scenarios in `node-dictation-service` spec
- [x] 8.4 Verify all scenarios in `windows-installer-packaging` spec
- [x] 8.5 Document developer run/build/package commands in project docs
