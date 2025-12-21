# 2025-12-21

## Anagrafica Video Incrementale

Implementato sistema anagrafica completo:

**Script `build_anagrafica.py`:**
- Crawler incrementale partenza seduta 219 (10/12/2025)
- Naviga verso futuro usando `div.next_link` (freccia destra)
- Si ferma quando non ci sono sedute future
- Estrae metadati senza download video
- **Rilevamento aggiornamenti**: confronta count video per seduta, aggiorna se diverso
- Output CSV `data/anagrafica_video.csv` con 12 colonne

**Funzionalità chiave:**
- Prima run: processa tutte sedute dal 10/12/2025 ad oggi
- Run successivi: solo sedute nuove o aggiornate
- Wrapper `run_daily.sh`: lock file, logging giornaliero, error handling
- Pronto per cron job

**Modifiche `src/scraper.py`:**
- `get_next_seduta_url()`: parametro `go_forward=True` usa `div.next_link`
- Supporta navigazione bidirezionale (passato/futuro)

**Setup autenticazione YouTube:**
- File `.env` con Client ID/Secret (non versionato)
- `config/youtube_secrets.json` con OAuth completo
- `config/token.json` generato con scope `youtube.upload` + `youtube.readonly`
- Test autenticazione riuscito su canale "Andrea Borruso"

**Primo run anagrafica:**
- Sedute processate: 2 (218, 219)
- Video catalogati: 28
- Tempo: ~10 secondi

**File aggiornati:**
- PRD.md: stato progetto con fasi
- README.md: sezione anagrafica e istruzioni
- config/config.yaml: start_url seduta 219

# 2025-12-19

## Implementazione Iniziale

- Struttura progetto completa creata
- Moduli Python implementati:
  - `src/scraper.py`: scraping pagine sedute ARS
  - `src/downloader.py`: download video HLS con yt-dlp
  - `src/uploader.py`: upload YouTube con OAuth2
  - `src/metadata.py`: costruzione metadati (titolo, descrizione, tags, recordingDate)
  - `src/logger.py`: gestione log CSV e indice sedute
  - `src/utils.py`: funzioni helper date/formattazione
- Script principale `main.py` con orchestrazione completa
- Configurazione `config/config.yaml` con parametri predefiniti
- README.md con istruzioni complete setup YouTube API
- `.gitignore` per credenziali e file temporanei

## Specifiche Implementate

- Naming convention: `Lavori d'aula: seduta n. 219/A del 10 Dicembre 2025 - 11:30`
- recordingDate API YouTube impostato con data/ora effettiva seduta
- Log CSV traccia: id_video, numero_seduta, data_seduta, ora_video, youtube_id, status
- Video temporanei eliminati dopo upload
- Una seduta per esecuzione (adatto a cron job)
- Link OdG e Resoconto in descrizione video

## Next Steps

- Setup Google Cloud e YouTube API (manuale)
- Prima autenticazione OAuth2
- Test download e upload su seduta campione
- Setup cron job per esecuzione automatica
