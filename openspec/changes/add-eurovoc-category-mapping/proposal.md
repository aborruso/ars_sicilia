# Change: Add EuroVoc category normalization mapping

## Why
The project needs a controlled vocabulary reference for themes. Normalizing existing categories to EuroVoc enables consistent indexing and future enrichment.

## What Changes
- Add a script that maps categories from `src/data/processed/categories.json` to EuroVoc concepts using a local EuroVoc dump and the `llm` CLI.
- Persist mappings in `data/eurovoc_mapping.json`, skipping categories already mapped and flagging low-confidence matches as `review`.
- Keep the EuroVoc dump locally and reference it during mapping.

## Impact
- Affected specs: `category-normalization` (new capability)
- Affected code/docs: new mapping script under `scripts/`, new mapping data file under `data/`, local EuroVoc dump under a data directory (exact path TBD in implementation)
