---
type: Panoramica
title: Panoramica architetturale
description: I tre livelli del sistema (backend, dati, frontend) e come il build data-driven li collega.
tags: [architettura, build]
timestamp: 2026-07-07T00:00:00Z
---

# Cos'è

Piattaforma civic-tech che rende consultabili le sedute dell'Assemblea
Regionale Siciliana (ARS): raccoglie i metadati delle sedute, carica i
video su YouTube, genera digest AI dalle trascrizioni, estrae i disegni
di legge dai PDF d'ordine del giorno, e pubblica un sito statico Astro su
GitHub Pages.

# I tre livelli

1. **Backend (Python, `scripts/`)** — pipeline di acquisizione e
   pubblicazione. Scrive dataset dentro `data/`.
2. **Livello dati (`data/`)** — dataset pubblici, il contratto tra
   backend e frontend. Vedi [dataset](dataset.md).
3. **Frontend (Astro, `src/`)** — sito statico generato a build time da
   `data/`.

# Il build è data-driven

`scripts/build-data.mjs` gira come hook `prebuild` di Astro. Legge i
dataset grezzi da `data/` ed emette JSON aggregato in
`src/data/processed/` (`sedute.json`, `videos.json`, `ddls.json`,
`categories.json`), che le pagine Astro consumano tramite
`src/lib/data-loader.ts`.

Conseguenza pratica: **modificare `data/` non basta** per vedere i
cambiamenti in locale — `prebuild` deve rigenerare il JSON processato
(`node scripts/build-data.mjs`, oppure `npm run dev` / `npm run build`
che lo eseguono automaticamente).

# Convenzioni di piattaforma

* Astro: output statico, `site: https://aborruso.github.io`,
  `base: /ars_sicilia` — ogni link interno deve rispettare il base path
  (spesso hardcoded come `/ars_sicilia/...` nelle pagine esistenti).
* Le pagine markdown in `src/pages/` ricevono un layout di default
  tramite il remark plugin `remark-default-layout.mjs`.
* `ars_sicilia_api/` è un client Python standalone per l'API di ricerca
  legislativa dell'ARS — indipendente dal build del sito, con proprio
  README e OpenSpec.

# Vedi anche

* [Pipeline di acquisizione](/wiki/pipeline/index.md)
* [Frontend](/wiki/frontend/index.md)
* [CI/CD](/wiki/ci-cd/index.md)
