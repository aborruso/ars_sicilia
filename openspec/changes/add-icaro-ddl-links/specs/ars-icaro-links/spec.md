## ADDED Requirements
### Requirement: Extract DDL links from ICARO page
The ARS API client SHALL expose a method `get_ddl_links(url)` that accepts a DDL ICARO URL and returns:
- the resolved `icaQueryId`
- `allegati_urls` as an array of absolute URLs
- `emendamenti_urls` as an array of absolute URLs

#### Scenario: DDL page includes allegati and emendamenti links
- **WHEN** `get_ddl_links(url)` is called with a valid DDL ICARO URL
- **THEN** it returns a non-null `icaQueryId`
- **AND** `allegati_urls` includes the attachment links
- **AND** `emendamenti_urls` includes the emendamenti/fascicolo links

#### Scenario: DDL page has no allegati or emendamenti
- **WHEN** `get_ddl_links(url)` is called with a DDL ICARO URL lacking those links
- **THEN** it returns empty arrays for the missing link types
- **AND** still returns the `icaQueryId` if available
