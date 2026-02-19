# Modern Floating Window UI/UX Guide

## Overview

DictaPilot's floating window has been redesigned with modern 2026 UI/UX principles, featuring glassmorphism, smooth animations, and intuitive visual feedback.

## Features

### Glassmorphism (Liquid Glass)
- Frosted glass effect with translucent background
- Backdrop blur for depth and layering
- Subtle borders with semi-transparent edges
- Vibrant accent colors with proper contrast

### Smooth Animations
- Breathing animation in idle state
- Pulsing glow during active recording
- Smooth state transitions with elastic easing
- Hover effects with subtle scale changes

### Modern Waveform Visualization
- 7 elegant bars with smooth interpolation
- Gradient fills (light → primary → dark)
- Glow effects during active states
- Responsive to audio input levels

## Configuration

Add these settings to your `.env` file:

```bash
# UI Style (modern or classic)
FLOATING_UI_STYLE=modern

# Accent Color (blue, purple, green)
FLOATING_ACCENT_COLOR=blue

# Enable glassmorphism effect
FLOATING_GLASSMORPHISM=1

# Enable animations
FLOATING_ANIMATIONS=1

# Reduced motion for accessibility
FLOATING_REDUCED_MOTION=0

# Layout style (circular, pill, card)
FLOATING_LAYOUT=pill
```

## Accent Colors

### Blue (Default)
- Professional and trustworthy
- Primary: #3B82F6
- Best for: General use, professional environments

### Purple
- Creative and modern
- Primary: #8B5CF6
- Best for: Creative work, design tasks

### Green
- Positive and energetic
- Primary: #10B981
- Best for: Success feedback, productivity

## Layout Options

### Pill (Default)
- Balanced visibility and compactness
- Idle: 180x44px, Active: expands smoothly
- Best for: Most users

### Circular
- Ultra-minimalist, iOS-inspired
- Idle: 80x80px circle
- Best for: Minimal screen footprint

### Card
- Maximum visual feedback
- Idle: 200x80px, Active: 280x120px
- Best for: Users who want more information

## Accessibility

### Reduced Motion
Set `FLOATING_REDUCED_MOTION=1` to disable animations for users sensitive to motion.

### High Contrast
The modern UI maintains WCAG 2.1 AA contrast ratios in all states.

### Classic Mode
Set `FLOATING_UI_STYLE=classic` to use the original UI design.

## Performance

- Animations run at 60 FPS
- CPU usage: <5% during animations
- GPU-accelerated rendering via Qt
- Optimized for high DPI displays

## Troubleshooting

### Animations are choppy
- Check CPU usage
- Try `FLOATING_REDUCED_MOTION=1`
- Switch to `FLOATING_UI_STYLE=classic`

### Glassmorphism not visible
- Ensure `FLOATING_GLASSMORPHISM=1`
- Check if compositor supports transparency
- Try different accent colors

### Window too small/large
- Adjust `FLOATING_WIDTH` and `FLOATING_HEIGHT`
- Try different `FLOATING_LAYOUT` options
