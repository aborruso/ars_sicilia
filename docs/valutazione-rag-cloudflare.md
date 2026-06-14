Valutazione: search RAG su trascrizioni e PDF con Cloudflare AI Search

Data: 2026-06-14. Stato: valutazione (nessuna implementazione).
Domanda: ha senso aggiungere al sito un search che fa RAG su trascrizioni e testi dei PDF? Cloudflare AI Search è adeguato e a che costi?

## I 3 livelli di ricerca (scegliere il livello giusto)

"Trova dove si parla di X" ha due sfumature: per **nome/entità esatta** (es. *Mondello*, un toponimo: la parola compare letteralmente) e per **concetto/sinonimi** (es. "sanità" → testi che dicono "ospedali", "ASP", "pronto soccorso" senza la parola "sanità"). La keyword pura copre la prima, non la seconda.

| Livello | "Mondello" (entità) | "sanità" → ospedali (concetto) | Risposta sintetizzata | Costo / infra |
|---|---|---|---|---|
| **1. Lessicale** (Pagefind, Algolia base) | sì | no | no | €0 / statico |
| **2. Semantico / ibrido — retrieval only** (Cloudflare AI Search *search mode*, Algolia NeuralSearch, Typesense/Meilisearch/Orama hybrid) | sì | sì | no (restituisce passaggi + link) | backend o SaaS |
| **3. RAG** (semantico + LLM) | sì | sì | sì | + costo LLM + rischio allucinazioni |

Note:
- Il **livello 2** è il *retrieval* del RAG usato **da solo**: trova per significato, restituisce link alle sedute, **niente allucinazioni e niente costo di generazione**. È spesso il punto giusto per "dove si parla di X".
- Il semantico (liv. 2-3) richiede **embeddings** sia sui testi (a build) sia sulla query (a runtime) → serve un servizio/backend, oppure un modello WASM in-browser (es. transformers.js con Orama). Pagefind (liv. 1) non fa semantico.
- I livelli sono **complementari**: si può fare lessicale/semantico per "trova dove" + RAG per "rispondi su".

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

Scegliere il **livello** prima del prodotto (vedi tabella in alto):
- Se basta cercare nomi/entità (es. *Mondello*): **livello 1 lessicale** → **Pagefind**, €0 e statico.
- Per "dove si parla di X" anche concettuale (sinonimi/parafrasi): serve **livello 2 semantico/ibrido, retrieval-only** — restituisce passaggi + link senza generare risposte (niente allucinazioni, niente costo LLM). Candidati: Cloudflare AI Search in *search mode*, oppure Orama in-browser (€0 ma più lavoro), o Typesense/Meilisearch self-host.
- Solo se serve la **risposta sintetizzata** in linguaggio naturale: **livello 3 RAG** (Cloudflare AI Search completo), con i caveat di backend/costo/allucinazioni.

Mossa pragmatica: **pilot gratuito durante la beta** (Cloudflare AI Search) **sulle sole trascrizioni** già pronte, provando prima la **modalità search (liv. 2)** e poi eventualmente la generazione (liv. 3), per misurare la qualità in italiano prima di investire nell'estrazione dei testi PDF. Per partire subito a costo/rischio zero sul caso "trova entità", **Pagefind** (liv. 1).

Collegamenti: [search-engine-analysis.md](search-engine-analysis.md) · [future-ideas.md](future-ideas.md)
