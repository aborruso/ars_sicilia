# Research Notes - Valutazione ARS Sicilia

## Scopo
Valutazione progetto senza usare valutazioni pregresse.

## Metodo (ricerca strutturata)
- M1: Overview repo (README, PRD, openspec)
- M2: Stato operativo (LOG, workflow, scripts entrypoint)
- M3: Stack e dipendenze (package.json, requirements)
- M4: Sintesi evidenze → ipotesi concorrenti → valutazione

## Fonti consultate
- README.md
- PRD.md
- LOG.md
- openspec/project.md
- package.json
- requirements.txt
- .github/workflows/deploy-site.yml
- .github/workflows/daily_upload.yml

## Evidenze chiave
- Sito statico Astro con data build-time, SEO, accessibilità e pubblicazione su GitHub Pages.
- Pipeline Python per crawl/upload YouTube, digest LLM, estrazione OdG in JSONL.
- Automazione giornaliera con GitHub Actions + limiti quota YouTube.
- Nessuna suite test automatica; smoke test manuali descritti.
- Backlog esplicito: search full-text, linkage video↔disegni, API pubblica.

## Hypothesis tree (concorrenza)
- H1: Progetto pronto per uso pubblico nello scope attuale.
  - Evidenze: deploy stabile, automazioni giornaliere, dataset pubblici.
  - Rischi: dipendenze esterne e assenza test.
  - Confidenza: 0.55
- H2: MVP operativo ma fragile su affidabilità/qualità dati.
  - Evidenze: no CI test, dipendenza da ARS/YouTube, pipeline eterogenea.
  - Confidenza: 0.35
- H3: Prototype sperimentale non pronto per utenti finali.
  - Evidenze: backlog ampio, LLM pipeline non monitorata.
  - Confidenza: 0.10

## Progress notes (confidenza)
- P1: Mappate fonti core e pipeline (0.8).
- P2: Evidenze su ops e automazioni da workflow/log (0.7).
- P3: Limiti qualità/testi inferiti, non verificati in codice (0.5).

## Auto-critica e correzioni
- Rischio: non ho letto codice sorgente per convalidare assunzioni.
- Mitigazione: se richiesto, campionare script core (build_anagrafica, upload_single, build-data).
- Rischio: valutazione basata su docs recenti; possibili drift operativi.
- Mitigazione: verificare ultimo run Actions e dataset attuali.

## Piano aggiornato (multi-fase)
- F1: Consolidare evidenze da docs (fatto).
- F2: Valutare rischi e qualità operativa.
- F3: Proporre priorità e raccomandazioni.

## Domande aperte
- Stato reale dei job GitHub Actions negli ultimi 30 giorni?
- Qualità/completezza trascrizioni YouTube su campione recente?
- Necessità legale/licenza per ri-pubblicazione e uso LLM?
