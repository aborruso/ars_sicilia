---
type: Pipeline
title: Trascrizioni e digest AI
description: Download dei sottotitoli via API YouTube e generazione dei digest con Gemini.
tags: [pipeline, youtube, llm]
timestamp: 2026-07-07T00:00:00Z
---

# Download trascrizioni

`scripts/download_transcripts.sh` → helper `scripts/download_caption_api.py`.
Usa la **YouTube Data API ufficiale** (`captions().list()` +
`captions().download(tfmt="srt")`) via OAuth — non l'estrazione via
yt-dlp (bloccata per IP in CI). Preferisce caption manuali su quelle ASR.

Per ogni `youtube_id` scrive:
* `data/trascrizioni/{youtube_id}.it.srt` — con timestamp
* `data/trascrizioni/{youtube_id}.it.txt` — testo puro derivato (rimossi
  numeri di sequenza, timestamp, righe vuote)

Video senza caption o con 404 finiscono in `data/trascrizioni/no_transcript.txt`.

# Generazione digest

`scripts/generate_digests.sh` → `llm -m gemini-2.5-flash -t config/digest.yaml
--schema config/digest-schema.json`. Due modalità (env `USE_LOCAL_TRANSCRIPTS`):

* **CI (`true`)**: usa solo i `.txt` locali già scaricati via API. Se manca,
  salta il video e riprova al run successivo. Mai `qv`.
* **Locale (`false`, default)**: scarica al volo con `qv "<url>" --text-only`.

Schema di output: vedi [dataset — digest AI](/wiki/architettura/dataset.md#digest-ai--schema-configdigest-schemajson).

# Automazione

Workflow GitHub "Transcripts and digests" (`transcripts_digests.yml`):
schedulato ogni notte (dopo il crawler e l'estrazione OdG), esegue in
sequenza download trascrizioni → digest → **rigenerazione e sync del
corpus RAG** → commit. Vedi [CI/CD](/wiki/ci-cd/index.md) e
[ricerca nelle trascrizioni](/wiki/ricerca-trascrizioni/architettura.md).

# Vedi anche

* [Acquisizione sedute e video](acquisizione.md)
* [Ricerca nelle trascrizioni](/wiki/ricerca-trascrizioni/index.md)
