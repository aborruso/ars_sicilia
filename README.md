# ARS YouTube Uploader

Sistema automatizzato per scaricare video sedute Assemblea Regionale Siciliana e pubblicarli su YouTube con metadati ricercabili.

## Funzionalità

### Anagrafica Video
- **Script:** `build_anagrafica.py`
- Crawler incrementale sedute dal 10/12/2025 in poi
- Naviga usando `div.next_link` (freccia destra)
- Estrae metadati senza scaricare video
- Rileva aggiornamenti sedute (nuovi video)
- Output CSV: `data/anagrafica_video.csv`
- Wrapper per cron: `run_daily.sh`

### Upload YouTube
- Scraping automatico pagine sedute da https://www.ars.sicilia.it
- Download video HLS con yt-dlp
- Upload su YouTube con metadati strutturati
- **Playlist annuali**: aggiunta automatica a playlist anno
- **Link ricerca seduta**: ogni video include link di ricerca globale basato su token univoco
- Logging upload per evitare duplicati
- Naming convention: `Lavori d'aula: seduta n. 219/A del 10 Dicembre 2025 - 11:30`
- Recording date impostato su data effettiva video (distingue data seduta da data video)
- Tags ottimizzati per ricerca: numero seduta, anno, mese
- Link a OdG e resoconti nella descrizione
- Token univoco in descrizione: `ARS_SEDUTA_<numero>-<YYYY-MM-DD>`

## Requisiti

- Python 3.10+
- yt-dlp
- Account YouTube
- Progetto Google Cloud con YouTube Data API v3 abilitata

## Setup Iniziale

### 1. Installazione Dipendenze

```bash
pip3 install -r requirements.txt
```

### 2. Setup Canale YouTube

1. Crea canale YouTube dedicato (es. "ARS Sicilia - Sedute Assemblea")
2. Verifica canale per video >15 minuti: https://www.youtube.com/verify
3. Annota Channel ID (opzionale)

### 3. Setup Google Cloud e YouTube API

#### 3.1 Crea Progetto Google Cloud

1. Vai su https://console.cloud.google.com/
2. Clicca "Nuovo Progetto"
3. Nome: `ars-youtube-uploader`
4. Clicca "Crea"

#### 3.2 Abilita YouTube Data API v3

1. Nel progetto, vai su "API & Services" → "Library"
2. Cerca "YouTube Data API v3"
3. Clicca "Abilita"

#### 3.3 Configura OAuth Consent Screen

1. Vai su "API & Services" → "OAuth consent screen"
2. Seleziona "External"
3. Compila campi richiesti:
   - App name: `ARS Video Uploader`
   - User support email: tua email
   - Developer contact: tua email
4. Clicca "Save and Continue"
5. Scopes: clicca "Add or Remove Scopes"
   - Cerca e seleziona: `https://www.googleapis.com/auth/youtube.upload`
6. Clicca "Save and Continue"
7. Test users: aggiungi email Google del canale YouTube
8. Clicca "Save and Continue" → "Back to Dashboard"

#### 3.4 Crea Credenziali OAuth 2.0

1. Vai su "API & Services" → "Credentials"
2. Clicca "Create Credentials" → "OAuth client ID"
3. Application type: "Desktop app"
4. Name: `ARS Uploader Desktop`
5. Clicca "Create"
6. Nella finestra popup, clicca "Download JSON"
7. Salva file scaricato come `config/youtube_secrets.json`

#### 3.5 Verifica Quota

1. Vai su "API & Services" → "YouTube Data API v3" → "Quotas"
2. Verifica quota disponibili:
   - Default: 10,000 units/day
   - Upload video: ~1,600 units
   - Max upload/giorno: ~6 video

Se serve più quota, richiedi aumento su Google Cloud Console.

### 4. Prima Autenticazione

```bash
python3 main.py https://www.ars.sicilia.it/agenda/sedute-aula/seduta-numero-219-del-10122025
```

Al primo avvio:
1. Si aprirà browser
2. Seleziona account Google del canale YouTube
3. Clicca "Continua" per autorizzare
4. Token salvato in `config/token.json` per riuso

### 5. Configurazione Playlist e Channel ID

#### 5.1 Ottieni Channel ID

1. Vai su YouTube Studio: https://studio.youtube.com
2. In alto a sinistra, clicca sull'icona del canale
3. Clicca "Impostazioni" → "Canale"
4. Copia l'ID canale (es. `UCxxxxxxxxxxxxxxxxxxx`) o handle (es. `@ARSSicilia`)
5. Apri `config/config.yaml` e compila `youtube.channel_id`:
   ```yaml
   youtube:
     channel_id: "@ARSSicilia"  # O UCxxxxxxxxxxxxxxxxxxx
   ```

**Nota:** Il channel_id resta opzionale; il link ricerca seduta usa una ricerca globale con token.

