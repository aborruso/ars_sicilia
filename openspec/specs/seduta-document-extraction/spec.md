# seduta-document-extraction Specification

## Purpose
Complete extraction of all document types from ARS seduta pages, including provisional and stenographic minutes, session attachments, and agenda documents. Ensures historical archive completeness by capturing all 4 possible document types (OdG, resoconto provvisorio, resoconto stenografico, allegato) that track the legislative process lifecycle.
## Requirements
### Requirement: Extract All Document Types
The scraper SHALL extract URLs for all available document types from seduta pages:
- OdG e Comunicazioni (agenda and communications)
- Resoconto provvisorio (provisional minutes)
- Resoconto stenografico (stenographic minutes)
- Allegato alla seduta (session attachments)

#### Scenario: Seduta with all document types
**Given** a seduta page contains all 4 document types
**When** `extract_seduta_documents()` is called
**Then** it returns a dict with 4 non-null URLs: `odg_url`, `resoconto_provvisorio_url`, `resoconto_stenografico_url`, `allegato_url`

#### Scenario: Seduta with partial documents
**Given** a seduta page contains only OdG and provisional resoconto
**When** `extract_seduta_documents()` is called
**Then** it returns `odg_url` and `resoconto_provvisorio_url` as non-null, others as None

#### Scenario: Document pattern matching
**Given** HTML contains `<h3>Resoconto stenografico</h3><a href="/path/to/doc.pdf">LEGGI</a>`
**When** extraction logic runs
**Then** the PDF URL is correctly associated with `resoconto_stenografico_url`

### Requirement: Backward Compatible Resoconto URL
The scraper SHALL populate a backward-compatible `resoconto_url` field using this priority:
1. Stenographic resoconto URL (if present)
2. Provisional resoconto URL (if present)
3. None (if neither present)

#### Scenario: Both resoconti present
**Given** a seduta has both provisional and stenographic resoconti
**When** `extract_seduta_documents()` is called
**Then** `resoconto_url` equals `resoconto_stenografico_url`

#### Scenario: Only provisional resoconto present
**Given** a seduta has only provisional resoconto
**When** `extract_seduta_documents()` is called
**Then** `resoconto_url` equals `resoconto_provvisorio_url`

### Requirement: CSV Schema Extension
The anagrafica CSV SHALL include these new columns:
- `resoconto_provvisorio_url`
- `resoconto_stenografico_url`
- `allegato_url`

The deprecated `resoconto_url` column SHALL be maintained for backward compatibility.

#### Scenario: CSV schema migration
**Given** an existing anagrafica CSV without new columns
**When** `init_anagrafica_csv()` runs
**Then** the new columns are added with empty values for existing rows

#### Scenario: New seduta cataloging
**Given** a seduta with stenographic resoconto and allegato
**When** `save_seduta_to_anagrafica()` is called
**Then** the CSV row contains populated `resoconto_stenografico_url` and `allegato_url` columns

### Requirement: Document Detection Algorithm
The scraper SHALL use the following algorithm to extract document URLs:
1. Find all `<h3>`, `<p>`, and `<div>` elements containing document label text
2. For each matched element, search for adjacent `<a>` tags with PDF hrefs
3. Associate the URL with the correct document type based on label text matching:
   - "OdG e Comunicazioni" → `odg_url`
   - "Resoconto provvisorio" → `resoconto_provvisorio_url`
   - "Resoconto stenografico" → `resoconto_stenografico_url`
   - "Allegato alla seduta" → `allegato_url`
4. Normalize relative URLs to absolute (prepend `https://www.ars.sicilia.it` if needed)

#### Scenario: Link discovery from heading
**Given** HTML `<h3>OdG e Comunicazioni<a href="https://w3.ars.sicilia.it/doc.pdf">LEGGI</a></h3>`
**When** document detection runs
**Then** `odg_url` is set to `https://w3.ars.sicilia.it/doc.pdf`

#### Scenario: Relative URL normalization
**Given** a link `<a href="/DocumentiEsterni/ODG_PDF/doc.pdf">`
**When** URL is extracted
**Then** it is normalized to `https://www.ars.sicilia.it/DocumentiEsterni/ODG_PDF/doc.pdf`

