## MODIFIED Requirements
### Requirement: RSS pubblico degli ultimi video
Il sistema SHALL pubblicare un feed RSS con gli ultimi video caricati nel feed ufficiale di produzione (`/rss.xml`), includendo solo video con digest disponibile.

#### Scenario: Generazione feed con filtro digest
- **WHEN** è disponibile la sorgente dati dei video usata da `src/pages/rss.xml.ts`
- **THEN** il feed RSS ufficiale viene generato includendo gli ultimi N video con digest valido
- **AND** i video senza digest non sono inclusi nel feed

#### Scenario: Video senza digest escluso
- **WHEN** un video ha digest mancante, nullo o composto solo da whitespace
- **THEN** il video MUST essere escluso dagli item RSS

#### Scenario: Ordinamento e limite sul sottoinsieme idoneo
- **WHEN** ci sono più video con digest valido rispetto al limite configurato
- **THEN** il feed include al massimo N item ordinati per `data_video` e `ora_video` decrescenti
