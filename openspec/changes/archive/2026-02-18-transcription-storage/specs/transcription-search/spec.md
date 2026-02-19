## ADDED Requirements

### Requirement: Fuzzy text search
The system SHALL support fuzzy matching for typo-tolerant search.

#### Scenario: Fuzzy match with threshold
- **WHEN** user calls `search_fuzzy('helo world', threshold=0.8)`
- **THEN** system returns transcriptions containing 'hello world' (typo tolerance)

#### Scenario: Adjustable similarity threshold
- **WHEN** user calls `search_fuzzy('test', threshold=0.6)`
- **THEN** system returns matches with similarity >= 0.6

### Requirement: Exact phrase search
The system SHALL support searching for exact phrases.

#### Scenario: Exact phrase match
- **WHEN** user calls `search_phrase('machine learning')`
- **THEN** system returns only transcriptions containing the exact phrase "machine learning"

### Requirement: Regex search
The system SHALL support regular expression search.

#### Scenario: Regex pattern search
- **WHEN** user calls `search_regex(r'\b(word1|word2)\b')`
- **THEN** system returns transcriptions matching the regex pattern

#### Scenario: Regex with capture groups
- **WHEN** user calls `search_regex(r'(error|warning): (.+)')`
- **THEN** system returns matches and extracted groups can be accessed

### Requirement: Combined search operators
The system SHALL support combining multiple search types.

#### Scenario: AND operator
- **WHEN** user calls `search('keyword1').AND('keyword2')`
- **THEN** system returns transcriptions containing both keywords

#### Scenario: OR operator
- **WHEN** user calls `search('keyword1').OR('keyword2')`
- **THEN** system returns transcriptions containing either keyword

#### Scenario: NOT operator
- **WHEN** user calls `search('keyword1').NOT('keyword2')`
- **THEN** system returns transcriptions containing keyword1 but not keyword2

### Requirement: Search ranking
The system SHALL rank search results by relevance.

#### Scenario: Ranked results
- **WHEN** user performs search without explicit ordering
- **THEN** results are sorted by relevance score (most relevant first)

### Requirement: Search highlighting
The system SHALL highlight matching terms in search results.

#### Scenario: Highlight matches
- **WHEN** user calls `search('query', highlight=True)`
- **THEN** results include highlighted markup around matched terms

### Requirement: Search within date range
The system SHALL support combining text search with date filtering.

#### Scenario: Text and date combined
- **WHEN** user calls `search('meeting').date_range(start, end)`
- **THEN** system returns transcriptions containing 'meeting' within the date range
