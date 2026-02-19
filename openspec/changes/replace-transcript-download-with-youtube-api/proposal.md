# Change: Replace transcript archive download with YouTube API

## Why
Il download archivio trascrizioni (`scripts/download_transcripts.sh`) usa oggi `yt-dlp`, che può essere instabile o bloccato per rate-limit/IP. È stato verificato che le credenziali OAuth YouTube del progetto permettono il recupero delle caption automatiche (`trackKind=asr`) via API ufficiali.

## What Changes
- Sostituire nel solo `scripts/download_transcripts.sh` il recupero trascrizioni da `yt-dlp` a YouTube Data API (`captions.list` + `captions.download`).
- Mantenere invariato il formato di output della pipeline corrente: `data/trascrizioni/<youtube_id>.it.srt` e `data/trascrizioni/<youtube_id>.it.txt`.
- Preservare il comportamento esistente su skip file già presenti e tracciamento `no_transcript.txt` quando non ci sono caption utilizzabili.

## Impact
- Affected specs: `transcript-download` (new capability)
- Affected code/docs (implementation phase): `scripts/download_transcripts.sh`, nuovo helper Python/API per captions, `scripts/README.md`, `README.md`
