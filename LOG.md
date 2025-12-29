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
