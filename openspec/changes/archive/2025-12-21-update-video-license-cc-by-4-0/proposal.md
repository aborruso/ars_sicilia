# Change: Impostare licenza video YouTube su CC BY 4.0

## Why
I video pubblicati devono usare la licenza Creative Commons Attribution 4.0 invece della licenza generica YouTube.

## What Changes
- Impostare la licenza video su Creative Commons (CC BY 4.0) durante l'upload
- (Opzionale) Backfill della licenza per video gia' caricati

## Impact
- Affected specs: ars-video-metadata
- Affected code: src/uploader.py, src/metadata.py (se usato), update_descriptions.py (se backfill)
