# Tasks

## Phase 1: Schema Extension + Download Integration

1. **Add `duration_minutes` column to CSV schema**
   - Update `init_anagrafica_csv()` in `scripts/build_anagrafica.py`
   - Add `'duration_minutes'` to `required_fields` list (line 43-61)
   - Ensure schema migration adds column with empty values for existing rows (lines 70-91)
   - **Validation**: Run `build_anagrafica.py`, verify CSV has `duration_minutes` column

2. **Extend downloader to extract duration from yt-dlp**
   - Modify `download_video()` in `src/downloader.py`
   - Add `--dump-json --no-download` call after successful download
   - Parse JSON output for `duration` field (seconds)
   - Convert to minutes: `round(duration / 60)` (handle 0-minute edge case)
   - Update return signature from `bool` to `tuple[bool, Optional[int]]`
   - Log warnings when duration extraction fails
   - **Validation**: Test download on known video, verify duration extracted correctly

3. **Update upload script to capture duration**
   - Modify `scripts/main.py` to unpack `(success, duration_mins)` from `download_video()`
   - Pass `duration_mins` to CSV update logic (where `youtube_id` is written)
   - Only update duration on upload success (preserve empty on failure)
   - **Validation**: Dry-run upload, verify duration written to CSV

4. **Extend anagrafica preservation logic for duration**
   - Update `get_existing_youtube_ids()` in `scripts/build_anagrafica.py`
   - Add `'duration_minutes'` to fields extracted from existing rows (lines 157-161)
   - Update `save_seduta_to_anagrafica()` to preserve duration when re-crawling (lines 245-270)
   - **Validation**: Manually edit duration value, re-run `build_anagrafica.py`, verify preserved

## Phase 2: Backfill Existing Uploads

5. **Create `scripts/backfill_durations.py`**
   - Read `anagrafica_video.csv`
   - Filter rows: `youtube_id != '' AND duration_minutes == ''`
   - Batch video IDs into groups of 50 (YouTube API limit)
   - Call `youtube.videos().list(part='contentDetails', id='...')` per batch
   - Parse ISO 8601 duration from `contentDetails.duration` (e.g., `PT1H23M45S`)
   - Convert to minutes using regex or `isodate` library
   - Update CSV rows with fetched durations
   - Log API quota consumption and errors
   - **Validation**: Test on 5-10 videos, verify durations match YouTube UI

6. **Add ISO 8601 duration parsing**
   - Option A: Add `isodate` to `requirements.txt` (simple but new dependency)
   - Option B: Implement regex parser `parse_iso_duration()` (no new deps)
   - Handle edge cases: videos <1 minute, missing hours/minutes components
   - **Validation**: Test `PT45S` → 1, `PT1H23M` → 83, `PT2H` → 120

7. **Run backfill script on production anagrafica**
   - Backup `data/anagrafica_video.csv` before running
   - Execute `python3 scripts/backfill_durations.py`
   - Verify ~200 rows updated with duration values
   - Check API quota usage (<10 units expected)
   - **Validation**: Spot-check 5 random videos against YouTube UI durations

## Phase 3: Optional Enhancements

8. **Update viewer to display duration (optional)**
   - Modify `viewer/index.html` to show `duration_minutes` in video cards
   - Format as "Durata: XX minuti" or "XX min"
   - Add filtering UI for duration ranges (e.g., "<30 min", "30-60 min", ">60 min")
   - **Validation**: Load viewer, verify duration visible and filters work

9. **Add duration to YouTube descriptions (optional)**
   - Update `build_youtube_metadata()` in `src/metadata.py`
   - Add line: `Durata: {duration_minutes} minuti` to description template
   - Only include if duration is available (handle empty gracefully)
   - **Validation**: Generate metadata for test video, verify description formatting

## Validation Checklist

- [x] CSV schema includes `duration_minutes` column
- [x] New downloads extract duration via yt-dlp
- [x] Duration stored as rounded minutes (integer)
- [x] Re-crawl preserves existing duration values
- [x] Backfill script fetches YouTube durations via API
- [x] Backfill API quota <10 units for ~200 videos
- [ ] Viewer displays duration (if implemented)
- [ ] YouTube description includes duration (if implemented)

## Dependencies

- Tasks 1-4 must complete before Phase 2 (backfill needs CSV schema)
- Tasks 5-7 can run in parallel with Tasks 8-9
- Task 6 must complete before Task 7 (parsing needed for backfill)
- Tasks 8-9 are independent optional enhancements

## Rollback Plan

If issues arise:
1. Remove `duration_minutes` column from CSV (data loss acceptable)
2. Revert `download_video()` return signature to `bool`
3. Delete `scripts/backfill_durations.py`
4. Revert `build_anagrafica.py` changes to required_fields and preservation logic

## Estimated Work

- Phase 1: ~2-3 hours (schema + download integration)
- Phase 2: ~1-2 hours (backfill script + execution)
- Phase 3: ~1 hour (viewer/metadata optional)

**Total: 4-6 hours**

Low complexity change - extends existing patterns (CSV columns, yt-dlp metadata extraction, YouTube API batch queries).
