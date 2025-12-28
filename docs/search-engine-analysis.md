# Analisi Search Engine per Sito Statico

Data: 2025-12-28

## Contesto Sito

- **Framework**: Astro statico (output: 'static')
- **Dimensione totale**: 1.8M
- **Dati JSON processati**: ~343K
  - sedute.json: 173K
  - videos.json: 163K
  - categories.json: 7.5K
- **Contenuti ricercabili**:
  - Digest testuali ricchi
  - Categorie tematiche
  - Persone menzionate
  - Trascrizioni sedute ARS

## Tecnologie Valutate

### 1. Pagefind (RACCOMANDATO)

**Caratteristiche:**
- Progettato specificamente per siti statici
- Compressione eccellente: indice ~1% dimensione sito
- Build-time indexing durante astro build
- Zero runtime server-side
- Ricerca client-side performante
- Lazy loading degli indici

**Vantaggi:**
- Index size: 1-5% del contenuto (343K → 3-15KB)
- Integrazione nativa Astro
- Indicizza automaticamente HTML renderizzato
- Filtering nativo (categoria, data, persone)
- UI componenti pronti
- Progressive enhancement
- Supporto multilingua

**Installazione:**

```bash
npm install -D pagefind
```

**Stima performance:**
- Indice: ~10-15KB
- Prima ricerca: <50ms
- Ricerche successive: <10ms

### 2. Fuse.js

**Caratteristiche:**
- Leggero (~3KB gzipped)
- Client-side fuzzy search
- Nessun build step aggiuntivo

**Limiti:**
- Carica tutto l'indice in memoria
- Con 343K JSON potrebbe appesantire
- Meno performante su dataset grandi

**Caso d'uso:** Piccoli dataset (<50K)

### 3. FlexSearch

**Caratteristiche:**
- Velocissimo
- Memoria-efficiente
- Configurabile per compressione

**Limiti:**
- Richiede creazione manuale indice
- Più complesso da configurare
- Meno documentazione per Astro

### 4. Lunr.js

**Caratteristiche:**
- Maturo, battle-tested
- Full-text search tradizionale

**Limiti:**
- Indice più pesante di Pagefind
- Meno ottimizzato per static sites moderni
- Tecnologia datata

## Raccomandazione

**Pagefind** è la scelta ottimale per:

1. **Compressione estrema** dei dati
2. **Zero configurazione** con Astro
3. **Indicizzazione automatica** contenuti HTML
4. **Filtering avanzato** nativo
5. **Performance eccellenti** su grandi dataset
6. **Mantiene il sito 100% statico**

## Prossimi Passi

1. Installare Pagefind come dev dependency
2. Configurare build step in astro.config.mjs
3. Creare componente SearchBar
4. Integrare UI in layout principale
5. Configurare filtri per categorie
6. Testare performance e dimensione indice
