# ars-video-metadata Specification

## Purpose
Definire i metadati YouTube (titolo, recording date/time) per i video ARS.
## Requirements
### Requirement: YouTube title format
The system SHALL publish videos with titles that include the seduta number, seduta date, and recording date/time.

#### Scenario: Recording date differs from seduta date
- **WHEN** a video recording date differs from the seduta date
- **THEN** the title shows the seduta date and separately shows the recording date/time

#### Scenario: Recording date equals seduta date
- **WHEN** the recording date equals the seduta date
- **THEN** the title still shows the seduta date and recording date/time in the standard format

### Requirement: Descrizione verbosa con escape orari
Il sistema SHALL generare la descrizione con una formulazione più verbosa e con orari neutralizzati da zero-width space per evitare che YouTube crei timestamp.

#### Scenario: Descrizione base
- **WHEN** viene generata la descrizione per un video
- **THEN** le prime righe descrivono la seduta con il testo verboso e includono data e ora di svolgimento

#### Scenario: Escape orari
- **WHEN** un orario e' presente nel testo della descrizione
- **THEN** l'orario contiene uno zero-width space tra ore e minuti (es. 11:\u200B37)

### Requirement: Licenza YouTube Creative Commons
Il sistema SHALL impostare la licenza dei video caricati su YouTube come Creative Commons Attribution 4.0.

#### Scenario: Upload standard
- **WHEN** un video viene caricato su YouTube
- **THEN** la licenza del video e' impostata a Creative Commons

#### Scenario: Configurazione licenza
- **WHEN** una configurazione di licenza e' presente
- **THEN** il sistema usa il valore configurato, con default Creative Commons

### Requirement: YouTube recordingDate da anagrafica
Il sistema SHALL impostare recordingDate su YouTube usando data_video e ora_video presenti in anagrafica.

#### Scenario: data e ora presenti
- **WHEN** data_video e ora_video sono presenti in anagrafica
- **THEN** recordingDate usa data_video e ora_video nella timezone configurata

#### Scenario: ora assente
- **WHEN** data_video e' presente ma ora_video e' assente
- **THEN** recordingDate usa data_video con ora 00:00 nella timezone configurata

### Requirement: Lingua audio nei metadati YouTube
Il sistema SHALL impostare `defaultAudioLanguage` su `it-IT` per i video pubblicati su YouTube.

#### Scenario: Upload standard
- **WHEN** un video viene caricato su YouTube
- **THEN** `defaultAudioLanguage` è impostato a `it-IT`

#### Scenario: Configurazione lingua audio
- **WHEN** una configurazione di lingua audio è presente
- **THEN** il sistema usa il valore configurato, con default `it-IT`

