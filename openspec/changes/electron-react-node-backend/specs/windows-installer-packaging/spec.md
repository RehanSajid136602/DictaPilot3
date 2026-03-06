## ADDED Requirements

### Requirement: Windows packaging produces installable executable artifacts
Build system SHALL produce Windows installer and executable outputs suitable for user installation and launch.

#### Scenario: CI release build
- **WHEN** release workflow runs on Windows
- **THEN** artifacts include installer executable, unpacked app bundle, and checksum metadata

#### Scenario: Local package build
- **WHEN** developer runs package command
- **THEN** build completes with versioned output in a documented dist directory

### Requirement: Packaged app maintains runtime parity with development mode
Packaged binaries SHALL support core dictation flows equivalent to development mode.

#### Scenario: Packaged app startup
- **WHEN** user launches packaged app
- **THEN** shell, UI, and backend initialize successfully with no missing path/dependency failures
