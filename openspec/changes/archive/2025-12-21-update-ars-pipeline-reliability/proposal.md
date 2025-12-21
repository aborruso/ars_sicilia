# Change: Improve ARS pipeline reliability and data integrity

## Why
The current pipeline works end-to-end but has a few reliability gaps (timeouts, directory creation) and data integrity issues (timezone handling, dedup keys, latest seduta selection). These changes reduce upload failures and prevent subtle data drift in logs/anagrafica.

## What Changes
- Use configurable HTTP timeouts/retries for scraping instead of hardcoded values.
- Ensure download output directories exist before invoking `yt-dlp`.
- Make recording date timezone-aware (Europe/Rome) to avoid incorrect UTC timestamps.
- Strengthen deduplication keys in logs/anagrafica to avoid collisions across dates/legislature.
- Select the most recent seduta URL deterministically when no URL is provided.
- Enforce `start_date` filter during anagrafica crawl to avoid stale/older sedute.

## Impact
- Affected specs: `ars-video-pipeline`
- Affected code: `src/scraper.py`, `src/downloader.py`, `src/metadata.py`, `src/logger.py`, `build_anagrafica.py`, `main.py`, `config/config.yaml`
