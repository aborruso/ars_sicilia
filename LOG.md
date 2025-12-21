# 2025-12-21

## Affidabilità Pipeline e Metadati

- Scraping con timeout/retry configurabili e backoff
- Creazione automatica directory download
- recordingDate timezone-aware (Europe/Rome)
- Dedup più robusto (id_video + numero_seduta + data_seduta)
- Selezione ultima seduta deterministica
- Filtro `start_date` in anagrafica

## Token Seduta e Link Ricerca

- Token univoco in descrizione: `ARS_SEDUTA_<numero>-<YYYY-MM-DD>`
- Link ricerca globale con operatori: `results?search_query="TOKEN"+intitle:"Lavori d'aula"`
- Script `update_descriptions.py` per aggiornare descrizioni già caricate

## Script Test Upload Singolo

**test_upload_single.py:**
- Upload primo video dall'anagrafica senza youtube_id
- Modalità `--dry-run` per preview senza caricare
- Aggiorna anagrafica con youtube_id dopo upload
- Previene duplicati in run successive

**Flusso:**
1. Trova primo video senza youtube_id in anagrafica
2. Autentica YouTube (skip in dry-run)
3. Download video da pagina ARS (skip in dry-run)
4. Costruisce metadati completi
5. Upload + aggiunta a playlist anno
6. Aggiorna anagrafica con youtube_id
7. Cleanup file temporaneo

**Funzioni:**
- `get_first_unuploaded_video()`: trova video da uploadare
- `update_anagrafica_youtube_id()`: aggiorna CSV dopo upload
- Conferma utente prima di upload reale

**Uso:**
```bash
python3 test_upload_single.py --dry-run  # Preview
python3 test_upload_single.py            # Upload reale
```

## Playlist Annuali e Link Ricerca Seduta

**Organizzazione contenuti YouTube:**
- Playlist annuali: video aggiunti automaticamente a playlist anno (es. "ARS 2025")
- Link ricerca seduta in descrizione: `youtube.com/@Canale/search?query=seduta+n+220`
- Utenti possono filtrare video per seduta specifica senza playlist dedicate

**Configurazione (`config/config.yaml`):**
- `youtube.channel_id`: ID canale o handle (es. `@ARSSicilia`)
- `youtube.playlists`: mapping anno → playlist ID (es. `2025: PLxxxxxxxxx`)

**Funzioni nuove (`src/uploader.py`):**
- `add_video_to_playlist()`: aggiunge video a playlist (50 units API)
- `get_playlist_id_for_year()`: seleziona playlist da anno
- `upload_video()`: parametro `playlist_id` opzionale

**Metadati migliorati (`src/metadata.py`):**
- Descrizione con link ricerca seduta (se channel_id configurato)
- Tags ottimizzati: "Seduta n. 220", "Dicembre 2025"
- Emoji per sezioni: 🔍 ricerca, 📄 documenti, 🔗 link

**Quota API aggiornata:**
- Upload: 1,600 units
- Playlist insert: 50 units
- **Totale: 1,650 units/video → ~6 video/giorno**

**Documentazione:**
- README: sezione configurazione playlist e channel_id
- Istruzioni creare playlist su YouTube Studio

## Fix Estrazione Date Video Multi-Date

**Problema rilevato:**
- Sedute con video distribuiti su più giorni (es. seduta 220: 16-21 dicembre)
- `data_video` errata: tutti video mostravano data_seduta invece di data effettiva

**Fix implementati src/scraper.py:**
- `extract_seduta_number()`: estrae da `<title>` invece di body (evita match link navigazione)
- `extract_video_metadata()`: usa `title` attribute video_box (contiene data+ora complete)
- Fallback robusto: h4 heading precedente se title mancante
- Distinzione corretta `data_seduta` vs `data_video`

**Risultato:**
- Seduta 220 (data_seduta: 16/12): 4 video 16/12, 3 video 17/12, 5 video 18/12, 3 video 19/12, 7 video 20/12, 2 video 21/12
- Seduta 219 (data_seduta: 10/12): 2 video 10/12, 2 video 15/12
- Anagrafica rigenerata: 28 video con date corrette

**Versionamento dati:**
- Anagrafica CSV ora committata su GitHub
- .gitignore modificato: esclusi solo logs, inclusa anagrafica pubblica

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
