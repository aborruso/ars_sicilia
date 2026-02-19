## Context
Il progetto mantiene un archivio persistente delle trascrizioni in `data/trascrizioni/` tramite `scripts/download_transcripts.sh`. Oggi lo script dipende da `yt-dlp`; la richiesta è sostituire solo questo punto con API ufficiali YouTube, lasciando invariati file prodotti e fasi successive.

## Goals / Non-Goals
- Goals: usare YouTube Data API per il download caption automatiche; preservare output `.it.srt`/`.it.txt`; mantenere semantica operativa corrente dello script.
- Non-Goals: modificare `scripts/generate_digests.sh` (rimane su `qv`), cambiare formato archivio trascrizioni, cambiare workflow CI.

## Decisions
- Implementare un helper Python dedicato al download caption via `captions.list` + `captions.download` con `tfmt=srt`.
- Integrare l'helper in `scripts/download_transcripts.sh` come sostituto della chiamata `yt-dlp`.
- Considerare idonea la prima caption italiana disponibile (priorità a `language=it`), inclusi track `asr`.
- In assenza caption italiana scaricabile, mantenere il comportamento esistente: warning e append a `no_transcript.txt`.

## Risks / Trade-offs
- Dipendenza da OAuth token valido: se `config/token.json` scade/revoca, lo script fallisce finché non viene rigenerato.
- Alcuni video potrebbero avere solo caption non italiane o nessuna caption: il numero di `no_transcript` può aumentare rispetto a `yt-dlp` in edge case.
- API quota: chiamate aggiuntive `captions.list`/`captions.download` per video.

## Migration Plan
- Nessuna migrazione dati: i file già presenti in `data/trascrizioni/` restano validi.
- Script idempotente: i file esistenti continuano a essere saltati.
