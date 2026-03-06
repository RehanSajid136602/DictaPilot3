## Context

This change introduces a new desktop stack for DictaPilot using Electron (desktop shell), React (UI), and Node/TypeScript (service/backend orchestration). The immediate target is Windows, with an installable executable workflow and high visual polish. Existing Python modules remain the baseline behavior reference while desktop implementation reaches feature parity.

**Constraints:**
- Windows-first delivery
- Secure Electron defaults (no direct Node in renderer)
- Keep implementation modular so backend services are testable outside UI
- Preserve current dictation behavior semantics where possible
- Prioritize “smooth/video-like” visual transitions in UI without sacrificing responsiveness

## Goals / Non-Goals

**Goals:**
- Establish Electron + React + Node monorepo/workspace under `desktop/`
- Define typed IPC contracts and strict process boundaries
- Implement core dictation lifecycle (idle -> recording -> processing -> output)
- Ship Windows packaging pipeline that produces `.exe` artifacts
- Reach apply-ready artifact set for implementation kickoff

**Non-Goals:**
- Full parity for every legacy Python feature in first implementation
- macOS/Linux packaging in this change
- Cloud sync, team features, or enterprise controls
- Complete visual redesign of every secondary screen before core flow works

## Decisions

### Decision 1: Architecture split by process boundary
**Choice:** Keep three layers: Electron main (app runtime), Electron preload (typed bridge), React renderer (UI), Node services (domain logic called via main process).

**Rationale:**
- Strong security boundary
- Easier testability and replacement of service internals
- Cleaner migration from current Python-centric architecture

### Decision 2: Typed IPC contract first
**Choice:** Define shared TypeScript IPC contracts (`desktop/shared/ipc.ts`) before feature implementation.

**Rationale:**
- Prevents ad-hoc string channels
- Enables compile-time safety across main/renderer
- Reduces regressions during rapid UI iteration

### Decision 3: Backend modules by domain
**Choice:** Backend services split into `audioService`, `transcriptionService`, `editingService`, `settingsService`, `historyService`.

**Rationale:**
- Limits blast radius of changes
- Supports targeted unit tests
- Aligns with existing DictaPilot module boundaries

### Decision 4: Windows packaging with electron-builder
**Choice:** Use Electron Builder for installer generation and update-ready artifact structure.

**Rationale:**
- Mature Windows support
- Straightforward CI integration
- Minimal custom packaging code

### Decision 5: Migration approach
**Choice:** Implement desktop stack in parallel under `desktop/` without deleting Python runtime paths.

**Rationale:**
- De-risks transition
- Allows behavior comparison against current app
- Keeps fallback path while desktop hardens

## Risks / Trade-offs

### Risk 1: Audio/hotkey parity drift
**Mitigation:** Define acceptance scenarios for hotkey latency and recording lifecycle in specs; keep contract tests.

### Risk 2: IPC surface growth and security regressions
**Mitigation:** Enforce typed allowlist channels and no dynamic eval/execution in IPC handlers.

### Risk 3: Packaging instability on Windows
**Mitigation:** Add deterministic build config, explicit artifact checks, and smoke test on packaged output.

### Risk 4: UI smoothness vs CPU usage
**Mitigation:** Use GPU-friendly transforms, throttle high-frequency updates, and profile render loops.

## Migration Plan

1. Bootstrap `desktop/` workspace and build scripts.
2. Implement secure Electron main/preload and typed IPC contracts.
3. Build minimal React shell + state machine views.
4. Implement Node service stubs and connect end-to-end dictation flow.
5. Add persistence and history/settings screens.
6. Add Windows packaging config and CI workflow.
7. Run parity and packaging smoke checks.
