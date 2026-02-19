## ADDED Requirements

### Requirement: Bar chart component
The system SHALL provide a reusable bar chart component with customizable colors, labels, and data.

#### Scenario: Render vertical bars
- **WHEN** bar chart is displayed with data
- **THEN** vertical bars are rendered with heights proportional to values

#### Scenario: Display axis labels
- **WHEN** bar chart is displayed
- **THEN** X-axis shows category labels and Y-axis shows value scale

#### Scenario: Hover interaction
- **WHEN** user hovers over a bar
- **THEN** bar brightens and tooltip shows label and value

### Requirement: Line chart component
The system SHALL provide a reusable line chart component with area fill and data points.

#### Scenario: Render line with area fill
- **WHEN** line chart is displayed with data
- **THEN** line is drawn with 2px stroke and area below is filled with 10% opacity

#### Scenario: Display data points on hover
- **WHEN** user hovers over the line
- **THEN** nearest data point shows as 6px circle with tooltip

#### Scenario: Display gridlines
- **WHEN** line chart is displayed
- **THEN** horizontal gridlines are shown at Y-axis intervals

### Requirement: Donut chart component
The system SHALL provide a reusable donut chart component with segments and center label.

#### Scenario: Render donut segments
- **WHEN** donut chart is displayed with data
- **THEN** segments are rendered with proportional angles and distinct colors

#### Scenario: Display center label
- **WHEN** donut chart is displayed
- **THEN** center shows aggregate value or label

#### Scenario: Segment hover
- **WHEN** user hovers over a segment
- **THEN** segment highlights and tooltip shows label, value, and percentage

### Requirement: Waveform component
The system SHALL provide a real-time waveform component for audio visualization.

#### Scenario: Render amplitude bars
- **WHEN** waveform receives audio data
- **THEN** bars are rendered with heights proportional to amplitude

#### Scenario: Update at 60fps max
- **WHEN** waveform is active
- **THEN** display updates are throttled to maximum 60 frames per second

#### Scenario: Idle animation
- **WHEN** no audio data is available
- **THEN** waveform shows flat line with subtle breathing animation

### Requirement: Theme integration
The system SHALL apply theme colors to all chart components automatically.

#### Scenario: Apply theme colors
- **WHEN** a chart is rendered
- **THEN** colors are sourced from theme token system

#### Scenario: Update on theme change
- **WHEN** user switches between dark and light theme
- **THEN** all charts update colors to match new theme
