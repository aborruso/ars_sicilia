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
