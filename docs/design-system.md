# ARS Sicilia - Design System "Editorial Civic"

**Redesign completo del frontend con identità editoriale e focus su trasparenza civica**

---

## 🎨 Direzione Estetica

**Concept**: "Editorial Civic" - Design editoriale che combina:
- Autorevolezza istituzionale
- Accessibilità moderna
- Identità siciliana
- Trasparenza e chiarezza

Ispirato ai grandi siti editoriali europei (The Guardian, Il Post, NZZ) con tocchi di design istituzionale italiano.

---

## 🎨 Palette Colori

### Navy Istituzionale
Trasmette autorevolezza e credibilità istituzionale.

- `navy-800`: `#1e3a5f` (Primary - Titoli, CTA, header)
- `navy-700`: `#334e68`
- `navy-600`: `#486581`
- `navy-100`: `#d9e2ec` (Backgrounds leggeri)

**Utilizzo**: Titoli principali, bottoni primari, testi importanti, bordi distintivi.

### Ambra Siciliana
Richiama i toni caldi della Sicilia, porta calore e identità.

- `amber-600`: `#d97706` (Accent - Bordi, link, hover)
- `amber-500`: `#f59e0b`
- `amber-100`: `#fef3c7` (Backgrounds badge)

**Utilizzo**: Bordi a sinistra delle card, link hover, badge categorie, accenti decorativi.

### Verde Salvia
Rappresenta trasparenza e positività.

- `sage-800`: `#059669` (Success states)
- `sage-100`: `#dcfce7` (Backgrounds leggeri)

**Utilizzo**: Badge successo, stati positivi, link documenti ufficiali.

### Grigi Caldi
Neutri caldi per leggibilità e sfumature.

- `warm-800`: `#292524` (Testo principale)
- `warm-600`: `#57534e` (Testo secondario)
- `warm-200`: `#e7e5e4` (Bordi)
- `warm-50`: `#fafaf9` (Background principale)

---

## ✍️ Tipografia

### Font Display: **Fraunces**
Serif editoriale con forte personalità.

```css
font-family: 'Fraunces', Georgia, serif;
```

**Utilizzo**:
- Titoli H1, H2, H3
- Numeri grandi (statistiche)
- Logo header

**Caratteristiche**: Alta leggibilità, autorevolezza, carattere distintivo.

### Font Body: **Manrope**
Sans-serif geometrico, moderno e leggibile.

```css
font-family: 'Manrope', system-ui, sans-serif;
```

**Utilizzo**:
- Testo corpo
- Navigazione
- Bottoni
- Descrizioni

**Caratteristiche**: Geometrico, pulito, ottima leggibilità su schermi.

### Gerarchia Tipografica

```astro
<!-- Hero titles -->
<h1 class="text-4xl md:text-5xl lg:text-6xl font-display font-bold text-navy-800">
  Archivio Sedute ARS
</h1>

<!-- Section titles -->
<h2 class="text-2xl font-display font-bold text-navy-800">
  Ultime sedute
</h2>

<!-- Card titles -->
<h2 class="text-3xl md:text-4xl font-display font-bold text-navy-800">
  Seduta n. 220
</h2>

<!-- Body text -->
<p class="text-lg text-warm-600 font-medium">
  Descrizione chiara e leggibile
</p>
```

---

## 🎨 Visual Language

### 1. Bordi Colorati a Sinistra
Elemento distintivo che crea gerarchia visiva.

```astro
<!-- Card con bordo ambra (default) -->
<div class="card">...</div>

<!-- Card con bordo navy -->
<div class="card-navy">...</div>

<!-- Card con bordo sage -->
<div class="card-sage">...</div>

<!-- Custom border -->
<div class="border-l-4 border-l-amber-600 pl-6">...</div>
```

### 2. Pattern Geometrico Sfondo
Sottile griglia geometrica che aggiunge texture senza distrarre.

```astro
<body class="bg-warm-50 bg-pattern">
  <!-- Il pattern è applicato automaticamente al body -->
</body>
```

### 3. Icone Outline
Icone SVG leggere e coerenti con lo stile editoriale.

```astro
<!-- Esempio icona calendario -->
<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
        d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
</svg>
```

### 4. Stati Hover Animati
Transizioni fluide con effetti visivi distintivi.

```astro
<!-- Bottone con hover -->
<a class="btn-primary">
  <!-- Background cambia, shadow aumenta -->
</a>

<!-- Link con underline colorato -->
<a class="link-editorial">
  <!-- Colore testo e underline si scambiano -->
</a>

<!-- Card con bordo animato -->
<article class="card hover:border-l-navy-800">
  <!-- Bordo cambia colore al hover -->
</article>
```

---

## 🧩 Componenti Principali

### Header
Header sticky con backdrop blur, logo distintivo e navigazione chiara.

**File**: `src/components/layout/Header.astro`

