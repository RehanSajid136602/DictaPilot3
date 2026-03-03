## ADDED Requirements

### Requirement: Waveform displays 11 bars with gradient fill
The waveform component SHALL display 11 vertical bars with gradient fill colors that match the current recording state.

#### Scenario: Recording state gradient
- **WHEN** recording state is "recording"
- **THEN** waveform bars display cyan gradient from #06b6d4 to #22d3ee

#### Scenario: Processing state gradient
- **WHEN** recording state is "processing"
- **THEN** waveform bars display purple gradient from #8b5cf6 to #a78bfa

### Requirement: Waveform bars have rounded caps
The waveform bars SHALL have rounded caps at the top for a smooth, modern appearance.

#### Scenario: Rendering bar caps
- **WHEN** waveform bars are rendered
- **THEN** each bar has rounded caps with radius matching the bar width

### Requirement: Waveform updates amplitude in real-time
The waveform component SHALL update bar amplitudes in real-time based on audio input, targeting 60fps refresh rate.

#### Scenario: Updating amplitudes
- **WHEN** audio amplitude data is received
- **THEN** waveform bars update their heights within 16ms (60fps) with smooth transitions

#### Scenario: Smooth amplitude transitions
- **WHEN** amplitude changes
- **THEN** bars animate to new heights over 250ms with ease-out easing

### Requirement: Waveform displays glow effect
The waveform component SHALL display a subtle outer glow effect matching the current state color.

#### Scenario: Recording glow
- **WHEN** recording state is "recording"
- **THEN** waveform displays cyan glow with 8px blur radius and 40% opacity

#### Scenario: Processing glow
- **WHEN** recording state is "processing"
- **THEN** waveform displays purple glow with 8px blur radius and 40% opacity

### Requirement: Waveform respects reduced motion preference
The waveform component SHALL disable smooth transitions when system reduced-motion preference is enabled.

#### Scenario: Reduced motion mode
- **WHEN** system reduced-motion preference is enabled
- **THEN** waveform bar height changes are instant without animation transitions
