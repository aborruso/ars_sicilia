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

# La storia del tuning (cinque problemi trovati e corretti)

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

## 5. Domande in linguaggio naturale: riscrittura in-Worker

Le domande ("dove si parla di mafia?") davano 0 risultati: le parole
interrogative diluiscono il match e il reranker le affossa. Il
`query_rewrite` nativo di AI Search si è rivelato inadatto: col prompt
di default non riscrive quasi nulla, e con un prompt custom il modello
piccolo (llama-3.1-8b) **inventava** termini mai menzionati ("Cosa
Nostra", nomi di persone, date). **Fix**: riscrittura fatta nel Worker
con `env.AI.run` e llama-3.3-70b, prompt rigido (1-2 parole, SOLO
termini presenti nella domanda, vietato aggiungere nomi/luoghi/date);
la query riscritta passa poi per le euristiche già validate (1 parola →
keyword puro). Risultati: "dove si parla di mafia?" → "mafia" → 13
sedute; "quando si è discusso di siccità?" → "siccità" → 10/10. La
risposta espone `query_used` e la pagina mostra "(cercato: …)" per
trasparenza. Nota misurata: il reranker `bge-reranker-base` produce
punteggi non discriminanti (0.03-0.07) su QUALSIASI query italiana di
1-2 parole — non è un problema solo delle monoparola.

## 6. Test "da giornalista" e ultimi difetti della generazione

Validazione con temi reali dalle cronache ARS 2026 (trovati via ricerca
web): voto segreto, terzo mandato dei sindaci, quote rosa nelle giunte,
indennità ex Province, manovrina, sblocca assunzioni. Esiti e fix:

* Recall buono sui temi d'aula (voto segreto 6 sedute, consigliere
  supplente 7, terzo mandato 5); onesti 0 sul lessico giornalistico
  assente dal parlato d'aula ("manovrina", "grano duro" — verificato col
  grep: non nel corpus; in aula si dice "variazione di bilancio").
* La riscrittura delle domande limitata a 2 parole perdeva il tema
  distintivo ("voto segreto sul terzo mandato" → "Voto segreto"):
  allargata a 1-4 parole con prompt che privilegia i termini specifici.
* `chatCompletions` fa un retrieval interno guidato dall'ultimo
  messaggio user: passandogli la domanda originale, il reranker la
  uccideva e il modello rispondeva "nessuna informazione" anche con
  sedute trovate. Fix: al retrieval va la query riscritta (messaggio
  user), la domanda originale sta nel system prompt.
* La similarity cache serviva vecchie risposte negative a domande
  simili: cache disabilitata per la sola generazione (opt-in e rara);
  resta attiva per la ricerca.
* Prompt di generazione ristrutturato in regole ordinate (sintesi max
  150 parole, cita solo 2-4 fonti nel formato [fonte: FILE], frase fissa
  senza citazioni se non pertinente) e retrieval del generatore limitato
  a 8 passaggi: prima produceva risposte contraddittorie con decine di
  segnaposto.

## 7. Reranker inaffidabile anche su multi-parola: merge con BM25 puro

Caso reale segnalato dall'utente: "dove si parla della polemica su italo
belga e mondello?" (argomento verificato nel corpus, 4 sedute) tornava 1
solo passaggio, per giunta quello sbagliato — un paragrafo adiacente
(stesso file, 60s prima) su un argomento del tutto diverso (caccia
bombardieri/Roma), perché due temi erano finiti nello stesso chunk a
causa di un cambio di oratore a metà paragrafo, e il chunk col
contenuto vero era stato scartato dal reranker. **Fix**: per le query
multi-parola si lanciano sempre in parallelo hybrid+reranker E un ramo
BM25 puro (no reranker, "or", stopword italiane rimosse prima —
altrimenti "di", "e", "il" fanno matchare qualunque documento, vedi
sotto), risultati uniti e deduplicati per id. Risultato: da 1 a 9
passaggi pertinenti da 4 sedute, risposta AI corretta con citazioni
puntuali.

Effetto collaterale scoperto e corretto nello stesso giro: la modalità
`keyword_match_mode: "or"` matcha anche le stopword ("di" compare 5000+
volte nel corpus) — query totalmente estranee al corpus ("colonizzazione
di Marte") tornavano 20 falsi positivi. Fix: lista di stopword italiane
rimossa dalla query prima del solo ramo keyword (non dal ramo
semantico/reranked, che le gestisce già). Residuo accettato: il
reranker a volte assegna punteggi alti (0.9+) a passaggi vettorialmente
"più vicini" ma comunque non pertinenti quando il tema è assente dal
corpus (limite noto dei cross-encoder: restituiscono sempre un
migliore-tra-i-peggiori) — verificato che questo non produce risposte
AI errate: il modello resta onesto ("non contengono informazioni…")
anche con questi chunk nel contesto.

# Configurazione applicata (istanza `ars-sicilia-trascrizioni`)

| Parametro | Valore | Perché |
|---|---|---|
| `chunk_size` / `chunk_overlap` | **512 token** / 10% | Deve stare nella finestra del reranker (512); default 1024 lo accecava |
| `index_method` | vector + keyword (**hybrid**, fusione RRF) | Il solo vettoriale ha recall pessimo su termini esatti e nomi propri |
| `reranking` | Attivo, `@cf/baai/bge-reranker-base` | Separa nettamente match veri da rumore (0.77-0.97 vs sotto soglia) |
| `keyword_match_mode` | "or" (override nel Worker, per request) | "and" azzera il recall delle query naturali multi-parola |
| Query monoparola | keyword-only, no rerank, soglia 0.1 (euristica nel Worker) | Il reranker azzera le query italiane di una parola; BM25 è già autorevole |
| Domande | riscrittura in-Worker (llama-3.3-70b, prompt rigido) → euristiche standard | Il query_rewrite nativo non riscrive (default) o inventa (8b + prompt custom) |
| Risposta AI | opt-in (checkbox `?ai=1`), `chatCompletions` con llama-3.3-70b e system prompt "solo dai passaggi" | Generazione = costo+latenza+rischio allucinazione: mai come default |
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
