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

### Stato Attuale

#### ✅ Fase 1: Anagrafica Video (Completata)

**Script:** `build_anagrafica.py`

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
- Wrapper: `run_daily.sh` con lock file e logging
- Pronto per cron job giornaliero

**Risultati primo run:**
- Sedute processate: 2 (218, 219)
- Video catalogati: 28
- Tempo esecuzione: ~10 secondi

#### 🔄 Fase 2: Upload YouTube (Da Implementare)

- Integrare anagrafica con `main.py`
- Processare solo video con `youtube_id` vuoto
- Popolare `youtube_id` dopo upload riuscito
- Rispettare quota YouTube API (max 6 video/giorno)

#### 📋 Fase 3: Automazione (Da Configurare)

- Cron job giornaliero per `build_anagrafica.py`
- Cron job per upload graduale video
- Monitoraggio e alerting