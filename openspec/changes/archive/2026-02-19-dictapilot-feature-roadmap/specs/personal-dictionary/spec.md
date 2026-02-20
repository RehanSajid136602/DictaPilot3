## ADDED Requirements

### Requirement: Auto-learn user words to personal dictionary
The system SHALL automatically add unfamiliar words to the personal dictionary when users explicitly correct or add them, with frequency tracking.

#### Scenario: User adds word via correction
- **WHEN** user corrects a transcribed word that was not in the dictionary
- **THEN** system prompts user to add the corrected word to personal dictionary
- **AND** if confirmed, word is stored with frequency count of 1

#### Scenario: User manually adds word
- **WHEN** user explicitly adds a word to personal dictionary via command or UI
- **THEN** word is stored with user-specified frequency or default of 1
- **AND** word is marked as manually added (not auto-learned)

#### Scenario: Word frequency increases on use
- **WHEN** personal dictionary word is used in transcription
- **THEN** system increments the frequency count for that word
- **AND** higher frequency words are prioritized in future predictions

### Requirement: Personal dictionary lookup during transcription
The system SHALL check personal dictionary during transcription to improve accuracy for user-specific words.

#### Scenario: Dictionary word matches transcription
- **WHEN** transcribed text matches a word in personal dictionary
- **THEN** system uses dictionary entry to boost transcription confidence
- **AND** no correction prompt is shown for that word

#### Scenario: Unknown word detected
- **WHEN** transcribed word is not in standard dictionary or personal dictionary
- **THEN** system flags the word as unknown
- **AND** offers option to add to personal dictionary

### Requirement: Personal dictionary management
The system SHALL allow users to view, edit, and delete personal dictionary entries.

#### Scenario: User views dictionary
- **WHEN** user requests to view personal dictionary
- **THEN** system displays all entries sorted by frequency (highest first)
- **AND** each entry shows word, frequency, and source (auto-learned/manual)

#### Scenario: User edits dictionary entry
- **WHEN** user modifies a dictionary entry
- **THEN** system updates the entry in SQLite database
- **AND** changes take effect immediately for future transcriptions

#### Scenario: User deletes dictionary entry
- **WHEN** user removes a word from personal dictionary
- **THEN** system deletes the entry from database
- **AND** word will be treated as unknown in future transcriptions

### Requirement: Import/export personal dictionary
The system SHALL support importing and exporting personal dictionary for backup and transfer.

#### Scenario: User exports dictionary
- **WHEN** user requests dictionary export
- **THEN** system generates JSON file with all entries
- **AND** file is saved to user-specified location

#### Scenario: User imports dictionary
- **WHEN** user provides JSON file to import
- **THEN** system validates format and merges entries
- **AND** existing entries have their frequencies updated if higher
