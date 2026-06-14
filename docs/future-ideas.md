## Idee future per il sito

Annotazioni di prodotto emerse navigando il sito. Da prioritizzare/valutare prima di implementare.

### Ricerca DDL per numero e descrizione (quick win)

- Ricerca di base sui disegni di legge per `numero_disegno` e `titolo_disegno`.
- Fattibile **client-side** su `src/data/processed/ddls.json` (dati statici, piccoli): input + filtro JS, nessun server.
- Costo basso, alto valore. Indipendente da Pagefind.
- **Priorità: ALTA.**

### Ricerca full-text (digest, trascrizioni, categorie, persone)

- Già analizzata in [search-engine-analysis.md](search-engine-analysis.md): **Pagefind** raccomandato (indice ~1-5%, build-time, client-side, filtri nativi).
- Più impegnativa della ricerca DDL base, ma copre tutto il contenuto.
- **Priorità: MEDIA.**

### Griglia / calendario sedute in home o in /sedute

- Vista calendario (mensile) o griglia delle sedute per data, come alternativa alla lista paginata.
- Le sedute hanno già `dataSeduta`/`yearMonthDay`: serve un componente Astro + logica date.
- Buon valore UX, costo medio.
- **Priorità: MEDIA.**

### Routing con legislatura nel path

Proposta: introdurre la legislatura come segmento dell'URL.

- `/ddl/1/` → `/18/ddl/1/`
- `/sedute/1/` → `/18/sedute/1/`
- `/sedute/2026/06/10/seduta-255/` → `/18/sedute/seduta-255/` (senza la data)

Valutazione:

- **Pro**: semanticamente corretto, future-proof per nuove legislature, URL più corti per le sedute.
- **Contro / costi**:
  - Oggi esiste **una sola legislatura (XVIII)**: il prefisso `/18/` non porta beneficio immediato.
  - Cambia **tutti** i link interni (rispettare `base: /ars_sicilia`) e `build-data.mjs`.
  - **Rompe gli URL esistenti** → servono redirect 301 per non perdere SEO/link condivisi.
  - Togliere la data dall'URL seduta riduce leggibilità/SEO dell'URL (trade-off).
- **Raccomandazione**: decidere ora la struttura target, ma implementare con redirect dagli URL vecchi — idealmente in concomitanza con l'arrivo di una seconda legislatura. **Priorità: BASSA** (debito di design da non accumulare, non urgente).

### Aggregazione DDL per numero: titoli multipli persi

- `build-data.mjs` aggrega i record per `numero_disegno` tenendo **un solo titolo**.
- Ma lo stesso numero può avere titoli diversi (es. 1030 = "Legge di stabilità" nelle sedute 219/220, ma "stralci" sanità/personale/lavoro nelle 237/238): gli altri titoli vanno persi e non sono ricercabili.
- Valutare: conservare tutti i titoli/varianti per numero, o aggregare per `(numero, titolo)`.
