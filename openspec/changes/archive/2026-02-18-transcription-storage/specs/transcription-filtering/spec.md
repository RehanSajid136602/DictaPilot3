## ADDED Requirements

### Requirement: Date range filtering
The system SHALL allow filtering transcriptions by date range.

#### Scenario: Filter by start and end date
- **WHEN** user calls `filter().date_range(start_date, end_date)`
- **THEN** system returns only transcriptions with timestamps between start and end (inclusive)

#### Scenario: Filter by relative date
- **WHEN** user calls `filter().last_n_days(7)`
- **THEN** system returns transcriptions from the last 7 days

### Requirement: Tag-based filtering
The system SHALL allow filtering transcriptions by tags.

#### Scenario: Filter by single tag
- **WHEN** user calls `filter().tags(['work'])`
- **THEN** system returns transcriptions containing the tag 'work'

#### Scenario: Filter by multiple tags (AND)
- **WHEN** user calls `filter().tags(['work', 'important'])`
- **THEN** system returns transcriptions containing ALL specified tags

#### Scenario: Filter by multiple tags (OR)
- **WHEN** user calls `filter().tags(['work', 'personal'], match_any=True)`
- **THEN** system returns transcriptions containing ANY of the specified tags

### Requirement: Language filtering
The system SHALL allow filtering transcriptions by detected language.

#### Scenario: Filter by language code
- **WHEN** user calls `filter().language('en')`
- **THEN** system returns transcriptions with language matching 'en'

### Requirement: Quality score filtering
The system SHALL allow filtering by quality score thresholds.

#### Scenario: Filter by minimum quality
- **WHEN** user calls `filter().quality_above(0.8)`
- **THEN** system returns transcriptions with quality_score >= 0.8

#### Scenario: Filter by quality range
- **WHEN** user calls `filter().quality_range(0.5, 0.9)`
- **THEN** system returns transcriptions with quality_score between 0.5 and 0.9 (inclusive)

### Requirement: Word count filtering
The system SHALL allow filtering by word count thresholds.

#### Scenario: Filter by minimum words
- **WHEN** user calls `filter().min_words(10)`
- **THEN** system returns transcriptions with word_count >= 10

#### Scenario: Filter by word count range
- **WHEN** user calls `filter().word_count_range(5, 50)`
- **THEN** system returns transcriptions with word_count between 5 and 50 (inclusive)

### Requirement: App name filtering
The system SHALL allow filtering by source application name.

#### Scenario: Filter by app
- **WHEN** user calls `filter().app('VSCode')`
- **THEN** system returns transcriptions where app_name matches 'VSCode'

### Requirement: Chainable filter builder
The system SHALL support method chaining for filter construction.

#### Scenario: Chain multiple filters
- **WHEN** user calls `filter().date_range(start, end).tags(['work']).quality_above(0.5)`
- **THEN** system returns transcriptions matching ALL specified criteria
