## Implementation
- [x] 1.1 Extend `build-data.mjs` to generate `ddls.json` with unique DDL grouped by (numero, legislatura) and linked sedute
- [x] 1.2 Add `loadDDLs()` function to `src/lib/data-loader.ts`
- [x] 1.3 Create `/ddl/[page].astro` page with pagination following sedute pattern
- [x] 1.4 Create `DDLCard.astro` component with editorial civic styling matching `SedutaCard`
- [x] 1.5 Add "DDL" navigation link in header after "Sedute"
- [x] 1.6 Add DDL link in footer "Links" section
- [x] 1.7 Verify pagination works correctly with ITEMS_PER_PAGE=10
- [x] 1.8 Test that DDL list displays correctly and links to sedute pages
