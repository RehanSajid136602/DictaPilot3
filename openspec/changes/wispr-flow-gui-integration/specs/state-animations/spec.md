## ADDED Requirements

### Requirement: State transitions animate smoothly
State transitions SHALL animate smoothly over 250ms with ease-out easing curve.

#### Scenario: Color transition
- **WHEN** a component's state changes (e.g., idle to recording)
- **THEN** the color transitions smoothly over 250ms with ease-out easing

#### Scenario: Size transition
- **WHEN** a component's size changes
- **THEN** the size transitions smoothly over 250ms with ease-out easing

### Requirement: View transitions animate
View transitions SHALL animate with fade effect over 300ms.

#### Scenario: Switching views
- **WHEN** user navigates from Home to Settings
- **THEN** Home fades out and Settings fades in over 300ms

### Requirement: Micro-interactions animate quickly
Micro-interactions (hover, focus, press) SHALL animate over 200ms.

#### Scenario: Button hover
- **WHEN** user hovers over a button
- **THEN** the background color transitions over 200ms

#### Scenario: Input focus
- **WHEN** user focuses an input field
- **THEN** the border color transitions over 200ms

### Requirement: Animations respect reduced motion
All animations SHALL be disabled or reduced when system reduced-motion preference is enabled.

#### Scenario: Reduced motion enabled
- **WHEN** system reduced-motion preference is enabled
- **THEN** all animation durations are set to 0ms (instant transitions)

#### Scenario: Reduced motion disabled
- **WHEN** system reduced-motion preference is disabled
- **THEN** animations use normal durations (200-300ms)

### Requirement: Animations use hardware acceleration
Animations SHALL use QPropertyAnimation for hardware-accelerated rendering.

#### Scenario: Property animation
- **WHEN** an animation is created
- **THEN** it uses QPropertyAnimation for GPU-accelerated rendering

### Requirement: Animations target 60fps
Animations SHALL target 60fps refresh rate (16ms per frame) for smooth motion.

#### Scenario: Animation performance
- **WHEN** an animation is running
- **THEN** it updates at least every 16ms to maintain 60fps
