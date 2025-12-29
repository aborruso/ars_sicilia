# ARS Sicilia API Documentation

This API provides access to Sicilian Regional Assembly (ARS) legislative database for "Disegni di Legge" (Bills/Law Drafts).

## Starting Point

**Search Start Page**: https://dati.ars.sicilia.it/home/cerca/221.jsp

This is the starting point for all search operations. From this page you can:
- Select legislature, year, bill number
- Set various filters (signatory, commission, topic, iteration)
- Execute searches to get results

## Base URL
```
https://dati.ars.sicilia.it
```

## Authentication
No explicit authentication required. Session management is handled via JSESSIONID cookie.

---

## API Endpoints

### 1. Search Endpoint

**URL**: `POST /home/cerca/221.jsp`

**Description**: Main search form that initiates a new search query. **Note**: This endpoint does NOT perform an HTTP redirect. Instead, it returns HTML that includes JavaScript to open results in a new window. API clients must manually call `/icaro/default.jsp` with the query parameters after the POST.

**Request Body (application/x-www-form-urlencoded)**:

| Parameter | Type | Required | Description |
|-----------|------|-----------|-------------|
| `legisl` | string | Yes | Legislature number (10, 11, 12, 13, 14, 15, 16, 17, 18) |
| `anno` | string | No | Year filter (e.g., "2024", "2025") |
| `legge` | string | No | Bill number |
| `iter` | string | No | Iteration filter (NESSUNO, ENTRAMBI, ATTUALE, STORICO) |
| `iterComm` | string | No | Commission iteration filter |
| `iterAltro` | string | No | Other iteration filter |
| `iterComm2` | string | No | Commission iteration 2 |
| `iterAltro2` | string | No | Other iteration 2 |
| `tipo` | string | No | Type filter (E for Exact) |
| `terms` | string | No | Search terms |
| `searchAction` | string | Yes | Must be "execute" |
| `queryText` | string | Yes | Query in custom search syntax (URL encoded) |

**Query Syntax**:
- Field search: `(FIELDNAME.value)` - e.g., `(18.LEGISL)` for all bills in legislature 18
- Operators: `AND`, `OR`, `NOT`, `ADJ`, `NEAR`, `SAME`, `WITH`, etc.
- Wildcards: `$` for prefix match, `%` for suffix match
- Range: `125/321` for numeric range
- Field qualifier: `.fieldname` to limit search to specific field

**Available Fields** (from help page):
- `LEGISL` (N2) - Legislature number
- `NUMDDL` (N5) - Bill number
- `DATPRE` (N6) - Presentation date (YYMMDD)
- `TITOLO` (V) - Title
- `SOMMAR` (V) - Summary
- `FIRMAT` (V) - Signatories
- `ITERST` (V) - Historical iteration
- `ITERAT` (V) - Current iteration
- `RIFSTE` (V) - Stenographic references
- `RELACO` (V) - Commission relators
- `RELAUL` (V) - Assembly relator
- `SETTOR` (V) - Sector
- `NOTE` (V) - Notes
- `TESTO` (V) - Full text

**Example Request**:
```bash
curl -X POST 'https://dati.ars.sicilia.it/home/cerca/221.jsp' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Cookie: JSESSIONID=your_session_id' \
  -d 'legisl=18&anno=2024&searchAction=execute&queryText=(18.LEGISL)'
```

**Response**: HTML page. The page contains JavaScript that opens `/icaro/default.jsp` in a new window/tab, but does NOT perform an HTTP redirect.

**API Client Workflow**:
1. POST to `/home/cerca/221.jsp` with search parameters
2. Store the `queryText` value used in the POST
3. Manually GET `/icaro/default.jsp?icaDB=221&icaQuery=<queryText>&_=<timestamp>`
4. Parse the results page to get total results and query ID

---

### 2. Results Page

**URL**: `GET /icaro/default.jsp`

**Description**: Main results display page. Returns HTML with results list.

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|-----------|-------------|
| `icaDB` | string | No | Database ID (default: 221 for Disegni di Legge) |
| `icaQuery` | string | No | Query in custom syntax (URL encoded) |
| `_` | number | No | Cache buster (timestamp) |

