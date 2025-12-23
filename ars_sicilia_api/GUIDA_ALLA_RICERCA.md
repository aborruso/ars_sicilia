# Guida alla Ricerca

## Note Generali sulla formulazione di una espressione di ricerca

### [Archivio](#a1)

### [Struttura di un archivio (Campi formattati e non)](#a2)

### [Un 'modulo di richiesta'](#a3)

- [Zone di ricerca specifica per un campo, a valori prestabiliti (tendina)](#a4)
- [Zone di ricerca specifica per un campo ad immissione libera](#a5)
- [Zone di ricerca libera](#a6)

### [Espressione di ricerca](#a7)

- [Elementi di ricerca](#a8)
- [Qualificare un elemento di ricerca (in quale parte del documento cercare)](#a9)
- [Operatori di relazione tra i termini](#a10)
- [Priorità di esecuzione (le parentesi)](#a11)

---

Per ricercare ed estrarre documenti da un Archivio necessita formulare, con una semplice sintassi, una espressione di ricerca.

Un ARCHIVIO è una raccolta organizzata di documenti omogenei aventi la medesima struttura informativa costituita da un insieme di campi. Per loro natura i campi possono essere di tipo **formattato** (di lunghezza prestabilita, numerici o alfanumerici) o **non formattato** ovvero a testo libero e ampiezza indefinita.

I campi **formattati** sono identificati, in una lista, da una descrizione, da una sigla abbreviata, dalla tipologia N(ampiezza) o A(ampiezza) per numerico o alfanumerico. I Campi **non formattati**, in una lista, sono identificati da una descrizione, da una sigla abbreviata, dalla tipologia V (Variabile)).

Per le ricerche in campi formattati di un ARCHIVIO è importante conoscerne la tipologia e la lunghezza massima; così ad esempio se il campo "data presentazione", in un archivio, è stato definito numerico di 6 cifre `N(6)` ricercare la data in formato di 8 cifre darebbe un risultato nullo.

### Modelli di ricerca

Per ciascun Archivio posso predisporsi diversi modelli che consentono la semplificazione della ricerca. Ogni modello può contenere diverse Zone di ricerca corrispondenti ai campi dell'Archivio interessato. Queste zone o aree di ricerca possono essere:

**\- Zone di ricerca specifiche a tendina (es. Anno):**
Permettono all'utente di scegliere un solo valore tra quelli ammessi. Il valore qui immesso sarà ricercato nell'archivio esclusivamente nel campo interessato.

**\- Zone di ricerca specifiche ad immissione libera (nel numero, nell'autore):**
In questo caso l'utente può, nei campi numerici, immettere un numero es. 10, un range esempio 10/15 o, una relazione OR esempio 10 or 12. Viceversa per le zone alfanumeriche può utilizzare qualunque espressione o termini con operatori di relazione:

Termine esatto: **SCIASCIA LEONARDO** (e non il viceversa)

Espressione: **SCIASCIA VICINO LEONARDO** o **SCIASCIA AND LEONARDO** ma anche **3/5 Vicino G**.

I valori immessi in zone definite verranno elaborati esclusivamente nelle parti dell'archivio interessato.

**\- Zone di ricerca libere:**
Oltre le zone di ricerca specifiche, un modulo di ricerca può contenere una zona di immissione dati a testo libero:

```
(sciascia vicino2 leonardo).AUTORE E ($ricerca).TITOLO
```

Le espressioni qui immesse, insieme ai dati immessi nelle zone specifiche, costituiranno un'unica espressione di ricerca.

In questa zona l'utente può utilizzare qualunque degli elementi di ricerca sotto specificati, con l'eventuale indicazione del campo di ricerca (es `xyz.titolo`) e, tra gli elementi indicherà gli operatori di relazione che riterrà opportuni.

Per semplificare una ricerca testuale in determinate zone del documento un modulo di ricerca contiene spesso la lista dei "campi" utilizzabili per la banca dati. Selezionando uno qualunque di essi, esempio titolo, apparirà nella zona una espressione `($ricerca).titolo` che permette all'utente di sostituire `$ricerca` con l'espressione desiderata:

Esempio: `(A ciascuno il suo).titolo`

Una espressione di ricerca è dunque un insieme costituito da termini di ricerca (parole, numeri, numeri negativi sigle, intervalli numerici, termini parziali..) tra loro relazionati da un operatore di relazione

### Elementi di ricerca

**Qualunque termine, sigla, verbo...** contenuto nel testo. I numeri devono essere ricercati senza i punti separatori e senza la virgola dei decimali a meno di non usare la identificazione di IMG(Image).

**Qualunque numero o cifra**, anche negativa (segno `-` dopo l'ultima cifra). I numeri devono essere ricercati senza i punti separatori e senza la virgola dei decimali a meno di non usare la identificazione di `IMG()` (Image).

**Un Intervallo Numerico**. Le cifre di intervallo sono separate in modo consecutivo dal simbolo `/` (es. `125/321`).

**Termini con la stessa radice**, seguito dal carattere `$`, per intendere tutti i termini che iniziano allo stesso modo. Il simbolo `$` può essere seguito da una cifra da 1 a 9 per limitare l'estensione dei termini.

**Termini con la stessa desinenza**, seguito dal carattere `%` per intendere tutti i termini che terminano allo stesso modo. Il simbolo `%` può essere seguito da una cifra da 1 a 9 per limitare l'estensione dei termini.

**Termine nell'Immagine esatta**, maiuscolo minuscolo e caratteri speciali, come contenuto nel testo. il termine esatto di ricerca `IMG(XYZ)` deve terminare (Z) con un carattere valido e non un simbolo (Vedi esempi).

**Selezione su campi formattati**, con la funzione Select `SEL(sigla_campo_formattato *operatore "valore di confronto")`.

Esempio ricerca testuale:
```
Occupazione giovanile O Consigli di quartiere
```

Equivale a:
```
Occupazione ADJ2 giovan$ OR Consigl$ ADJ2 quartiere
```

### L'**Archivio** delle INTERROGAZIONI PARLAMENTARI** ad esempio, è composto da "schede" omogenee contenente per ciascun atto i seguenti **campi**:

#### Campi formattati

1. **Data presentazione** DATPRE (Num. 6 cifre)
2. **Num. identificativo** NUMID (Num. 1 cifra)
3. **Sigla atto** SIGLA (Alfanumerico 1 carattere)
4. ...

#### Campi non formattati (testo libero, paragrafi)

1. **Titolo** TITOL (V)
2. **Firmatari** FIRMAT (V)
3. **Testo** TEXT (V)
4. **Note** NOTE (V)
5. ...

### Termini di ricerca sono:

**1. Qualunque termine** contenuto nel testo (parola, sigla, verbo, avverbio...):
`LEGGE`, `Ente`, `modifica`, `richiamato`, `hardware`

**Le sigle o abbreviazioni o numeri si ricercano senza i punti separatori**:
- `ACI` e non `A.C.I.`
- `IBM` e non `I.B.M.`
- `100012` e non `1.000,12`

**2. Numero Positivo, Negativo o Intervallo numerico** separato dal simbolo `/`:
`125`, `01`, `47-`, `121`, `12512-`
**(nella ricerca non usare i punti separatori delle migliaia o virgole per i decimali)**
Cercando il termine `10` si ha come risultato: `10`, `010`, `00010`, `0,10`

**3. Termini con radice** (carattere `$`):
- `LEG$2` → LEGGE, LEGGI
- `LEG$9` o `LEG$` → Legge, Leggio, Legislatore, ...
- `12$2` → 12, 120, 1212, ...

**4. Termini con desinenza** (carattere `%`):
- `ZIONE%2` → LEZIONE, RAZIONE, ...
- `10%2` → 410, 1210, ...

**5. Immagine esatta** `IMG()`:
- `IMG(Rossi)` → cerca "Rossi" e non "ROSSI"
- `IMG(Rossi)$2` → cerca "Rossi", "RossiTi" e non "ROSSI"
- `IMG(I.B.M)` → cerca "I.B.M." e non "ibm" o "IBM"
  *(N.B. Un termine IMG deve terminare con un carattere valido, omettere l'eventuale simbolo punto finale)*
- `IMG(1.000)` → cerca "1.000" e non "1000" o "001000"
- `IMG(10,02)` → cerca "10,02" e non "1002" o "1.002"

**6. SELEZIONE SU CAMPI FORMATTATI**
Se il campo "Nro protocollo" ha identificativo `NPROT` (Numerico di 5 cifre):
- `SEL(NPROT *GT "500")` → numeri maggiori di 500
- `SEL(NPROT RG "500" "632")` → documenti tra 500 e 632

Operatori select: `EQ` (uguale), `LT` (minore), `LE` (minore uguale), `GT` (maggiore), `GE` (maggiore uguale), `RG` (compreso tra 2 valori)

### 7. Livello di ricerca precedente `LVL()`

Ogni ricerca è contraddistinta da un numero di livello. È possibile relazionare i risultati di una ricerca precedente con una nuova ricerca.

Esempio:
```
LVL(12) ESCLUSO rossi.firmat
```
Dai documenti della ricerca n. 12, escludi quelli che contengono "ROSSI" nel campo firmatari.

### 8. Un documento specifico dell'archivio `DOCNO()`

Estrae un documento specifico dalla posizione xxx in archivio:
- `DOCNO(XXX)` → singolo documento
- `DOCNO(xxx/yyy)` → range di documenti

Normalmente utilizzato dai gestori dell'Archivio.

### 9. Tutti i documenti dell'archivio `ALLDOC`

Il termine speciale `ALLDOC` indica l'insieme di tutti i documenti attivi della banca dati.

Usato per criteri di esclusione:
```
ALLDOC NOT 10/12.legisl
```
Tutti i documenti tranne quelli con numero tra 10 e 12 nel campo `legisl`.

### Qualificare un termine di ricerca

Per restringere il campo di ricerca, un termine o un'intera espressione può essere qualificata indicando i campi del documento dove cercare.

**Simboli**:
- `.` (punto) → **inclusione**: cerca solo nei campi indicati
- `:` (due punti) → **esclusione**: cerca in tutti i campi tranne quelli indicati

**Sintassi**: `termine.campo1,campo2,campo3`

**Esempi**:
```
Rossi.FIRMAT ADJ Mario
```
```
(Rossi Mario NOT Bianchi Giovanni).FIRMAT,ORATOR
```
```
1/12.numleg,numpro,numseq
```

La lista degli identificativi di campo (max 6 caratteri) si ottiene dalla maschera di interrogazione con l'apposito pulsante.

### Gli operatori di relazione

Definiscono la relazione intercorrente tra un termine di ricerca ed il successivo.

**Nota importante**: Se tra due termini viene omesso l'operatore, viene assunto automaticamente `ADJ` (Adiacente, seguito).

**Attenzione agli operatori come termini**: Se cerchi `DIRITTO ESCLUSO`, questa query causerà errore perché `ESCLUSO` è un operatore. La formulazione corretta è:
```
DIRITTO ADJ ESCLUSO
```

## Operatori Booleani e di Prossimità

### `AND`, `E`, `ET`, `UND`
Entrambi i termini devono trovarsi nello stesso documento.

**Esempi**:
```
10.numleg AND 2004.ANNLEG
```
Documenti con numero legge 10 E anno 2004 nel campo `annleg`.

```
Sciascia.AUTOR E mafia:titolo
```
"Sciascia" nel campo autore E "mafia" ovunque tranne nel titolo.

### `OR`, `O`, `OU`, `ODER`
Uno o entrambi i termini devono trovarsi nello stesso documento.

**Esempio**:
```
10.numleg OR 20.PROTNUM
```
Documenti con numero legge 10 O numero protocollo 20 O entrambi.

### `XOR`, `ONONE`, `OUEXCLU`, `AODER`
Uno o l'altro termine, ma non entrambi.

**Esempio**:
```
10.numleg XOR 20.PROTNUM
```
Documenti con numero legge 10 O numero protocollo 20, ma NON entrambi.

### `NOT`, `NO`, `ESCLUSO`, `MENO`, `EXCLU`, `OHNE`, `SANS`
Il primo termine presente, il secondo escluso.

**Esempi**:
```
(occupazione giovanile) NOT finanziamenti
```
```
(occupazione giovanile) NOT finanziamenti.titol
```
Nel secondo caso, "finanziamenti" non deve esserci nel campo `titolo` ma può essere presente altrove.

### `SAME`, `SPARA`, `MPARA`, `GPARA`
Il primo termine ed il secondo devono trovarsi nello stesso documento e in uno stesso campo di ricerca.

**Esempi**:
```
(occupazione giovanile) SPARA finanziamenti
```
```
occupazione SPARA finanziamenti.titol
```
Nel secondo caso poiché finanziamenti deve trovarsi nel campo `titolo` la ricerca avrà esito se entrambi si trovano nello stesso campo titolo e non in altri campi.

### `NSAME`, `NSPARA`, `NMPARA`, `NGPARA`
Il primo termine deve essere presente nello stesso documento ma non nello stesso campo.

### `WITH`, `SFRASE`, `MPHRASE`, `GSATZ`
Il primo termine ed il secondo devono trovarsi nello stesso documento, nello stesso campo e nella medesima frase.

**Esempi**:
```
(occupazione giovanile) WITH finanziamenti
```
```
Occupazione WITH finanziamenti
```

### `NWITH`, `NSFRASE`, `NMPHRASE`, `NGSATZ`
Il primo termine ed il secondo devono trovarsi nello stesso documento, nello stesso campo ma in frasi diverse dello stesso campo.

### `LINE`, `MLINE`, `SRIGA`, `GLINE`
Il primo termine ed il secondo devono trovarsi nello stesso documento e nello stesso campo formattato o nella medesima riga di un campo non formattato a testo libero.

### `NLINE`, `NMLINE`, `NSRIGA`, `NGLINE`
Il primo termine ed il secondo devono trovarsi nello stesso documento ma non nella medesima riga di un campo non formattato a testo libero.

### `NEAR`, `VICINO`, `VOISINE`, `NAHE`, `NEARx`, `VICINOx`, `VOISINEx`, `NAHEx` (x = 1 - 9)
Il primo termine deve immediatamente precedere o seguire il secondo termine o massimo tra x (caso di `NEARx`) termini il secondo.

**Esempi**:
- `Mario NEAR ROSSI` dà MARIO ROSSI o ROSSI MARIO ma non ROSSI Sign. Mario.
- `MARIO VICINO3 ROSSI` dà MARIO Sign. ROSSI o MARIO Dr Ing. ROSSI.

### `ADJ`, `SEGUITO`, `SUIVI`, `GEFOLGT`, `ADJx`, `SEGUITOx`, `SUIVIx`, `GEFOLGTx` (x = 1 - 9)
Il primo termine deve immediatamente seguire il secondo termine o massimo tra x (caso di `ADJx`) termini il secondo.

**Esempi**:
- `Mario ADJ ROSSI` dà MARIO ROSSI e non ROSSI MARIO.
- `MARIO SEGUITO3 ROSSI` dà MARIO Sign. ROSSI o MARIO Dr Ing. ROSSI ma non ROSSI MARIO.

### Modifica della priorità di ricerca (le parentesi)

Una ricerca, composta da più termini e differenti operatori di relazione, viene elaborata dal motore di ricerca secondo l'ordine di priorità degli operatori: L'operatore più ristretto precede l'elaborazione dell'operatore più ampio.

**Esempio**:
```
Rossi ADJ Mario OR Giovanni
```

In questo esempio l'operatore `ADJ` è prioritario rispetto `OR` e quindi si avranno i documenti che contengono ROSSI subito seguito da MARIO o che contengono solo Giovanni.

Se si desidera invece ROSSI MARIO o ROSSI GIOVANNI la formulazione corretta è:
```
ROSSI GIOVANNI o ROSSI MARIO
```
oppure
```
ROSSI ADJ (GIOVANNI O MARIO)
```

La parentesi in questo caso obbliga il motore ad elaborare separatamente e prioritariamente il contenuto entro parentesi dal livello più basso al più alto:

```
( query3 AND ( query2 AND ( query1) ) )
```

Nel comporre il testo della domanda è possibile dunque usare le parentesi (massimo 255 livelli). Le parentesi aperte o chiuse precedono o seguono i termini e non gli operatori. A tante parentesi aperte devono corrispondere altrettante parentesi chiuse. Le parentesi forzano la priorità di elaborazione rispetto alla priorità degli operatori.

La sequenza, secondo la priorità di elaborazione, degli operatori di relazione, è la seguente:

```
ADJ, ADJx, NEAR, NEARx, LINE, NLINE, WITH, NWITH, SAME, NSAME, NOT, AND, XOR, OR
```
