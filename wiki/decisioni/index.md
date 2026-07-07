---
type: Decisione
title: Decisioni architetturali
description: Scelte rilevanti e il perché, in formato breve.
tags: [decisioni, adr]
timestamp: 2026-07-07T00:00:00Z
---

# Cloudflare AI Search (managed) invece di stack RAG self-hosted

Esisteva già una valutazione (`docs/rag/evaluation.md`, precedente a
questo lavoro) di uno stack self-hosted per il RAG sulle trascrizioni
(MarkItDown, LangChain, SentenceTransformers). Per il test attuale si è
scelto invece **Cloudflare AI Search**, un servizio gestito:

* **Perché**: zero infrastruttura da mantenere (embedding, vector index,
  chunking, reranking sono gestiti dalla piattaforma), piano free
  ampiamente sufficiente per un test (100.000 file/istanza, 20.000
  query/mese — vedi [tuning e valutazione](/wiki/ricerca-trascrizioni/tuning-e-valutazione.md)),
  integrazione diretta con R2 dove i dati vivono già nell'ecosistema
  Cloudflare del progetto.
* **Trade-off accettato**: meno controllo fine sulla pipeline di
  retrieval rispetto a uno stack self-hosted (es. niente scelta libera
  del modello di embedding, reranker limitato a un solo modello
  disponibile) — accettabile per una fase di test/beta.
* **Se lo stack self-hosted tornasse rilevante**: `docs/rag/evaluation.md`
  resta il punto di partenza per quella strada.

# Prima "labs" nascosta, poi rilascio pubblico

La ricerca nelle trascrizioni è stata lanciata come pagina non in menu,
esclusa da sitemap, con meta noindex e URL a slug casuale — non come
feature pubblica da subito.

* **Perché**: ha permesso di validare qualità del retrieval e limiti del
  piano free con traffico controllato. In quella fase sono emersi e sono
  stati corretti tre problemi sostanziali (reranking no-op, recall del
  solo vettoriale, chunk più lunghi della finestra del reranker) — vedi
  [tuning e valutazione](/wiki/ricerca-trascrizioni/tuning-e-valutazione.md).
* **Esito**: promossa a pagina pubblica `/ricerca/` (menu "Cerca") dopo
  l'estensione del corpus a tutte le trascrizioni e la stabilizzazione
  della configurazione. Il meccanismo "labs" (filtro sitemap + prop
  `noindex`) resta disponibile per futuri esperimenti.

# Corpus RAG dentro il workflow esistente, non uno separato

La generazione e sincronizzazione del corpus RAG (`data/rag_corpus/`)
sono state aggiunte come step finali di `transcripts_digests.yml`,
invece di creare un workflow GitHub dedicato.

* **Perché**: il corpus dipende direttamente dalle trascrizioni scaricate
  nello stesso workflow; aggiungerlo come step successivo evita di
  duplicare checkout, autenticazione e logica di commit di un workflow
  parallelo. Vedi [CI/CD](/wiki/ci-cd/index.md).
* **Costo del compromesso**: il corpus si aggiorna solo quando gira
  questo workflow (una volta a notte, o su `workflow_dispatch` manuale) —
  non in tempo reale rispetto al download di una singola trascrizione.
