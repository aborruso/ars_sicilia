Valutazione: search RAG su trascrizioni e PDF con Cloudflare AI Search

Data: 2026-06-14. Stato: valutazione (nessuna implementazione).
Domanda: ha senso aggiungere al sito un search che fa RAG su trascrizioni e testi dei PDF? Cloudflare AI Search è adeguato e a che costi?

## Cos'è Cloudflare AI Search

Servizio RAG **gestito** di Cloudflare (ex **AutoRAG**, rinominato AI Search): ingestione → chunking → embedding → vector store → retrieval (ibrido semantico + keyword, con metadata filtering) → generazione della risposta. Tutto managed: niente vector DB o orchestrazione da gestire.

Interfacce di interrogazione: **REST API**, **Worker binding**, **MCP server**, più UI embeddabile. Indicizzazione automatica/continua dalla sorgente. Le istanze nuove (post-16/4/2026) includono storage e vector index integrati.

Fonti: <https://developers.cloudflare.com/ai-search/>

## Volume dati del sito (misurato il 2026-06-14)

| Fonte | Stato | Volume |
|---|---|---|
| Trascrizioni `.txt` (`data/trascrizioni/`) | pronte | 59 file, ~2 MB, ~456k parole → ~900 chunk (~500 parole) |
| Digest (`data/digest/`) | pronti | 59 file |
| Testi PDF resoconti / OdG | **non archiviati** | solo URL + DDL estratti dall'OdG |
| Studi e pubblicazioni | metadati | 252 record (no full-text) |

Punto critico: le **trascrizioni sono pronte**; i *testi dei PDF* (resoconti stenografici, i più ricchi) **non sono ancora estratti**. Per includerli serve una pipeline di estrazione full-text dei resoconti (analoga a OdG→DDL, ma estraendo tutto il testo).

## Adeguatezza

Pro:
- Volume **minuscolo** rispetto ai limiti (900 chunk vs 100k file; poche query/mese vs 20k/mese free).
- Managed: nessuna infrastruttura RAG da gestire.
- Si integra con un **sito statico** (GitHub Pages senza backend): il sito chiama un endpoint.
- Hybrid search + citazioni → risposte con fonti linkabili (coerente con il requisito deep-linking).

Rischi / attenzioni:
- **Serve un backend minimo**: l'API richiede un token Cloudflare, **non esponibile nel sito statico** → necessario un **Worker proxy** (free tier) per token, CORS e rate-limit.
- **Ingestione**: le trascrizioni vanno caricate nello storage di AI Search (upload da CI dopo `generate_digests`); il web-crawler vedrebbe solo i digest pubblicati, non le trascrizioni complete.
- **Italiano**: qualità dipendente dai modelli Workers AI (embedding multilingue tipo bge-m3 + LLM tipo Llama) → **da testare** su testo parlamentare.
- **Allucinazioni**: mostrare sempre le **fonti** (link a seduta/minuto); trattare la risposta come sintesi.
- **Lock-in Cloudflare** e **pricing post-beta ignoto** (i dati restano nostri → migrabile).

## Costi

- **Open beta: €0** entro i limiti (Free: 100k file/istanza, 20.000 query/mese, 500 pagine crawl/giorno, max file 4 MB). Ampiamente sufficienti.
- Avviso ufficiale: "i prezzi saranno comunicati almeno 30 giorni prima dell'inizio della fatturazione".
- **Post-beta (stima ordine di grandezza)** a questo volume: probabilmente **pochi €/mese** (indicizzazione una-tantum trascurabile; costo dominato dalla generazione LLM per query). Worker proxy nel free tier per traffico modesto.

Fonte limiti/prezzi: <https://developers.cloudflare.com/ai-search/platform/limits-pricing/>

## Alternativa: Pagefind

Full-text classico, **100% statico, €0, nessun backend** (vedi `search-engine-analysis.md`). Non è RAG (niente risposte sintetizzate, solo match), ma su ~900 chunk copre bene "trova dove si è parlato di X". È il "buono a costo zero"; il RAG è il "di più" (risposte in linguaggio naturale) con backend e costi/rischi.

## Architettura proposta (se si procede)

1. CI carica trascrizioni (e poi testi PDF estratti) nello storage di AI Search dopo `generate_digests`.
2. Cloudflare AI Search indicizza (chunk + embedding + vector).
3. **Worker proxy** (Cloudflare) nasconde il token, espone un endpoint con CORS verso il sito.
4. Sito Astro: pagina `/cerca` con input → fetch al Worker → risposta sintetizzata + **fonti** (link alle sedute, deep-link). Query condivisibile via `?q=` (requisito deep-linking).

## Raccomandazione

Il RAG ha senso e Cloudflare AI Search è un buon candidato, ma introduce un backend (Worker) e una dipendenza con pricing futuro incerto. Mossa pragmatica: **pilot gratuito durante la beta, solo sulle trascrizioni** (già pronte), per misurare la qualità in italiano prima di investire nell'estrazione dei testi PDF. In assenza di budget/voglia di backend, **Pagefind** copre gran parte del bisogno a costo zero.

Collegamenti: [search-engine-analysis.md](search-engine-analysis.md) · [future-ideas.md](future-ideas.md)