**Example Request**:
```bash
curl 'https://dati.ars.sicilia.it/icaro/default.jsp?icaDB=221&icaQuery=%2818.LEGISL%29&_=1234567890'
```

**Response**: HTML page with:
- Total results count
- Pagination controls
- Results list (calls `shortList.jsp` via AJAX)

---

### 3. Results List (AJAX)

**URL**: `GET /icaro/shortList.jsp`

**Description**: Returns paginated list of results as HTML fragments. Called via AJAX.

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|-----------|-------------|
| `setPage` | number | No | Page number (1-based, default: 1) |
| `_` | number | No | Cache buster (timestamp) |

**Response Structure**:
```html
<div class="pagination">
  <span class="pagina_di">Pagina <b>1</b> di 108</span>
  <a href="javascript:setPage(1)" class="active">1</a>
  <a href="javascript:setPage(2)" class="">2</a>
  ...
</div>

<ul id="shortListTable" class="tabella">
  <li class="intestazione">
    <!-- Headers: Legisl., Numero, Data, Titolo -->
  </li>
  <li href="javascript:showDoc(1)">
    <div class="intesta intesta_12"><p>18</p></div>  <!-- Legislature -->
    <div class="intesta intesta_12"><p>1052</p></div>  <!-- Number -->
    <div class="intesta intesta_16"><p>1.12.25</p></div>  <!-- Date -->
    <div class="intesta intesta_50">
      <h3><a href="javascript:showDoc(1)">Title text</a></h3>
    </div>
  </li>
  <!-- 10 results per page -->
</ul>
```

**Example Request**:
```bash
curl 'https://dati.ars.sicilia.it/icaro/shortList.jsp?setPage=2&_=1234567890' \
  -H 'X-Requested-With: XMLHttpRequest' \
  -H 'Cookie: JSESSIONID=your_session_id'
```

**Pagination**: 
- 10 results per page
- Total pages shown in `pagina_di` span
- Navigation: call `setPage(N)` to change pages

---

### 4. Document Detail

**URL**: `GET /icaro/default.jsp`

**Description**: Displays document detail view.

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|-----------|-------------|
| `icaAction` | string | Yes | Must be "showDoc" |
| `id` | number | Yes | Document ID (1-indexed position in results) |
| `_` | number | No | Cache buster (timestamp) |

**Example Request**:
```bash
curl 'https://dati.ars.sicilia.it/icaro/default.jsp?icaAction=showDoc&id=1&_=1234567890' \
  -H 'Cookie: JSESSIONID=your_session_id'
```

**Response**: HTML page that loads document content via `doc221-1.jsp` AJAX call.

---

### 5. Document Content (AJAX)

**URL**: `GET /icaro/doc221-1.jsp`

**Description**: Returns full document content as HTML fragment.

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|-----------|-------------|
| `icaQueryId` | number | Yes | Query ID (from search) |
| `icaDocId` | number | Yes | Document ID (1-indexed) |
| `_` | number | No | Cache buster (timestamp) |

**Response Structure**:
```html
<div class="colonna_2">
  <div class="blocchi_info">
    <div class="title"><h3>Titolo</h3></div>
    <div class="testo_gestionale">Title text</div>
  </div>
  
  <div class="blocchi_info">
    <div class="title"><h3>Iter</h3></div>
    <div class="testo_gestionale">
      <p><strong>Attuale</strong><br/>Current status</p>
      <p><strong>Storico</strong><br/>Historical status</p>
    </div>
  </div>
  
  <div class="tab active">
    <div class="testo_gestionale">
      <div class="overflow"><pre>
        FULL DOCUMENT TEXT
        Bill content, articles, etc.
      </pre></div>
    </div>
  </div>
</div>
```

**Example Request**:
```bash
curl 'https://dati.ars.sicilia.it/icaro/doc221-1.jsp?icaQueryId=1&icaDocId=1&_=1234567890' \
  -H 'X-Requested-With: XMLHttpRequest' \
  -H 'Cookie: JSESSIONID=your_session_id'
```

---

### 6. Extract DDL Attachment and Amendment Links

**Method**: `get_ddl_links(url)`

**Description**: Extracts attachment and amendment PDF links from a DDL page URL. Resolves the `icaQueryId` from the page footer and parses AJAX content to find "Vedi Atti Allegati" (attachments) and "Vedi Fascicolo" (amendments) links.

