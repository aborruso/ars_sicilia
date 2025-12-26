# Change: Skip videos without transcript in digest generation

## Why
Alcuni video YouTube non contengono parlato (es. interruzioni tecniche, schermate fisse) e quindi non hanno trascrizione disponibile. Attualmente `generate_digests.sh` marca questi come falliti dopo retry, sprecando tempo e quota LLM. Serve un meccanismo per rilevare questi video al primo check e skipparli automaticamente nelle esecuzioni successive.

## What Changes
- Aggiungi colonna `no_transcript` (booleana) all'anagrafica CSV per marcare video senza parlato
- Modifica `generate_digests.sh` per rilevare trascrizioni vuote/troppo piccole (<100 bytes)
- Marca video come `no_transcript=true` invece di contarli come falliti
- Skippa automaticamente video già marcati `no_transcript=true` nelle esecuzioni successive
- Log distinti per video skipped vs failed

## Impact
- Affected specs: `video-duration-tracking` (modifica anagrafica CSV schema), nuova capability `video-digest-generation`
- Affected code: `scripts/generate_digests.sh`, `data/anagrafica_video.csv` (schema migration)
- Quota savings: evita 3 retry × N video silenziosi
