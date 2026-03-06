# DictaPilot Desktop App - Status & Fix Report

## 📋 Summary of What Has Occurred
We initiated a major migration to move DictaPilot from a Python-based prototype to a robust **Electron + React (Vite) + TypeScript** desktop application. The goal was to implement a modern, high-end "Cyber-Glass" UI, integrate real-time streaming with the Groq API, and create a perfectly synchronized floating widget without the overhead of running parallel Python processes.

## ✅ What Has Been Done
1. **Phase 1 & 2 (UI Architecture):** 
   - Rebuilt the main window into a single "Center Stage" view with a toggleable frosted-glass sidebar for Settings and History.
   - Connected the React frontend to the Electron `main` process using IPC (`dictationAPI` in `preload`).
2. **Phase 3 (Streaming Transcription):**
   - Implemented `GroqProvider` in the Node backend. It collects raw audio chunks and periodically (every 2 seconds) sends them to Groq's Whisper model to create a live streaming effect.
3. **Phase 4 (Smart Editing):**
   - Ported the Python LLM logic into a Node `EditingService`. When dictation finishes, it sends the raw text to `llama3-8b-8192` to process commands like "delete that" and strip filler words before delivering the final text.
4. **Phase 5 (Native Floating Widget & Hotkeys):**
   - Dropped the idea of running the Python PySide6 widget in the background. Instead, built a **Native Electron Widget** (`widgetWindow`) that mirrors the state and amplitude of the main app.
   - Replaced Electron's native `globalShortcut` with `node-global-key-listener` to support **true Press-and-Hold** behavior for the F9 key (triggering start on DOWN, stop on UP).

---

## 🎤 The Microphone Access & Crashing Errors

### Issue 1: `Error: spawn sox ENOENT`
* **The Cause:** The original backend used the `node-record-lpcm16` library to capture audio. This library relies on system-level binaries (like `sox` or `rec`). Because Windows does not have `sox` installed by default, the app crashed violently when F9 was pressed.
* **The Fix:** We completely removed the `node-record-lpcm16` dependency. We shifted the audio capture responsibility to the **React Frontend**. We now use the browser's native Web Audio API (`navigator.mediaDevices.getUserMedia`) to capture the mic, convert the stream to 16-bit PCM, and pipe it via IPC (`SendAudioData`) to the backend.

### Issue 2: Missing UI Updates & Freezing
* **The Cause:** When pressing F9, the terminal showed the state changing, but the UI (Main app and Widget) remained frozen. 
    1. **Media Permissions:** Electron blocks microphone access by default unless explicitly permitted.
    2. **React Race Condition:** In `WidgetApp.tsx` and `App.tsx`, the IPC event listener for `onStateChange` was placed inside a `useEffect` that had `dictationState` in its dependency array. The moment the state changed to "recording", React destroyed the listener and remounted it, missing all subsequent updates (like amplitude or the stop event).
* **The Fix:** 
    1. Hooked into `session.defaultSession.setPermissionRequestHandler` in `main/index.ts` to automatically approve `media` (microphone) requests.
    2. Refactored the React components to use `useRef` to track the state silently. The `useEffect` dependency array is now empty (`[]`), ensuring the IPC listener is permanent and never misses a beat.

---

## 🚀 Next Steps to Finalize

When you return, here is the exact checklist to finalize the build:

1. **Verify Web Audio Pipeline:**
   - Double-check the DevTools console in the app. Ensure `navigator.mediaDevices.getUserMedia` successfully acquires the mic. 
   - *Note:* We are currently using `ScriptProcessorNode` for audio capture. While it works reliably in Electron, it is technically deprecated in modern browsers. In the future, this can be migrated to an `AudioWorklet`.

2. **Clean up Debugging Code:**
   - In `desktop/main/index.ts`, remove or comment out `mainWindow?.webContents.openDevTools({ mode: 'detach' });`.
   - Remove the verbose `console.log` statements in the UI components if they become too noisy.

3. **Auto-Pasting Mechanism:**
   - The current implementation successfully gets the finalized LLM text and copies it to the internal history. We still need to implement the final step of simulating keystrokes to **paste the text into the user's active window** (e.g., using `robotjs` or `nut.js` in the main process).

4. **Package & Test:**
   - Run `npm run build` followed by `npm run package` to ensure the Windows installer (`.exe`) compiles correctly with the new native dependencies.