**Arguments**:

| Parameter | Type | Required | Description |
|-----------|------|-----------|-------------|
| `url` | string | Yes | Full DDL URL (e.g., `https://dati.ars.sicilia.it/icaro/default.jsp?icaDB=221&icaQuery=(18.LEGISL+E+1029.NUMDDL)`) |

**Returns**:

Dictionary with:
- `allegati`: Array of attachment PDF URLs
- `emendamenti`: Array of amendment PDF URLs
- `query_id`: Extracted query ID

**Example Usage**:

```python
from ars_sicilia_api.ars_api_client import ARSClient

client = ARSClient()
url = "https://dati.ars.sicilia.it/icaro/default.jsp?icaDB=221&icaQuery=(18.LEGISL+E+1029.NUMDDL)"
result = client.get_ddl_links(url)

print(f"Allegati: {result['allegati']}")
print(f"Emendamenti: {result['emendamenti']}")
```

**Response Example**:

```python
{
    "allegati": ["https://w3.ars.sicilia.it/ica_221/A18251106_01029.pdf"],
    "emendamenti": ["https://w3.ars.sicilia.it/ica_221/E18251106_01029.pdf"],
    "query_id": "1"
}
```

**Notes**:
- The method automatically normalizes scheme-less URLs (e.g., `//w3.ars.sicilia.it/...`) to HTTPS
- If `icaQueryId` cannot be extracted, returns empty arrays with an error message
- Parses link text to identify "Vedi Atti Allegati" and "Vedi Fascicolo"
- Other metadata (CED ID, argomenti) require JavaScript execution and are not available through this method

---

### 7. Show Query (Return to Results)

**URL**: `GET /icaro/default.jsp`

**Description**: Returns to results list view.

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|-----------|-------------|
| `icaAction` | string | Yes | Must be "showQuery" |
| `id` | number | Yes | Query ID |
| `doc` | string | Yes | "TRUE" or "FALSE" |
| `_` | number | No | Cache buster |

**Example Request**:
```bash
curl 'https://dati.ars.sicilia.it/icaro/default.jsp?icaAction=showQuery&id=1&doc=FALSE&_=1234567890' \
  -H 'Cookie: JSESSIONID=your_session_id'
```

---

### 8. Close Query

**URL**: `GET /icaro/default.jsp`

**Description**: Closes/deletes a search query.

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|-----------|-------------|
| `icaAction` | string | Yes | Must be "closeQuery" |
| `id` | number | Yes | Query ID to close |
| `_` | number | No | Cache buster |

**Example Request**:
```bash
curl 'https://dati.ars.sicilia.it/icaro/default.jsp?icaAction=closeQuery&id=1&_=1234567890' \
  -H 'Cookie: JSESSIONID=your_session_id'
```

---

### 9. Session Keep-alive

**URL**: `GET /icaro/alive.jsp`

**Description**: Maintains session alive. Called periodically.

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|-----------|-------------|
| `cnt` | number | Yes | Counter/increment value |
| `_` | number | Yes | Timestamp |

**Example Request**:
```bash
curl 'https://dati.ars.sicilia.it/icaro/alive.jsp?cnt=5&_=1234567890' \
  -H 'Cookie: JSESSIONID=your_session_id'
```

---

## Query Syntax Examples

### Basic Queries

```
(18.LEGISL)                                      # All bills from legislature 18
(18.LEGISL AND 1052.NUMDDL)                   # Specific bill
((18.LEGISL) AND 2024.ANNO)                # All bills from 2024, leg 18
(peschicoltura.TITOLO)                          # Search in title field
(Venezia.FIRMAT)                               # Bills signed by Venezia
(1050/1055.NUMDDL)                            # Range of bill numbers
```

### Advanced Operators

```
(A AND B)                                       # Both terms must be present
(A OR B)                                        # Either term can be present
(A NOT B)                                       # A must be present, B must not
(A ADJ B)                                       # A must be adjacent to B
(A NEAR2 B)                                     # A within 2 terms of B
(A SAME.TITOLO)                                  # Both in title field
(A WITH)                                        # In same sentence
(A LINE)                                         # In same line
```

### Field Qualifiers

