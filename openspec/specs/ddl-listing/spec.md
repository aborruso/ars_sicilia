# ddl-listing Specification

## Purpose
TBD - created by archiving change add-ddl-listing-page. Update Purpose after archive.
## Requirements
### Requirement: DDL listing page
The site MUST provide a `/ddl` route that displays all unique legislative bills (DDL) with their discussion history, including an introductory text explaining context and proper header navigation with active states.

#### Scenario: Header navigation shows all main links
- **WHEN** a user views the header navigation
- **THEN** links are displayed in order: Home, Sedute, DDL, Info, Sito ARS, RSS
- **AND** "Sedute" links to `/ars_sicilia/sedute/1`
- **AND** "DDL" links to `/ars_sicilia/ddl/1`
- **AND** "Info" links to `/ars_sicilia/about`
- **AND** "Sito ARS" links to external ARS site
- **AND** "RSS" links to `/ars_sicilia/rss.xml`

#### Scenario: Active state highlights current page
- **WHEN** a user navigates to a sedute page
- **THEN** "Sedute" link is highlighted with navy background and white text
- **WHEN** a user navigates to a DDL page
- **THEN** "DDL" link is highlighted with navy background and white text
- **WHEN** a user is on the homepage
- **THEN** "Home" link is highlighted with navy background and white text

#### Scenario: DDL page loads with intro
- **WHEN** a user navigates to `/ddl` or `/ddl/1`
- **THEN** a paginated list of DDL cards is displayed
- **AND** an introductory paragraph appears below "Disegni di Legge" heading
- **AND** text reads: "Qui la lista dei disegni di legge di cui si è discusso nelle <a href="/ars_sicilia/sedute/1" class="text-navy-800 hover:text-amber-600 underline underline-offset-2">sedute</a> archiviate in questo sito"

#### Scenario: DDL card links to sedute
- **WHEN** a user clicks on a DDL card
- **THEN** DDL displays a list of linked sedute
- **AND** each sedute links to its corresponding sedute page

#### Scenario: DDL data aggregation at build time
- **WHEN** the build process runs
- **THEN** `ddls.json` is generated with unique DDL grouped by (numero, legislatura)
- **AND** each DDL includes an array of linked sedute (numero, data, slug, yearMonthDay)
- **AND** DDL are sorted by numero descending

