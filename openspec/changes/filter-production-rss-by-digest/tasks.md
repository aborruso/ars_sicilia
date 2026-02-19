## Implementation
- [x] 1.1 Aggiornare `src/pages/rss.xml.ts` filtrando i video per digest valido prima della costruzione degli item RSS.
- [x] 1.2 Considerare non idonei i video con digest assente, nullo o composto solo da whitespace.
- [x] 1.3 Mantenere ordinamento cronologico discendente e limite massimo (20) applicati dopo il filtro per digest.
- [x] 1.4 Verificare localmente che `npm run build` generi `dist/rss.xml` senza item privi di digest.
- [x] 1.5 Aggiornare README/docs operative del feed ufficiale per esplicitare la regola di inclusione.
