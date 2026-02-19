## Context

Il prompt viene generato lato Astro nel componente `LlmExportButton.astro` e copiato in clipboard per l'uso in LLM esterni. La richiesta è testuale e puntuale: aggiungere una nuova istruzione nella sezione "La sintesi deve".

## Goals / Non-Goals

**Goals:**
- Inserire nel prompt una frase normativa chiara sugli stanziamenti economici.
- Conservare struttura e comportamento del componente senza modifiche funzionali ulteriori.

**Non-Goals:**
- Cambiare layout UI del bottone/modal.
- Modificare endpoint JSON o pipeline di generazione digest.
- Introdurre parsing automatico di importi nel codice applicativo.

## Decisions

- **Decisione:** intervenire solo su `src/components/sedute/LlmExportButton.astro`.
  - **Razionale:** la issue parla del prompt creato nelle pagine seduta/video; il testo è definito in questo componente.
  - **Alternativa valutata:** aggiornare anche `SedutaLlmExportButton.astro`. Scartata per mantenere scope aderente alla issue #9, che cita esplicitamente il prompt già esistente con i punti "spiegare di cosa si è parlato / decisioni prese".

- **Decisione:** usare una formulazione condizionale "se disponibili i dati".
  - **Razionale:** evita allucinazioni in assenza di cifre nelle risorse.
  - **Alternativa valutata:** imporre sempre importi numerici. Scartata perché non sempre presenti nelle fonti.

## Risks / Trade-offs

- [Rischio] Prompt più lungo e leggermente più prescrittivo -> **Mitigazione:** aggiunta di una sola riga coerente con il tono già usato.
- [Rischio] Dati economici non presenti e output ambiguo -> **Mitigazione:** mantenere esplicito "se disponibili i dati".
