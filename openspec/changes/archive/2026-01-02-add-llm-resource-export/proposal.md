# Change: add-llm-resource-export

## Why

Each video page represents a rich knowledge artifact—transcript, agenda, digest—that LLMs can consume to generate analyses. Currently, users must manually gather these resources from different URLs. A single-click "Export for LLM" button reduces friction and accelerates LLM-assisted research workflows, transforming the video page from a passive display into an active resource preparation tool.

## What Changes

- Add "Export for LLM" button on each video page (`[video].astro`)
- Generate a pre-formatted text block containing:
  - Video metadata (seduta number, date, time, duration, categories)
  - Link to transcript `.txt` file (raw GitHub raw URL)
  - Link to agenda PDF (OdG from `odg_url` CSV field)
  - Optional: link to digest JSON
- Copy-to-clipboard functionality (or display in a modal for manual copy)
- Text formatted for direct paste into LLM prompt

## Impact

- **Affected specs**: `seduta-page-layout` (UI change), `ars-video-metadata` (data exposure)
- **Affected code**: `src/pages/sedute/[anno]/[mese]/[giorno]/[seduta]/[video].astro`, new component `src/components/sedute/LlmExportButton.astro`
- **No breaking changes**: new button appended to existing layout, optional click action

## Related Changes

- `add-llms-txt-standard` (Livello 1 llms.txt)—this change implements Livello 2 endpoint discovery at video page granularity
