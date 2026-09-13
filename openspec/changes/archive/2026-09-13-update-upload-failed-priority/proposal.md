# Change: update-upload-failed-priority

## Why
`upload_single.py` sceglie per primo un video con stato `failed`, e il workflow `daily_upload` interrompe il ciclo al primo errore (`|| break`). Un video che fallisce sempre viene quindi ritentato per primo ogni notte e blocca l'upload delle sedute nuove.

## What Changes
- La selezione del prossimo video privilegia i video mai tentati (senza `youtube_id` e senza stato `failed`), nell'ordine dell'anagrafica.
- I video `failed` restano eleggibili per retry, ma solo quando non ci sono video mai tentati; fra più `failed` si parte da quello con `last_check` più vecchio.
- Il workflow resta invariato (`|| break`).

## Impact
- Affected specs: ars-video-pipeline
- Affected code: `scripts/upload_single.py` (`get_first_unuploaded_video`)
