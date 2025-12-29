# Change: Add date anchors to video sections

## Why
Gli utenti non possono condividere link diretti a una specifica data nella pagina seduta. URL senza ancore impediscono di linkare direttamente a gruppi di video di un giorno specifico.

## What Changes
- Aggiungere `id` attribute ai titoli h3 delle date in `VideosByDate.astro`
- Trasformare i titoli in link cliccabili che aggiornano URL con hash anchor
- Generare anchor ID dal formato data (es. `2025-12-16` → `#video-2025-12-16`)
- Mantenere accessibilità e styling esistente

## Impact
- Affected specs: seduta-page-navigation (nuovo)
- Affected code: `src/components/sedute/VideosByDate.astro:30-32`
