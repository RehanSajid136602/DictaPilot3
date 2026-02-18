## ADDED Requirements

### Requirement: Chunked audio capture
The system SHALL capture audio in fixed-duration chunks during recording.

#### Scenario: Audio captured in configurable chunks
- **WHEN** user is recording audio
- **THEN** audio is captured in chunks of configurable duration (default 1.5 seconds)

#### Scenario: Chunk callback invoked
- **WHEN** an audio chunk is captured
- **THEN** the registered chunk callback is invoked with the audio data

### Requirement: Overlapping chunk boundaries
The system SHALL include overlap between consecutive chunks to prevent word cutoff at boundaries.

#### Scenario: Chunks include configurable overlap
- **WHEN** consecutive chunks are created
- **THEN** each chunk includes configurable overlap (default 0.3 seconds) with adjacent chunks

#### Scenario: No word cutoff at chunk boundaries
- **WHEN** a word spans the boundary between two chunks
- **THEN** the overlap ensures the word is captured completely in at least one chunk

### Requirement: Audio buffer management
The system SHALL manage an audio buffer that accumulates all recorded audio for final processing.

#### Scenario: Full audio preserved for final pass
- **WHEN** user is recording with streaming enabled
- **THEN** all audio is preserved in a buffer for the final transcription pass

#### Scenario: Buffer cleared between recordings
- **WHEN** recording stops and finalizes
- **THEN** the audio buffer is cleared for the next recording session

### Requirement: Chunk queue management
The system SHALL maintain a queue of chunks awaiting transcription.

#### Scenario: Chunks queued for processing
- **WHEN** a chunk is captured
- **THEN** it is added to the processing queue

#### Scenario: Queue processed in order
- **WHEN** multiple chunks are queued
- **THEN** they are processed in the order they were captured
