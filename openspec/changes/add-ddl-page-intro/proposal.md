# Change: Add intro text to DDL listing page

## Why
Users need context about DDL list - that these are bills discussed in archived sedute. A clear introductory text improves understanding.

## What Changes
- Add introductory paragraph below "Disegni di Legge" heading on DDL page
- Text: "Qui la lista dei disegni di legge di cui si è discusso nelle sedute archiviate in questo sito"

## Impact
- Affected specs: `ddl-listing` (modify existing requirement)
- Affected code: `src/pages/ddl/[page].astro`
