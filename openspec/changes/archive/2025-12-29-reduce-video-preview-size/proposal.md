# Change: Reduce video preview size

## Why
Le preview video nella pagina seduta occupano troppo spazio, limitando il numero di video visibili contemporaneamente e richiedendo eccessivo scrolling per visualizzare tutti i contenuti.

## What Changes
- Modificare il grid layout in `VideosByDate.astro` per aumentare il numero di colonne
- Passare da 1/2/3 colonne (mobile/tablet/desktop) a 1/3/6 colonne
- Mantenere aspect ratio 16:9 e responsive design

## Impact
- Affected specs: seduta-page-layout (nuovo)
- Affected code: `src/components/sedute/VideosByDate.astro:34`
