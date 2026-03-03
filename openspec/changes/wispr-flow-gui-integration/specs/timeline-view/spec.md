## ADDED Requirements

### Requirement: Timeline view organizes items by day
The timeline view SHALL organize transcription items by day with visual day separators.

#### Scenario: Today section
- **WHEN** transcriptions exist from today
- **THEN** they appear under a "Today" heading

#### Scenario: Yesterday section
- **WHEN** transcriptions exist from yesterday
- **THEN** they appear under a "Yesterday" heading

#### Scenario: Older dates
- **WHEN** transcriptions exist from older dates
- **THEN** they appear under date headings (e.g., "February 18, 2026")

### Requirement: Timeline items display as glassmorphism cards
Each timeline item SHALL display as a glassmorphism card with metadata and preview text.

#### Scenario: Item card rendering
- **WHEN** a timeline item is rendered
- **THEN** it displays as a glassmorphism card with blur and transparency

### Requirement: Timeline items show metadata
Timeline items SHALL display time, word count, and quality score metadata.

#### Scenario: Metadata display
- **WHEN** a timeline item is rendered
- **THEN** it shows "2:34 PM • 145 words • 94% quality" in caption typography

### Requirement: Timeline items show preview text
Timeline items SHALL display truncated preview text (first 120 characters) of the transcription.

#### Scenario: Preview text
- **WHEN** a timeline item is rendered
- **THEN** it shows the first 120 characters of transcription text with ellipsis if truncated

### Requirement: Timeline items have action buttons
Timeline items SHALL include action buttons for play audio, copy text, and delete.

#### Scenario: Action buttons
- **WHEN** a timeline item is rendered
- **THEN** it displays "▶ Play", "📋 Copy", and "🗑 Delete" buttons

#### Scenario: Copy action
- **WHEN** user clicks the Copy button
- **THEN** the transcription text is copied to clipboard
