# ARS Sicilia - Archivio Consultabile Sedute Assemblea

**Piattaforma civic tech per trasparenza e consultazione sedute dell'Assemblea Regionale Siciliana**

> Questo progetto nasce da un'idea semplice da civic hacker: la trasparenza deve essere efficace. Non basta dire "i video sono online": chi vuole capire se e quando si è parlato di un argomento oggi ha davanti solo un elenco di video. Portarli su YouTube con metadati strutturati e trascrizione automatica, e creare un sito consultabile con categorie e digest AI cambia tutto: si può cercare nel testo, collegare sedute e video, e usare le trascrizioni come materia prima per analisi civica.

**🌐 Consulta il sito:** [aborruso.github.io/ars_sicilia](https://aborruso.github.io/ars_sicilia/)

---

## 🎯 Cosa Offre il Progetto

- ✅ **Sito web consultabile** - 108+ pagine statiche generate con Astro
- ✅ **Categorie tematiche** - Filtra sedute per argomento (Sanità, Bilancio, Lavoro, etc.)
- ✅ **Video YouTube ricercabili** - Metadati strutturati, playlist annuali, token univoci
- ✅ **Digest AI automatici** - Sintesi generate da trascrizioni video con LLM
- ✅ **Estrazione disegni legge** - Dati legislativi estratti da PDF ordini del giorno
- ✅ **Feed RSS pubblico** - Aggiornamenti automatici ultimi 20 video
- ✅ **Design accessibile** - WCAG 2.1 AA, mobile-first, semantic HTML
- ✅ **Dati aperti** - CSV, JSONL, JSON pubblicamente accessibili

---

## 🏗️ Architettura Sistema

Il progetto è composto da tre livelli:

### 1. Frontend - Sito Web Statico (Astro + Tailwind)

Sito statico generato a build-time con design system "Editorial Civic":

- **Tecnologie**: Astro 5.0, Tailwind CSS 3.4, TypeScript
- **Pagine**: Homepage, lista sedute paginata, singola seduta, singolo video, categorie, About
- **SEO**: Sitemap automatico, structured data (Schema.org VideoObject), OpenGraph
- **Hosting**: GitHub Pages con deploy automatico
- **Design**: Palette istituzionale (Navy, Ambra, Salvia), tipografia editoriale (Fraunces + Manrope)

📖 **Documentazione design**: [docs/design-system.md](docs/design-system.md)

### 2. Backend - Pipeline Automatizzata (Python)

Sistema di acquisizione e pubblicazione video sedute:

- **Crawler incrementale** - Estrae metadati sedute dal 10/12/2025 in poi
- **Download video HLS** - yt-dlp per scaricare stream video ARS
- **Upload YouTube** - API v3 con OAuth2, playlist annuali, metadati ricchi
- **Generazione digest AI** - LLM (Gemini 2.5 Flash) per sintesi automatiche
- **Estrazione disegni legge** - Pipeline PDF→testo→JSON strutturato

**Script principali:**
- `scripts/build_anagrafica.py` - Aggiorna anagrafica video
- `scripts/upload_single.py` - Test upload singolo video
- `scripts/generate_digests.sh` - Genera digest AI da trascrizioni
- `scripts/extract_odg_data.sh` - Estrae disegni legge da PDF OdG
- `scripts/generate_rss.py` - Genera feed RSS pubblico

### 3. Data Layer - Dati Strutturati

Dataset pubblici in formato aperto:

- `data/anagrafica_video.csv` - Metadati completi sedute (35+ record)
- `data/disegni_legge.jsonl` - Disegni di legge estratti da OdG
- `data/digest/{youtube_id}.json` - Digest AI per ogni video
- `rss.xml` - Feed RSS pubblico (ultimi 20 video)

---

## 🚀 Quick Start

### Consultare il Sito

Visita [aborruso.github.io/ars_sicilia](https://aborruso.github.io/ars_sicilia/) per:
- Esplorare sedute per data o categoria
- Guardare video direttamente dalla pagina
- Leggere digest AI automatici
- Accedere ai documenti ufficiali (OdG, Resoconti)

### Accedere ai Dati Aperti

Tutti i dataset sono pubblicamente accessibili nel repository:

```bash
# Clona repository
git clone https://github.com/aborruso/ars_sicilia.git

# Esplora dati
cd ars_sicilia/data
cat anagrafica_video.csv | head -20
cat disegni_legge.jsonl | jq .
```

### Feed RSS

Abbonati al feed per ricevere aggiornamenti automatici:

**URL feed**: [https://aborruso.github.io/ars_sicilia/rss.xml](https://aborruso.github.io/ars_sicilia/rss.xml)

---

## 💻 Setup Sviluppo Locale

### Prerequisiti

- Node.js 18+ e npm
- Python 3.10+ (opzionale, solo per backend)
- Git

### Frontend - Sito Web

```bash
# Installa dipendenze
npm install

# Build data + sito (genera dist/)
npm run build

# Dev server con hot reload
npm run dev
# Apri http://localhost:4321
```

### Creare nuove pagine in Markdown

È possibile aggiungere pagine statiche in Markdown dentro `src/pages/`.  
Consulta la guida completa: `docs/markdown-guide.md`.

**Struttura generata:**
- `dist/index.html` - Homepage
- `dist/sedute/` - Lista sedute paginata
- `dist/sedute/[anno]/[mese]/[giorno]/[seduta]/` - Pagine singole
- `dist/sitemap-0.xml`, `dist/rss.xml` - SEO

### Backend - Pipeline Python (Opzionale)

Solo necessario se vuoi replicare la pipeline di acquisizione/pubblicazione:

```bash
# Crea virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Installa dipendenze
pip3 install -r requirements.txt

# Testa crawler
python3 scripts/build_anagrafica.py

# Genera digest AI (richiede configurazione LLM)
./scripts/generate_digests.sh
```

---

## 📊 Stack Tecnologico

### Frontend
- **Framework**: Astro 5.0 (generazione statica)
- **Styling**: Tailwind CSS 3.4 + Typography plugin
- **Language**: TypeScript
- **Plugins**: @astrojs/sitemap, @astrojs/rss
- **Build**: npm scripts + prebuild hook (build-data.mjs)
- **Deploy**: GitHub Actions → GitHub Pages

### Backend
- **Language**: Python 3.10+
- **Scraping**: BeautifulSoup4, requests
- **Video**: yt-dlp (download HLS)
- **YouTube API**: google-api-python-client, oauth2client
- **AI**: LLM CLI (gemini-2.5-flash per digest)
- **Data**: PyYAML, csv-parse, markitdown (PDF→text)
- **CLI Tools**: miller (mlr), jq, qv (trascrizioni YouTube)

---

## 🤖 Pipeline YouTube - Setup Avanzato

<details>
<summary><strong>⚠️ Sezione tecnica - Solo per sviluppatori che vogliono replicare la pipeline YouTube</strong></summary>

### Requisiti

- Account YouTube verificato (per video >15 minuti)
- Progetto Google Cloud con YouTube Data API v3 abilitata
- Credenziali OAuth2 (client ID + secret)

### Setup Google Cloud e YouTube API

#### 1. Crea Progetto Google Cloud

1. Vai su [Google Cloud Console](https://console.cloud.google.com/)
2. Clicca "Nuovo Progetto" → Nome: `ars-youtube-uploader`
3. Nel progetto, vai su "API & Services" → "Library"
4. Cerca "YouTube Data API v3" → Clicca "Abilita"

#### 2. Configura OAuth Consent Screen

1. Vai su "API & Services" → "OAuth consent screen"
2. Seleziona "External" → Compila:
   - App name: `ARS Video Uploader`
   - User support email: tua email
3. Scopes: aggiungi `https://www.googleapis.com/auth/youtube.upload`
4. Test users: aggiungi email Google del canale YouTube

#### 3. Crea Credenziali OAuth 2.0

1. Vai su "API & Services" → "Credentials"
2. "Create Credentials" → "OAuth client ID"
3. Application type: "Desktop app" → Name: `ARS Uploader Desktop`
4. Download JSON → Salva come `config/youtube_secrets.json`

#### 4. Prima Autenticazione

```bash
# Esegui upload test
python3 scripts/upload_single.py --dry-run

# Al primo avvio si apre browser per autorizzazione
# Token salvato in config/token.json per riuso
```

### Configurazione Playlist e Channel ID

#### Ottieni Channel ID

1. Vai su [YouTube Studio](https://studio.youtube.com)
2. Impostazioni → Canale → Copia ID canale (es. `UCxxx...` o `@ARSSicilia`)
3. Apri `config/config.yaml`:
   ```yaml
   youtube:
     channel_id: "@ARSSicilia"  # O UCxxxxxxxxxxxxxxxxxxx
   ```

#### Crea Playlist Annuali

1. YouTube Studio → Playlist → Crea nuova playlist
   - Nome: `ARS 2025 - Sedute Assemblea`
   - Visibilità: Pubblica
2. Copia ID dall'URL: `https://www.youtube.com/playlist?list=PLxxx...`
3. Apri `config/config.yaml`:
   ```yaml
   youtube:
     playlists:
       "2025": "PLxxxxxxxxxxxxxxxxxxx"
       "2026": "PLyyyyyyyyyyyyyyyyyy"
   ```

### Utilizzo

#### Test Upload Singolo Video

```bash
# Preview senza caricare
python3 scripts/upload_single.py --dry-run

# Upload reale primo video da anagrafica
python3 scripts/upload_single.py
```

#### Build Anagrafica Video

```bash
# Aggiorna metadati sedute (crawler incrementale)
./scripts/run_daily.sh

# Con venv
.venv/bin/python3 scripts/build_anagrafica.py
```

#### Generazione Digest AI

```bash
# Genera digest per video con trascrizione
./scripts/generate_digests.sh
```

#### Estrazione Disegni Legge

```bash
# Estrai disegni da PDF ordini del giorno
./scripts/extract_odg_data.sh

# Forza rielaborazione di tutti i PDF (ignora dedup per pdf_url)
./scripts/extract_odg_data.sh --reprocess
```

### Automazione GitHub Actions

Il progetto include workflow automatici:

- **`daily_upload.yml`** - Esegue ogni giorno alle 01:37 UTC:
  - Aggiorna anagrafica sedute
  - Carica fino a 4 video/giorno (rispetta quota API)
  - Commit anagrafica aggiornata

- **`publish_rss.yml`** - Genera e pubblica feed RSS su gh-pages

**Secret richiesti** (Settings → Secrets):
- `YT_CLIENT_SECRET_JSON` - Contenuto `config/youtube_secrets.json`
- `YT_TOKEN_JSON` - Contenuto `config/token.json`

### Limiti e Quota YouTube API

- **Quota giornaliera**: 10,000 units/day (default)
- **Costo upload video**: ~1,600 units
- **Costo playlist insert**: ~50 units
- **Totale per video**: ~1,650 units
- **Max upload/giorno**: ~6 video

Se serve più quota, richiedi aumento su Google Cloud Console.

### Troubleshooting

#### Errore "File credenziali non trovato"
Verifica che `config/youtube_secrets.json` esista con credenziali OAuth2 da Google Cloud.

#### Errore "Quota exceeded"
Hai superato limite giornaliero (10,000 units). Aspetta 24h o richiedi aumento quota.

#### Token scaduto
Elimina `config/token.json` e riavvia script per ri-autenticarsi.

#### Download fallito
- Verifica connessione internet
- Controlla: `yt-dlp --version`
- Prova download manuale: `yt-dlp [URL]`

</details>

---

## 📚 Documentazione

- 📋 [PRD.md](PRD.md) - Product Requirements Document completo
- 🎨 [docs/design-system.md](docs/design-system.md) - Design system "Editorial Civic"
- 📊 [LOG.md](LOG.md) - Changelog dettagliato progetto (aggiornato quotidianamente)
- 🏗️ [openspec/project.md](openspec/project.md) - Specifica architettura backend + frontend
- 🔍 [ars_sicilia_api/](ars_sicilia_api/) - Client Python per API disegni di legge ARS
- 📖 [ars_sicilia_api/API_DOCUMENTATION.md](ars_sicilia_api/API_DOCUMENTATION.md) - Documentazione API ricerca legislativa
- 🔎 [ars_sicilia_api/GUIDA_ALLA_RICERCA.md](ars_sicilia_api/GUIDA_ALLA_RICERCA.md) - Sintassi query avanzate

---

## 📂 Struttura Progetto

```
ars_sicilia/
├── src/                          # Frontend Astro
│   ├── pages/                    # Routing (index, sedute, video, about)
│   ├── components/               # Componenti React/Astro
│   ├── layouts/                  # Layout base
│   └── lib/                      # Data loaders, utilities
├── scripts/                      # Backend Python
│   ├── build_anagrafica.py       # Crawler sedute
│   ├── upload_single.py          # Test upload YouTube
│   ├── generate_digests.sh       # Digest AI
│   ├── extract_odg_data.sh       # Estrai disegni legge
│   └── build-data.mjs            # Build data per Astro (JS)
├── data/                         # Dataset pubblici
│   ├── anagrafica_video.csv      # Metadati sedute
│   ├── disegni_legge.jsonl       # Disegni legge estratti
│   ├── digest/                   # Digest AI JSON
│   └── logs/                     # Log upload, build
├── config/                       # Configurazione
│   ├── config.yaml               # Config backend Python
│   ├── digest.yaml               # Template prompt LLM
│   ├── digest-schema.json        # Schema JSON digest
│   ├── youtube_secrets.json      # Credenziali OAuth2 (non versionato)
│   └── token.json                # Token OAuth2 (auto-generato)
├── docs/                         # Documentazione
│   └── design-system.md          # Guida design system
├── ars_sicilia_api/              # Client API disegni legge
├── dist/                         # Output build Astro (GitHub Pages)
├── package.json                  # Dipendenze frontend
├── requirements.txt              # Dipendenze backend Python
├── tailwind.config.mjs           # Config Tailwind CSS
└── astro.config.mjs              # Config Astro
```

---

## 📊 Dati Aperti

Tutti i dataset sono pubblicamente accessibili e versionati su GitHub:

### Dataset Disponibili

| File | Formato | Descrizione | Record |
|------|---------|-------------|--------|
| `data/anagrafica_video.csv` | CSV | Metadati completi sedute e video | 35+ |
| `data/disegni_legge.jsonl` | JSONL | Disegni di legge estratti da OdG | Variabile |
| `data/digest/{youtube_id}.json` | JSON | Digest AI generati da trascrizioni | 20+ |
| `rss.xml` | RSS 2.0 | Feed pubblico ultimi 20 video | 20 |

### Schema Anagrafica Video (CSV)

Campi principali:
- `numero_seduta` - Numero seduta (es. "219")
- `data_seduta` - Data seduta (YYYY-MM-DD)
- `data_video` - Data video effettiva (YYYY-MM-DD)
- `ora_video` - Ora inizio video (HH:MM)
- `youtube_id` - ID video YouTube (vuoto se non uploadato)
- `odg_url` - Link PDF ordine del giorno
- `resoconto_stenografico_url` - Link resoconto finale
- `duration_minutes` - Durata video in minuti
- `last_check` - Timestamp ultimo aggiornamento

### Schema Disegni Legge (JSONL)

Campi per record:
- `titolo_disegno` - Titolo completo
- `numero_disegno` - Numero DDL (solo parte numerica)
- `legislatura` - Numero romano (es. "XVIII")
- `data_ora` - Data e ora seduta (ISO 8601)
- `pdf_url` - URL PDF sorgente
- `url_disegno` - URL ICARO generato

Nota: lo script normalizza `numero_disegno` con regex `[0-9]+` e scarta record senza numero.

### Licenza Dati

I dati estratti sono derivati da fonti pubbliche dell'Assemblea Regionale Siciliana. Il software di estrazione è open source.

---

## 🗺️ Roadmap

### In Sviluppo
- [ ] Search engine full-text con Pagefind
- [ ] Dashboard query disegni legge (legislatura, anno, firmatario)
- [ ] Linkage automatico video↔disegni discussi

### Prossimi Passi
- [ ] Trascrizione automatica: export testo per analisi
- [ ] Dark mode per sito web
- [ ] Pagina About con storytelling civic hacking
- [ ] API pubblica per interrogare anagrafica

### Idee Future
- [ ] Notifiche Telegram/email per nuove sedute
- [ ] Analisi sentiment discussioni parlamentari
- [ ] Timeline legislativa per singolo DDL
- [ ] Integrazione dati voti elettronici

---

## 🤝 Contributi e Licenza

### Come Contribuire

1. Fork repository
2. Crea branch feature: `git checkout -b feature/nome-feature`
3. Commit modifiche: `git commit -m 'Add: descrizione'`
4. Push branch: `git push origin feature/nome-feature`
5. Apri Pull Request

### Linee Guida

- Segui convenzioni esistenti (Python PEP 8, Prettier per JS/TS)
- Aggiungi test per nuove funzionalità
- Aggiorna documentazione e LOG.md
- Mantieni commit atomici e messaggi chiari

### Licenza

Questo progetto è software libero sviluppato per rendere accessibili i lavori dell'Assemblea Regionale Siciliana.

### Crediti

**Sviluppo**: Civic hacker e contributor GitHub

**Tecnologie**: Astro, Tailwind CSS, Python, YouTube Data API, LLM CLI

**Skill AI utilizzati**:
- `frontend-design` - Design system "Editorial Civic"
- `openspec` - Gestione proposte architetturali

**Fonti dati**: [Assemblea Regionale Siciliana](https://www.ars.sicilia.it)

---

## 📞 Contatti

- **Issues GitHub**: [github.com/aborruso/ars_sicilia/issues](https://github.com/aborruso/ars_sicilia/issues)
- **Feed RSS**: [aborruso.github.io/ars_sicilia/rss.xml](https://aborruso.github.io/ars_sicilia/rss.xml)
- **Repository**: [github.com/aborruso/ars_sicilia](https://github.com/aborruso/ars_sicilia)

---

**Progetto civic tech per trasparenza democratica**
*Ultimo aggiornamento: 2025-12-28*
