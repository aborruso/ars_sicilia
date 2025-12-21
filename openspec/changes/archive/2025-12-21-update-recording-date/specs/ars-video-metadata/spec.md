## ADDED Requirements
### Requirement: YouTube recordingDate da anagrafica
Il sistema SHALL impostare recordingDate su YouTube usando data_video e ora_video presenti in anagrafica.

#### Scenario: data e ora presenti
- **WHEN** data_video e ora_video sono presenti in anagrafica
- **THEN** recordingDate usa data_video e ora_video nella timezone configurata

#### Scenario: ora assente
- **WHEN** data_video e' presente ma ora_video e' assente
- **THEN** recordingDate usa data_video con ora 00:00 nella timezone configurata
