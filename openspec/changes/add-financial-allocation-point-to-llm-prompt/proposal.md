## Why

La issue #9 richiede che il prompt esportato nelle pagine video/seduta renda esplicita la ricerca di eventuali stanziamenti economici decisi durante la discussione. Senza questa istruzione, la sintesi può omettere l'informazione su spesa pubblica e importi.

## What Changes

- Aggiornare il testo del prompt LLM esportato dalla pagina video per includere un requisito esplicito su interventi/progetti finanziati e risorse stanziate.
- Chiarire che l'indicazione degli importi va data per singolo intervento quando disponibile nelle risorse fornite.
- Mantenere invariato il resto del formato di export (copia appunti, JSON endpoint, comportamento UI).

## Capabilities

### New Capabilities

- Nessuna.

### Modified Capabilities

- `video-resource-export`: aggiornamento dei requisiti del testo di prompt copiato per includere l'estrazione delle informazioni finanziarie.

## Impact

- Affected specs: `video-resource-export` (modifica requisito su contenuto prompt)
- Affected code/docs (implementation phase): `src/components/sedute/LlmExportButton.astro`
