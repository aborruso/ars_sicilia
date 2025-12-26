# Scripts

Guida rapida agli script operativi. Tutti i comandi vanno eseguiti dalla root del repo.

## Principali

- `main.py` — Pipeline principale: download + upload su YouTube a partire da una seduta o da anagrafica.
- `build_anagrafica.py` — Crawler incrementale per aggiornare `data/anagrafica_video.csv`.
- `upload_single.py` — Upload singolo video (primo senza `youtube_id`), con `--dry-run`.
- `run_daily.sh` — Wrapper per esecuzione giornaliera con lock file.
- `generate_rss.py` — Genera `feed.xml` dai video caricati.
- `extract_odg_data.sh` — Estrae dati disegni legge dai PDF OdG e li salva in `data/disegni_legge.jsonl`.
- `update_descriptions.py` — Aggiorna descrizioni (e opzionalmente titoli) dei video già pubblicati.
- `generate_digests.sh` — Genera digest automatici dai video YouTube usando trascrizioni e template.

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

## Auth / Setup

- `get_auth_url.py` — Avvia flusso OAuth e stampa URL di autorizzazione.
- `complete_auth.py` — Completa OAuth e salva token.
- `test_youtube_auth.py` — Smoke test autenticazione e quota.
- `test_youtube_auth_manual.py` — Variante manuale per debug OAuth.
- `setup_playlist.py` — Crea playlist annuale e (opzionalmente) aggiunge video esistenti.

## Note

- Config: `config/config.yaml`
- Log/anagrafica: `data/`
- Stato playlist auto-create: `data/playlists.json`
- Per dettagli completi, vedi `README.md` principale.
