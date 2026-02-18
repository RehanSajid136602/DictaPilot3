## ADDED Requirements

### Requirement: Troubleshooting guide covers common issues
The system SHALL provide a troubleshooting guide covering the most common setup and usage issues.

#### Scenario: User finds solution for API key errors
- **WHEN** user encounters API key authentication errors
- **THEN** the troubleshooting guide provides step-by-step solutions for verifying and fixing API key configuration

#### Scenario: User finds solution for hotkey not working
- **WHEN** user's hotkey is not responding
- **THEN** the troubleshooting guide provides solutions for backend selection and permissions

#### Scenario: User finds solution for paste failures
- **WHEN** transcribed text is not pasting
- **THEN** the troubleshooting guide provides solutions for paste backend configuration and permissions

### Requirement: Troubleshooting uses flowchart format
The troubleshooting guide SHALL use flowchart-style decision trees to help users diagnose issues.

#### Scenario: User follows diagnostic flowchart
- **WHEN** user has an issue
- **THEN** they can follow a flowchart asking yes/no questions to narrow down the problem

#### Scenario: Flowchart leads to solution
- **WHEN** user completes a diagnostic flowchart
- **THEN** they arrive at a specific solution with actionable steps

### Requirement: FAQ answers frequently asked questions
The system SHALL provide an FAQ section answering common questions about features and usage.

#### Scenario: User finds answer about offline usage
- **WHEN** user wonders if DictaPilot works offline
- **THEN** the FAQ explains that it requires internet for Groq API but can use local whisper.cpp

#### Scenario: User finds answer about privacy
- **WHEN** user asks about data privacy
- **THEN** the FAQ explains what data is sent to APIs and what is stored locally

### Requirement: Troubleshooting includes diagnostic commands
The troubleshooting guide SHALL provide diagnostic commands users can run to check system status.

#### Scenario: User checks API connectivity
- **WHEN** user suspects API connection issues
- **THEN** the guide provides a command to test Groq API connectivity

#### Scenario: User checks audio device
- **WHEN** user suspects microphone issues
- **THEN** the guide provides a command to list available audio devices and test recording
