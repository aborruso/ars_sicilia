## ADDED Requirements
### Requirement: RSS pubblico degli ultimi video
Il sistema SHALL pubblicare un feed RSS con gli ultimi video caricati.

#### Scenario: Generazione feed
- **WHEN** è disponibile `data/anagrafica_video.csv`
- **THEN** il feed RSS viene generato includendo gli ultimi N video

#### Scenario: Data del feed
- **WHEN** un video ha `data_video` e `ora_video`
- **THEN** `pubDate` usa `data_video` + `ora_video` in timezone configurata

### Requirement: Pubblicazione su gh-pages
Il sistema SHALL pubblicare il feed RSS su un branch orfano `gh-pages` come area pubblica.

#### Scenario: Build e publish
- **WHEN** il workflow GitHub Actions è eseguito
- **THEN** il feed viene rigenerato e pubblicato su `gh-pages`
