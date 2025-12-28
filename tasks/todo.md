# Piano Aggiornamento README.md

## Problema
README attuale descrive solo la pipeline Python/YouTube uploader (OAuth, cron, quota API), ma ignora completamente:
- Sito web Astro (108+ pagine statiche)
- Frontend "Editorial Civic" con design system
- Categorie tematiche, paginazione, navigazione
- Digest AI generati da LLM
- Estrazione disegni legge da PDF OdG
- Feed RSS pubblico
- Piattaforma consultazione civica

Il progetto è evoluto da semplice uploader a piattaforma completa di civic engagement.

## Obiettivo
Ristrutturare README per presentare il progetto come piattaforma civic tech con due componenti principali:
1. **Sito web statico** per consultare sedute (frontend)
2. **Pipeline automatizzata** per acquisizione e pubblicazione (backend)

## Struttura Proposta

### Sezione 1: Introduzione
- Titolo: "ARS Sicilia - Archivio Consultabile Sedute Assemblea"
- Sottotitolo: "Piattaforma civic tech per trasparenza e consultazione sedute ARS"
- Descrizione breve del progetto (civic hacking, trasparenza, ricerca)
- Screenshot o link demo: https://aborruso.github.io/ars_sicilia/

### Sezione 2: Cosa Offre il Progetto
Lista funzionalità principali:
- ✅ Sito web con 108+ pagine sedute consultabili
- ✅ Categorie tematiche per filtrare sedute
- ✅ Video su YouTube con metadati ricercabili
- ✅ Digest AI automatici da trascrizioni
- ✅ Estrazione disegni legge da PDF OdG
- ✅ Feed RSS pubblico per aggiornamenti
- ✅ Design accessibile WCAG 2.1 AA

### Sezione 3: Architettura Sistema
Descrizione componenti:
1. **Frontend (Astro + Tailwind)**
   - Sito statico generato a build-time
   - Design system "Editorial Civic"
   - GitHub Pages hosting
   - Link: docs/design-system.md

2. **Backend Pipeline (Python)**
   - Crawler incrementale sedute ARS
   - Download video HLS (yt-dlp)
   - Upload YouTube con API v3
   - Generazione digest AI (LLM)
   - Estrazione disegni legge (PDF → JSONL)

3. **Data Layer**
   - anagrafica_video.csv (metadati sedute)
   - disegni_legge.jsonl (dati legislativi)
   - digest/{youtube_id}.json (sintesi AI)
   - rss.xml (feed pubblico)

### Sezione 4: Stack Tecnologico
**Frontend:**
- Astro 5.0, Tailwind CSS 3.4, TypeScript
- @astrojs/sitemap, @astrojs/rss
- GitHub Pages + GitHub Actions deploy

**Backend:**
- Python 3.10+, yt-dlp, google-api-python-client
- BeautifulSoup4, pyyaml, csv-parse
- LLM CLI (gemini-2.5-flash per digest)
- markitdown (PDF→text), miller (CSV ops)

### Sezione 5: Quick Start
**Consultare il sito:**
- Visita https://aborruso.github.io/ars_sicilia/
- Filtra per categoria, naviga sedute, leggi digest AI

**Contribuire al progetto:**
- Fork repository, setup locale, submit PR
- Link: CONTRIBUTING.md (se esiste)

### Sezione 6: Setup Sviluppo Locale
**Frontend:**
```bash
npm install
npm run build  # Genera sito in dist/
npm run dev    # Dev server localhost:4321
```

**Backend (opzionale):**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

### Sezione 7: Pipeline YouTube (Per Sviluppatori)
**⚠️ Sezione tecnica avanzata - solo per chi vuole replicare pipeline**

Collassare o spostare in documento separato:
- Setup Google Cloud e YouTube API
- OAuth2 configuration
- Credenziali secrets
- Cron jobs, GitHub Actions
- Quota management
- Troubleshooting

Oppure linkare a docs/youtube-setup.md (nuovo file)

### Sezione 8: Documentazione
Link a documenti esistenti:
- 📋 PRD.md - Product Requirements Document
- 🎨 docs/design-system.md - Design system "Editorial Civic"
- 📊 LOG.md - Changelog dettagliato progetto
- 🏗️ openspec/project.md - Specifica architettura
- 🔍 ars_sicilia_api/ - Client API disegni legge

### Sezione 9: Dati Aperti
**Dataset pubblici disponibili:**
- data/anagrafica_video.csv (metadati sedute)
- data/disegni_legge.jsonl (disegni legge estratti)
- data/digest/{youtube_id}.json (sintesi AI)
- feed pubblico: rss.xml

**Licenza dati:** (specificare se CC0, CC-BY, etc)

### Sezione 10: Roadmap e Prossimi Passi
- [ ] Trascrizione automatica export per analisi
- [ ] Dashboard query disegni legge
- [ ] Linkage video↔disegni discussi
- [ ] Search engine Pagefind (full-text)
- [ ] Dark mode