#### 5.2 Crea Playlist Annuali

1. Vai su YouTube Studio → Playlist
2. Crea nuova playlist:
   - Nome: `ARS 2025 - Sedute Assemblea`
   - Visibilità: Pubblica
   - Descrizione: `Sedute Assemblea Regionale Siciliana - Anno 2025`
3. Dalla pagina playlist, copia l'ID dall'URL:
   - URL: `https://www.youtube.com/playlist?list=PLxxxxxxxxxxxxxxxxxxx`
   - ID playlist: `PLxxxxxxxxxxxxxxxxxxx`
4. Ripeti per anno 2026, 2027, etc.
5. Apri `config/config.yaml` e compila playlist:
   ```yaml
   youtube:
     playlists:
       "2025": "PLxxxxxxxxxxxxxxxxxxx"
       "2026": "PLyyyyyyyyyyyyyyyyyy"
   ```

**Nota:** I video verranno aggiunti automaticamente alla playlist dell'anno corrispondente.

## Utilizzo

### Test Upload Singolo Video

Prima di caricare tutti i video, testa l'upload del primo:

```bash
# Modalità dry-run (mostra cosa farebbe senza caricare)
python3 test_upload_single.py --dry-run

# Upload reale del primo video
python3 test_upload_single.py
```

Lo script:
1. Trova primo video dall'anagrafica senza `youtube_id`
2. Scarica il video
3. Carica su YouTube con metadati completi
4. Aggiunge a playlist anno (se configurata)
5. **Aggiorna anagrafica** con `youtube_id` per evitare duplicati

**Importante:** Dopo upload successo, il video non verrà ricaricato in esecuzioni successive.

### Aggiornare Descrizioni Esistenti

Se hai video già caricati e vuoi aggiungere/aggiornare il token e il link di ricerca:

```bash
# Preview senza aggiornare
.venv/bin/python3 update_descriptions.py --dry-run

# Update reale delle descrizioni
.venv/bin/python3 update_descriptions.py
```

Il link di ricerca generato usa questa forma:
```
https://www.youtube.com/results?search_query="ARS_SEDUTA_219-2025-12-10"+intitle:"Lavori d'aula"
```

### Configurazione Avanzata (config.yaml)

Opzioni utili per robustezza e metadati:
```yaml
scraping:
  timeout: 30
  retries: 3
  backoff_factor: 0.5

youtube:
  timezone: "Europe/Rome"
```

### Build Anagrafica Video

Costruisce/aggiorna anagrafica sedute dal 10/12/2025:

```bash
# Manuale
./run_daily.sh

# Con venv
.venv/bin/python3 build_anagrafica.py
```

**Output:**
- `data/anagrafica_video.csv` - Metadati tutti video
- `data/logs/build_anagrafica_YYYY-MM-DD.log` - Log esecuzione

**Comportamento:**
- Prima esecuzione: estrae tutte sedute dal 10/12/2025
- Esecuzioni successive: solo nuove sedute o sedute con nuovi video
- Si ferma quando non ci sono più sedute future (next_link assente)

**Cron giornaliero:**
```cron
0 8 * * * /path/to/ars_sicilia/run_daily.sh
```

### Processare Seduta Specifica

```bash
python3 main.py https://www.ars.sicilia.it/agenda/sedute-aula/seduta-numero-XXX-del-DDMMYYYY
```

### Processare Ultima Seduta Disponibile

```bash
python3 main.py
```

Lo script cercherà automaticamente l'ultima seduta disponibile.

### Esecuzione Automatica (Cron)

Crea cron job per esecuzione giornaliera:

```bash
crontab -e
```

Aggiungi:

```cron
# Ogni giorno alle 3:00 AM
0 3 * * * cd /home/aborruso/git/idee/ars_sicilia && /usr/bin/python3 main.py >> data/logs/cron.log 2>&1
```

## Struttura File

```
ars_sicilia/
├── src/
│   ├── scraper.py          # Scraping pagine sedute
│   ├── downloader.py       # Download video HLS
│   ├── uploader.py         # Upload YouTube
│   ├── metadata.py         # Costruzione metadati
│   ├── logger.py           # Gestione log CSV
│   └── utils.py            # Utility functions
├── config/
│   ├── config.yaml         # Configurazione
│   ├── youtube_secrets.json # Credenziali OAuth2 (non committare!)
│   └── token.json          # Token OAuth2 (auto-generato)
├── data/
│   ├── anagrafica_video.csv # Anagrafica completa video
│   ├── logs/
│   │   ├── build_anagrafica_*.log # Log build anagrafica
│   │   ├── upload_log.csv  # Log upload video
│   │   └── index.csv       # Indice sedute
│   └── videos/             # Video temporanei (auto-cleanup)
├── build_anagrafica.py     # Script anagrafica incrementale
├── run_daily.sh            # Wrapper cron con lock
├── main.py                 # Script upload YouTube
├── requirements.txt
└── README.md
```

