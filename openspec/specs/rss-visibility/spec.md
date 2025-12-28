# rss-visibility Specification

## Purpose
TBD - created by archiving change add-rss-link. Update Purpose after archive.
## Requirements
### Requirement: RSS Link in Header Navigation

The site header MUST include a visible link to the RSS feed.

#### Scenario: RSS link appears in header
**Given** a user visits any page on the site
**When** the page header renders
**Then** an RSS icon link is visible in the header navigation
**And** the link is positioned in the navigation menu alongside "Home" and "Sito ARS"
**And** the link points to `/ars_sicilia/rss.xml`

#### Scenario: RSS link opens feed
**Given** a user sees the RSS icon in the header
**When** the user clicks the RSS icon
**Then** the browser navigates to `/ars_sicilia/rss.xml`
**And** the RSS feed XML is displayed or offered for subscription

#### Scenario: RSS icon is recognizable
**Given** the RSS link in the header
**When** a user views the icon
**Then** the icon uses a standard RSS symbol (📡 emoji or RSS SVG)
**And** the icon is visually distinct (e.g., orange color)
**Or** the icon matches the site's color scheme for consistency

### Requirement: Accessibility for RSS Link

The RSS link MUST be accessible to all users including screen readers.

#### Scenario: Screen reader announces RSS link
**Given** a user with a screen reader navigates the header
**When** the RSS link is focused
**Then** the screen reader announces "Feed RSS" or similar descriptive text
**And** the link has an appropriate aria-label attribute

#### Scenario: RSS link has tooltip on hover
**Given** a sighted user hovers over the RSS icon
**When** the cursor is over the icon
**Then** a browser tooltip displays "Feed RSS" or similar text
**Or** the aria-label provides context for assistive technologies

### Requirement: Responsive Design for RSS Link

The RSS link MUST display correctly on all screen sizes.

#### Scenario: RSS link visible on mobile
**Given** a user visits the site on a mobile device (< 640px)
**When** the header navigation renders
**Then** the RSS icon is visible and tappable
**And** the icon size is appropriate for touch targets (min 44x44px)

#### Scenario: RSS link visible on desktop
**Given** a user visits the site on desktop (> 1024px)
**When** the header navigation renders
**Then** the RSS icon is visible alongside other nav items
**And** hover effects work smoothly

### Requirement: Consistent Visual Style

The RSS link MUST follow the existing header navigation design patterns.

#### Scenario: RSS link matches nav style
**Given** the RSS link in the header navigation
**When** the user views the header
**Then** the RSS link uses the same font, spacing, and alignment as other nav items
**And** the link has similar hover/focus effects (color change, underline)
**And** the link maintains visual consistency with the site's design system

#### Scenario: RSS icon has appropriate color
**Given** the RSS icon in the header
**When** rendered
**Then** the icon uses orange (#FF6600 or similar RSS standard color)
**Or** the icon uses the site's primary link color for consistency
**And** the color provides sufficient contrast with the background (WCAG AA)

