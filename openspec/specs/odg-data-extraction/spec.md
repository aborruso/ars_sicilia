# odg-data-extraction Specification

## Purpose
Extract structured legislative bill data from seduta agenda PDFs (Ordine del Giorno) using PDF-to-text conversion and LLM-based parsing. Outputs deduped JSONL records for historical archiving and linkage to videos.
## Requirements
### Requirement: Estrazione dati da PDF OdG
Il sistema SHALL estrarre dai PDF OdG i seguenti campi per ogni disegno di legge: `titolo_disegno`, `numero_disegno` (solo parte numerica), `legislatura` (numero romano), `data_ora` (formato ISO 8601).

#### Scenario: PDF OdG valido con disegni
- **WHEN** il PDF OdG contiene uno o più disegni di legge
- **THEN** il sistema estrae tutti i disegni in formato JSON multi-item con i campi richiesti

#### Scenario: PDF OdG senza disegni
- **WHEN** il PDF OdG non contiene disegni di legge
- **THEN** il sistema restituisce un array vuoto `{"items": []}`

### Requirement: Deduplicazione PDF processati
Il sistema SHALL elaborare ogni PDF OdG una sola volta, tracciando quali URL sono già stati processati.

#### Scenario: PDF già elaborato
- **WHEN** un PDF OdG è già presente nel JSONL output
- **THEN** il sistema salta l'elaborazione e passa al successivo

#### Scenario: Nuovo PDF OdG
- **WHEN** un PDF OdG non è stato ancora processato
- **THEN** il sistema lo elabora ed aggiunge i risultati al JSONL

### Requirement: Archiviazione JSONL incrementale
Il sistema SHALL salvare i dati estratti in `data/disegni_legge.jsonl` in modalità append, aggiungendo i campi `pdf_url` e `url_disegno`.

#### Scenario: Append dati estratti
- **WHEN** nuovi disegni vengono estratti da un PDF
- **THEN** ogni disegno viene aggiunto come riga JSONL con `pdf_url` (URL PDF sorgente) e `url_disegno` (URL ICARO generato)

#### Scenario: Generazione URL ICARO
- **WHEN** un disegno ha `legislatura` e `numero_disegno`
- **THEN** `url_disegno` è `https://dati.ars.sicilia.it/icaro/default.jsp?icaDB=221&icaQuery=({legislatura}.LEGISL+E+{numero_disegno}.NUMDDL)` con legislatura senza `XVIII` → `18` e numero_disegno numerico

### Requirement: Pipeline markitdown + llm
Il sistema SHALL usare `markitdown` per convertire PDF in testo e `llm --schema-multi` per estrarre dati strutturati.

#### Scenario: Estrazione con schema multi
- **WHEN** un PDF viene processato
- **THEN** il comando è `markitdown <pdf_url> | llm --schema-multi "<schema>" --system "<prompt>"`

#### Scenario: Schema estrazione
- **WHEN** viene eseguito llm
- **THEN** lo schema richiede `titolo_disegno`, `numero_disegno`, `legislatura`, `data_ora` con prompt "estrai se presenti, i dati citati nell'ordine del giorno"

### Requirement: Input da anagrafica video CSV
Il sistema SHALL leggere gli URL PDF OdG dal campo `odg_url` di `data/anagrafica_video.csv`, considerando solo valori distinti.

#### Scenario: Lettura URL distinti
- **WHEN** il CSV contiene URL `odg_url` ripetuti
- **THEN** il sistema elabora ogni URL una sola volta

#### Scenario: Campi vuoti o mancanti
- **WHEN** una riga CSV ha `odg_url` vuoto
- **THEN** il sistema salta la riga

