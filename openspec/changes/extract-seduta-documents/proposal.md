# Extract All Seduta Documents

## Why
ARS seduta pages publish multiple document types that track the legislative process lifecycle. Currently, the scraper only captures 2 of 4 possible documents, missing critical information:

- **Resoconto stenografico** (final stenographic minutes) replaces the provisional version but both may coexist temporarily
- **Allegato alla seduta** (session attachments) contains supplementary materials referenced during proceedings

This incomplete extraction creates gaps in the historical archive and limits metadata quality for YouTube videos. Users searching for complete legislative records cannot access all available documents through our system.

Chrome DevTools analysis confirms all 4 document types follow consistent HTML patterns (`<h3>` labels + adjacent `<a>` tags with PDF links), making extraction straightforward.

## Summary
Extend the scraper to extract all available document URLs from seduta pages, including "Resoconto stenografico" (stenographic minutes) and "Allegato alla seduta" (session attachments), in addition to the currently extracted "OdG e Comunicazioni" and "Resoconto provvisorio".

## Problem Statement
The current scraper extracts only two document types from seduta pages:
- `odg_url`: "OdG e Comunicazioni" (agenda and communications)
- `resoconto_url`: "Resoconto provvisorio" (provisional minutes) **OR** "Resoconto stenografico" (stenographic minutes)

However, seduta pages can contain up to 4 different document types:
1. **OdG e Comunicazioni** (always present)
2. **Resoconto provvisorio** (provisional minutes - appears first, temporary)
3. **Resoconto stenografico** (stenographic minutes - appears later, replaces provisional)
4. **Allegato alla seduta** (session attachments - optional, when present)

**Current behavior:**
- The scraper only captures the first resoconto it finds (provisional or stenographic)
- "Allegato alla seduta" is never extracted
- When a seduta has both provisional and stenographic resoconti, only one is captured

**Expected behavior:**
- Extract all 4 document types separately
- Store both provisional and stenographic resoconti when present
- Include session attachments when available
- Maintain backward compatibility with existing CSV structure

## Use Cases
1. **Historical archive completeness**: Users need access to both provisional and final stenographic minutes
2. **Session attachments**: Important supplementary documents are currently ignored
3. **Data analysis**: Researchers need complete document sets for legislative analysis
4. **YouTube metadata**: Video descriptions can link to all available documents

## Proposed Changes
Modify the document extraction logic to:
1. Parse seduta pages for all 4 document type patterns
2. Add new CSV columns: `resoconto_provvisorio_url`, `resoconto_stenografico_url`, `allegato_url`
3. Deprecate generic `resoconto_url` but maintain for backward compatibility
4. Update metadata builder to include all documents in YouTube descriptions

## Success Criteria
- All 4 document types extracted correctly from test sedute (158, 217)
- Backward compatibility: existing workflows continue to function
- CSV schema migration: old data preserved, new columns added
- YouTube descriptions include all available document links

## Out of Scope
- PDF content extraction or analysis
- Document version tracking over time
- Automated detection of document publication dates

## Dependencies
None - this is an isolated enhancement to the scraper module.

## Risks
- **CSV schema change**: Existing tools reading anagrafica_video.csv may need updates
- **Data migration**: Historical records lack new columns (acceptable - will be NULL)

## Mitigation
- Keep deprecated `resoconto_url` column populated with stenographic URL (preferred) or provisional URL (fallback)
- Document CSV schema changes in README and migration guide
- Phase rollout: scraper first, then metadata, then analytics tools
