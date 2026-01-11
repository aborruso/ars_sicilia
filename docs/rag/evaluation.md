# Valutazione: Sistema RAG per Trascrizioni ARS

## Dataset Analizzato

- **Tipo**: Trascrizioni dibattiti Assemblea Regionale Siciliana
- **Formato**: File .txt e .srt (sottotitoli YouTube)
- **Volume**: ~26 video, 34.309 righe, 3.6MB
- **Contenuto**: Interventi parlamentari con speaker identificati
- **Caratteristiche**: Linguaggio naturale italiano, contesto politico-amministrativo

## Applicabilità del Sistema RAG

### ✅ Componenti Direttamente Applicabili

#### 1. Document Ingestion (MarkItDown)
**Applicabilità: ALTA** (con modifiche minori)

- I file .txt non richiedono conversione (già in formato testuale)
- MarkItDown può essere **saltato** completamente
- File .srt richiedono parsing per rimuovere timestamp e numeri sequenza

**Raccomandazione**: Parser custom per .srt, import diretto per .txt

#### 2. Text Chunking (LangChain)
**Applicabilità: ALTA**

- `RecursiveCharacterTextSplitter` ideale per trascrizioni parlamentari
- Chunk size 600-800 caratteri appropriato per interventi brevi
- Overlap 20% preserva continuità tra speaker diversi

**Adattamenti necessari**:
- Preservare metadati speaker (">>" marker)
- Rispettare confini logici degli interventi
- Considerare separator personalizzato per cambio speaker

#### 3. Embeddings (SentenceTransformers)
**Applicabilità: MEDIA-ALTA**

**Pro**:
- `multi-qa-mpnet-base-dot-v1` ottimizzato per Q&A
- Supporto italiano nelle varianti multilingua

**Attenzione**:
- Modello consigliato nell'articolo è principalmente inglese
- **Alternativa preferibile**: `paraphrase-multilingual-mpnet-base-v2` o `LaBSE` per italiano

**Test richiesto**: Confrontare performance su query in italiano

#### 4. Vector Database (ChromaDB)
**Applicabilità: ALTA**

- Dimensioni dataset (3.6MB, ~1000-1500 chunks stimati) ben gestibili
- PersistentClient garantisce persistenza tra sessioni
- Metadati facilmente estensibili (video ID, data seduta, speaker, argomento)

**Metadati consigliati**:

```python
{
    "video_id": "2dVWKAovY8g",
    "speaker": "Onorevole Giristro",
    "tipo_file": "txt",  # txt o srt
    "timestamp": "00:15:30"  # se da .srt
}
```

#### 5. LLM Generation (Ollama)
**Applicabilità: ALTA**

- Ollama locale elimina costi API e problemi privacy
- Modelli consigliati per italiano:
  - `gemma2:9b` (buon compromesso qualità/velocità)
  - `llama3.1:8b` (più veloce, italiano discreto)
  - `qwen2.5:14b` (miglior qualità italiano, più lento)

**Prompt template adattato**:

```python
"""Sei un assistente esperto di politica siciliana.
Basandoti sulle trascrizioni dei dibattiti dell'ARS,
rispondi alla domanda in modo chiaro e preciso.

Trascrizioni:
{context}

Domanda: {question}

Risposta (cita l'oratore quando rilevante):"""
```

#### 6. Web Interface (Gradio)
**Applicabilità: ALTA**

- Deployment immediato con `demo.queue().launch()`
- Streaming nativo per risposte progressive
- Esempi query personalizzabili per contesto ARS

## Vantaggi Specifici per Questo Use Case

### 1. Ricerca Semantica Contestuale
Query tipo:
- "Quali posizioni ha espresso Giristro sulla finanziaria?"
- "Critiche al governo regionale sul PNRR"
- "Interventi su consenso politico e equità territoriale"

### 2. Analisi Cross-Seduta
- Confrontare posizioni dello stesso speaker nel tempo
- Tracciare evoluzione temi (es. finanziaria, sanità)
- Identificare pattern argomentativi

### 3. Privacy e Controllo
- Dati sensibili (dibattiti politici) restano on-premise
- Nessun invio a API esterne (Google, OpenAI)
- Compliance GDPR facilitata

### 4. Costo Zero
- Tutti i componenti open-source
- Nessun costo API ricorrente
- Scalabilità lineare con hardware disponibile

## Criticità e Mitigazioni

### 🔴 Criticità 1: Qualità Trascrizioni
**Problema**: Trascrizioni automatiche YouTube contengono errori (es. "Giristro" vs nome corretto)

