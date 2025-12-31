## MODIFIED Requirements

### Requirement: DDL navigation
The site MUST provide navigation links to key sections including Home, Sedute, DDL, Info, external ARS site, and RSS feed.

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
