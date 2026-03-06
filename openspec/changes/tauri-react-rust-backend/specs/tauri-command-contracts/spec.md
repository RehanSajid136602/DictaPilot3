## ADDED Requirements

### Requirement: Frontend-backend contracts are typed and versioned
Shared contracts SHALL define request/response payloads, event payloads, and error models for all Tauri commands.

#### Scenario: Frontend invokes typed command
- **WHEN** frontend sends a valid command payload
- **THEN** backend accepts it and returns a response matching the shared contract shape

#### Scenario: Payload validation fails
- **WHEN** payload is missing required fields
- **THEN** backend rejects command with contract-compliant validation error

### Requirement: Contract changes are compatibility-checked
Contract evolution SHALL include explicit versioning and compatibility checks in CI/tests.

#### Scenario: Breaking contract change introduced
- **WHEN** a command response removes required fields
- **THEN** compatibility test fails and blocks merge until version/update strategy is applied
