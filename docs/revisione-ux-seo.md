Revisione UX / deep linking / SEO

Analisi d'insieme del sito e piano per un modello di interazione coerente.
Data: 2026-06-14.

## Quadro attuale

Route:
- `/` home (hero + stats + sedute recenti + categorie)
- `/sedute/[page]` lista paginata + calendario + categorie
- `/sedute/[anno]/[mese]/[giorno]/[seduta]` singola seduta (con prev/next)
- `/sedute/[anno]/[mese]/[giorno]/[seduta]/[video]` singolo video
- `/sedute/categoria/[slug]` lista per categoria
- `/ddl/[page]` lista DDL + ricerca `?q=`
- `rss.xml`, `404`

SEO già presente: `canonical`, OpenGraph, Twitter card, `sitemap` integrato, `robots.txt`.

## Problema centrale: tre paradigmi incoerenti

| Strumento | Comportamento | URL | SEO |
|---|---|---|---|
| Categorie | apre una **pagina** | `/sedute/categoria/sanita` (path) | indicizzabile |
| Calendario | filtro **live** | `?giorno=` / `?mese=` (query) | non indicizzabile |
| Ricerca DDL | filtro **live** | `?q=` (query) | non indicizzabile (corretto) |

Conseguenze:
- L'utente non capisce perché un clic a volte ricarica (categoria) e a volte no (giorno).
- I conteggi categoria non si aggiornano cambiando mese (due filtri live sulla stessa pagina che non si parlano).
- Gli stati "data" non sono indicizzabili né davvero condivisibili come path puliti.

## Principio guida (deep linking + SEO)

Il sito nasce per condividere link puntuali ("guarda qui") e per essere trovato su Google. Quindi:

- **Stati enumerabili** (categoria, anno, mese, giorno) → **pagine dedicate con path pulito**, generate a build-time: ottime da condividere e indicizzabili.
- **Ricerca libera** (testo) → unico filtro **live** `?q=` (non pre-generabile; per la ricerca va bene).

Comportamento unico e prevedibile: **clic → vai a una pagina; digitazione → ricerca live**.

## Modello target

- Calendario = **navigatore** (non più filtro live): cambio mese → `/sedute/[anno]/[mese]`; clic giorno → singola seduta se unica, altrimenti pagina giorno.
- Nuove pagine-lista server-rendered: `/sedute/[anno]`, `/sedute/[anno]/[mese]` (poche: ~7 mesi). In sitemap automaticamente.
- Categorie restano pagine; i loro conteggi sono **totali globali** (corretti, non contestuali al mese).
- Ricerca DDL `?q=` invariata.
- I filtri live del calendario (`?giorno`/`?mese`) vengono sostituiti dai path → si rimuove quella logica.

Questo risolve: coerenza UX, conteggi categoria, deep link forti (path), SEO (ogni periodo/categoria è una pagina in sitemap).

## Piano a fasi

- **Fase 1 — Pagine periodo**: `/sedute/[anno]` e `/sedute/[anno]/[mese]` (lista sedute del periodo, ordinata desc, breadcrumb). Riuso `SedutaCard`.
- **Fase 2 — Calendario navigante**: i giorni e le frecce linkano alle pagine periodo/seduta; rimossa la logica filtro-live + `?giorno`/`?mese`.
- **Fase 3 — Coerenza visiva**: uniformare i punti d'ingresso (categoria, periodo) come navigazione; verificare che la pagina `/sedute/categoria` e le pagine periodo condividano layout/intestazioni.
- **Fase 4 — SEO+**: JSON-LD `ItemList`/`BreadcrumbList`/`VideoObject` dove manca; verifica sitemap nuove pagine; titoli/description per pagina periodo.
- **Fase 5 (rinviata)** — legislatura nel path (`/18/...`): solo all'arrivo della 2ª legislatura, con redirect 301.

## Non toccare (già corretto)

- Ricerca DDL `?q=` (deep link live giustificato).
- SEO di base (canonical/OG/sitemap/robots).
- Ordinamento sedute per data desc.
