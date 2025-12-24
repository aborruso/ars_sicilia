# Tasks

## Phase 1: Scraper Enhancement
1. **Update `extract_seduta_documents()` in `src/scraper.py`**
   - Replace simple pattern matching with structured document detection
   - Extract all 4 document types: OdG, provisional resoconto, stenographic resoconto, allegato
   - Return dict with keys: `odg_url`, `resoconto_provvisorio_url`, `resoconto_stenografico_url`, `allegato_url`
   - Maintain backward-compatible `resoconto_url` (preferring stenographic over provisional)
   - **Validation**: Test against seduta 158 (has stenographic + allegato) and 217 (has provisional + allegato)

2. **Update CSV schema in `build_anagrafica.py`**
   - Add new columns to `init_anagrafica_csv()`: `resoconto_provvisorio_url`, `resoconto_stenografico_url`, `allegato_url`
   - Update `save_seduta_to_anagrafica()` to write all document URLs
   - Ensure existing `resoconto_url` column is populated for backward compatibility
   - **Validation**: Run build_anagrafica.py and verify CSV has new columns

3. **Update anagrafica field handling in `upload_single.py`**
   - Ensure script handles new CSV columns gracefully
   - Pass all document URLs to metadata builder
   - **Validation**: Dry-run upload on seduta with all documents present

## Phase 2: Metadata Integration
4. **Update `build_youtube_metadata()` in `src/metadata.py`**
   - Modify description template to include all available documents
   - Add conditional sections for provisional/stenographic resoconti
   - Include allegato link when present
   - **Validation**: Generate metadata for test sedute, verify description formatting

5. **Update description template**
   - Add emoji/labels for document types (📄 OdG, 📝 Resoconto provvisorio, 📋 Resoconto stenografico, 📎 Allegato)
   - Maintain backward compatibility with existing description format
   - **Validation**: Check description length stays under YouTube 5000 char limit

## Phase 3: Documentation & Migration
6. **Document CSV schema changes**
   - Update README.md with new column descriptions
   - Add migration notes for users/tools reading anagrafica_video.csv
   - Note that `resoconto_url` is deprecated but maintained
   - **Validation**: Review documentation for clarity

7. **Update viewer (optional)**
   - Modify `viewer/index.html` to display all document types
   - Add badges/icons for document availability
   - **Validation**: Load viewer with updated CSV, verify UI

## Validation Checklist
- [ ] Scraper extracts all 4 documents from seduta 158
- [ ] Scraper extracts all 4 documents from seduta 217
- [ ] CSV has new columns with correct URLs
- [ ] Old `resoconto_url` populated correctly
- [ ] YouTube metadata includes all documents
- [ ] Description format readable and under limit
- [ ] Viewer displays new document types
- [ ] No breakage in upload_single.py workflow

## Dependencies
- Tasks 1-3 can run in parallel
- Task 4-5 depend on Task 1 (scraper changes)
- Task 6-7 can run anytime after Task 2 (CSV changes)

## Rollback Plan
If issues arise:
1. Revert scraper changes to return only 2 URLs
2. Remove new CSV columns (data loss acceptable)
3. Restore original metadata template
