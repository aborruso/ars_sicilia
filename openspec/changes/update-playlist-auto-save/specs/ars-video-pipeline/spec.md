## ADDED Requirements
### Requirement: Persistenza playlist annuali
La pipeline SHALL salvare in modo persistente l'ID della playlist annuale quando viene creata automaticamente.

#### Scenario: Creazione playlist e salvataggio
- **WHEN** viene creata una playlist per un nuovo anno
- **THEN** l'ID playlist viene salvato in un file di stato o in `config/config.yaml` per riuso futuro

#### Scenario: File non scrivibile
- **WHEN** il file di stato o `config/config.yaml` non sono scrivibili
- **THEN** il sistema logga un avviso e continua l'upload senza bloccare
