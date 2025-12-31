# Change: Add Sedute link to header navigation

## Why
Users need direct access to sedute listing from the main navigation. Currently, sedute are only accessible through DDL pages or by knowing the URL.

## What Changes
- Add "Sedute" link to header navigation after "Home"
- Link points to `/ars_sicilia/sedute/1`
- Update active state logic to highlight "Sedute" when on sedute pages

## Impact
- Affected specs: `ddl-listing` (modify DDL navigation requirement)
- Affected code: `src/components/layout/Header.astro`
