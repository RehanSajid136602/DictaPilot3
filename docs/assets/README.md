# Visual Assets

This directory contains visual assets for documentation.

## Screenshots

Screenshots demonstrating key features:

- `floating-window.png` - Floating status window during recording
- `first-dictation.png` - First successful dictation
- `smart-editing.png` - Smart editing in action
- `voice-commands.png` - Voice command examples
- `onboarding-wizard.png` - Setup wizard screens

**To create screenshots:**
1. Run DictaPilot3
2. Use screenshot tool (Flameshot, macOS Screenshot, Snipping Tool)
3. Save to this directory with descriptive names
4. Update documentation to reference images

## GIFs

Animated demonstrations of workflows:

- `hold-to-dictate.gif` - Complete dictation workflow
- `voice-commands.gif` - Using voice commands
- `profile-switching.gif` - Switching between profiles
- `delta-paste.gif` - Delta paste in action

**To create GIFs:**
1. Use screen recording tool (OBS, QuickTime, Windows Game Bar)
2. Convert to GIF with tool like FFmpeg or online converter
3. Keep file size under 5MB
4. Save to this directory

**FFmpeg conversion:**
```bash
ffmpeg -i recording.mp4 -vf "fps=10,scale=800:-1:flags=lanczos" -c:v gif output.gif
```

## Videos

Tutorial videos (hosted on YouTube):

- Quick Start (3 min)
- Voice Commands (5 min)
- Smart Editing (4 min)
- Context Profiles (3 min)
- Troubleshooting (4 min)

**Video creation checklist:**
- [ ] Script outline
- [ ] Screen recording with audio
- [ ] Edit and add captions
- [ ] Upload to YouTube
- [ ] Update documentation with embed links

**Recommended tools:**
- OBS Studio (free, cross-platform)
- DaVinci Resolve (free editing)
- YouTube Studio (captions)

## Guidelines

**Screenshots:**
- Resolution: 1920x1080 or higher
- Format: PNG for UI, JPEG for photos
- Show realistic use cases
- Include context (window titles, etc.)

**GIFs:**
- Duration: 5-15 seconds
- Frame rate: 10-15 fps
- Size: < 5MB
- Show complete workflow

**Videos:**
- Resolution: 1080p minimum
- Format: MP4 (H.264)
- Audio: Clear narration
- Length: 3-5 minutes each
- Include captions

## Status

- [ ] Screenshots created
- [ ] GIFs created
- [ ] Videos recorded
- [ ] Videos uploaded to YouTube
- [ ] Documentation updated with links

**Last Updated:** 2026-02-17
