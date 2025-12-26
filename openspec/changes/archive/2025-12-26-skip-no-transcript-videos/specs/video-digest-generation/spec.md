## ADDED Requirements
### Requirement: Video Transcript Download
The digest generation script SHALL download video transcripts using `qv` (yt-dlp wrapper) before processing.

#### Scenario: Successful transcript download
**Given** a YouTube video has spoken content with auto-generated captions
**When** `qv "https://youtu.be/$youtube_id" --text-only` is executed
**Then** a text transcript is saved to a temporary file

#### Scenario: Video without transcript
**Given** a YouTube video has no spoken content (silent video, technical interruption)
**When** `qv` attempts to download transcript
**Then** an empty or very small file (<100 bytes) is returned

### Requirement: Empty Transcript Detection
The script SHALL detect videos without meaningful transcript content and mark them accordingly.

#### Scenario: Transcript too small
**Given** `qv` downloads a transcript file of 45 bytes
**When** transcript size is checked (threshold: 100 bytes)
**Then** the video is marked as `no_transcript=true` in anagrafica CSV
**And** the video is NOT counted as failed
**And** a log entry "SKIP: $youtube_id (no transcript, <100 bytes)" is written

#### Scenario: Completely empty transcript
**Given** `qv` creates a 0-byte transcript file
**When** transcript size is checked
**Then** the video is marked as `no_transcript=true`
**And** skipped as above

#### Scenario: Valid transcript size
**Given** `qv` downloads a transcript file of 8500 bytes
**When** transcript size is checked
**Then** processing continues to digest generation

### Requirement: Skip Previously Marked Videos
The script SHALL skip digest generation for videos already marked as `no_transcript=true`.

#### Scenario: Skip on subsequent run
**Given** anagrafica has a video with `no_transcript=true`
**When** `generate_digests.sh` processes the CSV
**Then** the video is skipped before attempting download
**And** a log entry "SKIP: $youtube_id (no transcript flagged)" is written
**And** the skipped counter is incremented

### Requirement: Separate Counters for No-Transcript Videos
The script SHALL maintain separate counters for skipped (no-transcript) vs failed (error) videos.

#### Scenario: Summary with no-transcript videos
**Given** a run processes 10 videos: 5 generated, 2 already exist, 2 no-transcript, 1 failed
**When** the final summary is logged
**Then** output shows:
- `Generati: 5`
- `Skipped (già esistenti): 2`
- `Skipped (no transcript): 2`
- `Falliti: 1`

### Requirement: Preserve Existing Digest Files
The script SHALL NOT overwrite or regenerate digests for videos already marked `no_transcript=true`.

#### Scenario: Digest file exists but video is no-transcript
**Given** a video has `no_transcript=true` but a digest JSON file exists (legacy data)
**When** the script runs
**Then** the existing digest is preserved (not deleted)
**And** the video is skipped
