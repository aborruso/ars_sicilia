# Fix duplicati / qualità dati disegni di legge

## Obiettivo
Eliminare i "duplicati" apparenti dei DDL nel sito, senza perdere informazione reale.

## Diagnosi (verificata sui PDF reali, niente OCR — sono PDF testo)

Due cause radice distinte:

1. **Stralci collassati al numero padre.** Il PDF elenca voci distinte
   `(n. 1030/A Stralcio I/A)`, `V/A`, `VI/A` con titoli e relatori diversi
   (sanità / personale / lavoro). Il prompt impone `numero_disegno = 1030` per tutti.
   `build-data.mjs` poi dedup per `numero` per seduta (riga 103) e aggrega per
   `${numero}-${legislatura}` (riga 179) → **tiene 1 stralcio su 3, scarta gli altri**.
   - Il numero 1030 (padre) è CORRETTO e non va cambiato (URL ICARO = padre).
   - Va preservato lo **stralcio** come campo distinto, e incluso nelle chiavi di build-data.

2. **Titolo non normalizzato.** Stesso disegno (es. 993) esce con 7 forme: virgolette
   curve/dritte, apostrofo `'`/`'`, spazi doppi (testo giustificato), punto finale,
   annotazione `(n. 993/A)`, escape `’`. Verificato: i PDF stessi differiscono
   (249 dritte/spazi singoli, 250+253 curve/spazi doppi) → la variazione non è solo
   l'LLM, serve normalizzazione deterministica a valle.

## Non è un bug
- 993 (giugno) e 974 (maggio) sono disegni DIVERSI realmente presenti negli stessi
  OdG → sedute sovrapposte = corretto. NON si "risolve".

## Cosa rende DAVVERO il sito (ddls.json) — verificato
- 22-record-per-DDL → 1 voce ciascuno. Corretto.
- 947 spazzatura (`{`, 6566 char) NON vince il display: rende "Comiso 'Città della pace'". OK in pagina, sporco solo nel JSONL.
- 1030 rende uno stralcio arbitrario ("transizione energetica") → fuorviante, ma utente ha scelto COLLASSARE.
- 738 rende con virgolette curve residue → cosmetico.

## Decisione presa
- **Stralci 1030: COLLASSARE a uno** (scelta utente, informata). Solo cambio chiave dedup, nessun campo stralcio, nessuna modifica a build-data.mjs.
- **NIENTE reprocess**: 947 rende già pulito; basta scartare il record-spazzatura.

## Fasi (tutto nel post-processing di extract_odg_data.sh, righe ~328-337)

### Fase 1 — Normalizzazione titolo (su JSONL esistente, no LLM)
- [ ] Step mlr: deescape `\\u2019` (DUE backslash!), togli annotazione finale `(n. …)`,
      togli virgolette apertura/chiusura + punto finale, canonicalizza apostrofo `’`→`'`
      e virgolette `“”`→`"`, collassa spazi (`clean_whitespace`).

### Fase 2 — Guard anti-spazzatura
- [ ] Filtro: scarta titoli con `{`/`}` o lunghezza > 400 (legittimi max 264). Elimina 947 corrotto.

### Fase 3 — Collasso stralci
- [ ] Dedup finale: chiave `pdf_url,numero_disegno` (era `+titolo_disegno`).

### Fase 4 — Applicare e verificare
- [ ] Eseguire script (skippa i PDF, riapplica post-processing al JSONL esistente).
- [ ] `node scripts/build-data.mjs` + check: 993 un titolo pulito, 947 niente spazzatura, 1030 un record/PDF.
- [ ] commit + LOG.md.

## Non è un bug (non toccare)
- 953/974/993/930 = debiti fuori bilancio mesi diversi (marzo/maggio/giugno/…), stesse sedute = corretto (voci ricorrenti in OdG finché non votate).
- 993 vs 974 = disegni diversi.
