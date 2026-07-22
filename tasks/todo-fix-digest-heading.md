# Fix digest con `##` che compromettono la leggibilità

## Contesto
Segnalato il video seduta 265 ore 15:44 (`hQ2AD_ax0Mw`): il digest ha `##` sparsi che lo rendono poco leggibile. Il digest è renderizzato come markdown da `DigestContent.astro` via `marked`.

## Diagnosi
Su ~85 digest, **solo 4** sono rotti; gli altri usano `## Titolo` / `### Sottotitolo` a inizio riga (corretto e leggibile). I 4 rotti hanno modalità diverse:

- `hQ2AD_ax0Mw` (segnalato) — blob su **riga singola**, `## tema ##` come enfasi inline. Struttura persa. Trascrizione 3838 righe (la più lunga).
- `BvrMdfTH9Do` — blob riga singola, `## Titolo` incollato al corpo. Struttura persa.
- `iD9fvoidp7Y` — contiene `\n` **letterali** invece di veri a-capo. Struttura recuperabile.
- `kYX47otETyE` — `**## Titolo**` (bold + heading mescolati), 36 righe. Struttura recuperabile.

Causa: comportamento intermittente del modello (`gemini-2.5-flash`). 3 dei 4 file precedono il pull di oggi → problema ricorrente, non risolvibile solo col prompt.

## Piano proposto

### Fase 1 — Riparazione dati
- `iD9fvoidp7Y`, `kYX47otETyE`: trasformazione deterministica (`\n` letterali → a-capo; strip `##`/`**##` inline).
- `hQ2AD_ax0Mw`, `BvrMdfTH9Do`: **rigenerazione** dal transcript (struttura persa; strip lascerebbe un muro di testo).

### Fase 2 — Guard a build-time (difesa in profondità)
- Piccolo normalizzatore in `build-data.mjs` accanto al drop dei digest <=10 char: converte `\n` letterali, rimuove `##`/`**` usati come enfasi inline (solo quando preceduti da testo sulla stessa riga — heading a inizio riga intatti).

### Fase 3 — Hardening prompt (prevenzione)
- In `config/digest.yaml`: istruire il modello a usare `##`/`###` solo a inizio riga, mai inline; separare le sezioni con riga vuota; mai `\n` letterali.

### Fase 4 — (Opzionale, da decidere) Modello
- Free tier ora raccomanda `gemini-3-flash-preview` (verificato via exa). `gemini-2.5-flash` e ancora free-tier e funzionante. `-preview` in pipeline notturna = rischio. Non retro-fixa i file esistenti.

## Domande aperte
- Scope: solo `hQ2AD` o tutti e 4 + guard build-time?
- Aggiornare il modello ora o lasciare 2.5-flash?
