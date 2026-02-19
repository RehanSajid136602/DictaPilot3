## ADDED Requirements

### Requirement: KPI cards display
The system SHALL display KPI cards showing total transcriptions, total words, average WPM, and average quality with trend indicators.

#### Scenario: Display KPI metrics
- **WHEN** Statistics view is displayed
- **THEN** four KPI cards show current metrics with large numbers and labels

#### Scenario: Display trend indicators
- **WHEN** Statistics view is displayed
- **THEN** each KPI card shows percentage change compared to previous period with up/down arrow

#### Scenario: Positive trend styling
- **WHEN** a metric has increased
- **THEN** trend indicator shows green color with up arrow

#### Scenario: Negative trend styling
- **WHEN** a metric has decreased
- **THEN** trend indicator shows red color with down arrow

### Requirement: Volume line chart
The system SHALL display a line chart showing transcription volume over time with selectable time ranges.

#### Scenario: Display 30-day volume
- **WHEN** user selects "30 days" time range
- **THEN** line chart shows transcription count per day for last 30 days

#### Scenario: Display 7-day volume
- **WHEN** user selects "7 days" time range
- **THEN** line chart shows transcription count per day for last 7 days

#### Scenario: Display 24-hour volume
- **WHEN** user selects "24 hours" time range
- **THEN** line chart shows transcription count per hour for last 24 hours

#### Scenario: Chart hover tooltip
- **WHEN** user hovers over a data point
- **THEN** tooltip shows date/time and transcription count

### Requirement: Word count histogram
The system SHALL display a histogram showing distribution of transcription lengths.

#### Scenario: Display word count distribution
- **WHEN** Statistics view is displayed
- **THEN** histogram shows bars for bins: 0-10, 10-50, 50-100, 100-500, 500+ words

#### Scenario: Histogram bar click
- **WHEN** user clicks a histogram bar
- **THEN** system navigates to History view filtered by that word count range

### Requirement: Quality score distribution
The system SHALL display quality score distribution as a donut chart.

#### Scenario: Display quality segments
- **WHEN** Statistics view is displayed
- **THEN** donut chart shows segments for Excellent (>0.9), Good (0.7-0.9), Fair (0.5-0.7), Poor (<0.5)

#### Scenario: Display average in center
- **WHEN** Statistics view is displayed
- **THEN** donut chart center shows overall average quality score as percentage

### Requirement: Voice commands table
The system SHALL display a table of most frequently used voice commands.

#### Scenario: Display top commands
- **WHEN** Statistics view is displayed
- **THEN** table shows top 10 voice commands with count and last used timestamp

#### Scenario: Sort by column
- **WHEN** user clicks a column header
- **THEN** table sorts by that column in ascending/descending order

#### Scenario: Show more commands
- **WHEN** user clicks "Show more" link
- **THEN** table expands to show additional commands
