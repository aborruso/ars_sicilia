# Categorie standard da vocabolario controllato (EuroVoc)

## Contesto

- Prima: 131 categorie libere nei digest (112 usate ≤3 volte), prompt aperto → deriva.
- Decisioni: vocabolario EuroVoc curato (~20 voci, label IT); storico normalizzato riscrivendo solo l'array `categories` dei digest (nessuna chiamata LLM).

## Fase 1 — Vocabolario controllato

- [x] `data/vocabolario_categorie.json`: 22 categorie chiuse con `label`, `slug`, `eurovoc_uri`, `eurovoc_label_it`, `descrizione`.
- [x] URI e label verificati sul dump locale `data/eurovoc/eurovoc_in_skos_core_concepts_20250702-0.rdf`.

## Fase 2 — Pipeline AI vincolata al vocabolario

- [x] `scripts/sync_vocabolario.mjs`: propaga il vocabolario verso schema (enum, minItems 1, maxItems 5, uniqueItems) e prompt (elenco tra marker `[INIZIO/FINE ELENCO CATEGORIE]`). Idempotente.
- [x] `config/digest.yaml` ristrutturato: scelta SOLO dal vocabolario, etichette esatte.
- [x] `generate_digests.sh` invariato (lo schema fa da vincolo).

## Fase 3 — Normalizzazione dello storico

- [x] `data/category_mapping.json`: 131 → 22, valori stringa o array (voci doppie tipo "Turismo e Cultura"). Copertura verificata: nessuna categoria orfana, nessun target fuori vocabolario.
- [x] `scripts/remap_digest_categories.mjs` (`--dry-run` supportato): applicato agli 82 digest, solo `categories` toccato.
- [x] Guardia anti-deriva in `build-data.mjs`: warning su categorie fuori vocabolario.
- [x] Verifica: `categories.json` = 22 voci, tutte nel vocabolario; nessun digest ha perso categorie.

## Fase 4 — Frontend, redirect, pulizia

- [x] Redirect statici vecchi slug → nuovi in `astro.config.mjs` (generati da mapping, skip degli slug che coincidono con pagine reali). Verificato in `dist/`.
- [x] Archiviati `normalize_eurovoc_categories.mjs`, `eurovoc_mapping.json`, `eurovoc-match-schema.json` in `scripts/archive/`.
- [x] Aggiornati `scripts/README.md`, `LOG.md`, `wiki/architettura/dataset.md`.
- [x] `npm run build` completo ok (172 pagine).

## Review

- I nuovi digest possono avere al massimo 5 categorie; gli storici remappati possono superarle (accettato, il limite vale in generazione).
- Un digest di prova con il nuovo enum (`MAX_DIGESTS=1`) non è stato ancora generato: da verificare al prossimo run reale della pipeline.
- Nessuna issue GitHub preesistente sul tema categorie.
