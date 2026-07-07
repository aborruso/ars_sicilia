---
type: Feature
title: Architettura della ricerca nelle trascrizioni
description: Corpus RAG, bucket R2, istanza Cloudflare AI Search, Worker proxy e pagina di ricerca.
tags: [ricerca, cloudflare, rag]
timestamp: 2026-07-07T00:00:00Z
---

# Perché

Le trascrizioni dei video (`data/trascrizioni/*.it.srt`) esistevano già
ma non erano ricercabili. Obiettivo: una ricerca in linguaggio naturale
che porti dal risultato al punto esatto del video in cui se ne parla —
non solo full-text, ma **deep-link al secondo**, possibile perché gli
SRT contengono i timestamp.

# Componenti

```
SRT (data/trascrizioni/) → corpus Markdown (data/rag_corpus/)
    → bucket R2 → Cloudflare AI Search (indicizzazione + retrieval)
    → Worker proxy (CORS, nessuna credenziale esposta)
    → pagina Astro (fetch + render risultati + link al video)
```

1. **Corpus** (`scripts/build_rag_corpus.py`) — converte ogni SRT in un
   file Markdown `{youtube_id}.md`: header con metadati seduta (numero,
   data, URL pagina video) + corpo in paragrafi aggregati (~60 secondi)
   con marker `[HH:MM:SS]` inline. Il marker è ciò che permette, dato un
   passaggio trovato, di risalire al secondo di partenza.
   Motivazione del formato: vedi
   [tuning e valutazione](tuning-e-valutazione.md).

2. **Bucket R2** (`ars-trascrizioni`) — sorgente dati dell'istanza AI
   Search. Caricamento con `scripts/upload_rag_corpus.sh` (locale) o dal
   [workflow CI](/wiki/ci-cd/index.md) (automatico).

3. **Istanza Cloudflare AI Search** (`ars-sicilia-trascrizioni`) —
   indicizza il bucket automaticamente (sync su schedule interno, oppure
   forzabile con un job via API: `POST .../ai-search/instances/{name}/jobs`).
   Configurazione e razionale: vedi
   [tuning e valutazione](tuning-e-valutazione.md).

4. **Worker proxy** (`cloudflare/search-proxy/`) — espone un endpoint
   `POST /search` che il sito chiama via `fetch`. Usa il **binding
   nativo** `[[ai_search]]` di Wrangler (non un token esposto lato
   client): il Worker gira nell'account Cloudflare e ha accesso diretto
   all'istanza. CORS ristretto al dominio del sito e a `localhost:4321`
   per lo sviluppo locale.

5. **Pagina** (`src/pages/ricerca/index.astro`, URL `/ricerca/`) —
   linkata nel menu principale ("Cerca"). Nata come pagina "labs"
   nascosta (slug casuale, noindex, fuori sitemap) per la fase di test,
   promossa a pagina pubblica dopo la validazione del retrieval; il
   filtro sitemap `/labs/` in `astro.config.mjs` e la prop `noindex` dei
   layout restano disponibili per futuri esperimenti (vedi
   [sito Astro](/wiki/frontend/sito-astro.md)).

   Pattern di ricerca client-side riusato da `src/pages/ddl/[page].astro`
   (fetch, stato, sync `?q=` nell'URL). Ogni risultato mostra: seduta,
   data, estratto, punteggio di rilevanza, link alla pagina video con
   `?t=SECONDI` (che `VideoEmbed.astro` traduce in `start=` sull'iframe)
   e link diretto a YouTube (`&t=Ns`). Sotto il campo, suggerimenti
   d'uso basati sui limiti misurati del retrieval (più parole = meglio,
   accenti richiesti).

# Vedi anche

* [Dataset](/wiki/architettura/dataset.md) — dove sta `data/rag_corpus/` nel contratto dati
* [CI/CD](/wiki/ci-cd/index.md) — come il corpus resta sincronizzato
* [Decisioni](/wiki/decisioni/index.md) — perché Cloudflare AI Search
