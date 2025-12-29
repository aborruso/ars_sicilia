# seduta-page-navigation Specification

## Purpose
TBD - created by archiving change add-date-anchors. Update Purpose after archive.
## Requirements
### Requirement: Date anchors for video groups
La pagina della seduta MUST esporre un'ancora URL per ogni gruppo di video aggregato per data.

#### Scenario: Anchors generated from the date
- **WHEN** una data contiene video nella seduta
- **THEN** il titolo della data MUST avere un attributo `id` derivato dalla data (es. `video-2025-12-16`)

### Requirement: Clickable date headings
I titoli delle date MUST essere cliccabili per aggiornare l'hash dell'URL alla relativa ancora.

#### Scenario: User clicks a date heading
- **WHEN** l'utente clicca sul titolo della data
- **THEN** l'URL MUST aggiornarsi con l'hash dell'ancora della data senza cambiare pagina

