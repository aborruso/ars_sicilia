# ars-video-pipeline Specification

## Purpose
Core video ingestion pipeline: scrape seduta pages, catalog videos, download streams, upload to YouTube, and maintain CSV logs. Implements idempotency, retry logic, and incremental processing.
## Requirements
### Requirement: Configurable HTTP timeouts and retries for scraping
The system SHALL use timeout and retry settings from configuration when fetching ARS pages.

#### Scenario: Scraping uses configured timeout
- **WHEN** a seduta page is requested
- **THEN** the HTTP request uses the configured timeout value

#### Scenario: Scraping retries on transient failure
- **WHEN** an HTTP request fails with a transient error
- **THEN** the system retries according to configured retry/backoff settings

### Requirement: Download directory creation
The system SHALL ensure the configured download directory exists before starting a video download.

#### Scenario: Download path does not exist
- **WHEN** a download is initiated and the directory is missing
- **THEN** the system creates the directory and continues the download

### Requirement: Timezone-aware recording date
The system SHALL emit `recordingDate` with a timezone-aware ISO 8601 value using the configured timezone.

#### Scenario: Recording date is generated
- **WHEN** a video has a date and time
- **THEN** the metadata includes a timezone-aware `recordingDate`

### Requirement: Stronger deduplication key
The system SHALL deduplicate uploads and anagrafica entries using a composite key that includes `id_video`, `numero_seduta`, and `data_seduta`.

#### Scenario: Same id_video across different sedute
- **WHEN** an `id_video` appears with a different seduta date or number
- **THEN** the entry is treated as distinct and not skipped erroneously

### Requirement: Deterministic latest-seduta selection
The system SHALL select the most recent seduta URL when a specific URL is not provided.

#### Scenario: Multiple sedute links are present
- **WHEN** the system discovers multiple seduta links on the listing page
- **THEN** it chooses the link with the latest seduta date

### Requirement: Enforce start_date filter in anagrafica crawl
The system SHALL ignore sedute older than the configured `start_date` during anagrafica crawling.

#### Scenario: Encountered seduta before start_date
- **WHEN** a seduta date is earlier than `start_date`
- **THEN** the seduta is skipped and the crawl proceeds to newer sedute

### Requirement: Persistenza playlist annuali
La pipeline SHALL salvare in modo persistente l'ID della playlist annuale quando viene creata automaticamente.

#### Scenario: Creazione playlist e salvataggio
- **WHEN** viene creata una playlist per un nuovo anno
- **THEN** l'ID playlist viene salvato in un file di stato o in `config/config.yaml` per riuso futuro

#### Scenario: File non scrivibile
- **WHEN** il file di stato o `config/config.yaml` non sono scrivibili
- **THEN** il sistema logga un avviso e continua l'upload senza bloccare

### Requirement: Tracciamento fallimenti upload
La pipeline SHALL registrare nello storico anagrafica lo stato `failed` e il motivo dell'errore quando un upload non va a buon fine.

#### Scenario: Upload fallito
- **WHEN** un upload fallisce con un errore gestito
- **THEN** la riga dell'anagrafica viene aggiornata con stato `failed` e `failure_reason`

#### Scenario: Retry successivo
- **WHEN** un video ha stato `failed`
- **THEN** il sistema lo considera eleggibile per retry in una run successiva

