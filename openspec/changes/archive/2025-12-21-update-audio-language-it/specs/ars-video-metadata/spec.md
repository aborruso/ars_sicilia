## ADDED Requirements
### Requirement: Lingua audio nei metadati YouTube
Il sistema SHALL impostare `defaultAudioLanguage` su `it-IT` per i video pubblicati su YouTube.

#### Scenario: Upload standard
- **WHEN** un video viene caricato su YouTube
- **THEN** `defaultAudioLanguage` è impostato a `it-IT`

#### Scenario: Configurazione lingua audio
- **WHEN** una configurazione di lingua audio è presente
- **THEN** il sistema usa il valore configurato, con default `it-IT`
