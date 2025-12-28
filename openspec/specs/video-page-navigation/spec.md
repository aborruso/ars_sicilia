# video-page-navigation Specification

## Purpose
Enable sequential navigation between videos of the same seduta on the video detail page, improving user experience for users watching multiple videos from a single session. Navigation buttons provide direct prev/next links without requiring users to return to the seduta overview page.
## Requirements
### Requirement: Previous/Next Video Navigation

The single video page MUST display navigation buttons to move between videos of the same seduta.

#### Scenario: User navigates to next video in sequence
**Given** a user is viewing video at 11:37 of seduta 220
**And** there is a video at 15:57 in the same seduta
**When** the user clicks the next button (→)
**Then** the page navigates to the video at 15:57
**And** the URL updates to the new video's path

#### Scenario: User navigates to previous video in sequence
**Given** a user is viewing video at 15:57 of seduta 220
**And** there is a video at 11:37 in the same seduta
**When** the user clicks the previous button (←)
**Then** the page navigates to the video at 11:37
**And** the URL updates to the new video's path

#### Scenario: First video disables previous button
**Given** a user is viewing the first video of a seduta (chronologically)
**When** the page renders
**Then** the previous button (←) is displayed but disabled
**And** the button shows visual disabled state (gray, cursor-not-allowed)
**And** clicking the disabled button does nothing

#### Scenario: Last video disables next button
**Given** a user is viewing the last video of a seduta (chronologically)
**When** the page renders
**Then** the next button (→) is displayed but disabled
**And** the button shows visual disabled state (gray, cursor-not-allowed)
**And** clicking the disabled button does nothing

### Requirement: Navigation Button Positioning

Navigation buttons MUST be positioned above the video embed for immediate visibility.

#### Scenario: Navigation buttons appear in header area
**Given** a user loads any video page
**When** the page renders
**Then** navigation buttons appear after the page header (title + date)
**And** navigation buttons appear before the video embed
**And** buttons are horizontally centered or aligned left

### Requirement: Consistent Visual Style

Navigation buttons MUST follow the existing Pagination component design pattern.

#### Scenario: Enabled button styling
**Given** a navigation button is enabled (not first/last video)
**When** the page renders
**Then** the button displays with border, rounded corners, and hover effect
**And** the button uses the same style as Pagination (border-gray-300, rounded-lg, hover:bg-gray-50)

#### Scenario: Disabled button styling
**Given** a navigation button is disabled (first/last video)
**When** the page renders
**Then** the button displays with muted colors (text-gray-400, border-gray-200)
**And** the button shows cursor-not-allowed
**And** the button matches the disabled state of Pagination component

### Requirement: Accessibility Support

Navigation buttons MUST include proper accessibility attributes.

#### Scenario: Screen reader support
**Given** a user with a screen reader loads a video page
**When** the navigation buttons are rendered
**Then** each button has an appropriate aria-label
**And** previous button has aria-label="Video precedente"
**And** next button has aria-label="Video successivo"
**And** disabled buttons have aria-disabled="true"

