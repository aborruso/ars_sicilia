# Change: Pubblicare un RSS su gh-pages con gli ultimi video

## Why
Serve un feed pubblico semplice che renda consultabili gli ultimi video caricati. Il feed RSS facilita monitoraggio, aggregazione e integrazione con altri strumenti.

## What Changes
- Generare un feed RSS degli ultimi video caricati usando `data/anagrafica_video.csv`
- Usare `data_video` + `ora_video` come data del feed (pubDate)
- Pubblicare il feed su un branch orfano `gh-pages` come area pubblica (per ora solo RSS)
- Aggiungere un workflow GitHub Actions per rigenerare e pubblicare il feed

## Impact
- Affected specs: ars-public-feed (nuova capability)
- Affected code: scripts/ (generatore RSS), .github/workflows/ (publish), gh-pages branch
