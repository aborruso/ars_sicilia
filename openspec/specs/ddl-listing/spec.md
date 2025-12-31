# ddl-listing Specification

## Purpose
TBD - created by archiving change add-ddl-listing-page. Update Purpose after archive.
## Requirements
### Requirement: DDL listing page
The site MUST provide a `/ddl` route that displays all unique legislative bills (DDL) with their discussion history, including an introductory text explaining the context.

#### Scenario: DDL list page loads with intro
- **WHEN** a user navigates to `/ddl` or `/ddl/1`
- **THEN** a paginated list of DDL cards is displayed
- **AND** an introductory paragraph appears below the "Disegni di Legge" heading
- **AND** the text reads: "Qui la lista dei disegni di legge di cui si è discusso nelle sedute archiviate in questo sito"
- **AND** the word "sedute" is a link to the sedute listing page

#### Scenario: DDL card links to sedute
- **WHEN** a user clicks on a DDL card
- **THEN** DDL displays a list of linked sedute
- **AND** each sedute links to its corresponding sedute page

#### Scenario: DDL data aggregation at build time
- **WHEN** the build process runs
- **THEN** `ddls.json` is generated with unique DDL grouped by (numero, legislatura)
- **AND** each DDL includes an array of linked sedute (numero, data, slug, yearMonthDay)
- **AND** DDL are sorted by numero descending

#### Scenario: DDL navigation
- **WHEN** a user views the header navigation
- **THEN** a "DDL" link is present after "Sedute"
- **WHEN** a user views the footer
- **THEN** a "DDL" link is present in the Links section

