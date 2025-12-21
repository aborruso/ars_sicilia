# Change: Impostare la lingua audio su it-IT nei metadati YouTube

## Why
I metadati YouTube mostrano `defaultAudioLanguage` errata (es. en-US). I video ARS sono in italiano e devono essere marcati come it-IT.

## What Changes
- Impostare `defaultAudioLanguage` su `it-IT` durante l'upload
- Aggiungere configurazione per la lingua audio (default: it-IT)
- (Opzionale) Backfill della lingua audio sui video già pubblicati

## Impact
- Affected specs: ars-video-metadata
- Affected code: src/metadata.py, src/uploader.py, update_descriptions.py (se backfill)
