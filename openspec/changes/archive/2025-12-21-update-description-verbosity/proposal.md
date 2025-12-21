# Change: Rendere la descrizione più verbosa e neutralizzare timestamp

## Why
YouTube interpreta gli orari nel testo come timestamp del video. Inoltre la descrizione deve spiegare in modo più verboso numero e data della seduta e la data/ora di svolgimento.

## What Changes
- Applicare escape con zero-width space negli orari per evitare l'interpretazione come timestamp
- Riscrivere le prime righe della descrizione con formulazione più verbosa
- Aggiornare l'utility di backfill descrizioni per applicare il nuovo formato

## Impact
- Affected specs: ars-video-metadata
- Affected code: src/metadata.py, update_descriptions.py
