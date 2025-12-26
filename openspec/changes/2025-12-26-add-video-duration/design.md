# Design: Video Duration Tracking

## Architecture Overview

The duration tracking feature integrates with three existing pipeline phases:

```
1. Catalog (build_anagrafica.py)
   ↓
2. Download (src/downloader.py)  ← Extract duration from yt-dlp
   ↓
3. Upload (scripts/main.py)
   ↓
4. Backfill (NEW: scripts/backfill_durations.py) ← Fetch YouTube durations
```

## Component Changes

### 1. CSV Schema (`build_anagrafica.py`)

**Current schema:**
```
numero_seduta,data_seduta,url_pagina,odg_url,...,youtube_id,last_check,status,failure_reason
```

**New schema:**
```
numero_seduta,data_seduta,url_pagina,odg_url,...,youtube_id,last_check,status,failure_reason,duration_minutes
```

**Migration strategy:**
- `init_anagrafica_csv()` adds `duration_minutes` to required_fields list
- Existing rows get empty `duration_minutes` on first run
- Schema migration uses same pattern as previous column additions (see lines 70-91)

**Preservation logic:**
When re-crawling sedute (e.g., recent sedute within 14 days):
- Load existing row data via `get_existing_youtube_ids()` (extended to include duration)
- Pass existing duration to `save_seduta_to_anagrafica()`
- Write preserved duration value (lines 245-270)

### 2. Downloader (`src/downloader.py`)

**Current approach:**
- Calls `yt-dlp` with `-o output_path` for direct download
- No metadata extraction

**New approach:**
- Add `--dump-json` flag to extract metadata without re-downloading
- Parse JSON output for `duration` field (seconds)
- Convert to minutes: `round(duration / 60)`
- Return duration alongside download success status

**Code changes:**
```python
def download_video(...) -> tuple[bool, Optional[int]]:
    # Existing download logic (unchanged)
    success = subprocess.run(['yt-dlp', ...])

    # NEW: Extract duration
    duration_mins = None
    try:
        result = subprocess.run(
            ['yt-dlp', '--dump-json', '--no-download', video_url],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            metadata = json.loads(result.stdout)
            duration_secs = metadata.get('duration')
            if duration_secs:
                duration_mins = round(duration_secs / 60)
    except Exception as e:
        print(f"  ⚠ Duration extraction failed: {e}")

    return success, duration_mins
```

**Why `--dump-json` instead of `--write-info-json`?**
- `--dump-json` prints JSON to stdout (no file I/O)
- `--write-info-json` writes `.info.json` file (requires cleanup)
- `--no-download` prevents re-downloading when only metadata needed

**Performance impact:**
- Adds ~1-2 seconds per video (metadata fetch only)
- Acceptable for pipeline (already waits minutes for download)

### 3. Upload Script (`scripts/main.py`)

**Current flow:**
```python
# Read anagrafica row
video_url = row['video_page_url']

# Download
success = download_video(video_url, temp_file)

# Upload to YouTube
upload_to_youtube(temp_file, metadata)

# Update anagrafica status
update_status(youtube_id, 'success')
```

**Updated flow:**
```python
# Download with duration extraction
success, duration_mins = download_video(video_url, temp_file)

# Upload to YouTube (unchanged)
upload_to_youtube(temp_file, metadata)

# Update anagrafica with status AND duration
update_status(youtube_id, 'success', duration_mins)
```

**Changes required:**
- Modify `download_video()` return signature
- Pass `duration_mins` to CSV update logic
- Update only if upload succeeds (preserve empty duration on failures)

### 4. Backfill Script (`scripts/backfill_durations.py`)

**Purpose:** Populate `duration_minutes` for videos already uploaded to YouTube.

**Algorithm:**
1. Read anagrafica CSV
2. Filter rows: `youtube_id IS NOT NULL AND duration_minutes IS NULL`
3. Batch video IDs (50 per API call - YouTube Data API limit)
4. Call `youtube.videos().list(part='contentDetails', id='id1,id2,...')`
5. Parse ISO 8601 duration (`PT1H23M45S`) → minutes
6. Update anagrafica CSV with duration values

