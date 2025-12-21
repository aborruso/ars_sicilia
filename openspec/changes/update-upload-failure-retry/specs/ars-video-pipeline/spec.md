## ADDED Requirements
### Requirement: Tracciamento fallimenti upload
La pipeline SHALL registrare nello storico anagrafica lo stato `failed` e il motivo dell'errore quando un upload non va a buon fine.

#### Scenario: Upload fallito
- **WHEN** un upload fallisce con un errore gestito
- **THEN** la riga dell'anagrafica viene aggiornata con stato `failed` e `failure_reason`

#### Scenario: Retry successivo
- **WHEN** un video ha stato `failed`
- **THEN** il sistema lo considera eleggibile per retry in una run successiva
