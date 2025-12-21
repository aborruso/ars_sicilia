# Build Anagrafica Filmati ARS

## Obiettivo

Creare script giornaliero che costruisce e mantiene aggiornata anagrafica filmati sedute ARS.

**Seduta di partenza:** 10 dicembre 2025 (seduta n. 219)
**URL start:** https://www.ars.sicilia.it/agenda/sedute-aula/seduta-numero-219-del-10122025

## Fase 1: Script anagrafica base ✅

- [x] Creare `build_anagrafica.py`
  - Crawler incrementale sedute (da URL start)
  - Estrae metadati senza download video
  - Salva in `data/anagrafica_video.csv`
  - **Filtra solo sedute dal 10/12/2025 in poi**

- [x] Schema CSV anagrafica
  - numero_seduta, data_seduta, url_pagina
  - odg_url, resoconto_url
  - id_video, ora_video, data_video
  - stream_url, video_page_url
  - youtube_id (null se non uploadato)
  - last_check (timestamp ultimo controllo ISO 8601)

- [x] Logica incrementale
  - Legge CSV esistente
  - Identifica sedute già processate
  - Crawla solo sedute nuove
  - Si ferma alle sedute precedenti al 10/12/2025

## Fase 2: Configurazione ✅

- [x] Aggiorna `config/config.yaml`
  - Parametro `anagrafica_file`
  - URL seduta di partenza (219 del 10/12/2025)
  - Filtro data limite hardcoded

- [x] Script wrapper per cron
  - `run_daily.sh` con lock file
  - Log output giornaliero in `data/logs/`
  - Error handling e trap cleanup

## Fase 3: Test ✅

- [x] Test crawler incrementale
  - Verifica filtra sedute prima del 10/12/2025 ✓
  - Controlla gestione sedute già processate (skip) ✓

- [x] Validazione CSV
  - Schema corretto con 12 colonne ✓
  - Timestamp ISO 8601 ✓
  - 4 video seduta 218 del 10/12/2025 processati ✓

---

## Review

**Implementazione completata:**

1. **Script `build_anagrafica.py`:**
   - Crawler incrementale che estrae metadati sedute ARS
   - Filtra solo sedute dal 10 dicembre 2025 in poi
   - Si ferma automaticamente quando raggiunge sedute più vecchie
   - Gestisce sedute già processate (skip)
   - Salva in CSV con timestamp ISO 8601

2. **Schema CSV:**
   - 12 colonne con tutti i metadati necessari
   - youtube_id inizialmente vuoto (popolato dopo upload)
   - last_check traccia ultimo aggiornamento

3. **Script wrapper `run_daily.sh`:**
   - Lock file per evitare esecuzioni concorrenti
   - Logging giornaliero in `data/logs/`
   - Error handling completo
   - Pronto per cron

**Uso:**
```bash
# Manuale
./run_daily.sh

# Cron (ogni giorno alle 8:00)
0 8 * * * /path/to/ars_sicilia/run_daily.sh
```

**Output primo run:**
- Sedute nuove: 1 (seduta 218 del 10/12/2025)
- Video totali: 4
- Sedute filtrate: 1 (217 del 09/12/2025 - precedente al limite)
