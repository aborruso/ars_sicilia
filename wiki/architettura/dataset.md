---
type: Dataset
title: Contratto dati (data/)
description: Schema e semantica di ciascun dataset pubblico che collega backend e frontend.
tags: [architettura, dati]
timestamp: 2026-07-07T00:00:00Z
---

# Dataset pubblici in `data/`

| File/directory | Contenuto | Chiave di join |
|---|---|---|
| `data/anagrafica_video.csv` | Metadati seduta/video (una riga per video; le sedute aggregano righe per `numero_seduta` + `data_seduta`) | `youtube_id` |
| `data/disegni_legge.jsonl` | Disegni di legge estratti dai PDF d'ordine del giorno (OdG) | join su `odg_url` ↔ `pdf_url` |
| `data/digest/{youtube_id}.json` | Digest AI per video (digest con corpo ≤10 caratteri vengono scartati come vuoti) | `youtube_id` |
| `data/trascrizioni/{youtube_id}.it.srt` / `.it.txt` | Trascrizione con timestamp (SRT) e testo puro (TXT) | `youtube_id` |
| `data/rag_corpus/{youtube_id}.md` | Corpus derivato per la ricerca semantica, vedi [ricerca-trascrizioni](/wiki/ricerca-trascrizioni/index.md) | `youtube_id` |

`youtube_id` è la chiave universale che collega CSV, trascrizioni, digest
e corpus RAG.

# Colonne di `anagrafica_video.csv`

```
numero_seduta, data_seduta, url_pagina, odg_url, resoconto_url,
resoconto_provvisorio_url, resoconto_stenografico_url, allegato_url,
id_video, ora_video, data_video, stream_url, video_page_url,
youtube_id, last_check, status, failure_reason, duration_minutes, no_transcript
```

# Digest AI — schema (`config/digest-schema.json`)

3 campi, tutti obbligatori:

* `digest` (string) — riassunto Markdown, 200-400 parole, in italiano.
* `categories` (array di string) — da 1 a 5 categorie tematiche scelte dal vocabolario
  controllato `data/vocabolario_categorie.json` (22 voci ancorate a concetti EuroVoc;
  enum imposto dallo schema, propagato da `scripts/sync_vocabolario.mjs`).
* `people` (array di oggetti `{name, role}`) — persone citate con ruolo.

# Trascrizioni

Scaricate via YouTube Data API ufficiale (`captions().download(tfmt="srt")`),
preferendo caption manuali su quelle ASR. Ogni SRT viene derivato in TXT
rimuovendo numeri di sequenza, timestamp e righe vuote — vedi
[trascrizioni e digest](/wiki/pipeline/trascrizioni-digest.md).

# Output processato (`src/data/processed/`)

Generato da `scripts/build-data.mjs` (prebuild Astro), non è un dataset
sorgente ma la vista aggregata che il frontend consuma:
`sedute.json`, `videos.json`, `ddls.json`, `categories.json`.

# Vedi anche

* [Panoramica architetturale](panoramica.md)
* [Pipeline di acquisizione](/wiki/pipeline/index.md)
