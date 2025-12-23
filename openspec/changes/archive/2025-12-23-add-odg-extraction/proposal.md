# Change: Estrazione dati disegni legge da PDF Ordine del Giorno

## Why
I PDF degli ordini del giorno (OdG) delle sedute ARS contengono dati strutturati sui disegni di legge discussi (titolo, numero, legislatura, data/ora). Attualmente questi dati non vengono estratti né archiviati. Estrarre e normalizzare queste informazioni consente di:
- Arricchire l'archivio storico con metadati sui disegni di legge
- Collegare video di seduta ai disegni discussi
- Generare URL diretti alla scheda ICARO di ogni disegno

## What Changes
- Script Bash `scripts/extract_odg_data.sh` che:
  - Legge tutti gli URL PDF distinti dal campo `odg_url` in `data/anagrafica_video.csv`
  - Usa `markitdown` per convertire PDF in testo e `llm` per estrarre dati strutturati
  - Salva output in formato JSONL in `data/disegni_legge.jsonl`
  - Traccia quali PDF sono già stati elaborati per evitare duplicati
  - Aggiunge campo `pdf_url` e campo generato `url_disegno` (link ICARO)
- Capability ADDED: `odg-data-extraction`

## Impact
- Affected specs: `odg-data-extraction` (new capability)
- Affected code: new script `scripts/extract_odg_data.sh`
- Affected data: new file `data/disegni_legge.jsonl`
- Dependencies: `markitdown`, `llm` CLI tool
