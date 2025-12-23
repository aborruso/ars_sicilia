# Change: Auto-salvataggio playlist annuali

## Why
Quando l'anno cambia, la pipeline crea automaticamente la playlist ma non salva l'ID in modo persistente, con rischio di duplicati e configurazione manuale ripetuta.

## What Changes
- Salvataggio automatico dell'ID playlist creato per anno in un file di stato o in `config/config.yaml`.
- Fallback non distruttivo se il file non è scrivibile (log + continuazione upload senza bloccare).

## Impact
- Affected specs: ars-video-pipeline
- Affected code: `src/uploader.py`, `scripts/upload_single.py`, possibile utilità per scrittura config