```
termo.TITOLO                                    # Search only in title
termo.SOMMAR                                    # Search only in summary
termo.TESTO                                      # Search only in full text
termo.FIRMAT                                     # Search only in signatories
termo:ITERAT                                      # Search everywhere except current iteration
```

### Wildcards

```
legis$                                            # Terms starting with "legis"
zione%2                                           # Terms ending in "zione" (max 2 chars)
```

---

## Response Data Format

All API responses are **HTML**, not JSON. Parse using HTML parser.

### Bill Record Fields

| Field | Description | Example |
|-------|-------------|---------|
| Legislature | Legislature number | 18 |
| Number | Bill number | 1052 |
| Date | Presentation date | 1.12.25 (DD.MM.YY) |
| Title | Bill title | Interventi per la valorizzazione... |
| Summary | Brief description | (from TITOLO field) |
| Current Status | Current iteration status | Assegnato per esame Commissione TERZA |
| Historical Status | Previous iteration steps | Multiple status entries |
| Full Text | Complete bill text | Articles, sections, etc. |
| Signatories | First and other signatories | List of names |
| Committee | Assigning commission | 3. Terza - Attività produttive |
| Arguments | Subject matter tags | • Pesca, • Cultura, etc. |
| Attachments | Linked documents | Nessuno (None) |

---

## Pagination Mechanism

1. Initial search returns results page with `shortListTable` loaded via AJAX
2. Each page shows 10 results
3. Pagination links: `1`, `2`, `3`, ... `Next`
4. JavaScript function `setPage(N)` loads new page:
   ```javascript
   $("#mainContent").load("/icaro/shortList.jsp?setPage=" + page + "&_=" + Date.now());
   ```
5. Navigation between pages is done via AJAX, no page reload

---

## Common Use Cases

### Get All Bills from Legislature
```bash
# Step 1: Execute search
curl -X POST 'https://dati.ars.sicilia.it/home/cerca/221.jsp' \
  -d 'legisl=18&searchAction=execute&queryText=(18.LEGISL)' \
  -c cookies.txt

# Step 2: Get results list (page 1)
curl 'https://dati.ars.sicilia.it/icaro/shortList.jsp?_='$(date +%s)' \
  -b cookies.txt
```

### Search by Year
```bash
curl -X POST 'https://dati.ars.sicilia.it/home/cerca/221.jsp' \
  -d 'legisl=18&anno=2024&searchAction=execute&queryText=((18.LEGISL)%20AND%202024.ANNO)' \
  -c cookies.txt
```

### Search by Signatory
```bash
curl -X POST 'https://dati.ars.sicilia.it/home/cerca/221.jsp' \
  -d 'legisl=18&searchAction=execute&queryText=(Venezia.FIRMAT%20AND%2018.LEGISL)' \
  -c cookies.txt
```

### Get Specific Bill
```bash
# First get the bill position, then load content
curl -X POST 'https://dati.ars.sicilia.it/home/cerca/221.jsp' \
  -d 'legisl=18&legge=1052&searchAction=execute&queryText=((18.LEGISL)%20AND%201052.NUMDDL))' \
  -c cookies.txt
```

### Get Full Bill Text
```bash
# After finding the bill (document #1 in results)
curl 'https://dati.ars.sicilia.it/icaro/doc221-1.jsp?icaQueryId=1&icaDocId=1&_='$(date +%s)' \
  -H 'X-Requested-With: XMLHttpRequest' \
  -b cookies.txt
```

---

## Rate Limiting & Best Practices

1. **Session Management**: Maintain JSESSIONID cookie across requests
2. **Cache Busting**: Always include `_` parameter with timestamp
3. **User-Agent**: Use appropriate user-agent
4. **Rate Limiting**: Add delays between page requests (1-2 seconds)
5. **Pagination**: Process one page at a time, respect pagination structure
6. **Error Handling**: Check for "Nessun risultato" (No results) in response

---

## Notes

- The API returns HTML, not JSON - requires HTML parsing
- Session IDs (icaQueryId) are generated per search
- Document IDs are 1-indexed positions within results
- Date format in results is DD.MM.YY
- Legislature numbers: 10-18 (X to XVIII)
- Total results may be up to ~2000+ per legislature
- Results show latest bills first (descending by number)