**API cost analysis:**
- ~200 existing videos in anagrafica
- Batch size: 50 IDs per call
- API calls needed: 200 / 50 = 4 calls
- Cost per call: 1 unit (videos.list with minimal parts)
- Total quota: ~4 units (negligible, daily quota = 10,000)

**Dependencies:**
- `google-api-python-client` (already installed)
- OAuth token (`config/token.json`)
- ISO 8601 duration parsing (use `isodate` library or regex)

**Error handling:**
- Skip videos not found on YouTube (deleted/private)
- Log API errors but continue processing remaining batches
- Update CSV incrementally (partial success is acceptable)

**Example ISO 8601 parsing:**
```python
import re

def parse_iso_duration(iso_str: str) -> int:
    """Convert PT1H23M45S to minutes (rounded)."""
    # PT1H23M45S → 1*60 + 23 + 45/60 = 83.75 → 84 minutes
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso_str)
    h = int(match.group(1) or 0)
    m = int(match.group(2) or 0)
    s = int(match.group(3) or 0)
    return round(h * 60 + m + s / 60)
```

## Data Flow

```
[ARS Website]
      ↓
[build_anagrafica.py] → anagrafica.csv (duration=empty)
      ↓
[main.py: download_video()] → extract duration from yt-dlp
      ↓
[main.py: update CSV] → anagrafica.csv (duration=45)
      ↓
[YouTube upload]
      ↓
[backfill_durations.py] → fetch duration for old uploads → anagrafica.csv (backfill)
```

## Alternative Approaches Considered

### Alt 1: Store duration in seconds (not minutes)
**Rejected:** User explicitly requested minutes, rounded to integer.
**Trade-off:** Lose precision, but sufficient for stated use cases (analytics, filtering).

### Alt 2: Extract duration during catalog phase (build_anagrafica)
**Rejected:** Catalog phase intentionally avoids downloads/streams to remain fast.
**Trade-off:** Duration requires accessing video metadata (yt-dlp or API call), not available from seduta HTML.

### Alt 3: Store duration only in YouTube metadata (not CSV)
**Rejected:** Requires API call to query duration; CSV should be self-contained catalog.
**Trade-off:** Adds API dependency for basic queries.

### Alt 4: Use FFmpeg/MediaInfo on downloaded file
**Rejected:** Requires downloading entire video first; yt-dlp metadata is faster.
**Trade-off:** 100% accurate post-download, but adds processing overhead.

## Testing Strategy

### Unit Tests (if added later)
- `test_parse_iso_duration()`: Verify PT1H23M45S → 84
- `test_round_duration()`: Verify 63.08 → 63, 0.75 → 1

### Integration Tests
1. **New video download:**
   - Run `main.py` on test seduta
   - Verify `duration_minutes` populated in CSV
   - Check value matches YouTube upload duration

2. **Backfill existing uploads:**
   - Run `backfill_durations.py` on test anagrafica
   - Verify durations fetched from YouTube API
   - Check API quota consumption (<10 units)

3. **Re-crawl preservation:**
   - Edit seduta 220 row (set duration=99)
   - Run `build_anagrafica.py` (triggers recent seduta refresh)
   - Verify duration=99 preserved (not overwritten)

### Validation Checklist
- [ ] CSV schema includes `duration_minutes` column
- [ ] `download_video()` returns tuple `(bool, Optional[int])`
- [ ] New downloads populate duration in CSV
- [ ] Backfill script fetches durations from YouTube API
- [ ] Re-crawl preserves existing duration values
- [ ] Viewer displays duration (optional Phase 3)

## Rollback Plan

If issues arise:
1. Remove `duration_minutes` column from CSV (data loss acceptable)
2. Revert `download_video()` return signature to `bool`
3. Delete `backfill_durations.py` script
4. No YouTube metadata changes (none made)

Low risk change - purely additive to CSV schema and download metadata extraction.
