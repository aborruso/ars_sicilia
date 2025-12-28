# digest-disclaimer Specification

## Purpose
TBD - created by archiving change add-digest-disclaimer. Update Purpose after archive.
## Requirements
### Requirement: AI Disclaimer Display

The digest section MUST display a disclaimer warning users that content is AI-generated.

#### Scenario: Disclaimer appears before digest text
**Given** a video page with a valid digest
**When** the page is rendered
**Then** a disclaimer box appears immediately after "Sintesi della seduta" heading
**And** the disclaimer appears before the digest content
**And** the disclaimer is visually distinct from digest content

#### Scenario: Disclaimer text content
**Given** a digest disclaimer is displayed
**When** the user reads the disclaimer
**Then** the text reads: "**ATTENZIONE:** Il testo di questo digest è stato generato automaticamente da un LLM, analizzando l'audio trascritto della seduta. Quindi potrebbe contenere errori e allucinazioni."
**And** the word "ATTENZIONE" is bold or emphasized
**And** the message clearly states AI generation and potential errors

#### Scenario: No disclaimer when digest missing
**Given** a video page without a digest (transcript unavailable)
**When** the page is rendered
**Then** no disclaimer box is displayed
**And** only the "Sintesi non disponibile" message appears

### Requirement: Visual Warning Style

The disclaimer MUST use warning/caution visual styling to draw attention.

#### Scenario: Warning color scheme
**Given** a disclaimer box is rendered
**When** the user views the page
**Then** the box has a yellow/amber background (bg-yellow-50 or bg-amber-50)
**And** the box has a matching border (border-yellow-200 or border-amber-200)
**And** text color provides sufficient contrast (text-yellow-900 or text-amber-900)

#### Scenario: Warning icon
**Given** a disclaimer box is rendered
**When** the user views the disclaimer
**Then** a warning icon appears (⚠️ emoji or SVG icon)
**And** the icon is positioned at the start of the text or in the left margin

#### Scenario: Visual consistency with existing warnings
**Given** the site has existing warning patterns (e.g., "Sintesi non disponibile" box)
**When** the disclaimer is rendered
**Then** it uses similar Tailwind classes (p-4, rounded-lg, border)
**And** styling is consistent with site design system

### Requirement: Accessibility

The disclaimer MUST be accessible to all users including screen readers.

#### Scenario: Semantic HTML structure
**Given** a disclaimer box is rendered
**When** examined with accessibility tools
**Then** the disclaimer uses semantic HTML (e.g., `<aside>`, `<div role="note">`)
**And** the disclaimer has appropriate ARIA attributes if needed

#### Scenario: Screen reader announcement
**Given** a user with a screen reader navigates to a video page
**When** the digest section is reached
**Then** the disclaimer is announced before the digest content
**And** the warning nature is conveyed (e.g., via role or icon alt text)

#### Scenario: Color contrast compliance
**Given** a disclaimer box with yellow/amber styling
**When** tested with WCAG contrast checker
**Then** text-to-background contrast ratio is at least 4.5:1 (AA standard)
**And** the disclaimer is readable for users with color vision deficiencies

### Requirement: Responsive Design

The disclaimer MUST display correctly on all screen sizes.

#### Scenario: Mobile display
**Given** a video page is viewed on mobile (< 640px width)
**When** the digest section is rendered
**Then** the disclaimer box is full-width and readable
**And** text wraps appropriately without overflow
**And** padding and font size are touch-friendly

#### Scenario: Desktop display
**Given** a video page is viewed on desktop (> 1024px width)
**When** the digest section is rendered
**Then** the disclaimer box width matches digest content width
**And** the box does not stretch unnecessarily wide

