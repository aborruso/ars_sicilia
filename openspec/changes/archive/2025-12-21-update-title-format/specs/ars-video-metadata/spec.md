## ADDED Requirements
### Requirement: YouTube title format
The system SHALL publish videos with titles that include the seduta number, seduta date, and recording date/time.

#### Scenario: Recording date differs from seduta date
- **WHEN** a video recording date differs from the seduta date
- **THEN** the title shows the seduta date and separately shows the recording date/time

#### Scenario: Recording date equals seduta date
- **WHEN** the recording date equals the seduta date
- **THEN** the title still shows the seduta date and recording date/time in the standard format
