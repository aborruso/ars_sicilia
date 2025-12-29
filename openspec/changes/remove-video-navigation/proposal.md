# Change: Remove video page navigation arrows

## Why
The previous/next navigation arrows on single video pages are no longer desired and should be removed to simplify the viewing experience.

## What Changes
- Remove the prev/next navigation UI from the single video page.
- Remove the `video-page-navigation` capability from specs.

## Impact
- Affected specs: `specs/video-page-navigation/spec.md`
- Affected code: single video page UI (Astro page/component rendering the arrows)
