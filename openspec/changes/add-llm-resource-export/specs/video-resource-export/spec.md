# Spec: video-resource-export

LLM resource export UI for video pages—format and expose transcript, agenda, and metadata links as copy-to-clipboard text block.

## ADDED Requirements

### Requirement: video-page-export-button

The system SHALL display a clickable button on each video detail page (`/sedute/[anno]/[mese]/[giorno]/[seduta]/[video]/`) labeled "📋 Copia risorse per LLM" that exports video metadata, transcript, and agenda links for LLM consumption.

#### Scenario: user clicks export button on seduta 220 video

User navigates to video page for seduta 220, 11:37, 2025-12-16 (youtube_id: `Rq3Gd0J7OMQ`). Button is visible below video metadata and categories. User clicks button. Export text is copied to clipboard or displayed in fallback modal. Export text reads:

```
Seduta n. 220 | 16 Dicembre 2025 | Ore 11:37 (13 minuti)

📚 Trascrizione automatica:
https://raw.githubusercontent.com/aborruso/ars_sicilia/main/data/trascrizioni/Rq3Gd0J7OMQ.it.txt

📄 Ordine del Giorno:
https://w3.ars.sicilia.it/DocumentiEsterni/ODG_PDF/ODG_18_2025_12_16_220_A.pdf

💬 Digest AI:
https://raw.githubusercontent.com/aborruso/ars_sicilia/main/data/digest/Rq3Gd0J7OMQ.json

🎬 Video YouTube:
https://www.youtube.com/watch?v=Rq3Gd0J7OMQ

📊 Categorie: [list from digest]
```

User can immediately paste into LLM chat or text editor.

### Requirement: export-text-formatting

Export text MUST be human-readable, scannable by LLM, and include: metadata header (seduta number, date, time, duration), labeled section headers with emoji, direct absolute URLs (no shortened links), and category list from digest (if available).

#### Scenario: video with all resources available

Seduta 220, video at 11:37 has transcript, agenda PDF, and AI digest. Export includes all sections with live URLs pointing to raw GitHub and ARS CDN resources. Formatting uses emoji prefixes for visual hierarchy.

### Requirement: copy-to-clipboard-feedback

Button click SHALL trigger copy action with immediate visual feedback: toast notification ("✓ Risorse copiate negli appunti") confirms success. Fallback modal MUST display export text for manual selection if Clipboard API unavailable.

#### Scenario: clipboard success on modern browser

User clicks button. Toast appears briefly (2–3 sec) confirming copy. User opens LLM chat, Ctrl+V pastes full export text.

#### Scenario: clipboard fallback on older browser

Clipboard API unavailable. Modal pops up with export text pre-selected and highlighted. Message reads "Testo copiato. Premi Ctrl+C per copiare se il bottone non ha funzionato." User manually copies.

### Requirement: handle-missing-resources

Export SHALL gracefully handle missing transcript, agenda, or digest by omitting that section or noting "⚠️ Non disponibile" inline. Button MUST remain visible and functional even if some resources are absent.

#### Scenario: video without transcript

Video recorded but `no_transcript=true` in CSV (transcript generation failed). Export button still renders. Export text omits trascrizione section or displays "📚 Trascrizione: ⚠️ Non disponibile". OdG, digest, and video links are present.

#### Scenario: video without agenda

Edge case: OdG URL missing from CSV. Export skips "📄 Ordine del Giorno" section entirely. All other sections present.

## MODIFIED Requirements

### Requirement: seduta-page-layout

The video page component (`src/pages/sedute/[anno]/[mese]/[giorno]/[seduta]/[video].astro`) SHALL be extended to render LlmExportButton component. Button placement MUST be immediately below categories badges section and above digest content. Button MUST use site's Tailwind CSS and "Editorial Civic" design palette.

#### Scenario: export button renders in video page layout

Video page renders: header, video embed, categories, **[NEW] LLM Export Button**, digest content, people cited, back link. Button is visually prominent (primary color) and accessible via keyboard Tab + Enter.

## REMOVED Requirements

(None)

## Cross-References

- Spec: `seduta-page-layout` — page structure hosting the button
- Spec: `ars-video-metadata` — CSV fields (`odg_url`, `youtube_id`, `no_transcript`) populating export text
- Spec: `video-digest-generation` — digest JSON availability for export link
- Related change: `add-llms-txt-standard` — Livello 1; this change implements Livello 2 per-video export

## Rationale

LLMs consume video metadata, transcripts, and agendas to generate analyses (summaries, bill tracking, speaker identification). Single-click export reduces friction: users no longer manually copy/paste 3–4 URLs. Emoji formatting ensures human readability while structured layout suits LLM parsing.
