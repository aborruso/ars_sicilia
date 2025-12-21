# Scripts

Guida rapida agli script operativi. Tutti i comandi vanno eseguiti dalla root del repo.

## Principali

- `main.py` — Pipeline principale: download + upload su YouTube a partire da una seduta o da anagrafica.
- `build_anagrafica.py` — Crawler incrementale per aggiornare `data/anagrafica_video.csv`.
- `upload_single.py` — Upload singolo video (primo senza `youtube_id`), con `--dry-run`.
- `run_daily.sh` — Wrapper per esecuzione giornaliera con lock file.
- `generate_rss.py` — Genera `public/feed.xml` dai video caricati.
- `update_descriptions.py` — Aggiorna descrizioni (e opzionalmente titoli) dei video già pubblicati.

## Auth / Setup

- `get_auth_url.py` — Avvia flusso OAuth e stampa URL di autorizzazione.
- `complete_auth.py` — Completa OAuth e salva token.
- `test_youtube_auth.py` — Smoke test autenticazione e quota.
- `test_youtube_auth_manual.py` — Variante manuale per debug OAuth.
- `setup_playlist.py` — Crea playlist annuale e (opzionalmente) aggiunge video esistenti.

## Note

- Config: `config/config.yaml`
- Log/anagrafica: `data/`
- Per dettagli completi, vedi `README.md` principale.
