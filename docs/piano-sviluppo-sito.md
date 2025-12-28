# Piano Sviluppo Sito Astro - ARS Sicilia

## Contesto

Sviluppo sito statico Astro per consultare sedute Assemblea Regionale Siciliana, partendo da zero (no setup esistente).

**Dati disponibili:**
- `data/anagrafica_video.csv` - 27 video, 2 sedute (219, 220)
- `data/disegni_legge.jsonl` - 4 disegni legge discussi
- `data/digest/*.json` - 26 digest con summary, categorie, persone

**Requisiti UX:**
- Home: lista sedute paginata (max 10), filtri categorie, ordinamento data DESC
- Single seduta: video raggruppati per date, link documenti/disegni
- Single video: embed YouTube, digest, breadcrumb
- URL: `/sedute/YYYY/MM/DD/seduta-NNN/` e `/sedute/YYYY/MM/DD/seduta-NNN/video-HHMM/`

**Riferimento UI esistente:** `viewer/index.html` (HTML standalone con stile simile da replicare)

---

## Fase 1: Setup Base e Data Pipeline

### 1.1 Inizializzazione Astro

Creare progetto Astro con Tailwind CSS:

**File da creare:**
- `package.json` - dependencies Astro, Tailwind, csv-parse, marked
- `astro.config.mjs` - config GitHub Pages (site, base, output static)
- `tailwind.config.mjs` - theme custom (colori, typography plugin)
- `tsconfig.json` - TypeScript config

**Script npm:**
```json
{
  "prebuild": "node scripts/build-data.mjs",
  "dev": "npm run prebuild && astro dev",
  "build": "astro build"
}
```

### 1.2 Script Data Processing

Creare `scripts/build-data.mjs` per processare dati a build time:

**Logica:**
1. Legge `anagrafica_video.csv` (csv-parse)
2. Legge `disegni_legge.jsonl` (parse line by line)
3. Legge tutti `digest/*.json`
4. Join:
   - CSV + digest via `youtube_id`
   - CSV + disegni via `odg_url = pdf_url`
5. Aggrega video per seduta
6. Estrae categorie unique con count
7. Output JSON in `src/data/processed/`:
   - `sedute.json` - array sedute con video nested
   - `videos.json` - array video flat con riferimento seduta
   - `categories.json` - array categorie con slug e count

**File da creare:**
- `/home/aborruso/git/idee/ars_sicilia/scripts/build-data.mjs`
- `/home/aborruso/git/idee/ars_sicilia/src/data/processed/` (directory auto-generata)

### 1.3 TypeScript Types

Definire interfaces in `src/types/`:

**File da creare:**
- `src/types/seduta.ts` - interface Seduta, Video, Digest, DisegnoLegge, Person
- `src/lib/data-loader.ts` - funzioni async per caricare JSON processed
- `src/lib/utils.ts` - utility (formatDate, slugify, etc)

---

## Fase 2: Layouts e Componenti Base

### 2.1 Layout Base

Creare `src/layouts/BaseLayout.astro` con:
- HTML semantico (lang="it")
- Meta tags completi (title, description, OG, Twitter)
- Skip link accessibilità (focus-visible al top)
- Slot header, main, footer
- ViewTransitions Astro

**File da creare:**
- `/home/aborruso/git/idee/ars_sicilia/src/layouts/BaseLayout.astro`
- `/home/aborruso/git/idee/ars_sicilia/src/layouts/PageLayout.astro` (wrapper con container)

### 2.2 Componenti Layout

**File da creare:**
- `src/components/layout/Header.astro` - logo, nav, link ARS
- `src/components/layout/Footer.astro` - credits, link progetto
- `src/components/layout/Breadcrumb.astro` - breadcrumb navigation (array items)

### 2.3 Componenti UI

**File da creare:**
- `src/components/ui/Pagination.astro` - paginazione classica (← 1 2 3 →)
- `src/components/ui/CategoryFilter.astro` - filtri categorie (progressive enhancement)

### 2.4 Stili Globali

**File da creare:**
- `src/styles/global.css` - import Tailwind, custom utilities, focus-visible

---

## Fase 3: Componenti Sedute

### 3.1 Componenti Visualizzazione

**File da creare:**
- `src/components/sedute/SedutaCard.astro` - card per lista (header gradient, meta, toggle)
- `src/components/sedute/VideoThumbnail.astro` - thumbnail YouTube lazy + orario
- `src/components/sedute/VideosByDate.astro` - raggruppa video per `data_video`
- `src/components/sedute/VideoEmbed.astro` - iframe YouTube responsive
- `src/components/sedute/DigestContent.astro` - render digest markdown (marked)
- `src/components/sedute/DisegniList.astro` - lista disegni legge con link ICARO
- `src/components/sedute/CategoryBadge.astro` - badge categoria cliccabile

**Note implementazione:**
- `VideosByDate`: heading H3 per ogni data, array video sotto
- `DigestContent`: fallback se digest assente (video senza transcript)
- `VideoThumbnail`: thumbnail URL `https://i.ytimg.com/vi/{youtubeId}/hqdefault.jpg`

---

## Fase 4: Pagine e Routing

### 4.1 Homepage

**File:** `src/pages/index.astro`

- Carica prime 10 sedute
- Loop con `<SedutaCard>`
- Pagination se `totalPages > 1`
- CategoryFilter component

### 4.2 Lista Sedute Paginata

**File:** `src/pages/sedute/[page].astro`

