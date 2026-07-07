---
type: Feature
title: Tuning e valutazione della ricerca
description: Metodologia di valutazione usata e scelte di configurazione dell'istanza Cloudflare AI Search, con il perché.
tags: [ricerca, cloudflare, rag, valutazione]
timestamp: 2026-07-08T00:00:00Z
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
all'inizio del testo.

# Metodologia di valutazione

Un set di ~10 query rappresentative (termini isolati, frasi naturali,
domande) lanciate via `wrangler ai-search search --json` o via REST,
confrontando punteggio e pertinenza dei risultati in scenari diversi.
Fondamentale il **controllo di verità sul corpus sorgente** (`grep -ic
"termine" data/rag_corpus/*.md`): permette di distinguere "il tema non
c'è" da "la ricerca non lo trova".

# La storia del tuning (tre problemi trovati e corretti)

## 1. Senza reranking: punteggi piatti e falsi positivi

I punteggi di sola similarità vettoriale erano schiacciati (0.40-0.61):
query senza vero contenuto pertinente restituivano comunque match deboli
sopra soglia. **Fix**: reranking con `@cf/baai/bge-reranker-base`
(cross-encoder; attenzione: abilitare il flag non basta, va impostato
anche il modello, altrimenti è un no-op). I match veri salgono a
0.77-0.97, i non-match scendono sotto soglia.

## 2. Solo vettoriale: recall pessimo sui termini esatti

Caso emblematico: "siccità" compare in **10 sedute su 82**, ma la
ricerca ne restituiva **1**. Con una query di una parola sola, i chunk
in cui il termine compare una volta dentro un lungo dibattito generico
non sono abbastanza "simili" semanticamente e non entrano nemmeno nel
pool di candidati. Due aggravanti scoperte per strada: il tokenizer
keyword **non normalizza gli accenti** ("siccita" → 0 risultati) e la
**similarity cache** (attiva, "strong") fa sembrare inefficaci gli
override per-request perché risponde dalla cache sulla stessa query.
**Fix**: hybrid search attivato (`index_method.keyword: true`, fusione
RRF) — richiede re-indicizzazione completa, che parte da sola al cambio
di configurazione.

## 3. Reranker cieco: chunk più lunghi della sua finestra

Anche con l'hybrid attivo, "siccità" tornava solo 3 sedute e "precari
lavoratori licenziati" 0 — ma disattivando il reranking per-request la
fusione RRF trovava **12 sedute** con punteggi sani. Causa:
`bge-reranker-base` accetta **max 512 token di input**, mentre i chunk
erano da **1024 token** → il reranker vedeva solo la prima metà di ogni
chunk e azzerava il punteggio dei match nella seconda metà; la soglia
0.4 falciava tutto. Diagnosi fatta leggendo gli `scoring_details` della
risposta (vector_score / keyword_score / rank per ramo). **Fix**:
`chunk_size` ridotto a 512 token (altra re-indicizzazione automatica).
Bonus: chunk più corti = marker `[HH:MM:SS]` più vicino al punto esatto,
quindi deep-link più precisi.

Inoltre il default `keyword_match_mode: "and"` (tutti i termini della
query devono comparire nel documento) penalizza le query naturali
multi-parola: il Worker proxy ora passa `keyword_match_mode: "or"` come
override per-request (scelta versionata nel repo, non nella config
dell'istanza — l'endpoint REST per aggiornare `retrieval_options`
dell'istanza non è risultato disponibile).

## 4. Query di una sola parola: il reranker le azzera

Anche a configurazione sistemata, "caccia" o "siccità" da sole davano 0
risultati: il cross-encoder `bge-reranker-base` (addestrato
prevalentemente su inglese) assegna punteggi quasi nulli a una singola
parola italiana confrontata con un chunk lungo — nemmeno con soglia
0.05 passava qualcosa, mentre le query multi-parola escono a 0.7-0.9.
**Fix (euristica nel Worker)**: se la query è una parola sola →
`retrieval_type: "keyword"` (BM25 puro), reranking disattivato, soglia
0.1, pool 20 — il match keyword è già autorevole (il chunk contiene la
parola = è pertinente) e il recall torna completo ("siccità": 10 sedute
su 10, verificato col grep). Query multi-parola → hybrid + reranker come
prima. Nota: anche l'header del corpus è stato ridotto al solo titolo —
URL e ID nei metadati facevano da esca per query contenenti quei token
(scoperto incollando per sbaglio l'URL della pagina nel campo di
ricerca: 10 "risultati" al 74%).

# Configurazione applicata (istanza `ars-sicilia-trascrizioni`)

| Parametro | Valore | Perché |
|---|---|---|
| `chunk_size` / `chunk_overlap` | **512 token** / 10% | Deve stare nella finestra del reranker (512); default 1024 lo accecava |
| `index_method` | vector + keyword (**hybrid**, fusione RRF) | Il solo vettoriale ha recall pessimo su termini esatti e nomi propri |
| `reranking` | Attivo, `@cf/baai/bge-reranker-base` | Separa nettamente match veri da rumore (0.77-0.97 vs sotto soglia) |
| `keyword_match_mode` | "or" (override nel Worker, per request) | "and" azzera il recall delle query naturali multi-parola |
| Query monoparola | keyword-only, no rerank, soglia 0.1 (euristica nel Worker) | Il reranker azzera le query italiane di una parola; BM25 è già autorevole |
| `score_threshold` | 0.4 | Default; con reranking efficace taglia bene il rumore |
| `max_num_results` | 20 | Pool più ampio per la fusione/reranking |
| similarity cache | Attiva, "strong" | Risparmia quota; da tenere presente nei test (stessa query = risposta cache) |

# Lezioni per test futuri

* Verificare sempre la verità sul corpus con grep prima di giudicare il retrieval.
* Nei test A/B via API, variare il testo della query o disabilitare la cache per-request, altrimenti si confrontano risposte cache identiche.
* Leggere `scoring_details` per capire quale ramo (vettoriale/keyword) trova cosa e dove il punteggio si perde.
* Controllare la compatibilità tra `chunk_size` e finestra di input del reranker.

# Comandi utili per rivalutare

```bash
# stato indicizzazione
npx wrangler ai-search stats ars-sicilia-trascrizioni

# query di test
npx wrangler ai-search search ars-sicilia-trascrizioni --query "..." --json

# verità sul corpus
grep -ic "termine" data/rag_corpus/*.md | grep -v ":0$"

# forzare un sync (utile dopo upload manuale su R2)
curl -X POST "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/ai-search/instances/ars-sicilia-trascrizioni/jobs" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN"

# modificare la configurazione
npx wrangler ai-search update ars-sicilia-trascrizioni --help
```

# Vedi anche

* [Architettura](architettura.md)
* [Decisioni](/wiki/decisioni/index.md)
