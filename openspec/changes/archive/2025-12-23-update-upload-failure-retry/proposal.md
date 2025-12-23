# Change: Gestione fallimenti upload con retry

## Why
Quando un upload fallisce, oggi non resta traccia strutturata dell'errore nell'anagrafica e la selezione del prossimo video non distingue i fallimenti. Serve uno stato `failed` con motivo per poter ritentare in modo controllato.

## What Changes
- Registrare in anagrafica lo stato `failed` e il motivo dell'errore.
- Consentire retry nelle run successive per i video con stato `failed`.

## Impact
- Affected specs: ars-video-pipeline
- Affected code: `scripts/upload_single.py`, `src/logger.py` o utilità anagrafica
