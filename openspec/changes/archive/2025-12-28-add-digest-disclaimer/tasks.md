# Tasks: Add Digest Disclaimer

## Implementation

- [x] **Add disclaimer box to DigestContent.astro**
  - Open `src/components/sedute/DigestContent.astro`
  - Locate the section rendering digest content (after h2 heading, before prose div)
  - Insert disclaimer `<div>` between heading and content
  - Use existing warning pattern: `bg-yellow-50 border border-yellow-200 rounded-lg p-4`

- [x] **Add disclaimer content**
  - Insert warning icon: `⚠️` emoji or Unicode
  - Add text: "**ATTENZIONE:** Il testo di questo digest è stato generato automaticamente da un LLM, analizzando l'audio trascritto della seduta. Quindi potrebbe contenere errori e allucinazioni."
  - Use `<strong>` or `<b>` tag for "ATTENZIONE" (or Markdown if using marked)
  - Ensure text is in Italian as specified

- [x] **Style disclaimer text**
  - Apply text color: `text-yellow-800` or `text-yellow-900` for contrast
  - Use appropriate text size: `text-sm` for compact appearance
  - Add margin bottom: `mb-4` or `mb-6` to separate from digest content

- [x] **Add accessibility attributes**
  - Wrap disclaimer in semantic element (`<aside>` or `<div role="note">`)
  - Consider adding `aria-label="Avviso: contenuto generato automaticamente"` if appropriate
  - Ensure icon has appropriate semantic meaning (emoji is self-describing)

## Validation

- [x] **Visual verification**
  - Run `npm run dev`
  - Navigate to any video page with a digest (e.g., seduta 220 video)
  - Verify disclaimer appears between heading and digest text
  - Check color scheme matches warning style (yellow/amber)
  - Verify icon appears correctly

- [x] **Content verification**
  - Read disclaimer text carefully
  - Ensure text matches specification exactly
  - Verify "ATTENZIONE" is bold/emphasized
  - Check for typos or formatting issues

- [x] **Edge case: No digest**
  - Navigate to a video without digest (shows "Sintesi non disponibile")
  - Verify disclaimer does NOT appear
  - Confirm only the "non disponibile" message shows

- [x] **Responsive design test**
  - Test on mobile viewport (375px, 414px width)
  - Verify disclaimer box is readable and doesn't overflow
  - Test on tablet (768px width)
  - Test on desktop (1280px, 1920px width)
  - Ensure text wraps properly at all sizes

- [x] **Accessibility audit**
  - Run Lighthouse accessibility check
  - Verify color contrast meets WCAG AA (4.5:1 minimum)
  - Test with screen reader (VoiceOver, NVDA, or browser extension)
  - Verify disclaimer is announced before digest content
  - Check keyboard navigation works (can tab through)

- [x] **Build test**
  - Run `npm run build`
  - Verify build succeeds without errors
  - Check generated HTML in `dist/` contains disclaimer markup
  - Run `npm run preview` and test built site

- [x] **Cross-browser test** (optional but recommended)
  - Test in Chrome/Edge
  - Test in Firefox
  - Test in Safari (if available)
  - Verify emoji renders consistently across browsers

## Dependencies

None - standalone component change.

## Notes

- Current component already has warning pattern for "Sintesi non disponibile" (lines 22-26) - reuse similar Tailwind classes for consistency
- Consider future enhancement: link to methodology page explaining digest generation process
- If disclaimer text needs to change frequently, consider extracting to a constant or config file (not needed for now)
- Emoji ⚠️ is widely supported; if rendering issues occur, can replace with SVG icon
