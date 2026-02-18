## 1. Configuration & Infrastructure

- [x] 1.1 Add streaming configuration options to `config.py` (streaming_enabled, streaming_chunk_duration, streaming_chunk_overlap, streaming_min_chunks, streaming_final_pass)
- [x] 1.2 Add environment variable support for streaming settings
- [x] 1.3 Update `DictaPilotConfig` dataclass with new streaming fields and defaults

## 2. Audio Buffer & Chunking

- [x] 2.1 Create `audio_buffer.py` module with `ChunkedAudioBuffer` class
- [x] 2.2 Implement audio chunk creation with configurable duration and overlap
- [x] 2.3 Add chunk queue management for streaming processing
- [x] 2.4 Implement buffer accumulation for full audio (final pass)

## 3. Streaming Transcriber

- [x] 3.1 Create `streaming_transcriber.py` module with `StreamingTranscriber` class
- [x] 3.2 Implement worker thread for async chunk transcription
- [x] 3.3 Add chunk transcription with Groq API integration
- [x] 3.4 Implement partial result callback mechanism
- [x] 3.5 Add text assembly logic for merging overlapping chunk transcriptions
- [x] 3.6 Implement error handling and retry logic for failed chunks

## 4. Recorder Integration

- [x] 4.1 Modify `recorder.py` to support chunk callbacks during recording
- [x] 4.2 Integrate `ChunkedAudioBuffer` into recording workflow
- [x] 4.3 Add streaming mode flag to `AudioRecorder` class

## 5. GUI Preview Display

- [x] 5.1 Add preview text display capability to `GUIManager` in `app.py`
- [x] 5.2 Create preview overlay widget with draft styling
- [x] 5.3 Position preview below recording window
- [x] 5.4 Implement preview update debouncing (100ms)
- [x] 5.5 Add streaming status indicator ("Streaming..." / "Finalizing...")
- [x] 5.6 Handle preview visibility state transitions

## 6. App Integration

- [x] 6.1 Integrate `StreamingTranscriber` into main `app.py` workflow
- [x] 6.2 Implement dual-pass transcription flow (streaming + final)
- [x] 6.3 Connect preview updates to GUI
- [x] 6.4 Add fallback logic when streaming fails
- [x] 6.5 Implement streaming/batch mode switching based on configuration

## 7. Error Handling & Fallback

- [x] 7.1 Add streaming health monitoring (track consecutive failures)
- [x] 7.2 Implement automatic fallback to batch mode on repeated errors
- [x] 7.3 Add user notification when fallback occurs
- [x] 7.4 Implement recovery logic to re-enable streaming after cooldown

## 8. Testing

- [x] 8.1 Add unit tests for `ChunkedAudioBuffer` chunk creation
- [x] 8.2 Add unit tests for text assembly from overlapping chunks
- [x] 8.3 Add integration tests for streaming transcription flow
- [x] 8.4 Test streaming with various speech patterns (fast, slow, pauses)
- [x] 8.5 Test fallback scenarios (API errors, timeouts)
- [x] 8.6 Test configuration options (enable/disable streaming)

## 9. Documentation

- [x] 9.1 Update README.md with streaming feature description
- [x] 9.2 Add streaming configuration documentation
- [x] 9.3 Document streaming vs batch trade-offs
