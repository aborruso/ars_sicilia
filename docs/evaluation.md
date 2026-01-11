# Valutazione Progetto - ARS Sicilia

## Sintesi
Progetto maturo per uso pubblico nello scope attuale, con rischi operativi su affidabilità, test e dipendenze esterne. Priorità: resilienza pipeline, qualità dati, observability minima.

## Ambito e fonti
Fonti principali: README, PRD, LOG, openspec/project, workflow GitHub Actions, package/requirements.

## Punti forti
- Missione chiara e valore civico alto; output pubblici già disponibili.
- Architettura separata: sito statico + pipeline dati automatizzata.
- Automazioni giornaliere con quota e logging; dataset open e versionati.
- Design/accessibilità curati; SEO e structured data inclusi.

## Rischi e gap
- Assenza test automatizzati e monitoraggio; dipendenza da successo job e API esterne.
- Pipeline LLM e PDF extraction poco verificabile; rischio qualità/consistenza.
- Dipendenza forte da struttura HTML ARS e quota YouTube.
- Governance dati: policy su errori digest/trascrizioni non formalizzata.

## Opportunità immediate
- Validazioni automatiche: CSV schema, digest schema, link dead-check.
- Telemetria minima: summary run + alert su fallimenti Actions.
- Documentare SLA pipeline e fallback quando ARS/YouTube falliscono.

## Piano multi-fase (proposto)
- F1: Stabilità pipeline (retry/backoff, alerting, health report).
- F2: Qualità dati (validazioni, campioni QA, metriche errori).
- F3: Esperienza utente (search Pagefind, linkage video↔DDL, API pubblica).

## Domande aperte
- Quota YouTube reale e failure rate ultimi 30 giorni?
- Copertura trascrizioni e percentuale `no_transcript`?
- Esiste un piano di governance per errori LLM?

## Valutazione complessiva
MVP+ in produzione; pronto per utenti, ma serve hardening operativo.
