## ADDED Requirements
### Requirement: Descrizione verbosa con escape orari
Il sistema SHALL generare la descrizione con una formulazione più verbosa e con orari neutralizzati da zero-width space per evitare che YouTube crei timestamp.

#### Scenario: Descrizione base
- **WHEN** viene generata la descrizione per un video
- **THEN** le prime righe descrivono la seduta con il testo verboso e includono data e ora di svolgimento

#### Scenario: Escape orari
- **WHEN** un orario e' presente nel testo della descrizione
- **THEN** l'orario contiene uno zero-width space tra ore e minuti (es. 11:\u200B37)
