## Implementation
- [x] 1.1 `get_first_unuploaded_video`: restituire il primo video mai tentato; se non ce ne sono, il `failed` con `last_check` più vecchio.
- [x] 1.2 Verificare su un CSV di prova: nuovo dopo un failed nel file → scelto il nuovo; solo failed → scelto il più vecchio; nessun candidato → `None`.
- [x] 1.3 Verificare sull'anagrafica reale che la selezione resti "nessun video da uploadare".
