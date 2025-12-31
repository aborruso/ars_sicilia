# Tasks: Add Markdown Support

## Setup and Configuration

- [x] **Install MDX integration**
  - Run `npm install @astrojs/mdx`
  - Verify package appears in `package.json` dependencies
  - Run `npm install` to ensure lock file is updated

- [x] **Configure Astro for MDX**
  - Edit `astro.config.mjs`
  - Import `@astrojs/mdx` at top: `import mdx from '@astrojs/mdx';`
  - Add to integrations array: `mdx()`
  - Save and verify config syntax is valid

- [x] **Configure default layout for Markdown**
  - Update MDX integration config to include layout option
  - Set layout path: `mdx({ layout: './src/layouts/PageLayout.astro' })`
  - Ensure path is correct relative to project root

- [x] **Verify Tailwind Typography is active**
  - Check `tailwind.config.mjs` includes `@tailwindcss/typography` plugin
  - Confirm `package.json` has `@tailwindcss/typography` dependency
  - If missing, install with `npm install -D @tailwindcss/typography`
  - Add to Tailwind config if not present

## Content Migration (Proof of Concept)

- [x] **Create about.md from about.astro**
  - Create new file `src/pages/about.md`
  - Add frontmatter with title and description:
    ```yaml
    ---
    title: "Informazioni sul progetto"
    description: "Informazioni sul progetto ARS Sicilia: archivio video e documenti delle sedute dell'Assemblea Regionale Siciliana"
    ---
    ```
  - Copy HTML content from `about.astro` (lines 10-83)
  - Convert HTML to Markdown (headings, paragraphs, lists, links)
  - Remove Astro layout wrapper (handled by config)

- [ ] **Test about.md rendering**
  - Run `npm run dev`
  - Navigate to `/ars_sicilia/about/`
  - Verify content renders correctly
  - Check that PageLayout header/footer appear
  - Verify Tailwind Typography styles are applied

- [x] **Keep or remove about.astro**
  - If `about.md` works correctly, delete `about.astro`
  - Or rename to `about.astro.backup` temporarily
  - Ensure only one "about" page exists to avoid conflicts

## Documentation

- [x] **Create Markdown authoring guide**
  - Create `docs/markdown-guide.md`
  - Document frontmatter fields (title, description)
  - Provide Markdown syntax examples
  - Explain file placement (`src/pages/` → routes)
  - Include example template for new pages

- [x] **Update project documentation**
  - Update `README.md` to mention Markdown support
  - Add section "Creating New Pages" with Markdown instructions
  - Link to `docs/markdown-guide.md`

## Validation

- [x] **Build test**
  - Run `npm run build`
  - Verify build succeeds without errors
  - Check `dist/about/index.html` exists and contains rendered Markdown
  - Verify no duplicate pages or routing conflicts

- [x] **Content rendering verification**
  - Open built site with `npm run preview`
  - Navigate to `/ars_sicilia/about/`
  - Verify all Markdown elements render:
    - Headings (h1, h2)
    - Paragraphs
    - Lists (ul, ol)
    - Links (internal, external with target="_blank")
    - Bold/italic text

- [x] **Layout integration test**
  - Verify about page includes site header (with logo/nav)
  - Verify about page includes site footer
  - Check breadcrumbs or navigation work correctly
  - Verify page matches visual style of .astro pages

- [x] **SEO metadata test**
  - View page source in browser
  - Confirm `<title>` contains frontmatter title
  - Confirm `<meta name="description">` exists
  - Verify OpenGraph tags (og:title, og:description)
  - Check sitemap.xml includes `/about/` entry

- [ ] **Responsive design test**
  - Test page on mobile viewport (< 640px)
  - Test on tablet viewport (768px-1024px)
  - Verify Tailwind Typography prose styles work at all sizes
  - Check links and navigation are touch-friendly

- [ ] **Hot reload test**
  - Run `npm run dev`
  - Open about.md in browser
  - Edit Markdown content and save
  - Verify browser auto-reloads within 2 seconds
  - Confirm changes appear correctly

## Optional Enhancements (Post-Implementation)

- [ ] **Create additional Markdown pages** (if needed)
  - Privacy policy (`src/pages/privacy.md`)
  - Methodology (`src/pages/metodologia.md`)
  - FAQ (`src/pages/faq.md`)

- [ ] **Add custom Markdown components** (if MDX features needed later)
  - Create components for callouts, alerts, or special blocks
  - Document MDX component usage
  - Examples: `<Note>`, `<Warning>`, `<CodeBlock>`

## Dependencies

- **Blocked by**: None
- **Parallel work**: Can be done independently of other changes

## Notes

- Astro has native Markdown support; MDX integration adds MDX features (components in Markdown) but also improves standard Markdown handling
- Default layout via config is cleaner than requiring `layout:` in every frontmatter
- Tailwind Typography (`@tailwindcss/typography`) is already a dependency (line 18, package.json), just needs to be enabled if not active
- Consider keeping `about.astro` as backup until Markdown version is fully validated in production
