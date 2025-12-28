# Add RSS Feed Link to Header

## Summary
Add a visible RSS feed link in the site header to make the existing RSS feed discoverable to users. The feed is already generated at `/ars_sicilia/rss.xml` but not linked anywhere in the UI.

## Motivation
The site generates an RSS feed with the latest 20 videos, but users cannot discover it because there's no visible link in the interface. This reduces the feed's utility for users who want to subscribe to updates via RSS readers.

Adding a prominent RSS link in the header:
- Makes the feed discoverable
- Follows web standards (RSS links typically in header/footer)
- Enables users to subscribe to updates
- Improves accessibility for power users who prefer RSS

## Scope
- **Affected Component**: `src/components/layout/Header.astro`
- **Visual Element**: RSS icon link in navigation menu
- **Link Target**: `/ars_sicilia/rss.xml`
- **Icon**: RSS standard icon (📡 emoji or SVG)

## User-Facing Changes
- Header navigation will include an RSS icon link next to "Home" and "Sito ARS"
- Clicking the icon opens the RSS feed XML file
- Icon has tooltip/aria-label "Feed RSS" for accessibility
- Icon uses standard RSS orange color (#FF6600 or similar)
- Responsive: icon visible on all screen sizes

## Implementation Approach
1. Add RSS link as new `<li>` item in Header navigation `<ul>`
2. Use RSS emoji 📡 or inline SVG icon
3. Apply same styling as other nav links (hover effects, transitions)
4. Add aria-label for screen readers
5. Link points to `/ars_sicilia/rss.xml`
6. Optional: add orange color to make it distinctive

## Out of Scope
- Modifying RSS feed content or structure
- Adding RSS autodiscovery `<link>` tag in `<head>` (already exists via Astro sitemap)
- Adding RSS link to footer (only header for now)
- Creating custom RSS icon SVG (use emoji or simple SVG)

## Related Changes
None

## Timeline
Trivial change - single component edit, can be completed in minutes.

## Trade-offs
**Pros:**
- Improved discoverability of existing feature
- Standard web practice
- No new dependencies or complexity
- Minimal visual impact

**Cons:**
- Adds one more item to header nav (slight visual clutter)
- Users unfamiliar with RSS may not understand the icon
