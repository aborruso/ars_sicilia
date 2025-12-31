## ADDED Requirements

### Requirement: DDL listing page
The site MUST provide a `/ddl` route that displays all unique legislative bills (DDL) with their discussion history.

#### Scenario: DDL list page loads
- **WHEN** a user navigates to `/ddl` or `/ddl/1`
- **THEN** a paginated list of DDL cards is displayed
- **AND** each DDL shows title, number, legislature, and count of related sedute

#### Scenario: DDL card links to sedute
- **WHEN** a user clicks on a DDL card
- **THEN** the DDL displays a list of linked sedute
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
