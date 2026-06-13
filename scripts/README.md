# Scripts

Guida rapida agli script operativi. Tutti i comandi vanno eseguiti dalla root del repo.

## Principali

- `main.py` — Pipeline principale: download + upload su YouTube a partire da una seduta o da anagrafica.
- `build_anagrafica.py` — Crawler incrementale per aggiornare `data/anagrafica_video.csv`.
- `upload_single.py` — Upload singolo video (primo senza `youtube_id`), con `--dry-run`.
- `run_daily.sh` — Wrapper per esecuzione giornaliera con lock file.
- `download_transcripts.sh` — Scarica trascrizioni archiviate (`.it.srt` + `.it.txt`) via YouTube Data API.
- `generate_rss.py` — Genera `feed.xml` dai video caricati.
- `extract_odg_data.sh` — Estrae dati disegni legge dai PDF OdG e li salva in `data/disegni_legge.jsonl`.
- `scrape_studi_pubblicazioni.py` — Scraper incrementale delle sezioni correnti di "Studi e Pubblicazioni" (archivio escluso), output JSONL.
- `update_descriptions.py` — Aggiorna descrizioni (e opzionalmente titoli) dei video già pubblicati.
- `generate_digests.sh` — Genera digest automatici dai video YouTube usando trascrizioni e template.
- `normalize_eurovoc_categories.mjs` — Normalizza le categorie su EuroVoc e aggiorna `data/eurovoc_mapping.json`.

### download_transcripts.sh

Scarica le trascrizioni per i video presenti in `data/anagrafica_video.csv` usando
YouTube Data API (`captions.list` + `captions.download`) tramite OAuth locale.

Output per ciascun `youtube_id`:
1) `data/trascrizioni/<youtube_id>.it.srt`
2) `data/trascrizioni/<youtube_id>.it.txt` (testo estratto dal file SRT)

Prerequisiti:
- `config/youtube_secrets.json`
- `config/token.json` con scope `youtube.readonly` e `youtube.force-ssl`

Uso:
```bash
./scripts/download_transcripts.sh
```

### generate_digests.sh

Genera un digest JSON per ogni video YouTube elencato in `data/anagrafica_video.csv`.
Per ogni riga con `youtube_id` non vuoto:
1) scarica la trascrizione con `qv`;
2) passa la trascrizione al comando `llm` usando il template `config/digest.yaml`
   e lo schema `config/digest-schema.json`;
3) salva l’output in `data/digest/<youtube_id>.json`.

Se il file di output esiste già, lo script salta il video. In caso di errori
di download o generazione, il video viene conteggiato come fallito e l’elaborazione
prosegue con il successivo. Tra una generazione e l’altra applica una pausa
(configurata in `SLEEP_SECONDS` nello script).

Requisiti: `qv`, `llm`, `mlr` e accesso al modello configurato (attualmente `gemini-2.5-flash`).

Uso:
```bash
./scripts/generate_digests.sh
```

Modelli testati per la configurazione iniziale:
- `gemini-2.5-flash` — scelto: senza costi e output accettabile.
- `claude-sonnet-4.5`
- `mistral-medium`
- `gpt-5.2`

### normalize_eurovoc_categories.mjs

Normalizza le categorie presenti in `src/data/processed/categories.json` verso EuroVoc
usando il dump locale e `llm` con il modello `gemini-2.5-flash`. Lo script aggiorna
incrementalmente `data/eurovoc_mapping.json` senza sovrascrivere le associazioni esistenti.
Richiede `unzip` per estrarre il dump.

Uso:
```bash
node scripts/normalize_eurovoc_categories.mjs
```

Opzioni principali:
- `--version` (es. `20250702-0`) per forzare una versione EuroVoc
- `--review-threshold` per marcare come `review` le associazioni sotto soglia
- `--refresh-dump` per riscaricare ed estrarre il dump
- `--limit` per limitare il numero di categorie processate (test)
- `--timeout-ms` timeout per singola richiesta LLM (default 120000)

### scrape_studi_pubblicazioni.py

Estrae i documenti dalle sezioni tematiche correnti di:
`https://www.ars.sicilia.it/studi-e-pubblicazioni`

Esclude volutamente `Archivio`, estrae eventuali numeri DDL dal titolo e salva in JSONL:
- `titolo`
- `url`
- `data_pubblicazione` (formato `YYYY-MM` quando deducibile dalla URL download)
- `numeri_ddl_estratti`
- `fonte`

