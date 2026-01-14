## Context
We need a durable, incremental mapping from project categories to EuroVoc concepts, backed by a local EuroVoc dump and generated via the `llm` CLI.

## Goals / Non-Goals
- Goals: deterministic, incremental mapping; local EuroVoc reference; no mutation of source categories; flag low-confidence results for review.
- Non-Goals: automatic enrichment of sedute/videos/digests; publishing the dump to frontend.

## Decisions
- Store mappings in `data/eurovoc_mapping.json` keyed by category name with EuroVoc URI, labels, confidence, status, and timestamps.
- Use a local EuroVoc dump (SKOS/JSON or CSV) as the sole reference for candidate concepts.
- The script uses `llm` with model `gemini-2.5-flash` and must not re-map categories already present in the mapping file.

## Risks / Trade-offs
- LLM may choose suboptimal concepts; mitigated by `review` status for low-confidence matches.
- Keeping the dump local requires periodic refresh; document the dump version in the mapping file metadata or script output.

## Migration Plan
- None. New mapping file is created if absent.

## Open Questions
- Final dump format and location (to be decided during implementation).
