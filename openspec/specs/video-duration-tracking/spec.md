# video-duration-tracking Specification

## Purpose
Track video duration metadata in the anagrafica CSV to enable analytics, filtering, and no-transcript detection. Duration is extracted from yt-dlp during download and backfilled via YouTube API for already-uploaded videos.
## Requirements
### Requirement: Extract Duration from yt-dlp Metadata
The downloader SHALL extract video duration from yt-dlp JSON metadata during the download phase.

#### Scenario: Duration extraction via --dump-json
**Given** a video is being downloaded via yt-dlp
**When** `download_video()` calls `yt-dlp --dump-json`
**Then** the duration in seconds is extracted from the `duration` field in the JSON output

#### Scenario: Missing duration metadata
**Given** yt-dlp metadata lacks a `duration` field
**When** extraction runs
**Then** duration is set to `None` and logged as a warning

#### Scenario: Non-numeric duration
**Given** yt-dlp returns invalid duration metadata (e.g., non-numeric)
**When** extraction runs
**Then** duration is set to `None` and logged as an error

### Requirement: Store Duration in Minutes (Rounded)
The system SHALL store video duration in the anagrafica CSV as integer minutes (rounded from seconds).

#### Scenario: Duration conversion
**Given** yt-dlp reports duration as 3785 seconds (63.08 minutes)
**When** duration is stored
**Then** `duration_minutes` is set to `63` (rounded to nearest integer)

#### Scenario: Duration under 1 minute
**Given** yt-dlp reports duration as 45 seconds
**When** duration is stored
**Then** `duration_minutes` is set to `1` (rounded up from 0.75)

#### Scenario: Very short videos
**Given** yt-dlp reports duration as 5 seconds
**When** duration is stored
**Then** `duration_minutes` is set to `0` (rounded down from 0.08)

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

### Requirement: Backfill Duration from YouTube API
The system SHALL provide a script to backfill duration for videos already uploaded to YouTube.

#### Scenario: Batch fetch durations
**Given** 200 videos in anagrafica have `youtube_id` but missing `duration_minutes`
**When** `scripts/backfill_durations.py` runs
**Then** it fetches durations via YouTube Data API v3 `videos.list` (batch up to 50 IDs per call)
**And** updates anagrafica CSV with rounded minute values

#### Scenario: API quota management
**Given** YouTube Data API quota is limited
**When** backfill script runs
**Then** it batches requests (50 videos per API call, ~1 unit cost per call)
**And** logs quota consumption

#### Scenario: Missing YouTube uploads
**Given** an anagrafica row has no `youtube_id` (not yet uploaded)
**When** backfill script runs
**Then** duration remains empty and row is skipped

### Requirement: Duration Preservation on Re-crawl
The system SHALL preserve existing `duration_minutes` values when re-crawling sedute.

#### Scenario: Seduta re-crawl with duration
**Given** a seduta row has `duration_minutes=45`
**When** `build_anagrafica.py` re-crawls the seduta (e.g., recent seduta refresh)
**Then** `duration_minutes=45` is preserved (not overwritten with empty value)

#### Scenario: Seduta re-crawl without duration
**Given** a seduta row has empty `duration_minutes`
**When** re-crawl happens and video has not been downloaded yet
**Then** `duration_minutes` remains empty

