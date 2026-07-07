---
type: Pipeline
title: Estrazione disegni di legge
description: Estrazione dei disegni di legge dai PDF d'ordine del giorno (OdG) delle sedute.
tags: [pipeline, ddl]
timestamp: 2026-07-07T00:00:00Z
---

# Estrazione

`scripts/extract_odg_data.sh` estrae i disegni di legge dai PDF d'ordine
del giorno (testo, non OCR) e scrive `data/disegni_legge.jsonl`. Il join
con le sedute avviene su `odg_url` (CSV) ↔ `pdf_url` (JSONL) — vedi
[dataset](/wiki/architettura/dataset.md).

# Qualità dati (normalizzazione)

Lo script applica un post-processing (mlr) per evitare falsi duplicati:

* **Normalizzazione titolo** — stesso disegno con forme diverse tra
  sedute (virgolette curve/dritte, apostrofi diversi, spazi doppi da
  testo giustificato, punto finale, annotazioni `(n. …)`).
* **Stralci** — voci OdG distinte (es. "1030/A Stralcio I/V/VI")
  collassate a una voce per PDF.
* **Guard anti-corruzione** — scarta record con flood di newline/graffe
  da estrazione fallita (nessuna graffa attesa, lunghezza < 400 char;
  legittimi max ~264).
* **Dedup** per `(pdf_url, numero_disegno)`.

# Automazione

Workflow GitHub "Extract OdG data" (`extract_odg.yml`), schedulato
quotidianamente. Vedi [CI/CD](/wiki/ci-cd/index.md).

# Vedi anche

* [Dataset](/wiki/architettura/dataset.md)
