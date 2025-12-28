# Tasks: Add Video Navigation

## Implementation

- [ ] **Calculate previous/next video indices**
  - In `[video].astro`, find the current video's index within `seduta.videos` array
  - Calculate `prevVideoIndex = currentIndex - 1` and `nextVideoIndex = currentIndex + 1`
  - Validate indices to determine if prev/next exist

- [ ] **Generate navigation URLs**
  - Build prev/next video URLs using seduta path + video slug
  - Format: `/ars_sicilia/sedute/{year}/{month}/{day}/{seduta-slug}/{video-slug}`
  - Set to `null` when prev/next don't exist

- [ ] **Create navigation markup**
  - Add navigation `<nav>` element after header, before video embed
  - Render previous button (←) with conditional disabled state
  - Render next button (→) with conditional disabled state
  - Apply Tailwind classes matching Pagination component style

- [ ] **Add accessibility attributes**
  - Add `aria-label="Video precedente"` to prev button
  - Add `aria-label="Video successivo"` to next button
  - Add `aria-disabled="true"` to disabled buttons
  - Wrap in `<nav aria-label="Navigazione video">`

## Validation

- [ ] **Visual verification**
  - Build site locally with `npm run build`
  - Navigate to a video page in the middle of a seduta
  - Verify both buttons are enabled and styled correctly
  - Click prev/next buttons and verify correct navigation

- [ ] **Edge case testing - First video**
  - Navigate to the first video (chronologically) of any seduta
  - Verify previous button is disabled (gray, no-cursor)
  - Verify next button is enabled
  - Verify clicking disabled button does nothing

- [ ] **Edge case testing - Last video**
  - Navigate to the last video (chronologically) of any seduta
  - Verify next button is disabled (gray, no-cursor)
  - Verify previous button is enabled
  - Verify clicking disabled button does nothing

- [ ] **Edge case testing - Single video seduta**
  - Find or create a seduta with only one video
  - Verify both buttons are disabled
  - Verify page renders without errors

- [ ] **Accessibility audit**
  - Run browser accessibility checker (Lighthouse, axe DevTools)
  - Verify navigation has proper ARIA labels
  - Test with keyboard navigation (tab through buttons)
  - Verify screen reader announces button states correctly

## Dependencies

None - uses existing data structures and styling patterns.

## Notes

- Navigation order follows chronological sorting already present in `seduta.videos` (sorted by `dataVideo` + `oraVideo` in `build-data.mjs:130-133`)
- No new TypeScript types needed - reuses existing `Seduta` and video types
- No new API calls or data fetching required
- Consider extracting to separate `VideoNavigation.astro` component if markup becomes complex (optional, can refactor later)