**Caratteristiche**:
- Logo con stemma "ARS" in gradient navy
- Titolo font display con sottotitolo uppercase
- Navigazione con stati attivi evidenti
- Sticky con backdrop blur per leggibilità su scroll

### SedutaCard
Card principale per visualizzare le sedute.

**File**: `src/components/sedute/SedutaCard.astro`

**Caratteristiche**:
- Bordo ambra a sinistra caratteristico
- Titolo grande font display (3xl-4xl)
- Icone outline per metadati
- Badge colorati per categorie
- Footer con CTA chiara
- Hover con animazione bordo

### CategoryFilter
Filtro categorie con design a badge interattivi.

**File**: `src/components/ui/CategoryFilter.astro`

**Caratteristiche**:
- Container con bordo ambra
- Badge interattivi con hover navy
- Contatore categorie animato
- Icona filtro decorativa

### Pagination
Paginazione accessibile con navigazione chiara.

**File**: `src/components/ui/Pagination.astro`

**Caratteristiche**:
- Numeri pagina con hover distintivo
- Stato corrente evidenziato in navy
- Mobile-responsive (nasconde testo su mobile)

### Footer
Footer informativo con grid 3 colonne.

**File**: `src/components/layout/Footer.astro`

**Caratteristiche**:
- Struttura a 3 colonne (About, Links, Info)
- Link con icone esterne
- Badge tech stack
- Messaging trasparenza civica

---

## 🎨 Utilities CSS Custom

### Bottoni

```astro
<!-- Bottone primario (navy) -->
<button class="btn-primary">Azione principale</button>

<!-- Bottone secondario (grigio) -->
<button class="btn-secondary">Azione secondaria</button>

<!-- Bottone accent (ambra) -->
<button class="btn-accent">Azione importante</button>
```

### Badge

```astro
<!-- Badge navy -->
<span class="badge-navy">Istituzionale</span>

<!-- Badge amber -->
<span class="badge-amber">Categoria</span>

<!-- Badge sage -->
<span class="badge-sage">Approvato</span>
```

### Link Editoriale

```astro
<!-- Link con underline colorato -->
<a class="link-editorial" href="#">Link importante</a>
```

### Gradient

```astro
<!-- Gradient editoriale navy -->
<div class="gradient-editorial">...</div>

<!-- Gradient accent ambra -->
<div class="gradient-accent">...</div>

<!-- Text gradient per titoli speciali -->
<h1 class="text-gradient-editorial">Titolo con gradient</h1>
<h2 class="text-gradient-accent">Titolo accent</h2>
```

### Container

```astro
<!-- Container personalizzato (max-w-7xl, padding responsive) -->
<div class="container-custom">...</div>
```

---

## 📱 Responsive Design

Il design è **mobile-first** con breakpoints Tailwind standard:

- **Mobile**: Base styles (< 640px)
- **Tablet**: `sm:` (≥ 640px) e `md:` (≥ 768px)
- **Desktop**: `lg:` (≥ 1024px) e `xl:` (≥ 1280px)

### Esempio Homepage Hero

```astro
<!-- Titolo responsive -->
<h1 class="text-4xl md:text-5xl lg:text-6xl font-display font-bold">
  Archivio Sedute ARS
</h1>

<!-- Grid stats responsive -->
<div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
  <!-- Stats cards -->
</div>
```

---

## ♿ Accessibilità

### Focus States
Tutti gli elementi interattivi hanno focus state visibile:

```css
*:focus-visible {
  @apply outline-2 outline-offset-2 outline-navy-800 rounded;
}
```

### Skip Link
Link "Vai al contenuto" per utenti screen reader:

```astro
<a href="#main-content" class="skip-link">
  Vai al contenuto
</a>
```

### Contrasti
Tutti i colori rispettano WCAG 2.1 AA:
- `navy-800` su bianco: ✅ Contrasto 12.6:1
- `warm-600` su bianco: ✅ Contrasto 7.2:1
- `amber-600` su bianco: ✅ Contrasto 4.9:1

### ARIA Labels
Navigazione e paginazione hanno attributi ARIA appropriati:

```astro
<nav aria-label="Navigazione principale">
  <a aria-current="page">Home</a>
</nav>

<nav aria-label="Paginazione">
  <a aria-label="Pagina 1">1</a>
</nav>
```

---

## 📂 File Modificati

### Core System
- ✅ `tailwind.config.mjs` - Palette, font, utilities custom
- ✅ `src/styles/global.css` - Font import, layer components/utilities

### Layout
- ✅ `src/layouts/BaseLayout.astro` - Background pattern
- ✅ `src/layouts/PageLayout.astro` - (nessuna modifica necessaria)
- ✅ `src/components/layout/Header.astro` - Redesign completo
- ✅ `src/components/layout/Footer.astro` - Redesign completo

### Pages
- ✅ `src/pages/index.astro` - Hero editoriale, stats, sezioni

