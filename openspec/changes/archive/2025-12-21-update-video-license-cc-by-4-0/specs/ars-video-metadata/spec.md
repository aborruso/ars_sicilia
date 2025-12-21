## ADDED Requirements
### Requirement: Licenza YouTube Creative Commons
Il sistema SHALL impostare la licenza dei video caricati su YouTube come Creative Commons Attribution 4.0.

#### Scenario: Upload standard
- **WHEN** un video viene caricato su YouTube
- **THEN** la licenza del video e' impostata a Creative Commons

#### Scenario: Configurazione licenza
- **WHEN** una configurazione di licenza e' presente
- **THEN** il sistema usa il valore configurato, con default Creative Commons
