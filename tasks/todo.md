# Task: ricerca full-text trascrizioni con Cloudflare AI Search (pagina test nascosta)

Piano completo: vedi piano approvato (Cloudflare AI Search, Worker proxy, pagina `/labs/ricerca-<random>/`).
Documentazione di progetto (formato OKF): [wiki/](../wiki/index.md), in particolare
[wiki/ricerca-trascrizioni/](../wiki/ricerca-trascrizioni/index.md).

## Fase 0 — Corpus RAG (valutazione formato)
- [x] `scripts/build_rag_corpus.py`: SRT → Markdown con marker `[HH:MM:SS]` per paragrafo (~60 s)
- [x] Corpus esteso a **tutti gli 82 SRT disponibili** (`data/rag_corpus/*.md`), non solo i 10 di test iniziali
- [x] Variante di confronto → scelta marker inline (coerente con pratiche RAG-su-video)

## Fase 1 — Setup Cloudflare
- [x] Bucket R2 `ars-trascrizioni` popolato con tutti gli 82 file
- [x] Istanza AI Search `ars-sicilia-trascrizioni` creata (utente, dashboard) e indicizzata (82/82, 0 errori)
- [x] Valutazione con ~10 query di test: senza reranking punteggi indistinguibili (0.4-0.6) e falsi positivi; con reranking (`@cf/baai/bge-reranker-base`) punteggi 0.77-0.97 sui match veri, 0 risultati onesti sui non-match
- [x] Tuning applicato: reranking attivo, `max_num_results` 20 — dettagli e osservazioni aperte in [wiki/ricerca-trascrizioni/tuning-e-valutazione.md](../wiki/ricerca-trascrizioni/tuning-e-valutazione.md)

## Fase 2 — Worker proxy
- [x] `cloudflare/search-proxy/` (binding nativo `[[ai_search]]`, CORS aborruso.github.io + localhost:4321)
- [x] Deploy fatto, bug fix (risposta `search()` usa `result.chunks`, non `result.data`), verificato via curl

## Fase 3 — Pagina nascosta
- [x] `src/pages/labs/ricerca-035553.astro`, sitemap filter + noindex, nota "powered by Cloudflare AI Search"
- [x] Verificata in locale (screenshot utente): query in linguaggio naturale, risultati con timestamp e link

## Fase 4 — Deep-link al secondo
- [x] `VideoEmbed.astro`: legge `?t=` → iframe `?start=`
- [ ] Non ancora verificato end-to-end il click reale dal risultato al secondo esatto nel player

## Automazione (GitHub Actions)
- [x] `transcripts_digests.yml` esteso: dopo trascrizioni+digest, rigenera il corpus RAG, carica su R2 solo i file nuovi/cambiati (`git status --porcelain`), forza un sync job via API, committa
- [x] Secret `CLOUDFLARE_API_TOKEN` e `CLOUDFLARE_ACCOUNT_ID` impostati nel repo (fatto dall'utente)
- [ ] Non ancora testato con un run reale del workflow (né `workflow_dispatch` né schedulato)

## Wiki di progetto
- [x] `wiki/` creato in formato OKF: architettura, dataset, pipeline, frontend, ricerca-trascrizioni, ci-cd, decisioni
- [x] Verificati tutti i link interni; verificata assenza di dati sensibili (account ID, token, slug pagina nascosta)

## Ancora da fare
- [ ] Commit e push di tutto il lavoro (finora solo locale)
- [ ] Test end-to-end del workflow GitHub (dispatch manuale consigliato prima di aspettare lo schedule notturno)
- [ ] Eventuale hybrid search (BM25+vettoriale) — candidato di miglioramento, non ancora provato

## Review
Feature realizzata end-to-end e funzionante in locale: ricerca semantica su tutte le
trascrizioni disponibili (82 sedute), con tuning basato su valutazione empirica (il
reranking è stato il cambio con l'impatto maggiore). Automazione predisposta perché il
corpus resti sincronizzato ad ogni nuova trascrizione scaricata, senza intervento manuale.
Aperta un'osservazione non risolta (query che perdono match forte quando il corpus cresce)
documentata nel wiki per non perderla. Prossimo passo naturale: commit, push, e un run di
prova del workflow.
