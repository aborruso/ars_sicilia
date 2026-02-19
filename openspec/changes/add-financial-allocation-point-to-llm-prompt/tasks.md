## 1. Prompt update

- [x] 1.1 Aggiornare `src/components/sedute/LlmExportButton.astro` aggiungendo tra i vincoli della sintesi il requisito su interventi/progetti finanziati e risorse stanziate per singolo intervento se disponibili.
- [x] 1.2 Mantenere invariato il resto della struttura del prompt e del comportamento del componente.

## 2. Validation

- [x] 2.1 Verificare che la stringa generata del prompt includa il nuovo punto senza errori di formattazione.
- [x] 2.2 Rieseguire il controllo OpenSpec (`openspec instructions apply`) per confermare stato applicabile e poi marcare task completate.