### Sezione 11: Contributi e Licenza
- Come contribuire
- Licenza progetto (MIT, Apache, GPL?)
- Crediti: ARS Sicilia, civic hackers, skill utilizzati

### Sezione 12: Contatti
- Issues GitHub per bug/feature request
- Link canale YouTube (se pubblico)
- Link feed RSS

## Cambiamenti Chiave
1. **Titolo e focus**: da "YouTube Uploader" a "Archivio Consultabile Sedute"
2. **Struttura**: sito web FIRST, pipeline YouTube SECOND (invertito)
3. **Audience**: da sviluppatori Python a cittadini + sviluppatori
4. **Lunghezza**: ridurre parte tecnica YouTube (collassare o spostare in docs/)
5. **Link esterni**: più link a docs esistenti invece di duplicare contenuto

## Sezioni da Mantenere (Spostate)
Dal README attuale, preservare ma riorganizzare:
- ✅ Setup YouTube API (spostare in docs/youtube-setup.md o collassare)
- ✅ OAuth2 configuration (idem)
- ✅ Anagrafica video (descrivere brevemente, dettagli in docs/)
- ✅ Upload workflow (idem)
- ✅ Troubleshooting (spostare in docs/troubleshooting.md)

## Todo

- [x] Leggere file chiave (PRD.md, LOG.md, design-system.md, package.json)
- [x] Verificare piano con utente
- [x] Approvazione utente
- [x] Scrivere nuovo README.md con struttura approvata
- [x] Aggiornare LOG.md con entry nuovo README

## Review

### Completato

README.md completamente ristrutturato con successo.

### Cambiamenti Implementati

**Titolo e posizionamento:**
- Titolo cambiato: "YouTube Uploader" → "Archivio Consultabile Sedute Assemblea"
- Sottotitolo: "Piattaforma civic tech per trasparenza e consultazione"
- Link demo prominente: https://aborruso.github.io/ars_sicilia/

**Struttura finale (12 sezioni):**
1. ✅ Introduzione - Quote civic hacking, link demo
2. ✅ Cosa Offre - 8 funzionalità chiave con emoji
3. ✅ Architettura - 3 livelli (Frontend, Backend, Data)
4. ✅ Quick Start - Consultare sito, dati aperti, RSS
5. ✅ Setup Sviluppo - Frontend (npm), Backend (Python opzionale)
6. ✅ Stack Tecnologico - Frontend + Backend dettagliato
7. ✅ Pipeline YouTube - Collassato in `<details>` tag
8. ✅ Documentazione - Link a PRD, design-system, LOG, openspec, API
9. ✅ Struttura Progetto - Tree ASCII completo
10. ✅ Dati Aperti - Tabella dataset, schema CSV/JSONL
11. ✅ Roadmap - In sviluppo, prossimi passi, idee future
12. ✅ Contributi e Licenza - How to contribute, crediti, contatti

**Priorità invertita:**
- Frontend/sito web NOW in sezioni 1-5 (prominente)
- Backend/YouTube NOW in sezione 7 (collassato, tecnico)
- Audience: cittadini + sviluppatori (era solo sviluppatori)

**Riduzione complessità:**
- Setup YouTube: da ~500 righe standalone → ~150 righe collapsate in `<details>`
- Informazioni tecniche preservate ma organizzate meglio
- Più link a docs/ esistenti invece duplicare contenuto

**Aggiunte nuove:**
- Sezione Dati Aperti (tabella dataset, schema campi)
- Sezione Roadmap (in sviluppo, prossimi passi, idee future)
- Sezione Struttura Progetto (tree ASCII completo)
- Quick Start per cittadini (non solo dev)

**Miglioramenti SEO/UX:**
- Emoji strategici per scansionabilità
- Link diretti a demo sito (3 occorrenze)
- Feed RSS prominente
- Code blocks con syntax highlighting
- Tabelle Markdown per dati strutturati

### File Modificati

- `README.md` - Completa riscrittura (494 righe)
- `LOG.md` - Aggiunta entry 2025-12-28
- `tasks/todo.md` - Questo file (piano + review)

### Completezza

Tutti gli obiettivi del piano sono stati raggiunti:
- ✅ Titolo e focus aggiornati
- ✅ Struttura invertita (sito first, YouTube second)
- ✅ Audience ampliata (cittadini + dev)
- ✅ Setup tecnico collassato/organizzato
- ✅ Più link a docs esistenti
- ✅ Sezioni dati aperti e roadmap aggiunte

### Note Opzionali Non Implementate

- **docs/youtube-setup.md** - Non creato (le info sono già complete e ben organizzate nel `<details>` tag del README)
- **docs/troubleshooting.md** - Non creato (troubleshooting già nel `<details>` YouTube)

Queste sezioni possono essere estratte in futuro se il README diventa troppo lungo, ma per ora la struttura collassabile `<details>` è sufficiente.
