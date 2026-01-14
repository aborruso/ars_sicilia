## ADDED Requirements
### Requirement: EuroVoc category mapping
The system SHALL provide a script that maps categories from `src/data/processed/categories.json` to EuroVoc concepts using a local EuroVoc dump and the `llm` CLI with model `gemini-2.5-flash`.

#### Scenario: Incremental mapping without overwrites
- **WHEN** the script runs and `data/eurovoc_mapping.json` already contains a mapping for a category
- **THEN** the script MUST NOT create a new mapping for that category
- **AND** the existing mapping remains unchanged

#### Scenario: Low-confidence match flagged for review
- **WHEN** the script assigns a match below the configured confidence threshold
- **THEN** the mapping MUST be stored with `status: "review"`
- **AND** the mapping MUST include the proposed EuroVoc URI and labels

#### Scenario: No source mutation
- **WHEN** the script completes successfully
- **THEN** `src/data/processed/categories.json` MUST remain unchanged