**Mitigazioni**:
- Preprocessing con correzioni comuni (dizionario nomi parlamentari)
- Fuzzy matching per nomi propri
- Post-editing manuale delle trascrizioni più importanti

### 🟡 Criticità 2: Embeddings Italiano
**Problema**: Modelli ottimizzati per inglese degradano su italiano

**Mitigazioni**:
- Test comparativo modelli multilingua
- Eventuale fine-tuning su corpus ARS (avanzato)
- Fallback a modelli italiani specifici (es. `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`)

### 🟡 Criticità 3: Contesto Speaker
**Problema**: Attributi speaker potrebbero perdersi nel chunking

**Mitigazioni**:
- Parser custom che preserva speaker per chunk
- Metadata speaker in ChromaDB
- Prompt template che include speaker nelle risposte

### 🟢 Criticità 4: Dimensioni Dataset Ridotte
**Non è un problema**: 26 video sono sufficienti per dimostrare valore
**Opportunità**: Sistema facilmente estensibile aggiungendo nuove trascrizioni

## Architettura Proposta

### Pipeline Semplificata

```
File .txt/.srt
    ↓
[Parser Custom] → Estrae testo + metadati (speaker, video_id, timestamp)
    ↓
[LangChain Splitter] → Chunk 600 chars, overlap 20%, preserva speaker
    ↓
[SentenceTransformers] → Embeddings multilingua italiano
    ↓
[ChromaDB] → Storage persistente con metadati ricchi
    ↓
[Ollama LLM] → Generazione risposte contestualizzate
    ↓
[Gradio] → Interfaccia web con streaming
```

### Differenze dall'Articolo

| Componente | Articolo | Adattamento ARS |
|------------|----------|------------------|
| Ingestion | MarkItDown (PDF) | Parser .txt/.srt custom |
| Embedding Model | `multi-qa-mpnet-base-dot-v1` | `paraphrase-multilingual-mpnet-base-v2` |
| Chunk Size | 600 chars | 600-800 chars (test) |
| Metadati | Solo source | + speaker, video_id, timestamp |
| Prompt | Python programming | Politica siciliana ARS |
| LLM | llama3.2 | gemma2:9b o qwen2.5:14b |

## Stima Effort Implementazione

### Fase 1: Core RAG (2-3 ore)
- Parser .txt/.srt con metadati speaker
- Setup ChromaDB con schema metadati
- Test embeddings modelli italiano
- Query base funzionanti

### Fase 2: LLM Integration (1-2 ore)
- Setup Ollama locale
- Prompt engineering per contesto ARS
- Test generazione risposte

### Fase 3: Interface (1 ora)
- Gradio UI con esempi query
- Streaming risposte
- Visualizzazione fonti

### Fase 4: Refinement (2-3 ore)
- Ottimizzazione chunking per speaker
- Miglioramento prompt template
- Test qualità risposte

**Totale stimato**: 6-9 ore per MVP funzionante

## Raccomandazioni Finali

### ✅ Procedi con Implementazione
Il sistema RAG dell'articolo è **altamente applicabile** con modifiche minori.

### 🎯 Quick Wins Immediati
1. Inizia con parsing .txt (più semplice dei .srt)
2. Usa `paraphrase-multilingual-mpnet-base-v2` come baseline
3. Test su subset 5-10 video prima di indicizzare tutto
4. Deploy Gradio locale prima di considerare production

### 🔬 Test Critici Prima di Scaling
1. **Benchmark embeddings**: Confronta 3-4 modelli su query reali
2. **Qualità chunking**: Verifica che interventi non siano spezzati male
3. **Prompt effectiveness**: Testa su 10+ domande rappresentative
4. **Performance**: Misura latenza query end-to-end

### 📊 Metriche Successo
- Retrieval accuracy: Top-3 chunks contengono risposta (>80%)
- Answer quality: Risposte coerenti e citate (valutazione manuale)
- Query latency: <3 secondi per risposta completa
- User satisfaction: Interfaccia usabile senza training

### 🚀 Estensioni Future
- Classificazione automatica argomenti (sanità, economia, etc.)
- Timeline visualizzazione posizioni speaker
- Export report tematici automatici
- Integrazione dati strutturati ARS (leggi, delibere)

## Conclusione

L'approccio dell'articolo è **production-ready** per questo use case.
Il dataset ridotto (3.6MB) è un **vantaggio** per iterare velocemente.
L'unico rischio reale è qualità embeddings italiano → **mitigabile con test**.

**Verdict**: 🟢 **GREEN LIGHT** per implementazione.
