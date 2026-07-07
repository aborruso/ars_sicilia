---
type: Componente
title: Sito Astro
description: Routing, layout e data loader del sito statico pubblicato su GitHub Pages.
tags: [frontend, astro]
timestamp: 2026-07-07T00:00:00Z
---

# Config (`astro.config.mjs`)

Output statico (`output: 'static'`, `build.format: 'directory'`),
`site: https://aborruso.github.io`, `base: /ars_sicilia`. Integrazioni:
tailwind, sitemap, mdx. Le pagine Markdown in `src/pages/` ricevono un
layout di default via il remark plugin `remark-default-layout.mjs`.

**Convenzione**: il base path `/ars_sicilia` non ha un helper centrale,
è per lo più hardcoded nelle pagine e negli script client-side (es.
`const BASE = '/ars_sicilia'`). `import.meta.env.BASE_URL` è usato solo
in `rss.xml.ts`.

# Layout

* `src/layouts/BaseLayout.astro` — shell HTML, meta OG/Twitter,
  ViewTransitions, prop `noindex` opzionale (per pagine da escludere dai
  motori di ricerca).
* `src/layouts/PageLayout.astro` — wrappa BaseLayout + Header + Footer +
  container. È il layout di default per le pagine "normali".

# Routing e data loader

* `src/lib/data-loader.ts` — funzioni `loadSedute()`, `loadVideos()`,
  `loadCategories()`, `loadDDLs()` che leggono da `src/data/processed/*.json`
  (generato dal build data-driven, vedi
  [panoramica architetturale](/wiki/architettura/panoramica.md)).
* Pagina video: `src/pages/sedute/[anno]/[mese]/[giorno]/[seduta]/[video].astro`,
  URL nella forma `/ars_sicilia/sedute/{year}/{month}/{day}/{sedutaSlug}/{videoSlug}`.
* `src/components/sedute/VideoEmbed.astro` — player YouTube
  (`youtube-nocookie.com/embed/`). Legge il query param `?t=SECONDI` e lo
  traduce in `start=` sull'iframe (deep-link al secondo, aggiunto per la
  feature di [ricerca nelle trascrizioni](/wiki/ricerca-trascrizioni/index.md)).

# Pattern di ricerca client-side

`src/pages/ddl/[page].astro` è il riferimento per ricerca full-text lato
client su dataset piccoli: dati serializzati inline in un
`<script type="application/json">`, filtro vanilla JS, sync
dell'URL (`?q=`) per link condivisibili, re-init su
`astro:page-load` (per compatibilità con ViewTransitions). Lo stesso
pattern è riusato dalla pagina di [ricerca nelle
trascrizioni](/wiki/ricerca-trascrizioni/architettura.md).

# Vedi anche

* [Panoramica architetturale](/wiki/architettura/panoramica.md)
* [Dataset](/wiki/architettura/dataset.md)
