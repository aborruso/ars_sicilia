## MODIFIED Requirements
### Requirement: Tracciamento fallimenti upload
La pipeline SHALL registrare nello storico anagrafica lo stato `failed` e il motivo dell'errore quando un upload non va a buon fine, e MUST selezionare i video mai tentati prima di quelli con stato `failed`.

#### Scenario: Upload fallito
- **WHEN** un upload fallisce con un errore gestito
- **THEN** la riga dell'anagrafica viene aggiornata con stato `failed` e `failure_reason`

#### Scenario: Retry successivo
- **WHEN** un video ha stato `failed`
- **THEN** il sistema lo considera eleggibile per retry in una run successiva

#### Scenario: Video nuovi prima dei falliti
- **WHEN** in anagrafica ci sono sia video mai tentati sia video con stato `failed`
- **THEN** il sistema seleziona il primo video mai tentato nell'ordine dell'anagrafica
- **AND** un video che fallisce sempre non impedisce l'upload delle sedute nuove

#### Scenario: Rotazione fra più falliti
- **WHEN** restano solo video con stato `failed`
- **THEN** il sistema seleziona quello con `last_check` più vecchio