- `getStaticPaths()` genera pagine (1, 2, 3...)
- 10 sedute per pagina
- Pagination con currentPage highlight

### 4.3 Single View Seduta

**File:** `src/pages/sedute/[anno]/[mese]/[giorno]/[seduta]/index.astro`

**getStaticPaths():**
- Loop sedute, genera params da `yearMonthDay` + `slug`
- Props: seduta completa

**Template:**
- Breadcrumb (Home > Sedute > Seduta NNN)
- H1: "Seduta n. {numero}"
- Meta: data formattata (giorno, mese anno)
- Link documenti: ARS, OdG PDF, Resoconto PDF
- `<DisegniList>` se presente
- `<VideosByDate>` con video raggruppati

### 4.4 Single View Video

**File:** `src/pages/sedute/[anno]/[mese]/[giorno]/[seduta]/[video].astro`

**getStaticPaths():**
- Double loop: sedute > videos
- Params: anno/mese/giorno/seduta/video
- Props: seduta + video

**Template:**
- Breadcrumb (Home > Sedute > Seduta NNN > Video HH:MM)
- H1: "Seduta n. {numero} - Video {ora}"
- `<VideoEmbed>` YouTube
- Categorie badge cliccabili
- `<DigestContent>` se presente
- Link "← Torna alla seduta"

### 4.5 Pagina Categorie

**File:** `src/pages/sedute/categoria/[slug].astro`

**getStaticPaths():**
- Loop categories.json
- Filtra video con categoria = slug

**Template:**
- Lista video filtrati ordinati per data DESC
- Thumbnail + link

### 4.6 Pagine Statiche

**File da creare:**
- `src/pages/about.astro` - About progetto
- `src/pages/404.astro` - Error page

---

## Fase 5: SEO e Feed

### 5.1 Sitemap Automatico

**File:** `astro.config.mjs`

Aggiungere integration:
```js
import sitemap from '@astrojs/sitemap';

integrations: [tailwind(), sitemap()]
```

### 5.2 RSS Feed

**File:** `src/pages/rss.xml.ts`

Endpoint Astro che genera RSS:
- Ultimi 20 video
- Item: titolo, link, pubDate, description (digest substring)

### 5.3 Structured Data

Aggiungere script JSON-LD nelle single view video:
- Schema.org VideoObject
- Name, uploadDate, duration, thumbnailUrl, embedUrl

### 5.4 Assets SEO

**File da creare:**
- `public/og-default.png` - immagine OG default
- `public/favicon.svg` - favicon
- `public/robots.txt` - allow all + sitemap URL

---

## Fase 6: Deploy GitHub Pages

### 6.1 Workflow CI

**File:** `.github/workflows/deploy-site.yml`

**Trigger:**
- Push main su path: `data/`, `src/`, `scripts/build-data.mjs`, config Astro
- workflow_dispatch

**Jobs:**
1. Build: checkout, setup Node 20, npm ci, npm run build, upload artifact
2. Deploy: deploy-pages action

**Permissions:**
- contents: read
- pages: write
- id-token: write

### 6.2 GitHub Pages Setup

Configurare repo:
- Settings > Pages > Source: GitHub Actions
- Base URL in astro.config.mjs: `/ars_sicilia`

---

## Ordine Implementazione

### Sprint 1 (Fondamenta)
1. Setup Astro + package.json + configs
2. Script build-data.mjs + test output JSON
3. TypeScript types + data-loader
4. BaseLayout + global styles

### Sprint 2 (Componenti)
5. Header, Footer, Breadcrumb
6. SedutaCard, VideoThumbnail, VideosByDate
7. VideoEmbed, DigestContent, DisegniList
8. Pagination, CategoryFilter

### Sprint 3 (Pagine)
9. Homepage + lista paginata
10. Single view seduta
11. Single view video
12. Pagina categorie

### Sprint 4 (Deploy)
13. RSS feed + sitemap
14. Structured data + OG images
15. GitHub Actions workflow
16. Test produzione

---

## File Critici

1. **`scripts/build-data.mjs`** - core data pipeline, join CSV+JSONL+JSON
2. **`src/pages/sedute/[anno]/[mese]/[giorno]/[seduta]/index.astro`** - template seduta
3. **`src/layouts/BaseLayout.astro`** - foundation accessibilità + SEO
4. **`src/lib/data-loader.ts`** - load JSON processed
5. **`astro.config.mjs`** - config build + deploy

---

## Considerazioni Tecniche

### Sedute Multi-Giorno
Seduta 220 ha video dal 16/12 al 20/12. Soluzione: `VideosByDate.astro` raggruppa per `data_video` con heading date.

### Video Senza Digest
1 video (youtube_id `dIkMd2LLKgw`) ha `duration_minutes=0` e digest vuoto. Soluzione: fallback in `DigestContent.astro`.

### Categorie Normalizzate
Slug categorie normalizzato in `build-data.mjs` (lowercase, no accenti, dash-case). Display name originale.

### URL Stabili
URL basato su `data_seduta` (non `data_video`). Numero seduta è stabile da fonte ARS.

---

## Domande Aperte

**Design:**
- Palette colori preferita? (viewer usa gradient viola-blu, possiamo mantenerlo o cambiare)
- Logo/brand ARS da includere in header?

**Contenuti:**
- Testo About page: cosa includere? (metodologia, crediti, link esterni)
- Footer: quali link oltre a GitHub?

**Accessibilità:**
- Target contrasto: WCAG AA o AAA?
- Testare con screen reader specifico?
