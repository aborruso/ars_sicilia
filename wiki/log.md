# Log wiki

## 2026-07-08
* **Update**: riscritta [tuning e valutazione](ricerca-trascrizioni/tuning-e-valutazione.md) dopo l'indagine sul caso "siccità" (10 sedute nel corpus, 1 sola restituita): attivato hybrid search (BM25+vettoriale, fusione RRF), ridotto `chunk_size` a 512 token perché il reranker `bge-reranker-base` ha finestra di input di 512 token e con chunk da 1024 vedeva solo metà del testo, `keyword_match_mode: "or"` come override nel Worker. Documentate anche le insidie di test (similarity cache, accenti non normalizzati dal tokenizer keyword).

## 2026-07-07
* **Creazione**: costituito il wiki di progetto (formato OKF), con sezioni [architettura](architettura/), [pipeline](pipeline/), [frontend](frontend/), [ricerca nelle trascrizioni](ricerca-trascrizioni/), [ci-cd](ci-cd/), [decisioni](decisioni/).
* **Creazione**: documentata la feature sperimentale di ricerca semantica sulle trascrizioni (Cloudflare AI Search), inclusa la metodologia di valutazione e le scelte di tuning (reranking, chunking, soglie).
