## ADDED Requirements

### Requirement: Streaming preview pass
The system SHALL perform transcription on audio chunks during recording for preview purposes.

#### Scenario: Chunks transcribed during recording
- **WHEN** audio chunks are captured during recording
- **THEN** each chunk is transcribed for preview display

#### Scenario: Preview results shown immediately
- **WHEN** a chunk transcription completes
- **THEN** the result is displayed in the preview overlay

### Requirement: Final accuracy pass
The system SHALL perform a final transcription on the complete audio after recording stops.

#### Scenario: Final pass after recording stops
- **WHEN** user releases the hotkey and recording stops
- **THEN** the complete audio is transcribed for the final result

#### Scenario: Final result replaces preview
- **WHEN** the final transcription completes
- **THEN** the final result replaces the preview text

#### Scenario: Final pass configurable
- **WHEN** `streaming_final_pass` is set to `false` in configuration
- **THEN** only streaming results are used without a final accuracy pass

### Requirement: Result quality indication
The system SHALL indicate the quality difference between preview and final results.

#### Scenario: Preview marked as draft
- **WHEN** preview text is displayed
- **THEN** it is visually indicated as a draft/partial result

#### Scenario: Final result quality matches batch
- **WHEN** final transcription completes
- **THEN** the accuracy matches the existing batch transcription quality

### Requirement: Text assembly from chunks
The system SHALL assemble coherent text from overlapping chunk transcriptions.

#### Scenario: Overlapping text merged correctly
- **WHEN** two consecutive chunks have overlapping transcriptions
- **THEN** the system merges them without duplicating the overlapping portion

#### Scenario: Partial sentences handled gracefully
- **WHEN** a chunk ends mid-sentence
- **THEN** the preview shows the partial sentence until the next chunk completes it
