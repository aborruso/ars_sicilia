## Implementation
- [ ] 1.1 Choose a local storage path and format for the EuroVoc dump and document the source/version.
- [ ] 1.2 Add a mapping script that reads `src/data/processed/categories.json`, loads the EuroVoc dump, and proposes mappings via `llm` using `gemini-2.5-flash`.
- [ ] 1.3 Implement incremental updates to `data/eurovoc_mapping.json` (skip existing mappings, add new ones with confidence + review status).
- [ ] 1.4 Add minimal usage documentation and example command for the script.
- [ ] 1.5 Validate mapping output format with a sample run and confirm no writes to categories source files.
