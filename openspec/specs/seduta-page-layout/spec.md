# seduta-page-layout Specification

## Purpose
TBD - created by archiving change reduce-video-preview-size. Update Purpose after archive.
## Requirements
### Requirement: Video preview grid density
Il sistema SHALL mostrare le preview video in un grid responsive che massimizza il numero di video visibili per riga.

#### Scenario: Mobile viewport
- **WHEN** l'utente visualizza la pagina su dispositivo mobile
- **THEN** le preview sono disposte in 1 colonna

#### Scenario: Tablet viewport
- **WHEN** l'utente visualizza la pagina su tablet (breakpoint sm)
- **THEN** le preview sono disposte in 3 colonne

#### Scenario: Desktop viewport
- **WHEN** l'utente visualizza la pagina su desktop (breakpoint lg)
- **THEN** le preview sono disposte in 6 colonne

### Requirement: Video thumbnail aspect ratio
Il sistema SHALL mantenere aspect ratio 16:9 per tutte le preview video indipendentemente dalla dimensione.

#### Scenario: Ridimensionamento finestra
- **WHEN** la finestra viene ridimensionata
- **THEN** le thumbnail mantengono proporzioni 16:9 senza distorsioni

