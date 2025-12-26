## MODIFIED Requirements
### Requirement: Anagrafica CSV Duration Column
The anagrafica CSV SHALL include a `duration_minutes` column to store video duration and a `no_transcript` column to flag videos without spoken content.

#### Scenario: CSV schema migration
**Given** an existing anagrafica CSV without `duration_minutes` and `no_transcript` columns
**When** `init_anagrafica_csv()` runs
**Then** both columns are added with empty values for existing rows

#### Scenario: New video cataloging with duration
**Given** a video is downloaded and duration extracted
**When** `save_seduta_to_anagrafica()` is called
**Then** the CSV row contains the `duration_minutes` value and `no_transcript` is empty (not yet checked)

#### Scenario: Video cataloging without download
**Given** a seduta is cataloged without downloading videos
**When** `save_seduta_to_anagrafica()` is called
**Then** `duration_minutes` and `no_transcript` are set to empty string (not yet known)

#### Scenario: Video marked as no transcript
**Given** digest generation detects empty transcript for a video
**When** the CSV is updated
**Then** `no_transcript` is set to `true` for that video row
