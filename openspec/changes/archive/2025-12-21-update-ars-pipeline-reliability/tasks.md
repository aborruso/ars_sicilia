## Implementation
- [x] 1.1 Add configurable HTTP timeout/retry handling to scraping layer
- [x] 1.2 Ensure download temp directory exists before download
- [x] 1.3 Make recordingDate timezone-aware using configured timezone
- [x] 1.4 Strengthen deduplication key in log/anagrafica and update checks
- [x] 1.5 Improve latest-seduta selection logic in `main.py`
- [x] 1.6 Apply `start_date` filter during anagrafica crawl

## Validation
- [x] 2.1 Run `build_anagrafica.py` smoke check
- [x] 2.2 Run `test_upload_single.py --dry-run`
