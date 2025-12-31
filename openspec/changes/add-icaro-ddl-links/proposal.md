# Change: Add DDL links extraction in ARS API client

## Why
Serve a machine-to-machine way to extract attachments/emendamenti links from a DDL page without browser automation.

## What Changes
- Add a new ARS client method to accept a DDL URL, resolve `icaQueryId`, and parse link arrays for allegati/emendamenti.
- Document the method with a minimal usage example.

## Impact
- Affected specs: `ars-icaro-links` (new capability)
- Affected code: `ars_sicilia_api/ars_api_client.py`, `ars_sicilia_api/API_DOCUMENTATION.md`, `ars_sicilia_api/examples.py`

## Notes (example + parsing)
- Example DDL URL: `https://dati.ars.sicilia.it/icaro/default.jsp?icaDB=221&icaQuery=(18.LEGISL+E+1029.NUMDDL)`
- The page loads content via AJAX at:
  `https://dati.ars.sicilia.it/icaro/doc221-1.jsp?icaQueryId=<id>&icaDocId=1`
- `icaQueryId` is shown in the footer of `default.jsp` as `QRY<id>`.
- Parse the AJAX HTML for link text:
  - Allegati: anchor text contains `Vedi Atti Allegati`
  - Emendamenti: anchor text contains `Vedi Fascicolo`
- Normalize scheme-less links (e.g., `//w3.ars.sicilia.it/...`) to absolute HTTPS.
