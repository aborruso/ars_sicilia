# 2026-08-12

## Fix workflow `extract_odg` rotto da openai 3.0.0

- Il job schedulato falliva su `uv tool run llm install llm-gemini` con `ModuleNotFoundError: No module named 'httpx'`.
- Causa a monte: `llm==0.32` fa `import httpx` ma non lo dichiara tra le dipendenze (arrivava transitivamente da `openai`); `openai==3.0.0` è passato a `httpx2<3,>=2.7.0` e `llm` non ha tetto sulla versione, quindi nell'env finisce `httpx2` e l'import esplode.
- Fix in `.github/workflows/extract_odg.yml`: `uv tool install llm --with httpx`. Preferito al pin `openai<3` perché la pipeline passa da `llm-gemini` e il client openai non viene mai usato.
- Stesso rischio in locale: `generate_digests.sh` usa l'`llm` installato con `uv tool`, che regge solo perché precedente a openai 3.0.0 — si romperà al prossimo `uv tool upgrade llm` (rimedio: `uv tool install llm --with httpx --force`).
- Segnalato a monte: issue [simonw/llm#1608](https://github.com/simonw/llm/issues/1608) e PR da una riga [simonw/llm#1609](https://github.com/simonw/llm/pull/1609) (dichiarare `httpx` in `dependencies`).
- Secondo difetto emerso testando il loro repo, segnalato nella #1608 ma non corretto da noi: sotto openai 3 `pytest-httpx` non intercetta più (mocka `httpx`, openai usa `httpx2`) e i test partono verso `api.openai.com` per davvero. A/B su venv puliti: `tests/test_openai_responses.py` fa 64 passed con openai 2.54.0, 18 failed/46 passed/18 errors con 3.0.0.

# 2026-07-28

## Analisi della ricerca RAG sulle trascrizioni

- Report in `docs/rag/report-analisi-ricerca.md`: analisi di architettura + 12 test dal vivo sul Worker con ground truth via grep.
- Conferme: recall pieno su entità/monoparola, riscrittura domande affidabile, risposta AI corretta (~13 s).
- Problemi: tetto 20 risultati taglia il recall sui temi frequenti ("sanità" 12/41 sedute); falsi positivi al 90-100% su query fuori corpus; rumore "or" sulle frasi generiche; refusi ASR sui cognomi ("Cracoligi"); endpoint senza rate limiting; le query senza accento ora funzionano (UI e wiki dicono il contrario → piattaforma cambiata).
- Raccomandazioni prioritarie: max_num_results 50 + raggruppamento per seduta, flag "nessuna corrispondenza esatta", "and" con fallback "or", suite di regressione con golden set.
- Piano operativo con checklist in `docs/rag/piano-miglioramenti.md` (14 interventi in 3 fasce di priorità).

# 2026-07-22

## Fix digest con `##` che rompevano la leggibilità

- Segnalato il digest del video seduta 265 ore 15:44 (`hQ2AD_ax0Mw`): pieno di `##` che `marked` rendeva come heading spurii. Su ~85 digest solo 4 rotti (gli altri usano `## Titolo` a inizio riga, corretto); artefatto intermittente di gemini-2.5-flash con modalità diverse: blob monolinea con `## tema ##` inline (hQ2AD, BvrMdfTH9Do), `\n` letterali al posto dei ritorni a capo (iD9fvoidp7Y), `**## Titolo**` bold+heading mescolati (kYX47otETyE).
- `config/digest.yaml`: regole di formattazione markdown (heading solo a inizio riga, enfasi con `**`, veri ritorni a capo, mai `\n` letterali) — prevenzione.
- `build-data.mjs`: `normalizeDigestMarkdown()` al caricamento — converte `\n` letterali e rimuove i `#{2,}` inline preservando gli heading a inizio riga (difesa in profondità sui digest futuri).
- Dati riparati: hQ2AD e BvrMdfTH9Do (struttura persa) rigenerati dal transcript col prompt aggiornato; iD9fvoidp7Y e kYX47otETyE (struttura intatta) puliti con la stessa trasformazione deterministica.
- Modello pipeline invariato (gemini-2.5-flash, ancora free-tier). Nota: il free-tier ora raccomanda `gemini-3-flash-preview`, valutabile in futuro.

# 2026-07-11

## Categorie sedute: vocabolario controllato EuroVoc

- Problema: categorie dei digest generate liberamente dal LLM → 131 voci distinte, 112 usate ≤3 volte.
- Nuovo `data/vocabolario_categorie.json`: 22 categorie chiuse, label IT citizen-friendly, ognuna ancorata a un concetto EuroVoc (URI verificati sul dump locale `data/eurovoc/`).
- `scripts/sync_vocabolario.mjs` propaga il vocabolario verso `config/digest-schema.json` (enum, 1–5 categorie, uniqueItems) e `config/digest.yaml` (elenco con descrizioni tra marker) — unica fonte di verità, pipeline digest invariata per il resto.
- Storico normalizzato: `data/category_mapping.json` (131 → 22, revisionabile) applicato una tantum da `scripts/remap_digest_categories.mjs` agli 82 digest — solo l'array `categories` toccato, zero chiamate LLM.
- Riclassificazione LLM dello storico: i vecchi digest erano sovra-taggati (64/85 con piu' di 5 categorie, fino a 18). `scripts/reclassify_digest_categories.mjs` passa il testo del digest a gemini-2.5-flash con l'enum del vocabolario: ora tutti gli 85 hanno 1-5 categorie centrali. Scoperto e corretto al volo: l'API Gemini rifiuta `uniqueItems` nello schema JSON (avrebbe rotto la pipeline notturna).
- Mapping revisionato leggendo i digest reali (con ok dell'utente su 7 casi dubbi): "Elezioni e Nomine"→Elezioni e riforme ist.; "Riforme", "Politiche Istituzionali", "Politiche Regionali"→Procedure parlamentari (etichette generiche, si dissolvono per dedup); "Pace e Diritti Umani"→solo UE e relazioni internazionali (sedute su Comiso Città della Pace); "Gestione (del) Patrimonio"→Bilancio e finanze (sedute di bilancio); "Sicurezza e Legalità"→solo Giustizia e legalità (tag senza riscontro nei testi).
- `build-data.mjs`: warning se un digest contiene categorie fuori vocabolario (anti-deriva).
- `astro.config.mjs`: redirect statici dai vecchi slug categoria ai nuovi (generati dal mapping), deep link preservati.
- Archiviati in `scripts/archive/`: `normalize_eurovoc_categories.mjs`, `eurovoc_mapping.json`, `eurovoc-match-schema.json` (approccio precedente, mai entrato in produzione).

# 2026-07-08

## Ricerca trascrizioni: tuning retrieval + rilascio pubblico

- Caso "siccità" (10 sedute nel corpus, 1 restituita) → indagine con `scoring_details`: tre fix. (1) Hybrid search attivato (BM25+vettoriale, fusione RRF) — il solo vettoriale ha recall pessimo sui termini esatti. (2) `chunk_size` 1024→512 token: il reranker `bge-reranker-base` ha finestra di 512 token e vedeva solo metà chunk, azzerando i match nella seconda metà. (3) `keyword_match_mode: "or"` per-request nel Worker — il default "and" azzerava il recall delle query naturali multi-parola. Insidie documentate: similarity cache nei test A/B, accenti non normalizzati dal tokenizer keyword.
- Rilascio pubblico: pagina spostata da `/labs/ricerca-<random>/` a `/ricerca/`, tolto noindex (ora in sitemap), voce "Cerca" con icona nel menu principale, suggerimenti d'uso sotto il campo (più parole = meglio, accenti richiesti), testo aggiornato (corpus completo, aggiornamento notturno).
- Wiki aggiornato: `ricerca-trascrizioni/tuning-e-valutazione.md` riscritto con la storia dei tre problemi e le lezioni per test futuri.
- Bug reale segnalato dall'utente ("dove si parla della polemica su italo belga e mondello?" → 1 solo passaggio, sbagliato): il reranker aveva scartato il chunk giusto (verificato riga per riga nel corpus) a favore di uno adiacente non pertinente, nello stesso file. Fix strutturale: per le query multi-parola si lancia sempre anche un ramo BM25 puro (no reranker) in parallelo all'hybrid+reranker, risultati uniti e deduplicati — da 1 a 9 passaggi corretti. Effetto collaterale scoperto e corretto nello stesso giro: `keyword_match_mode: "or"` matcha anche le stopword ("di" 5000+ occorrenze) facendo tornare falsi positivi su query estranee al corpus ("colonizzazione di Marte": 20 risultati) — fix con lista stopword italiane rimossa dal solo ramo keyword. Residuo noto e accettato: il reranker a volte è "sicuro" anche su non-match (limite dei cross-encoder), ma verificato che il modello di generazione resta comunque onesto.
- Domande in linguaggio naturale + risposta AI opt-in: le domande vengono riscritte in parole chiave nel Worker (llama-3.3-70b, prompt rigido — il query_rewrite nativo non riscrive o, con l'8b, inventa termini mai detti) e instradate sulle euristiche validate ("dove si parla di mafia?" → "mafia" → 13 sedute). Checkbox "Risposta AI (sperimentale)" (`?ai=1`): genera una sintesi coi passaggi come fonti (`chatCompletions`, system prompt "solo dai passaggi forniti"), mai attiva di default. Pagina: mostra "(cercato: …)" quando la query è riscritta.
- Guardrail risposta AI: 0 passaggi = nessuna generazione (niente risposte enciclopediche fuori corpus); prompt indurito (frase fissa se le fonti non bastano, vietata la conoscenza esterna); citazioni [fonte: file] sostituite in pagina con link leggibili "seduta n. X del …". Fallback per multi-parola azzerate dal reranker: keyword "and" (tutte le parole nello stesso chunk).
- Fix back del browser: `VideoEmbed` ora sostituisce il nodo iframe invece di riassegnare `src` (cambiare src a iframe caricato aggiunge una voce di history: il back restava sulla pagina video).
- Quarto fix (post-rilascio): il reranker azzera le query italiane di una sola parola → euristica nel Worker (monoparola = BM25 puro senza reranker, soglia 0.1): "siccità" da 0-1 a 10/10 sedute. Header del corpus ridotto al solo titolo: URL/ID nei metadati matchavano query spurie (scoperto incollando l'URL della pagina nel campo di ricerca: 10 falsi risultati al 74%). Suggerimenti in pagina riscritti: parole chiave, non domande.

# 2026-07-08 (sera)

## Bug critico: ricerca non funzionava dopo rimozione checkbox AI

- Rimuovendo il checkbox "Risposta AI" (esaurita franchigia Workers AI a metà giornata, fallimento silenzioso — vedi `wiki/decisioni/`) sono rimasti 3 riferimenti orfani a `aiCheckbox` non più dichiarata: `ReferenceError` silenzioso nel submit handler, ricerca completamente bloccata senza alcun feedback. Fix verificato in locale con agent-browser prima del push (lezione: da ora, verifica end-to-end locale prima di ogni push su questa pagina).
- Aggiunto uno spinner di caricamento (SVG animato) + disabilitazione del pulsante "Cerca" durante la richiesta, per dare un riscontro visivo immediato.
- Confronto costi Risposta AI: Cloudflare llama-3.3-70b ~$0.0016/richiesta con franchigia gratuita ~60-70/giorno; DeepSeek V3.2 Exp via OpenRouter ~$0.0011/richiesta ma senza franchigia gratuita — per il traffico atteso del sito, Cloudflare resta preferibile. Dettagli e istruzioni per riattivare la feature (Worker intatto, solo UI da reintegrare) in `wiki/decisioni/index.md`.

# 2026-07-07

## Ricerca semantica trascrizioni (beta, Cloudflare AI Search)

- Corpus RAG: `scripts/build_rag_corpus.py` converte gli SRT in Markdown con marker `[HH:MM:SS]` per paragrafo (~60 s) + header metadati (seduta, data, URL video). Formato validato contro le pratiche correnti (finestre 30–120 s, timestamp per chunk); marker inline perché AI Search non supporta metadati per chunk. Esteso a tutte le 82 trascrizioni disponibili → `data/rag_corpus/`.
- Bucket R2 `ars-trascrizioni` popolato con gli 82 file (`scripts/upload_rag_corpus.sh`); istanza AI Search `ars-sicilia-trascrizioni` creata e indicizzata (82/82, 0 errori).
- Valutazione empirica con ~10 query di test: senza reranking i punteggi erano indistinguibili (0.4-0.6) con falsi positivi; con reranking (`@cf/baai/bge-reranker-base`) salgono a 0.77-0.97 sui match veri e restituiscono onestamente 0 risultati sui non-match. Reranking attivato, `max_num_results` alzato a 20. Osservazione non risolta: alcune query perdono il match quando il corpus cresce (20→82 doc) — vedi `wiki/ricerca-trascrizioni/tuning-e-valutazione.md`.
- Worker proxy `cloudflare/search-proxy/` (binding nativo `[[ai_search]]`, niente token esposto, CORS su aborruso.github.io + localhost) deployato; fix bug lettura risposta (`result.chunks`, non `result.data`).
- Pagina nascosta `/labs/ricerca-035553/`: fuori dai menu, esclusa da sitemap (filtro `/labs/`), meta noindex (nuova prop `noindex` nei layout), nota "powered by Cloudflare AI Search". Risultati con estratto e deep-link `?t=` alla pagina video; `VideoEmbed.astro` ora legge `?t=` e imposta `start=` nell'iframe.
- Automazione: `transcripts_digests.yml` esteso per rigenerare il corpus, caricare su R2 solo i file nuovi/cambiati e forzare un sync job via API ad ogni run notturno — nessun intervento manuale per le trascrizioni future. Secret `CLOUDFLARE_API_TOKEN`/`CLOUDFLARE_ACCOUNT_ID` aggiunti al repo.
- Creato `wiki/` (formato OKF) con documentazione di progetto per concetti: architettura, dataset, pipeline, frontend, questa feature, CI/CD, decisioni architetturali.

# 2026-07-05

## Navigazione a frecce + DDL nella pagina video

- Pagina video: pannello a comparsa (`<details>`, zero JS) con i disegni di legge della seduta, sotto il player — il digest li cita, ora sono a un click.
- Sedute multi-video: nel titolo `‹ Seduta n. N (video X di N) ›`, frecce per saltare tra i video della stessa seduta (`seduta.videos` già ordinato).
- Pagina seduta: stesse frecce ai lati del titolo per seduta precedente/successiva (riusa i props `prev`/`next` già esistenti).
- Frecce estratte in `NavArrow.astro` (prev/next, stato disabilitato ai bordi); touch target 44px su mobile, 36px da `sm`. Card DDL estratta in `DisegnoCard.astro`, riusata da `DisegniList` e dal nuovo pannello.
- README: rimosso conteggio hardcoded "108+ pagine statiche".

# 2026-06-18

## Qualità dati disegni di legge (titoli + stralci)

- Diagnosi (verificata sui PDF reali, niente OCR — sono PDF testo): due cause dei "duplicati".
- **Titolo non normalizzato**: stesso disegno con 7 forme (virgolette curve/dritte, apostrofo `'`/`’`/`‘`, spazi doppi da testo giustificato, punto finale, annotazione `(n. …)`, escape letterale `’`). I PDF stessi differiscono tra sedute → serve normalizzazione deterministica.
- **Stralci collassati al numero padre**: 1030/A Stralcio I/V/VI sono voci OdG distinte ma con numero 1030; apparivano come record ripetuti. Scelta: collassarli a una voce per PDF.
- **Estrazione corrotta**: un record 947 con flood di newline + `{` (6566 char). Scartato via guard (no graffe, lunghezza < 400; legittimi max 264).
- Fix in `extract_odg_data.sh` (post-processing mlr): normalizza titolo, guard anti-spazzatura, dedup per `(pdf_url, numero_disegno)`. Applicato al JSONL esistente: 188 → 160 record, 15 DDL tutti con titolo pulito. Nessun reprocess LLM.
- Non bug: 953/974/993/930 = debiti fuori bilancio mesi diversi, stesse sedute = corretto (voci ricorrenti in OdG finché non votate).

# 2026-06-14

## Coerenza UX + deep linking + SEO delle sedute

- Diagnosi: tre paradigmi incoerenti (categorie = pagina, calendario e ricerca = filtro live). Analisi in `docs/revisione-ux-seo.md`.
- Modello adottato: **stati enumerabili → pagine dedicate (path); ricerca libera → live `?q=`**. Comportamento unico: clic → pagina, digitazione → ricerca.
- Nuove pagine periodo `/sedute/[anno]` e `/sedute/[anno]/[mese]` (server-rendered, in sitemap).
- Calendario reso **navigante**: titolo → pagina mese, giorno → seduta (o mese se più d'una); frecce sfogliano client-side. Rimosso il filtro-live e `?giorno`/`?mese`.
- Breadcrumb seduta collega anno/mese; layout calendario+categorie affiancati su desktop.
- SEO: JSON-LD `BreadcrumbList` (componente Breadcrumb) + `ItemList` (pagine periodo).
- Deep linking registrato come **requisito** di prodotto ([[deep-linking-requisito]], `docs/future-ideas.md`).

## Altre migliorie sito

- Ricerca DDL per numero/descrizione, condivisibile via `?q=` (`/ddl/[page]`).
- Navigazione precedente/successiva tra sedute.
- Lista DDL nella seduta collassabile (primi 3 + "Mostra tutti").

## Fix rimozione in-place record OdG (formato)

- Audit notturno: la rimozione in-place dei vecchi record falliva (`grep -F` cercava `"pdf_url":"..."` ma `mlr` scrive `"pdf_url": "..."` con spazio) → i PDF "ripuliti" mantenevano i vecchi record (es. ODG 237: 96 invece di 12).
- Fix: rimozione con `jq` per chiave (`select(.pdf_url != $u)`), robusta al formato. Verificato: 237 → 12 record.
- Log svuotato per ri-migrare i PDF con la rimozione corretta.

## Fix estrazione disegni di legge da OdG

- Causa dati sporchi (`disegni_legge.jsonl`): prompt LLM debole + `--reprocess` in append + dedup solo esatto → duplicati massivi (stesso DDL ×10), record con titolo=frammenti di PDF, legislatura `XVIII Legislatura`, numero corrotto (es. `7793267088` da `779-3-26-70-88/A`).
- Verifica estrattori testo (`lit`/liteparse, markitdown, pdftotext): equivalenti → mantenuto markitdown. Il collo di bottiglia era il **prompt**, non il testo.
- `extract_odg_data.sh` riscritto: prompt/schema rigoroso (testato su 233 e 237), normalizzazione numero+legislatura, dedup per `(pdf_url, numero, titolo)`, scarto titoli vuoti.
- **Idempotente e progressivo**: `--limit N` (default env `ODG_LIMIT`), sostituzione in-place dei record per PDF, throttle (`ODG_SLEEP`, 7s) + retry/backoff sui 429 del free tier Gemini (10 RPM / 250 RPD).
- `extract_odg.yml`: gira con `--limit 10` e committa anche il log di avanzamento. Svuotato il log per ripulire i 37 PDF storici (~4 notti).
- `1030/A Stralcio I/VI/...`: confermato che sono stralci legittimi dello stesso DDL 1030 (non un errore).

# 2026-06-13

## Automazione trascrizioni + digest in CI

- App OAuth captions (`youtube-captions-downloader`) portata da Testing a **In production**: il refresh token non scade più ogni 7 giorni (causa dei blocchi ricorrenti).
- Test diagnostico da runner GitHub: **API ufficiale `captions.download` funziona** (autenticata, non bloccata per IP); **yt-dlp/qv falliscono** ("Sign in to confirm you're not a bot").
- `scripts/auth_captions.py`: nuovo helper per rigenerare `config/token.json` con scope corretti (`youtube.readonly` + `youtube.force-ssl`).
- `scripts/generate_digests.sh`: nuova modalità `USE_LOCAL_TRANSCRIPTS=true` — in CI usa solo i `.txt` locali; se mancano salta e ritenta al run successivo (self-healing), mai `qv`, mai marcatura `no_transcript`.
- `.github/workflows/transcripts_digests.yml`: nuovo workflow schedulato (04:30 UTC) che scarica trascrizioni via API e genera digest con Gemini, poi committa e triggera il deploy.
- Secret aggiornati: `YOUTUBE_REFRESH_TOKEN`, `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`.

# 2026-01-15

## Fix path assoluti per config e stato playlist YouTube

- Impostata playlist 2026 in `config/config.yaml`
- Stato playlist ora risolto sempre su root repo (`data/playlists.json`) per evitare duplicati
- Config path reso assoluto negli script principali e in `scripts/archive`
- Default assoluti per config/anagrafica in `scripts/generate_rss.py`
- File modificati: src/uploader.py, scripts/upload_single.py, scripts/main.py, scripts/build_anagrafica.py, scripts/update_descriptions.py, scripts/setup_playlist.py, scripts/archive/sync_youtube_ids.py, scripts/archive/check_playlist.py, scripts/archive/backfill_durations.py, scripts/generate_rss.py, config/config.yaml

# 2026-01-11

## Valutazione progetto

- Creata valutazione sintetica progetto in `docs/evaluation.md`
- Aggiunte note ricerca con ipotesi e confidenza in `docs/research-notes.md`

# 2026-01-09

## Valutazione applicabilità sistema RAG per trascrizioni ARS

- Analizzato dataset: 26 video, 34.309 righe, 3.6MB trascrizioni dibattiti parlamentari
- Valutata architettura RAG (MarkItDown + LangChain + ChromaDB + Ollama + Gradio)
- **Verdict**: Sistema altamente applicabile con modifiche minori
- Adattamenti necessari: parser .txt/.srt custom, embeddings multilingua italiano, metadati speaker
- Modelli consigliati: `paraphrase-multilingual-mpnet-base-v2` (embeddings), `gemma2:9b` o `qwen2.5:14b` (LLM)
- Stima effort MVP: 6-9 ore per sistema funzionante
- Output: docs/rag/evaluation.md con analisi dettagliata componenti, criticità, architettura proposta

# 2026-01-02

## Export risorse per LLM su video page

- Implementato bottone "📋 Copia risorse per LLM" su ogni pagina video
- Nuovo componente `src/components/sedute/LlmExportButton.astro` con export text generator
- Export contiene: metadata seduta, link trascrizione (GitHub raw), OdG (ARS CDN), YouTube link
- Rimosse AI-generated content (digest JSON, categorie) per esportare solo raw materials
- **Nuovo**: JSON endpoint `/sedute/[anno]/[mese]/[giorno]/[seduta]/[video].json` per machine-to-machine access
- JSON contiene: metadata seduta, metadata video (ora, data, durata, youtube_id), risorse (trascrizione, OdG, video)
- Copy-to-clipboard con toast notification "✓ Risorse copiate negli appunti" (fade 3s)
- Fallback modal se Clipboard API non disponibile (per browser vecchi)
- Link "⚙️ JSON" per scarica endpoint JSON
- Accessibilità: ARIA label "Esporta risorse per assistente AI", keyboard navigabile
- Formatting human-readable con emoji per sezioni: 📚 📄 🎬
- Integrato in video.astro dopo section categorie, prima digest content
- Build: 93 pagine HTML + 28 file JSON, zero errors
- Test funzionale: button click copia testo corretto, JSON link funzionale, both esportano raw materials
- Responsive: buttons adattati su mobile/tablet, modal scalabile

## Fix Menu Mobile Hamburger dopo ViewTransitions

- **Problema**: Menu hamburger su mobile funzionava solo su homepage, non su altre pagine
- **Root cause**: Script utilizzava `DOMContentLoaded` che non si triggera dopo Astro ViewTransitions navigation
- **Soluzione**: Cambiato a `astro:page-load` event che si triggera sia al caricamento iniziale che dopo ogni navigazione ViewTransitions
- **Refactoring**: Estratta logica `initMobileMenu()` in funzione riutilizzabile
- **File modificato**: src/components/layout/Header.astro (script tag, righe 136-174)
- **Test**: Build completato con successo, 93 pagine generate

# 2025-12-31

## Validazione automatica digest con LLM

- Creato template `config/validate-digest.yaml` per verificare completezza digest
- Aggiunta funzione `validate_digest_completeness()` in `generate_digests.sh`
- Lo script ora valida che i digest siano autoconcludenti (non troncati)
- Retry automatico (max 3 tentativi) se digest incompleto
- Test: rilevato e rigenerato correttamente digest troncato (hdBrcmGOUWM)
- File modificati: scripts/generate_digests.sh, config/validate-digest.yaml (nuovo)

## Normalizzazione numero DDL e flag reprocess per OdG

- `extract_odg_data.sh` ora normalizza `numero_disegno` a soli numeri (regex) e scarta record senza match
- Aggiunto flag `--reprocess` per rielaborare tutti i PDF (default: skip se `pdf_url` già presente)
- Dedup finale mantiene `uniq -a` dopo normalizzazione e filtro
- File modificato: scripts/extract_odg_data.sh
- README aggiornato: uso `--reprocess` e nota su normalizzazione numero

## Supporto Markdown per pagine statiche

- Aggiunta integrazione `@astrojs/mdx` e layout predefinito per `.md` in `src/pages/`
- Layout PageLayout ora usa frontmatter `title` e `description` quando non passati come props
- Migrazione pagina About a Markdown (`src/pages/about.md`)
- Guida autore: `docs/markdown-guide.md`
- Spec creato: `openspec/specs/markdown-pages/spec.md`
- File modificati: astro.config.mjs, src/lib/remark-default-layout.mjs, src/layouts/PageLayout.astro, README.md

# 2025-12-29

## Riduzione Preview Video Seduta

- Grid layout pagina seduta: da 1/2/3 a 1/3/6 colonne (mobile/tablet/desktop)
- Dimensioni preview dimezzate su desktop: 6 colonne invece di 3
- Più video visibili per riga, ridotto scrolling necessario
- Aspect ratio 16:9 mantenuto, responsive design preservato
- OpenSpec: change archiviato, spec creato in openspec/specs/seduta-page-layout/
- File modificato: src/components/sedute/VideosByDate.astro:34

## Fix Logo Header: testo bianco su sfondo bianco

- **Problema**: scritta "ARS" nel box header non visibile (testo bianco su sfondo bianco)
- Classe CSS `.gradient-editorial` non applicata (Header.astro usava `bg-gradient-editorial`)
- **Fix**:
  - Rinominata `.gradient-editorial` → `.bg-gradient-editorial` in global.css
  - Rinominata `.gradient-accent` → `.bg-gradient-accent` per coerenza
  - Ora gradiente navy applicato correttamente, testo bianco visibile
- File modificato: src/styles/global.css:94,99

## Fix CSV Schema: campo no_transcript

- **Problema**: build_anagrafica.py scriveva 18 campi ma header aveva 19 (mancava no_transcript)
- Causava CSV corrotto quando generate_digests.sh aggiungeva il campo
- **Fix**:
  - Aggiunto 'no_transcript' a required_fields in init_anagrafica_csv()
  - get_existing_youtube_ids() ora preserva no_transcript
  - save_seduta_to_anagrafica() scrive no_transcript alla fine della row
- CSV ora sempre valido con 19 campi in tutte le righe
- File modificato: scripts/build_anagrafica.py

# 2025-12-28

## Ristrutturazione Completa README.md

- README trasformato da "YouTube Uploader" a "Archivio Consultabile Sedute Assemblea"
- Focus principale: piattaforma civic tech con sito web consultabile
- Struttura 12 sezioni: Introduzione, Funzionalità, Architettura, Stack, Quick Start, Setup, Pipeline YouTube, Docs, Dati Aperti, Roadmap, Contributi, Contatti
- **Sito web FIRST** (frontend Astro), pipeline YouTube SECOND (backend Python)
- Audience ampliata: da sviluppatori Python a cittadini + sviluppatori
- Setup tecnico YouTube collassato in `<details>` (ridotto da 500+ righe)
- Aggiunta sezione Dati Aperti con schema CSV/JSONL
- Aggiunta sezione Roadmap con sviluppi futuri
- Più link a documentazione esistente (PRD, design-system, LOG, openspec)
- Mantiene completezza tecnica ma con organizzazione user-friendly
- File modificato: README.md (completa riscrittura)

## Redesign Completo "Editorial Civic"

- Implementato nuovo design system con identità visiva distintiva
- **Palette colori**: Navy istituzionale (#1e3a5f), Ambra siciliana (#d97706), Verde salvia (#059669), Grigi caldi
- **Tipografia**: Fraunces (font display serif editoriale) + Manrope (sans geometrico)
- **Visual language**: Bordi colorati a sinistra come elemento signature, pattern geometrico sfondo
- **Componenti aggiornati**:
  - Header: Logo stemma "ARS" in gradient, navigazione editoriale
  - Footer: Layout 3 colonne informativo, badge tech stack
  - SedutaCard: Tipografia grande, bordi animati hover, sezioni organizzate
  - CategoryFilter: Badge interattivi con hover states
  - Pagination: Bottoni con icone, responsive
- **Homepage**: Hero editoriale con bordo ambra, stats cards con bordi colorati
- **Accessibilità**: Contrasti WCAG 2.1 AA, focus states evidenti, ARIA labels
- **Mobile-first**: Responsive design con breakpoints Tailwind
- File modificati: tailwind.config.mjs, src/styles/global.css, tutti i layout/componenti principali
- Documentazione: docs/design-system.md (guida completa), docs/design-preview.html (preview HTML)
- Skill utilizzato: frontend-design per direzione estetica e implementazione

## Link RSS Feed Visibile nell'Header

- Aggiunto link RSS con icona 📡 nell'header di navigazione
- Posizionato dopo link "Sito ARS"
- Icona arancione (text-orange-600) per standard RSS
- Link punta a /ars_sicilia/rss.xml
- Attributi accessibilità: aria-label="Feed RSS", title tooltip
- Attributi semantici: rel="alternate" type="application/rss+xml"
- Apre in nuova tab (target="_blank")
- File modificato: src/components/layout/Header.astro
- OpenSpec: change archiviato, spec creato in openspec/specs/rss-visibility/

## Disclaimer AI per Digest Video

- Implementato disclaimer prominente prima contenuto digest
- Box warning (bg-yellow-50, border-yellow-200) con icona ⚠️
- Testo: "ATTENZIONE: Il testo di questo digest è stato generato automaticamente da un LLM..."
- Appare solo quando digest disponibile (no disclaimer per "Sintesi non disponibile")
- Accessibilità: semantic `<aside>` con `role="note"` e `aria-label`
- Styling consistente con pattern warning esistenti
- File modificato: src/components/sedute/DigestContent.astro
- OpenSpec: change archiviato, spec creato in openspec/specs/digest-disclaimer/
- Aggiornato openspec/project.md con menzione AI transparency

## Navigazione Video Precedente/Successivo

- Implementata navigazione prev/next nella pagina single video
- Pulsanti ← → posizionati sopra video embed, dopo header
- Calcolo automatico indici da array seduta.videos
- Pulsanti disabilitati (gray) al primo/ultimo video
- Styling coerente con componente Pagination
- ARIA labels per accessibilità
- Build test: 108 pagine OK, edge cases verificati (primo/ultimo video)
- File modificato: src/pages/sedute/[anno]/[mese]/[giorno]/[seduta]/[video].astro

## Analisi Search Engine

- Valutate tecnologie search per sito statico: Pagefind, Fuse.js, FlexSearch, Lunr.js
- Raccomandato Pagefind per compressione eccellente (~1% size) e integrazione Astro nativa
- Dataset attuale: 343K JSON → indice stimato 10-15KB
- Analisi salvata in docs/search-engine-analysis.md

## Sviluppo sito Astro completo

- Implementato sito statico completo con Astro + Tailwind CSS
- Setup base: package.json, configs, TypeScript types, data-loader
- Script build-data.mjs: processa CSV + JSONL + JSON digest a build-time
- Layout: BaseLayout con accessibilità (skip link, semantic HTML), Header, Footer, Breadcrumb
- Componenti sedute: SedutaCard, VideoThumbnail, VideosByDate, VideoEmbed, DigestContent, DisegniList, CategoryBadge
- Componenti UI: Pagination classica, CategoryFilter
- Pagine: Homepage, lista sedute paginata, single view seduta, single view video, categorie, About, 404
- SEO: RSS feed, sitemap automatico, structured data (Schema.org VideoObject), robots.txt
- Deploy: GitHub Actions workflow per deploy automatico su GitHub Pages
- Build test: 108 pagine generate con successo in 2.14s
- Piano salvato in docs/piano-sviluppo-sito.md

## Riorganizzazione scripts/

- Creata `scripts/tests/` per file di test
- Creata `scripts/archive/` per script obsoleti
- Spostati test_youtube_auth.py e test_youtube_auth_manual.py in tests/
- Archiviati: backfill_durations.py, check_playlist.py, fix_csv_carriage_returns.py, sync_youtube_ids.py
- Aggiornati riferimenti in scripts/README.md e openspec/project.md

# 2025-12-27

## Fix Error Handling No Transcript

- Script generate_digests.sh ora marca video con `no_transcript=true` quando:
  - `qv` fallisce scaricamento trascrizione
  - Trascrizione scaricata è vuota
- Coerente con comportamento esistente per trascrizioni <100 bytes
- Contatore `no_transcript` invece di `failed` per questi casi
- Video Ec3zq1hXafw marcato manualmente (1 minuto, no transcript)
- Skip automatico run successivi: video già marcati non vengono più ritentati

# 2025-12-26

## Fix CSV Carriage Returns

- Rimossi `\r` (carriage return) dai valori CSV in anagrafica
- Bug introdotto quando aggiunta colonna `no_transcript`
- `\r` nei valori causava display corrotto con `mlr --c2t`
- Script `fix_csv_carriage_returns.py` pulisce 28 record
- CSV ora valido: parsing corretto con miller e Python csv
- Prevenzione: codice già usa `newline=''` correttamente

## Video Duration Tracking

- Aggiunta colonna `duration_minutes` a anagrafica CSV
- Estrazione durata automatica da yt-dlp durante download (metadata JSON)
- Durata salvata in minuti (arrotondata) per ogni video caricato
- Preservation logic: re-crawl preserva durate esistenti
- Script `scripts/backfill_durations.py`: backfill durate per video già su YouTube
- Parser ISO 8601 (es. PT1H23M45S → 84 minuti)
- Backfill completato: 20 video aggiornati via YouTube Data API v3 (<1 quota unit)
- Range durate: 0-162 minuti
- Nuovi upload ottengono durata automaticamente

# 2025-12-25

## Validazione JSON e Retry per Digest

- Fix JSON corrotti generati da LLM (es. v4mq1poSzOw.json)
- Funzione `validate_json()` in generate_digests.sh: verifica sintassi con `jq empty`
- Retry automatico: max 3 tentativi per digest, validazione dopo ogni generazione
- Attesa 5 secondi tra retry per rate limiting
- File JSON malformati rimossi automaticamente
- Cleanup digest esistenti: verificati tutti, rimosso 1 corrotto
- Al prossimo run, digest mancanti vengono rigenerati con validazione

# 2025-12-24

## Generazione Automatica Digest Video con LLM

- Sistema completo per generare digest AI da trascrizioni YouTube
- Template prompt `config/digest.yaml` (in italiano)
- JSON Schema `config/digest-schema.json`: digest (Markdown), categories, people
- Script `scripts/generate_digests.sh`:
  - Input: anagrafica CSV con youtube_id
  - Estrazione ID con mlr: `--c2n cut -f youtube_id then filter '$youtube_id=~".+"`
  - Download trascrizioni: `qv https://youtu.be/ID --text-only`
  - Generazione: `llm -m gemini-2.5-flash -t digest.yaml --schema digest-schema.json`
  - Output: `data/digest/{youtube_id}.json`
  - Skip file esistenti, retry logic, pausa 5s tra chiamate
- Test sperimentali modelli: Gemini 2.5 Flash, Claude Sonnet 4.5, Mistral Medium, GPT-5.2
- Output JSON strutturato:
  - digest: Markdown con ## headers, **bold**, liste
  - categories: array temi parlamentari (Bilancio, Sanità, etc.)
  - people: array {name, role}
- Digest completi ~4-8KB, 200-500 parole
- Logging automatico in `data/logs/digest_*.log`

## Estrazione Completa Documenti Seduta

- Scraper estrae 4 tipi di documenti: OdG, Resoconto provvisorio, Resoconto stenografico, Allegato
- Schema CSV: aggiunte colonne `resoconto_provvisorio_url`, `resoconto_stenografico_url`, `allegato_url`
- Backward compatibility: `resoconto_url` mantenuto (preferenza stenografico > provvisorio)
- Metadata YouTube: descrizioni includono tutti documenti disponibili con emoji
- Viewer: visualizza tutti documenti con tooltip e emoji (📄 📋 📝 📎)
- Pattern HTML uniforme: `<h3>Label<a href>` per tutti documenti
- Test: seduta 158 (stenografico+allegato), seduta 217 (provvisorio+allegato)
- OpenSpec proposal: extract-seduta-documents validata e implementata

## Retry con Backoff Esponenziale per Upload

- Aggiunto retry automatico per errori SSL/network temporanei (EOF occurred in violation of protocol)
- Download: 3 tentativi, delay iniziale 2s, backoff esponenziale (2s → 4s → 8s)
- Upload: 5 tentativi, delay iniziale 3s, backoff esponenziale (3s → 6s → 12s → 24s → 48s)
- Funzione `is_temporary_error()`: rileva errori SSL, timeout, network
- Funzione `retry_with_backoff()`: gestisce retry con backoff configurabile
- Video failed hanno priorità assoluta e vengono riprovati al prossimo run
- Errori permanenti (quota, file not found) falliscono subito senza retry

# 2025-12-23

## Client Python per API ARS Sicilia

- Creato client completo per database Disegni di Legge ARS
- Fix: search() ora chiama get_results_page() dopo POST (redirect JavaScript non HTTP)
- Endpoint principale: POST /home/cerca/221.jsp → GET /icaro/default.jsp
- Funzionalità: ricerca, paginazione (10 risultati/pagina), contenuto completo DDL
- Documentazione completa API con esempi curl e workflow
- 4 esempi funzionanti: ricerca legislatura, anno, firmatario, numero DDL
- Test OK: 1079 risultati legislatura 18, 108 pagine, contenuto completo accessibile
- Directory: `ars_sicilia_api/` con client, docs, examples, requirements.txt

## Guida alla Ricerca Formattata

- Formattata GUIDA_ALLA_RICERCA.md con backtick per code markup
- Operatori: AND, OR, NOT, ADJ, NEAR, SAME, WITH, LINE, XOR
- Field qualifiers: .LEGISL, .FIRMAT, .TITOLO, .TESTO, etc.
- Funzioni speciali: IMG(), SEL(), LVL(), DOCNO(), ALLDOC
- Wildcards: $, %, /
- Code blocks per esempi query
- Migliorata leggibilità struttura markdown

## Estrazione Dati Disegni Legge da PDF OdG

- Script `extract_odg_data.sh` per estrazione strutturata da PDF ordini giorno
- Pipeline: markitdown (PDF→testo) + llm CLI (testo→JSON strutturato)
- Campi estratti: titolo_disegno, numero_disegno, legislatura, data_ora (ISO 8601)
- Deduplicazione automatica: PDF già processati saltati
- Output: `data/disegni_legge.jsonl` (append incrementale)
- URL ICARO auto-generati: link diretto scheda disegno (legislatura + numero)
- Input: URL PDF distinti da campo odg_url in anagrafica_video.csv
- Cleanup finale: `mlr uniq -a` rimuove duplicati esatti (safety measure)

# 2025-12-22

## Auto-aggiornamento ID Video con Preservazione YouTube IDs

- build_anagrafica.py aggiorna sempre sedute ultimi 14 giorni (ARS cambia ID video)
- Preserva youtube_id esistenti usando chiave (numero_seduta, data_video, ora_video)
- Fix: download falliva per ID obsoleti + re-upload duplicati
- Workflow daily_upload già esegue build_anagrafica prima upload

# 2025-12-21

## Affidabilità Pipeline e Metadati

- Scraping con timeout/retry configurabili e backoff
- Creazione automatica directory download
- Download limitato a max 720p quando disponibile
- recordingDate timezone-aware (Europe/Rome)
- Dedup più robusto (id_video + numero_seduta + data_seduta)
- Selezione ultima seduta deterministica
- Filtro `start_date` in anagrafica

## Token Seduta e Link Ricerca

- Token univoco in descrizione: `ARS_SEDUTA_<numero>-<YYYY-MM-DD>`
- Link ricerca globale con operatori: `results?search_query="TOKEN"+intitle:"Lavori d'aula"`
- Script `update_descriptions.py` per aggiornare descrizioni già caricate
- Flag `--update-titles` per aggiornare i titoli già pubblicati

## Script Test Upload Singolo

**upload_single.py:**
- Rinominato da `test_upload_single.py`
- Upload primo video dall'anagrafica senza youtube_id
- Modalità `--dry-run` per preview senza caricare
- Aggiorna anagrafica con youtube_id dopo upload
- Previene duplicati in run successive

**Flusso:**
1. Trova primo video senza youtube_id in anagrafica
2. Autentica YouTube (skip in dry-run)
3. Download video da pagina ARS (skip in dry-run)
4. Costruisce metadati completi
5. Upload + aggiunta a playlist anno
6. Aggiorna anagrafica con youtube_id
7. Cleanup file temporaneo

**Funzioni:**
- `get_first_unuploaded_video()`: trova video da uploadare
- `update_anagrafica_youtube_id()`: aggiorna CSV dopo upload
- Conferma utente prima di upload reale

**Uso:**
```bash
python3 upload_single.py --dry-run  # Preview
python3 upload_single.py            # Upload reale
```

## Playlist Annuali e Link Ricerca Seduta

**Organizzazione contenuti YouTube:**
- Playlist annuali: video aggiunti automaticamente a playlist anno (es. "ARS 2025")
- Link ricerca seduta in descrizione: `youtube.com/@Canale/search?query=seduta+n+220`
- Utenti possono filtrare video per seduta specifica senza playlist dedicate

**Configurazione (`config/config.yaml`):**
- `youtube.channel_id`: ID canale o handle (es. `@ARSSicilia`)
- `youtube.playlists`: mapping anno → playlist ID (es. `2025: PLxxxxxxxxx`)

**Funzioni nuove (`src/uploader.py`):**
- `add_video_to_playlist()`: aggiunge video a playlist (50 units API)
- `get_playlist_id_for_year()`: seleziona playlist da anno
- `upload_video()`: parametro `playlist_id` opzionale

**Metadati migliorati (`src/metadata.py`):**
- Descrizione con link ricerca seduta (se channel_id configurato)
- Tags ottimizzati: "Seduta n. 220", "Dicembre 2025"
- Emoji per sezioni: 🔍 ricerca, 📄 documenti, 🔗 link

**Quota API aggiornata:**
- Upload: 1,600 units
- Playlist insert: 50 units
- **Totale: 1,650 units/video → ~6 video/giorno**

**Documentazione:**
- README: sezione configurazione playlist e channel_id
- Istruzioni creare playlist su YouTube Studio

## Fix Estrazione Date Video Multi-Date

**Problema rilevato:**
- Sedute con video distribuiti su più giorni (es. seduta 220: 16-21 dicembre)
- `data_video` errata: tutti video mostravano data_seduta invece di data effettiva

**Fix implementati src/scraper.py:**
- `extract_seduta_number()`: estrae da `<title>` invece di body (evita match link navigazione)
- `extract_video_metadata()`: usa `title` attribute video_box (contiene data+ora complete)
- Fallback robusto: h4 heading precedente se title mancante
- Distinzione corretta `data_seduta` vs `data_video`

**Risultato:**
- Seduta 220 (data_seduta: 16/12): 4 video 16/12, 3 video 17/12, 5 video 18/12, 3 video 19/12, 7 video 20/12, 2 video 21/12
- Seduta 219 (data_seduta: 10/12): 2 video 10/12, 2 video 15/12
- Anagrafica rigenerata: 28 video con date corrette

**Versionamento dati:**
- Anagrafica CSV ora committata su GitHub
- .gitignore modificato: esclusi solo logs, inclusa anagrafica pubblica

## Anagrafica Video Incrementale

Implementato sistema anagrafica completo:

**Script `build_anagrafica.py`:**
- Crawler incrementale partenza seduta 219 (10/12/2025)
- Naviga verso futuro usando `div.next_link` (freccia destra)
- Si ferma quando non ci sono sedute future
- Estrae metadati senza download video
- **Rilevamento aggiornamenti**: confronta count video per seduta, aggiorna se diverso
- Output CSV `data/anagrafica_video.csv` con 12 colonne

**Funzionalità chiave:**
- Prima run: processa tutte sedute dal 10/12/2025 ad oggi
- Run successivi: solo sedute nuove o aggiornate
- Wrapper `run_daily.sh`: lock file, logging giornaliero, error handling
- Pronto per cron job

**Modifiche `src/scraper.py`:**
- `get_next_seduta_url()`: parametro `go_forward=True` usa `div.next_link`
- Supporta navigazione bidirezionale (passato/futuro)

**Setup autenticazione YouTube:**
- File `.env` con Client ID/Secret (non versionato)
- `config/youtube_secrets.json` con OAuth completo
- `config/token.json` generato con scope `youtube.upload` + `youtube.readonly`
- Test autenticazione riuscito su canale "Andrea Borruso"

**Primo run anagrafica:**
- Sedute processate: 2 (218, 219)
- Video catalogati: 28
- Tempo: ~10 secondi

**File aggiornati:**
- PRD.md: stato progetto con fasi
- README.md: sezione anagrafica e istruzioni
- config/config.yaml: start_url seduta 219

# 2025-12-19

## Implementazione Iniziale

- Struttura progetto completa creata
- Moduli Python implementati:
  - `src/scraper.py`: scraping pagine sedute ARS
  - `src/downloader.py`: download video HLS con yt-dlp
  - `src/uploader.py`: upload YouTube con OAuth2
  - `src/metadata.py`: costruzione metadati (titolo, descrizione, tags, recordingDate)
  - `src/logger.py`: gestione log CSV e indice sedute
  - `src/utils.py`: funzioni helper date/formattazione
- Script principale `main.py` con orchestrazione completa
- Configurazione `config/config.yaml` con parametri predefiniti
- README.md con istruzioni complete setup YouTube API
- `.gitignore` per credenziali e file temporanei

## Specifiche Implementate

- Naming convention: `Lavori d'aula: seduta n. 219/A del 10 Dicembre 2025 - 11:30`
- recordingDate API YouTube impostato con data/ora effettiva seduta
- Log CSV traccia: id_video, numero_seduta, data_seduta, ora_video, youtube_id, status
- Video temporanei eliminati dopo upload
- Una seduta per esecuzione (adatto a cron job)
- Link OdG e Resoconto in descrizione video

## Next Steps

- Setup Google Cloud e YouTube API (manuale)
- Prima autenticazione OAuth2
- Test download e upload su seduta campione
- Setup cron job per esecuzione automatica
