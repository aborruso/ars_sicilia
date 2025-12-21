# Change: Impostare recordingDate da data_video/ora_video

## Why
Il recordingDate su YouTube deve riflettere l'effettiva data/ora del video (data_video + ora_video) presenti in anagrafica.

## What Changes
- Aggiunta regola per valorizzare recordingDate usando data_video e ora_video di anagrafica
- Fallback esplicito quando ora_video non e' disponibile

## Impact
- Affected specs: ars-video-metadata
- Affected code: src/metadata.py, src/uploader.py, update_descriptions.py (se aggiorna recordingDate)
