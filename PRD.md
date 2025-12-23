# Introduzione

L'obiettivo del progetto è rendere più leggibili e analizzabili i contenuti pubblicati dall'Assemblea Regionale Siciliana.

## Ripubblicare su YouTube le sedute assemblea

Sedute pubblicate su https://www.ars.sicilia.it/agenda/lavori-aula

### Obiettivi

1. **Anagrafica video** - Sistema incrementale che estrae metadati sedute dal 10/12/2025 in poi
2. **Download e upload** - Scaricare video e pubblicare su YouTube con metadati ricercabili
3. **Metadati ricchi** - Titoli, descrizioni, tags, recordingDate, link OdG/Resoconti
4. **Trascrizione automatica** - Abilitare estrazione testo YouTube
5. **Registro completo** - Log upload per evitare duplicati
6. **Feed pubblico** - RSS con gli ultimi video caricati

### Stato Attuale

#### ✅ Fase 1: Anagrafica Video (Completata)

**Script:** `scripts/build_anagrafica.py`

Funzionalità:
- Crawler incrementale partendo da seduta 219 (10/12/2025)
- Naviga sedute usando `div.next_link` (freccia destra)
- Si ferma quando non ci sono più sedute future
- Estrae metadati senza scaricare video:
  - numero_seduta, data_seduta, url_pagina
  - odg_url, resoconto_url
  - id_video, ora_video, data_video
  - video_page_url
- **Rilevamento aggiornamenti**: se seduta ha nuovi video, aggiorna anagrafica
- Output: `data/anagrafica_video.csv`
- Wrapper: `scripts/run_daily.sh` con lock file e logging
- Pronto per cron job giornaliero

**Output:** `data/anagrafica_video.csv`

#### ✅ Fase 2: Upload YouTube (Completata)

- Pipeline di upload integrata in `scripts/main.py`
- Processa solo video con `youtube_id` vuoto
- Popola `youtube_id` dopo upload riuscito
- Rispetta la quota YouTube API (max teorico ~6 video/giorno)

#### ✅ Fase 3: Automazione (Configurata)

- GitHub Actions giornaliero per aggiornare anagrafica e caricare fino a 4 video/giorno
- Workflow separato per generare e pubblicare RSS su `gh-pages`
- Smoke test singolo upload: `scripts/upload_single.py`

#### ✅ Fase 4: Feed pubblico RSS (Configurata)

- Feed pubblicato su GitHub Pages: `https://aborruso.github.io/ars_sicilia/feed.xml`
- Generazione via `scripts/generate_rss.py` con limite 20 video
- `pubDate` derivato da `data_video` + `ora_video`

#### 📌 Backlog / Prossimi passi

- Trascrizione automatica: abilitare e verificare export testo per analisi

---

## Estrazione Dati Disegni Legge da PDF OdG

Estrazione strutturata dei disegni di legge discussi dai PDF degli ordini del giorno (OdG).

### Obiettivi

1. **Archiviazione storica** - Catalogo completo disegni legge con metadati strutturati
2. **Linkage video↔disegni** - Collegare video sedute ai disegni discussi
3. **URL ICARO** - Generazione automatica link alle schede ICARO
4. **Tracciabilità** - Storico di quando ogni disegno è stato discusso

### Stato Attuale

#### ✅ Fase 1: Estrazione PDF OdG (Completata)

**Script:** `scripts/extract_odg_data.sh`

Funzionalità:
- Legge URL PDF distinti dal campo `odg_url` in `data/anagrafica_video.csv`
- Pipeline: `markitdown` (PDF→testo) + `llm` (estrazione strutturata con LLM)
- Campi estratti per ogni disegno:
  - `titolo_disegno` - Titolo completo del disegno
  - `numero_disegno` - Numero (solo parte numerica)
  - `legislatura` - Numero romano (es. XVIII)
  - `data_ora` - Data e ora seduta (ISO 8601)
  - `pdf_url` - URL PDF sorgente
  - `url_disegno` - URL ICARO generato automaticamente
- Deduplicazione: PDF già processati saltati, cleanup duplicati esatti con `mlr`
- Output: `data/disegni_legge.jsonl` (formato JSONL incrementale)
- Esecuzione: manuale on-demand

**Output:** `data/disegni_legge.jsonl`

#### 📌 Prossimi passi

- Linkage automatico video→disegni usando numero_seduta e data_ora
- Arricchimento descrizioni YouTube con link ai disegni discussi
- Dashboard query disegni per legislatura/anno/stato