## Log Upload

File: `data/logs/upload_log.csv`

Campi:
- `id_video`: ID univoco video ARS
- `numero_seduta`: Numero seduta (es. "219/A")
- `data_seduta`: Data seduta (YYYY-MM-DD)
- `data_video`: Data video (YYYY-MM-DD)
- `ora_video`: Ora video (HH:MM)
- `video_id_youtube`: ID video YouTube
- `upload_timestamp`: Timestamp upload (ISO 8601)
- `status`: success | failed | pending
- `error_message`: Dettaglio errore (se failed)

## Anagrafica Video

File: `data/anagrafica_video.csv`

Campi:
- `numero_seduta`: Numero seduta (es. "219")
- `data_seduta`: Data seduta (YYYY-MM-DD)
- `url_pagina`: URL pagina seduta ARS
- `odg_url`: Link OdG PDF
- `resoconto_url`: Link resoconto stenografico
- `id_video`: ID univoco video ARS
- `ora_video`: Ora inizio video (HH:MM)
- `data_video`: Data video (YYYY-MM-DD)
- `stream_url`: URL stream HLS (attualmente vuoto)
- `video_page_url`: URL pagina video ARS
- `youtube_id`: ID video YouTube (vuoto se non uploadato)
- `last_check`: Timestamp ultimo controllo (ISO 8601)

## Indice Sedute

File: `data/logs/index.csv`

Campi:
- `numero_seduta`
- `data_seduta`
- `url_pagina`
- `video_count`

## Configurazione

File: `config/config.yaml`

Parametri principali:
- `scraping.start_date`: Data inizio crawling (default: 2025-12-01)
- `download.cleanup_after_upload`: Elimina video dopo upload (default: true)
- `youtube.privacy`: public | unlisted | private (default: public)
- `youtube.tags`: Tags base applicati a tutti video

## Monitoraggio

### Verificare Log

```bash
# Ultimi upload
tail -20 data/logs/upload_log.csv

# Upload falliti
grep ",failed," data/logs/upload_log.csv
```

### Statistiche

```python
from src.logger import get_upload_stats

stats = get_upload_stats('data/logs/upload_log.csv')
print(stats)
# {'total': 150, 'success': 145, 'failed': 5, 'pending': 0}
```

### Verificare Quota YouTube

1. Vai su https://console.cloud.google.com/
2. Seleziona progetto `ars-youtube-uploader`
3. API & Services → YouTube Data API v3 → Quotas
4. Verifica utilizzo giornaliero

## Troubleshooting

### Errore "File credenziali non trovato"

Verifica che `config/youtube_secrets.json` esista e contenga credenziali OAuth2 scaricate da Google Cloud Console.

### Errore "Quota exceeded"

Hai superato limite giornaliero YouTube API (10,000 units). Aspetta 24h o richiedi aumento quota.

### Download fallito

- Verifica connessione internet
- Controlla se yt-dlp è installato: `yt-dlp --version`
- Prova download manuale: `yt-dlp [URL]`

### Upload fallito

- Verifica account YouTube verificato (per video >15 min)
- Controlla quota API disponibile
- Verifica token OAuth2 valido

### Token scaduto

Elimina `config/token.json` e riavvia script per ri-autenticarsi.

## Note Importanti

### Limiti YouTube API

- **Quota giornaliera**: 10,000 units/day
- **Costo upload video**: ~1,600 units
- **Max upload/giorno**: ~6 video (con quota default)

Se seduta ha >6 video, processare in 2 giorni o richiedere aumento quota.

### Video Lunghi

Account YouTube deve essere **verificato** per caricare video >15 minuti.

Verifica account: https://www.youtube.com/verify

### Sicurezza

**NON committare** su git:
- `config/youtube_secrets.json`
- `config/token.json`

Questi file sono già in `.gitignore`.

### Bandwidth

Stima: ~1 GB per ora di video (720p).

Seduta con 4 video da 2 ore ciascuna = ~8 GB download.

## Sviluppo

### Test Singolo Video

```python
from src.downloader import download_video

download_video(
    'https://www.ars.sicilia.it/agenda/seduta/aula/video/2484769',
    'test.mp4'
)
```

### Test Scraping

```python
from src.scraper import get_seduta_page, extract_seduta_info

html = get_seduta_page('https://www.ars.sicilia.it/agenda/sedute-aula/seduta-numero-219-del-10122025')
info = extract_seduta_info(html, 'https://...')
print(info)
```

## Licenza

Progetto sviluppato per rendere accessibili i lavori dell'Assemblea Regionale Siciliana.

## Contatti

Per domande o problemi, apri issue su repository GitHub.