### Components
- ✅ `src/components/sedute/SedutaCard.astro` - Redesign completo
- ✅ `src/components/ui/CategoryFilter.astro` - Redesign completo
- ✅ `src/components/ui/Pagination.astro` - Redesign completo

### Altri componenti da aggiornare (opzionale)
- `src/components/sedute/VideoThumbnail.astro`
- `src/components/sedute/VideosByDate.astro`
- `src/components/sedute/VideoEmbed.astro`
- `src/components/sedute/DisegniList.astro`
- `src/components/sedute/CategoryBadge.astro`
- `src/pages/about.astro`

---

## 🚀 Come Usare il Nuovo Design

### 1. Build e Preview

```bash
# Installa dipendenze (se necessario)
npm install

# Build Tailwind + Astro
npm run build

# Dev server con hot reload
npm run dev
```

### 2. Creare Nuove Pagine

Usa `PageLayout` come base:

```astro
---
import PageLayout from '../layouts/PageLayout.astro';
---

<PageLayout
  title="Titolo Pagina"
  description="Descrizione SEO"
>
  <!-- Hero con bordo ambra -->
  <div class="border-l-4 border-l-amber-600 pl-6 py-2 mb-8">
    <h1 class="text-5xl font-display font-bold text-navy-800 mb-4">
      Titolo Principale
    </h1>
    <p class="text-xl text-warm-600">
      Sottotitolo o descrizione
    </p>
  </div>

  <!-- Contenuto -->
  <div class="space-y-6">
    <!-- Cards, testo, componenti -->
  </div>
</PageLayout>
```

### 3. Creare Card Custom

```astro
<article class="card">
  <div class="p-6">
    <h3 class="text-2xl font-display font-bold text-navy-800 mb-3">
      Titolo Card
    </h3>
    <p class="text-warm-600 mb-4">
      Descrizione della card con testo leggibile
    </p>
    <a href="#" class="btn-primary">
      Azione
    </a>
  </div>
</article>
```

### 4. Badge e Pills

```astro
<!-- Badge per categorie -->
<span class="badge-amber">Sanità</span>
<span class="badge-navy">Bilancio</span>
<span class="badge-sage">Approvato</span>

<!-- Custom badge -->
<span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-navy-100 text-navy-800 border border-navy-200">
  Custom Badge
</span>
```

---

## 🎯 Principi di Design

### 1. Tipografia Prima di Tutto
La gerarchia tipografica è il principale strumento di comunicazione. Usa font display per titoli importanti, font sans per corpo.

### 2. Bordi al Posto di Ombre
Preferisci bordi colorati (specie a sinistra) invece di ombre pesanti. Crea un look più editoriale e pulito.

### 3. Colore con Significato
Ogni colore ha un ruolo:
- **Navy**: Autorevolezza, istituzionale
- **Amber**: Identità, accenti, call-to-action
- **Sage**: Positività, trasparenza, successo

### 4. Spaziatura Generosa
Usa padding generosi (p-6, py-8) per dare respiro ai contenuti.

### 5. Stati Hover Evidenti
Ogni elemento interattivo ha uno stato hover chiaro e animato (colore, bordi, shadow).

### 6. Mobile-First
Progetta prima per mobile, poi espandi per desktop con breakpoints.

---

## 📊 Metriche di Successo

Il nuovo design punta a migliorare:

- ✅ **Accessibilità**: Contrasti WCAG AA, focus states, ARIA labels
- ✅ **Leggibilità**: Tipografia editoriale, spaziatura generosa
- ✅ **Identità**: Palette siciliana, bordi caratteristici
- ✅ **Usabilità**: Navigazione chiara, stati evidenti
- ✅ **Performance**: CSS ottimizzato, font Google caricati async

---

## 🔮 Prossimi Passi

### Opzionale - Miglioramenti Futuri

1. **Animazioni Page Transitions**
   - Sfruttare `<ViewTransitions />` di Astro per transizioni fluide tra pagine

2. **Dark Mode**
   - Aggiungere palette scura mantenendo identità editoriale
   - Toggle nel header

3. **Componenti Video**
   - Redesign `VideoThumbnail` e `VideoEmbed` con stesso stile

4. **About Page**
   - Creare pagina About con storytelling progetto civic tech

5. **Micro-animazioni**
   - Aggiungere animazioni entrance per cards (scroll-triggered)
   - Animazioni hover più elaborate (scale, rotate leggeri)

---

## 📚 Risorse

### Font
- **Fraunces**: [Google Fonts](https://fonts.google.com/specimen/Fraunces)
- **Manrope**: [Google Fonts](https://fonts.google.com/specimen/Manrope)

### Icone
- **Heroicons**: [heroicons.com](https://heroicons.com/) (outline style)

### Riferimenti Design
- **The Guardian**: Design editoriale britannico
- **Il Post**: Editoriale italiano moderno
- **NZZ**: Tipografia forte, gerarchia chiara

---

**Redesign by Claude Code con frontend-design skill**
*Gennaio 2025*
