## ADDED Requirements
### Requirement: Description updater tool
The system SHALL provide a script that updates YouTube descriptions for videos missing the seduta token, based on anagrafica data.

#### Scenario: Missing token in description
- **WHEN** a video description does not contain the seduta token
- **THEN** the script updates the description to include the token and updated search link

### Requirement: Dry-run mode
The description updater SHALL support a dry-run mode that prints planned changes without calling the YouTube API.

#### Scenario: Dry-run execution
- **WHEN** the script is executed with `--dry-run`
- **THEN** no API updates are performed and planned changes are logged
