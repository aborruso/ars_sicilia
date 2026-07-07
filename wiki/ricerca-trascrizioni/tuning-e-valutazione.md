---
type: Feature
title: Tuning e valutazione della ricerca
description: Metodologia di valutazione usata e scelte di configurazione dell'istanza Cloudflare AI Search, con il perché.
tags: [ricerca, cloudflare, rag, valutazione]
timestamp: 2026-07-07T00:00:00Z
---

# Formato del corpus

Scelto dopo un confronto tra alternative (SRT grezzo, TXT senza
timestamp, Markdown con marker per paragrafo), verificato anche contro
le pratiche correnti per RAG su trascrizioni video (letteratura di
settore, 2026): finestre di 30-120 secondi con timestamp per chunk sono
lo standard; il marker deve stare **dentro il testo del chunk**, non in
un campo metadata separato, perché il servizio scelto (Cloudflare AI
Search) applica chunking automatico per token e non garantisce un
metadato per singolo chunk (i metadata custom sono per-file, max 5
campi).

Risultato: paragrafi di ~60 secondi, marker `[HH:MM:SS]` inline
all'inizio del testo. Verificato che il marker sopravvive al chunking
automatico dell'istanza (chunk_size 1024 token > lunghezza tipica di un
paragrafo di 60s).

# Metodologia di valutazione

Un set di ~10 query rappresentative (termini isolati, frasi naturali,
domande) lanciate via `wrangler ai-search search --json`, confrontando
punteggio e pertinenza dei risultati in scenari diversi:

1. Baseline (10 documenti, reranking disattivato — default piattaforma).
2. Stesso corpus, con reranking attivato.
3. Corpus esteso a 20, poi a tutti gli 82 documenti disponibili.

# Osservazioni chiave

* **Senza reranking**, i punteggi (solo similarità vettoriale) erano
  schiacciati in un intervallo stretto (0.40-0.61), poco discriminante:
  query senza vero contenuto pertinente nel corpus (es. "sanità" quando
  nessun documento ne parlava) restituivano comunque match deboli sopra
  soglia — falsi positivi silenziosi.
* **Con reranking** (`@cf/baai/bge-reranker-base`, cross-encoder — non
  basta abilitare il flag, va anche impostato il modello, altrimenti
  resta un no-op), i punteggi dei match veri salgono a 0.77-0.97 e le
  query senza contenuto pertinente restituiscono onestamente **0
  risultati** invece di rumore. Trade-off: un passo di inferenza in più
  per query (latenza maggiore).
* **Corpus più grande non è sempre "solo meglio"**: alcune query che
  trovavano un match forte nel corpus da 20 documenti sono tornate a 0
  risultati con tutti gli 82 (es. "dimissioni gruppo parlamentare").
  Verificato che non è un problema di soglia (`--score-threshold 0`) né
  di ampiezza del pool pre-reranking (`--max-num-results` alzato a 30):
  il risultato non cambiava. Ipotesi più probabile: variabilità del
  retrieval vettoriale (ricerca approssimata) su un indice più grande,
  oppure la query generica compete con più chunk "simili" nel corpus
  esteso. **Da tenere d'occhio** se ricorre con corpus futuri più ampi:
  non è stata trovata una causa definitiva, solo escluse due ipotesi.
* Le query con termini/frasi esatte presenti nel testo (numeri di
  seduta, nomi propri, frasi istituzionali ricorrenti) ottengono i
  punteggi più alti e affidabili — coerente con la letteratura: il BM25
  (ricerca per parole chiave) tende a battere il solo vettoriale su
  nomi propri e ID, motivo per cui l'hybrid search (vedi sotto) resta
  un miglioramento plausibile non ancora implementato.

# Configurazione applicata (istanza `ars-sicilia-trascrizioni`)

| Parametro | Valore | Perché |
|---|---|---|
| `chunk_size` / `chunk_overlap` | 1024 token / 10% | Default piattaforma, coerente con paragrafi di ~60s |
| `reranking` | Attivo, modello `@cf/baai/bge-reranker-base` | Unico modello di reranking disponibile; salto di qualità netto (vedi sopra) |
| `score_threshold` | 0.4 | Default piattaforma; con reranking attivo si comporta bene (taglia i non-match) |
| `max_num_results` | 20 (default 10) | Tentativo di allargare il pool pre-reranking; non ha risolto il caso descritto sopra, ma non ha controindicazioni note |
| `hybrid_search` (keyword/BM25) | Non attivo | Non ancora testato; candidato per un miglioramento futuro dato il pattern sui nomi propri |

# Comandi utili per rivalutare

```bash
# stato indicizzazione
npx wrangler ai-search stats ars-sicilia-trascrizioni

# query di test
npx wrangler ai-search search ars-sicilia-trascrizioni --query "..." --json

# forzare un sync (utile dopo upload manuale su R2)
curl -X POST "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/ai-search/instances/ars-sicilia-trascrizioni/jobs" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN"

# modificare la configurazione
npx wrangler ai-search update ars-sicilia-trascrizioni --help
```

# Vedi anche

* [Architettura](architettura.md)
* [Decisioni](/wiki/decisioni/index.md)
