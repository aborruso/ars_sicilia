## Context
Il repository espone due generatori RSS: `scripts/generate_rss.py` (feed.xml su branch `gh-pages`) e il feed del sito Astro (`src/pages/rss.xml.ts`) pubblicato in produzione su `https://aborruso.github.io/ars_sicilia/rss.xml`.

La richiesta riguarda esclusivamente il feed ufficiale di produzione.

## Goals / Non-Goals
- Goals: garantire che ogni item del feed ufficiale rappresenti un video con digest già generato e non vuoto.
- Non-Goals: cambiare il comportamento di `scripts/generate_rss.py` o del workflow `publish_rss.yml`.

## Decisions
- Applicare il filtro nel punto di generazione del feed ufficiale (`src/pages/rss.xml.ts`).
- Definire "digest disponibile" come `video.digest?.digest` presente e non composto solo da whitespace.
- Conservare comportamento attuale per ordinamento e limite, applicandolo al sottoinsieme filtrato.

## Risks / Trade-offs
- Il feed può contenere meno di 20 item quando i digest non sono ancora stati generati.
- Riduce la tempestività dell'inclusione nel feed, ma aumenta consistenza editoriale e qualità percepita.

## Migration Plan
- Nessuna migrazione dati richiesta.
