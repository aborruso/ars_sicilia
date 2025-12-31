# Capability: Markdown Pages

## Purpose
Enable static pages authored in Markdown to render with the shared site layout and metadata.

## Requirements

### Requirement: Markdown pages render with the default layout
Static pages authored as Markdown in `src/pages/` MUST render using the site PageLayout wrapper and typography styles.

#### Scenario: Markdown page is built
- **WHEN** a Markdown file is placed in `src/pages/`
- **THEN** the generated page includes the shared header and footer
- **AND** the content is rendered with typography styling

### Requirement: Markdown frontmatter drives page metadata
Markdown pages MUST use frontmatter `title` and `description` to populate HTML metadata when no explicit layout props are provided.

#### Scenario: Frontmatter provides title and description
- **WHEN** a Markdown page defines `title` and `description` in frontmatter
- **THEN** the HTML `<title>` includes the frontmatter title
- **AND** the meta description and OpenGraph fields use the frontmatter description
