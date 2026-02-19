## ADDED Requirements
### Requirement: Transcript archive download via YouTube API
Il sistema SHALL scaricare le trascrizioni archiviate dei video da YouTube Data API nel flusso `scripts/download_transcripts.sh`.

#### Scenario: Download caption italiana con API ufficiali
- **WHEN** lo script processa un `youtube_id` con caption disponibile in italiano
- **THEN** usa YouTube API (`captions.list` e `captions.download`) per ottenere la trascrizione
- **AND** salva `data/trascrizioni/<youtube_id>.it.srt`

#### Scenario: Output invariato per pipeline corrente
- **WHEN** il file `.it.srt` viene scaricato con successo
- **THEN** lo script genera `data/trascrizioni/<youtube_id>.it.txt` con lo stesso flusso di estrazione testo attuale
- **AND** le fasi successive della pipeline possono usare i file senza modifiche

#### Scenario: Video senza caption utilizzabile
- **WHEN** non esiste una caption italiana scaricabile per il video
- **THEN** lo script non interrompe il batch
- **AND** registra il `youtube_id` in `data/trascrizioni/no_transcript.txt`

#### Scenario: Idempotenza su file esistenti
- **WHEN** esistono già `data/trascrizioni/<youtube_id>.it.srt` e `data/trascrizioni/<youtube_id>.it.txt`
- **THEN** lo script salta il download per quel video
- **AND** non sovrascrive i file esistenti
