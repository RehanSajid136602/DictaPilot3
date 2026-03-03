## ADDED Requirements

### Requirement: Charts display with gradient fills
Chart components SHALL display bars, lines, and areas with gradient fills using Wispr Flow accent colors.

#### Scenario: Bar chart gradient
- **WHEN** a bar chart is rendered
- **THEN** bars display with accent-blue gradient from #3b82f6 to #60a5fa

#### Scenario: Line chart gradient
- **WHEN** a line chart is rendered
- **THEN** the area under the line displays with gradient fill

### Requirement: Charts have rounded bar caps
Bar charts SHALL display bars with rounded caps for a modern appearance.

#### Scenario: Rendering bar caps
- **WHEN** a bar chart is rendered
- **THEN** each bar has rounded caps with 4px radius

### Requirement: Charts display subtle grid lines
Charts SHALL display subtle grid lines in bg-surface color for better readability.

#### Scenario: Grid line rendering
- **WHEN** a chart is rendered
- **THEN** horizontal grid lines appear in bg-surface color with 1px width

### Requirement: Charts support hover interactions
Charts SHALL display hover state showing data values when user hovers over bars or data points.

#### Scenario: Hovering over bar
- **WHEN** user hovers over a bar in a bar chart
- **THEN** a tooltip displays showing the exact value

### Requirement: Charts use caption typography for labels
Charts SHALL use caption typography (12px, 400 weight) for axis labels and legends.

#### Scenario: Axis label typography
- **WHEN** a chart is rendered
- **THEN** axis labels display in caption size (12px) with text-secondary color
