# Add Video Duration to Anagrafica

## Why
The current anagrafica (video catalog CSV) lacks duration metadata, making it difficult to:
- Estimate total archive size or storage requirements
- Filter/query videos by length for analytical purposes
- Provide users with duration information before viewing
- Track the typical length of legislative sessions over time

Video duration is a fundamental metadata attribute that should be captured during the download phase using `yt-dlp`, which extracts this information natively from the source streams. This avoids additional API calls and provides immediate visibility into video characteristics.

User request: store video duration in minutes (rounded to integer) in the anagrafica CSV.

## Summary
Capture video duration during download phase using `yt-dlp` metadata extraction, store duration in minutes (rounded) in `anagrafica_video.csv`, and backfill existing YouTube uploads via API batch query.

## Problem Statement
The current system extracts extensive metadata (numero_seduta, data_seduta, documents, youtube_id, status) but missing duration creates gaps:

**Current behavior:**
- Videos are downloaded via `yt-dlp` which extracts duration from stream metadata
- Duration is not captured or stored in anagrafica CSV
- No visibility into video length in catalog queries
- No duration metadata for analytics or filtering

**Expected behavior:**
- Extract duration during download via `yt-dlp --dump-json`
- Store duration in minutes (rounded to integer) in new `duration_minutes` column
- Backfill duration for existing YouTube uploads via YouTube Data API v3
- Update build_anagrafica.py to preserve duration on re-crawls

## Use Cases
1. **Archive analytics**: Calculate total hours of legislative footage archived
2. **User queries**: Filter videos by duration (e.g., "sessions under 30 minutes")
3. **Storage planning**: Estimate bandwidth/storage from duration metadata
4. **Viewer UX**: Display video length in viewer interface before playback
5. **Historical trends**: Analyze how session lengths change over time

## Proposed Changes
1. Extend `src/downloader.py` to extract duration from yt-dlp JSON metadata
2. Add `duration_minutes` column to anagrafica CSV schema
3. Update `build_anagrafica.py` to initialize and preserve duration column
4. Create `scripts/backfill_durations.py` to fetch duration for existing YouTube uploads
5. Update `src/metadata.py` to optionally include duration in YouTube descriptions (future enhancement)

## Implementation Strategy
- **Phase 1**: Schema + download extraction (new videos get duration immediately)
- **Phase 2**: Backfill script for existing uploads (~200 videos, single API batch call)
- **Phase 3**: Optional viewer/analytics integration

## Non-Goals
- Extracting exact seconds precision (minutes rounded to integer is sufficient per user request)
- Modifying YouTube metadata to include duration (already visible in YouTube UI)
- Real-time duration calculation during upload (rely on pre-download extraction)
