# Pulizia file di test in scripts

## Todo

- [x] Creare directory `scripts/tests/` per i file di test
- [x] Spostare `test_youtube_auth.py` in `scripts/tests/`
- [x] Spostare `test_youtube_auth_manual.py` in `scripts/tests/`
- [x] Verificare se ci sono riferimenti a questi file da aggiornare (README, documentazione, workflow)
- [x] Creare directory `scripts/archive/` per script obsoleti
- [x] Identificare script obsoleti da archiviare
- [x] Spostare script obsoleti in `scripts/archive/`

## Review

**File spostati in `scripts/tests/`:**
- test_youtube_auth.py
- test_youtube_auth_manual.py

**File spostati in `scripts/archive/`:**
- backfill_durations.py
- check_playlist.py
- fix_csv_carriage_returns.py
- sync_youtube_ids.py

**Riferimenti aggiornati:**
- scripts/README.md:47-48
- openspec/project.md:39

La directory `scripts/` ora contiene solo gli script attivi, con test e obsoleti organizzati in sottodirectory.