Modalità operative:
- `append` (default): aggiunge solo nuovi record (dedup su `url`)
- `snapshot`: rigenera interamente il file output

Uso:
```bash
python3 scripts/scrape_studi_pubblicazioni.py
python3 scripts/scrape_studi_pubblicazioni.py --mode snapshot
python3 scripts/scrape_studi_pubblicazioni.py --output data/studi_pubblicazioni.jsonl
```

### extract_odg_data.sh

Estrae i disegni di legge dalla sezione "DISCUSSIONE DEI DISEGNI DI LEGGE" dei PDF OdG
(`markitdown` + `llm`, modello `gemini-2.5-flash`) e li salva in `data/disegni_legge.jsonl`.

Caratteristiche:
- **Idempotente e progressivo**: salta i PDF già nel log `data/logs/odg_pdfs_processed.txt`;
  per ogni PDF lavorato rimuove i vecchi record e li sostituisce (in-place, nessun buco).
- **`--limit N`**: processa al massimo N PDF per lancio (rispetta il free tier Gemini: ~10 RPM, 250 RPD).
- **Throttle + retry**: `sleep` tra i PDF (env `ODG_SLEEP`, default 7s) e retry con backoff sui 429.
- **Normalizzazione**: numero (primo gruppo di cifre), legislatura (solo romano), dedup per
  `(pdf_url, numero_disegno, titolo_disegno)`, scarto record con titolo mancante.
- **`--reprocess`**: ricostruisce tutto da zero (backup `.bak`).

```bash
# avanza di 10 PDF per volta (idempotente: rilancia finché finisce)
./scripts/extract_odg_data.sh --limit 10

# rielabora TUTTI i PDF da capo col prompt corrente: svuota il log una volta, poi lancia a batch
: > data/logs/odg_pdfs_processed.txt
./scripts/extract_odg_data.sh --limit 10   # ripeti finché il log contiene tutti i PDF
```

In CI (`extract_odg.yml`) gira ogni notte con `--limit 10`.

## Auth / Setup

- `auth_captions.py` — **Rigenera il token OAuth del progetto captions** (`config/token.json`) con gli scope corretti per scaricare i sottotitoli (`youtube.readonly` + `youtube.force-ssl`). Apre un server locale e il browser per il consenso; salva un `refresh_token` valido. Da usare quando il refresh token è scaduto o gli scope cambiano.
  ```bash
  .venv/bin/python3 scripts/auth_captions.py
  ```
  Note:
  - L'app OAuth deve essere **In production** (non Testing), altrimenti il refresh token scade dopo 7 giorni.
  - In WSL, se il browser non si apre da solo, copiare l'URL stampato nel browser Windows.
  - Comparirà l'avviso "Google non ha verificato questa app" → Avanzate → Continua (app a uso personale).
  - Dopo la rigenerazione aggiornare i secret del repo (vedi sotto).
- `get_auth_url.py` / `complete_auth.py` — Flusso OAuth a due passi per il client di **upload** (scope `youtube.upload` + `youtube.readonly`). Non usare per le captions: mancherebbe `force-ssl`.
- `setup_playlist.py` — Crea playlist annuale e (opzionalmente) aggiunge video esistenti.

### Aggiornare i secret GitHub dopo la rigenerazione del token captions

```bash
jq -r '.refresh_token'         config/token.json          | gh secret set YOUTUBE_REFRESH_TOKEN
jq -r '.installed.client_id'   config/youtube_secrets.json | gh secret set YOUTUBE_CLIENT_ID
jq -r '.installed.client_secret' config/youtube_secrets.json | gh secret set YOUTUBE_CLIENT_SECRET
```

## Note

- Sottodirectory: `tests/` (smoke test auth), `archive/` (script obsoleti).


- Config: `config/config.yaml`
- Log/anagrafica: `data/`
- Stato playlist auto-create: `data/playlists.json`
- Per dettagli completi, vedi `README.md` principale.

## Esecuzione manuale (non gestita da workflow)

Questi step vanno eseguiti **in locale**. Inizia sempre da un repo aggiornato:

1) `scripts/run_transcripts_and_digests.sh`
2) `git add data/trascrizioni/ data/digest/`
3) `git commit -m "chore: add transcripts and AI digests"`
4) `git push`
