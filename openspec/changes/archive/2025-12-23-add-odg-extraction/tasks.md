# Implementation Tasks

## 1. Script Development
- [x] 1.1 Create `scripts/extract_odg_data.sh` with PDF URL extraction from CSV
- [x] 1.2 Implement deduplication logic (check processed PDFs in JSONL)
- [x] 1.3 Add markitdown + llm pipeline for each unprocessed PDF
- [x] 1.4 Generate `url_disegno` from `numero_disegno` and `legislatura`
- [x] 1.5 Append results to `data/disegni_legge.jsonl` in incremental mode

## 2. Testing
- [x] 2.1 Test script on sample PDF from seduta 219
- [x] 2.2 Verify deduplication (re-run script should skip processed PDFs)
- [x] 2.3 Validate JSONL output format and field completeness
- [x] 2.4 Check generated ICARO URLs are valid

## 3. Documentation
- [x] 3.1 Add usage instructions to script header comments
- [x] 3.2 Update `LOG.md` with change summary
