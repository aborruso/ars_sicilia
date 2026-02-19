# Change: Filter production RSS items by digest availability

## Why
Il feed ufficiale in produzione (`https://aborruso.github.io/ars_sicilia/rss.xml`) oggi può includere video senza digest generato. Questo crea incoerenza con l'obiettivo editoriale di pubblicare nel feed solo contenuti già arricchiti dalla sintesi.

## What Changes
- Definire a livello di specifica che il feed RSS ufficiale (`/rss.xml`) includa solo video con digest disponibile e non vuoto.
- Chiarire che i video senza digest (digest mancante, nullo o testualmente vuoto) devono essere esclusi dal feed.
- Mantenere invariata la logica di ordinamento e limite sui soli item idonei.

## Impact
- Affected specs: `ars-public-feed` (modifica requisito di generazione feed)
- Affected code/docs (implementation phase): `src/pages/rss.xml.ts` e relativa documentazione operativa del feed ufficiale
