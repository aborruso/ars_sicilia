# Add Video Navigation Buttons

## Summary
Add previous/next navigation buttons to the single video page, allowing users to navigate between videos of the same seduta without returning to the seduta overview page.

## Motivation
Currently, when viewing a single video page, users must go back to the seduta page to watch the next or previous video. This creates friction in the user experience, especially when watching multiple videos from the same session sequentially.

## Scope
- **Affected Component**: Video single page (`src/pages/sedute/[anno]/[mese]/[giorno]/[seduta]/[video].astro`)
- **New Component**: `VideoNavigation.astro` component (optional, for better organization)
- **Data**: Uses existing `seduta.videos` array data

## User-Facing Changes
- Users will see navigation buttons (← →) positioned above the video embed
- Buttons are disabled (grayed out) when at first/last video
- Clicking navigation buttons takes users to prev/next video in the same seduta
- Navigation follows chronological order (by `dataVideo` + `oraVideo`)

## Implementation Approach
1. Calculate prev/next video from `seduta.videos` array based on current video
2. Generate URLs for prev/next video pages
3. Render navigation buttons following existing Pagination component style
4. Position buttons above the video embed, after the header

## Out of Scope
- Cross-seduta navigation (jumping to videos from different sessions)
- Keyboard shortcuts for navigation
- Video autoplay after navigation

## Related Changes
None

## Timeline
Small, self-contained change - can be completed in single implementation session.
