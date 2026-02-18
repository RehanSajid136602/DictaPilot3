## ADDED Requirements

### Requirement: Platform-specific setup guides exist for all supported platforms
The system SHALL provide dedicated setup guides for Linux, macOS, and Windows.

#### Scenario: Linux user finds platform guide
- **WHEN** a Linux user needs setup instructions
- **THEN** they can access a Linux-specific guide covering X11/Wayland, permissions, and dependencies

#### Scenario: macOS user finds platform guide
- **WHEN** a macOS user needs setup instructions
- **THEN** they can access a macOS-specific guide covering Accessibility permissions and Keychain setup

#### Scenario: Windows user finds platform guide
- **WHEN** a Windows user needs setup instructions
- **THEN** they can access a Windows-specific guide covering permissions and backend selection

### Requirement: Platform guides cover platform-specific troubleshooting
Each platform guide SHALL include a troubleshooting section for common platform-specific issues.

#### Scenario: Linux user troubleshoots hotkey issues
- **WHEN** a Linux user has hotkey problems
- **THEN** the Linux guide provides solutions for X11/Wayland backend selection and permissions

#### Scenario: macOS user troubleshoots paste issues
- **WHEN** a macOS user has paste problems
- **THEN** the macOS guide provides solutions for Accessibility permissions and osascript backend

#### Scenario: Windows user troubleshoots audio issues
- **WHEN** a Windows user has audio problems
- **THEN** the Windows guide provides solutions for microphone permissions and device selection

### Requirement: Platform guides include backend selection guidance
Platform guides SHALL explain which backends work best for each platform and how to configure them.

#### Scenario: User selects optimal backend
- **WHEN** user reads platform guide
- **THEN** they understand which HOTKEY_BACKEND and PASTE_BACKEND values are recommended for their platform

#### Scenario: User troubleshoots backend issues
- **WHEN** default backend fails
- **THEN** platform guide provides alternative backend options with configuration examples
