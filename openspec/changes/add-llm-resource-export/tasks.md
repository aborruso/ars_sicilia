# Tasks: add-llm-resource-export

## Phase 1: Component Implementation

- [x] Create `src/components/sedute/LlmExportButton.astro` component
  - Props: `video`, `seduta` (data objects)
  - Export function to generate formatted text block
  - Copy-to-clipboard handler (with fallback modal)
  - Visual feedback (toast/button state)
  - **Validation**: render component locally, test copy action

- [x] Generate export text in format:
  ```
  Seduta n. {numero} | {data_formattata} | Ore {ora_video} ({durata} minuti)

  📚 Trascrizione automatica:
  {transcript_url}

  📄 Ordine del Giorno:
  {odg_url}

  💬 Digest AI:
  {digest_url}

  🎬 Video:
  https://www.youtube.com/watch?v={youtube_id}

  📊 Categorie: {comma_separated_categories}
  ```
  - **Validation**: verify URLs are absolute, no broken links

## Phase 2: Page Integration

- [x] Update `src/pages/sedute/[anno]/[mese]/[giorno]/[seduta]/[video].astro`
  - Import `LlmExportButton` component
  - Pass `video` and `seduta` props
  - Position button in layout (after categories, before digest)
  - **Validation**: build and check visual placement

- [x] Test with real data:
  - Load video page for seduta 220, youtube_id `Rq3Gd0J7OMQ`
  - Click button, verify copy works
  - Check export text contains all required fields
  - Test edge cases: no transcript, no digest, missing OdG

## Phase 3: Styling & UX Polish

- [x] Apply Tailwind CSS classes matching site design
  - Button: primary action style (Editorial Civic palette)
  - Modal/fallback: centered, readable font
  - Toast: brief, non-blocking

- [x] Add accessibility:
  - `aria-label` on button ("Esporta risorse per assistente AI")
  - Keyboard navigation (Tab, Enter)
  - Screen reader support for toast/modal

- [x] Test responsive layout:
  - Desktop (>1024px)
  - Tablet (768–1024px)
  - Mobile (<768px)
  - **Validation**: screenshot on each breakpoint

## Phase 4: Documentation & Testing

- [x] Update `LOG.md` with change summary
- [x] Update `openspec/changes/add-llm-resource-export/proposal.md` with final status
- [x] Build and deploy to `dist/`
  - Run `npm run build`
  - Verify no build errors
  - **Validation**: `dist/sedute/2025/12/16/seduta-220/video-1557/index.html` contains button

- [x] Manual smoke test on production-like build:
  - Visit `/sedute/2025/12/16/seduta-220/video-1557/`
  - Click "📋 Copia risorse per LLM"
  - Paste into text editor, verify all fields present

## Dependencies & Sequencing

1. Component creation (Phase 1) is independent; can run in parallel with Phase 3 styling prep
2. Page integration (Phase 2) depends on Phase 1 completion
3. Documentation (Phase 4) depends on Phases 1–3
4. No external API changes required; uses existing CSV/JSON data

## Definition of Done

- ✅ Component renders on video page
- ✅ Copy-to-clipboard works (or fallback modal appears)
- ✅ Export text includes all required fields (metadata, links, categories)
- ✅ Accessibility pass (keyboard, screen reader, ARIA)
- ✅ Responsive on desktop, tablet, mobile
- ✅ Build succeeds, no console errors
- ✅ LOG.md updated
- ✅ Proposal marked complete
