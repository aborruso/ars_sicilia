# TODO: JSON validation con retry in generate_digests.sh

## Fase 1: Modifica script

- [x] Aggiungere funzione `validate_json` che verifica con `jq` se il JSON è valido
- [x] Modificare logica generazione digest:
  - Loop retry fino a 3 tentativi
  - Dopo ogni generazione, validare JSON
  - Se valido, salvare e uscire dal loop
  - Se non valido, loggare errore e ritentare
  - Se falliscono tutti i tentativi, incrementare counter `failed`
- [x] Eliminare file JSON corrotto se tutti i tentativi falliscono

## Fase 2: Fix file corrotto

- [x] Rimuovere `data/digest/v4mq1poSzOw.json` corrotto
- [x] Rigenerare digest per questo video (al prossimo run)

---

## Review

Modifiche implementate in `scripts/generate_digests.sh`:

1. **Funzione validazione** (righe 30-38): `validate_json()` usa `jq empty` per verificare sintassi JSON
2. **Retry loop** (righe 95-136): max 3 tentativi per digest, validazione dopo ogni generazione
3. **Attesa retry**: 5 secondi tra tentativi falliti
4. **Cleanup**: verificati tutti i digest esistenti, rimosso 1 file corrotto (v4mq1poSzOw.json)

Il digest mancante verrà rigenerato automaticamente al prossimo run dello script con validazione attiva.
