# Scripts

Guida rapida agli script operativi. Tutti i comandi vanno eseguiti dalla root del repo.

## Principali

- `main.py` — Pipeline principale: download + upload su YouTube a partire da una seduta o da anagrafica.
- `build_anagrafica.py` — Crawler incrementale per aggiornare `data/anagrafica_video.csv`.
- `upload_single.py` — Upload singolo video (primo senza `youtube_id`), con `--dry-run`.
- `run_daily.sh` — Wrapper per esecuzione giornaliera con lock file.
- `generate_rss.py` — Genera `feed.xml` dai video caricati.
- `extract_odg_data.sh` — Estrae dati disegni legge dai PDF OdG e li salva in `data/disegni_legge.jsonl`.
- `scrape_studi_pubblicazioni.py` — Scraper incrementale delle sezioni correnti di "Studi e Pubblicazioni" (archivio escluso), output JSONL.
- `update_descriptions.py` — Aggiorna descrizioni (e opzionalmente titoli) dei video già pubblicati.
- `generate_digests.sh` — Genera digest automatici dai video YouTube usando trascrizioni e template.
- `normalize_eurovoc_categories.mjs` — Normalizza le categorie su EuroVoc e aggiorna `data/eurovoc_mapping.json`.

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

## Auth / Setup

- `get_auth_url.py` — Avvia flusso OAuth e stampa URL di autorizzazione.
- `complete_auth.py` — Completa OAuth e salva token.
- `setup_playlist.py` — Crea playlist annuale e (opzionalmente) aggiunge video esistenti.

## Note

- Sottodirectory: `tests/` (smoke test auth), `archive/` (script obsoleti).


- Config: `config/config.yaml`
- Log/anagrafica: `data/`
- Stato playlist auto-create: `data/playlists.json`
- Per dettagli completi, vedi `README.md` principale.

## Esecuzione manuale (non gestita da workflow)

Questi step vanno eseguiti **in locale**. Inizia sempre da un repo aggiornato:

1) `git pull`
2) `./scripts/download_transcripts.sh`
3) `./scripts/generate_digests.sh`
4) `git add data/trascrizioni/ data/digest/`
5) `git commit -m "chore: add transcripts and AI digests"`
6) `git push`
