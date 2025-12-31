# Change: Add Markdown Support for Static Pages

## Why
Currently, all pages are `.astro` components with hardcoded HTML, requiring technical knowledge to edit content. Adding Markdown support enables easier content authoring by non-technical contributors and faster creation of documentation pages.

## What Changes
- Install and configure `@astrojs/mdx` integration
- Configure `astro.config.mjs` to apply PageLayout to all `.md` files in `src/pages/`
- Set frontmatter defaults (title, description) for Markdown pages
- Enable Tailwind Typography plugin for Markdown content styling
- Migrate `about.astro` to `about.md` as proof-of-concept

## Impact
- Affected specs: None (new capability, no existing spec to modify)
- Affected code:
  - `astro.config.mjs` (add MDX integration and layout config)
  - `package.json` (add @astrojs/mdx dependency)
  - `src/pages/about.astro` → `src/pages/about.md` (migration example)
- User-facing: Content editors can create new pages by adding `.md` files to `src/pages/`
- Build: No breaking changes, URLs remain unchanged (e.g., `about.md` → `/ars_sicilia/about/`)

## Timeline
Small change - can be completed in single session. Minimal risk as Astro has native Markdown support.

## Trade-offs
**Pros:**
- Simpler content authoring
- Non-technical contributors can edit pages
- Markdown is portable (can migrate to other systems)
- Separation of content (Markdown) from presentation (Layout)

**Cons:**
- Adds dependency (`@astrojs/mdx`, ~400KB)
- Markdown is less flexible than Astro components for complex layouts
- Need to document frontmatter conventions for content creators

## Out of Scope
- Content Collections (explicit grouping/validation of content)
- Multiple layouts per directory
- Blog functionality (pagination, tags, categories for Markdown posts)
- MDX components (using Astro components inside Markdown) - enabled but not required initially
- Syntax highlighting themes (use default)

## Related Changes
None
