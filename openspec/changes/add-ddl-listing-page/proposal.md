# Change: Add DDL listing page

## Why
Users want to browse all legislative bills (DDL) with their discussion history across multiple sedute. Currently, users can only discover DDL through individual sedute pages.

## What Changes
- Add new `/ddl` page with paginated list of all unique DDL
- Generate `ddls.json` during build with unique DDL and linked sedute (reverse mapping from existing sedute data)
- Create `DDLCard` component following `SedutaCard` styling pattern
- Add DDL navigation link in header/footer

## Impact
- Affected specs: `ddl-listing` (new capability)
- Affected code: `scripts/build-data.mjs`, `src/pages/ddl/[page].astro` (new), `src/components/ddl/DDLCard.astro` (new), `src/lib/data-loader.ts`, `src/components/layout/Header.astro`, `src/components/layout/Footer.astro`
