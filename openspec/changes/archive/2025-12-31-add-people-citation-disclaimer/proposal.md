# Change: Add AI disclaimer for cited people list

## Why
The “Persone citate” list is automatically extracted via AI and may contain inaccuracies in names or roles. A clear warning improves transparency and reduces misinterpretation.

## What Changes
- Add an admonition below the “Persone citate” heading warning that names and roles are AI-extracted and may contain errors.
- Match the visual style of the existing digest disclaimer for consistency.

## Impact
- Affected specs: `people-citation-disclaimer` (new capability)
- Affected code: `src/pages/sedute/[anno]/[mese]/[giorno]/[seduta]/[video].astro`
