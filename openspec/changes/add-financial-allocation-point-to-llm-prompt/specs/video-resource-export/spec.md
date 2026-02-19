## MODIFIED Requirements

### Requirement: export-text-formatting

Export text MUST be human-readable, scannable by LLM, and include: metadata header (seduta number, date, time, duration), labeled section headers with emoji, direct absolute URLs (no shortened links), and category list from digest (if available). The summary instructions MUST explicitly ask to report funded interventions/projects and the financial resources allocated for each intervention when data is available in the provided resources.

#### Scenario: video with all resources available

- **WHEN** the user copies the export text for a video where transcript and agenda include references to funding decisions
- **THEN** the exported prompt includes an explicit instruction to indicate allocated financial resources per intervention when available
- **AND** all existing formatting sections remain present and usable

#### Scenario: no funding amounts in available sources

- **WHEN** the provided transcript/agenda do not include explicit amounts or funding details
- **THEN** the prompt still requests funding information conditionally ("when available")
- **AND** the summary can omit amounts without violating prompt constraints
