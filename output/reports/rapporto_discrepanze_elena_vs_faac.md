================================================================================
RAPPORTO DISCREPANZE: Data Elena P.xlsx vs FAAC_master_data_v1.xlsx
Generato il: 2025-12-15 21:59:10
================================================================================

## 1. PANORAMICA FILE

| File | Prodotti | Nomi Unici | SKU |
|------|----------|------------|-----|
| Data Elena P.xlsx | 33 righe | 33 | 298 |
| FAAC_master_data_v1.xlsx | 149 righe | 86 | 511 |

## 2. FILE SORGENTE IDML

| Tipo | Quantità | Descrizione |
|------|----------|-------------|
| Pagine Prodotto Principali | 64 | Fonte dati corretta |
| Schema Installazione (*_SI) | 46 | Schemi di installazione - DA ESCLUDERE |
| Pagine Kit | 31 | Gestiti da kit.xlsx |
| **Totale** | 141 | |

## 3. CAUSA PRINCIPALE

L'estrazione FAAC elabora i file Schema Installazione (SI) come prodotti separati,
creando voci duplicate con metadati ERRATI:
- Categoria errata: "Schema Installazione" invece della categoria reale
- Numeri pagina errati: pagine SI (263-285) invece delle pagine prodotto
- SKU errati: codici riferimento kit invece dei codici modello
- Titoli errati: spesso preleva testo non correlato


## 4. PRODOTTI DUPLICATI IN FAAC_master_data_v1.xlsx

Prodotti che appaiono più volte:


### 390 230V (3 occorrenze)
  - Pagina 082-083: Automazioni per ante a battente esterno
  - Pagina 154-155: Automazioni per porte a libro
  - Pagina 263: Schema Installazione

### 392 C (2 occorrenze)
  - Pagina 084-085: Automazioni per ante a battente esterno
  - Pagina 263: Schema Installazione

### 400 (2 occorrenze)
  - Pagina 090-091: Automazioni per ante a battente esterno
  - Pagina 268: Schema Installazione

### 402 (2 occorrenze)
  - Pagina 086-087: Automazioni per ante a battente esterno
  - Pagina 266: Schema Installazione

### 412 (2 occorrenze)
  - Pagina 074-075: Automazioni per ante a battente esterno
  - Pagina 264: Schema Installazione

### 413 230V (2 occorrenze)
  - Pagina 076-077: Automazioni per ante a battente esterno
  - Pagina 264: Schema Installazione

### 415 230V (2 occorrenze)
  - Pagina 078-079: Automazioni per ante a battente esterno
  - Pagina 265: Schema Installazione

### 415 24V (2 occorrenze)
  - Pagina 080-081: Automazioni per ante a battente esterno
  - Pagina 265: Schema Installazione

### 422 (2 occorrenze)
  - Pagina 088-089: Automazioni per ante a battente esterno
  - Pagina 267: Schema Installazione

### 433 (3 occorrenze)
  - Pagina 200-201: Trasmittenti e riceventi
  - Pagina 202-203: Trasmittenti e riceventi
  - Pagina 206-207: Trasmittenti e riceventi

### 541 (2 occorrenze)
  - Pagina 279: Schema Installazione
  - Pagina 279: Schema Installazione

### 550 (2 occorrenze)
  - Pagina 148-149: Automazioni per porte basculanti
  - Pagina 280: Schema Installazione

### 580 (2 occorrenze)
  - Pagina 150-152: Automazioni per porte a libro
  - Pagina 281: Schema Installazione

### 620 (8 occorrenze)
  - Pagina 168-171: Barriere automatiche
  - Pagina 168-171: Barriere automatiche
  - Pagina 168-171: Barriere automatiche
  - Pagina 172-175: Barriere automatiche
  - Pagina 172-175: Barriere automatiche
  - Pagina 172-175: Barriere automatiche
  - Pagina 283: Schema Installazione
  - Pagina 283: Schema Installazione

### 740 (2 occorrenze)
  - Pagina 114-115: Automazioni per cancelli scorrevoli
  - Pagina 270: Schema Installazione

### 740 C (2 occorrenze)
  - Pagina 116-117: Automazioni per cancelli scorrevoli
  - Pagina 271: Schema Installazione

### 741 (2 occorrenze)
  - Pagina 118-119: Automazioni per cancelli scorrevoli
  - Pagina 272: Schema Installazione

### 741 C (2 occorrenze)
  - Pagina 120-121: Automazioni per cancelli scorrevoli
  - Pagina 271: Schema Installazione

### 746 C (2 occorrenze)
  - Pagina 122-123: Automazioni per cancelli scorrevoli
  - Pagina 274: Schema Installazione

### 770N 230V (2 occorrenze)
  - Pagina 098-099: Automazioni per ante a battente con moto
  - Pagina 268: Schema Installazione

### 770N 24V (2 occorrenze)
  - Pagina 100-101: Automazioni per ante a battente con moto
  - Pagina 269: Schema Installazione

### 844 C (3 occorrenze)
  - Pagina 124-125: Automazioni per cancelli scorrevoli
  - Pagina 275: Schema Installazione
  - Pagina 275: Schema Installazione

### 884 (2 occorrenze)
  - Pagina 128-129: Automazioni per cancelli scorrevoli
  - Pagina 276: Schema Installazione

### B614 (4 occorrenze)
  - Pagina 160-163: Barriere automatiche
  - Pagina 160-163: Barriere automatiche
  - Pagina 160-163: Barriere automatiche
  - Pagina 282: Schema Installazione

### B680H (3 occorrenze)
  - Pagina 176-179: Barriere automatiche
  - Pagina 176-179: Barriere automatiche
  - Pagina 281: Schema Installazione

### C4000I (2 occorrenze)
  - Pagina 108-109: Motoriduttore integrato 24V
  - Pagina 273: Schema Installazione

### C720 (2 occorrenze)
  - Pagina 110-111: Automazioni per cancelli scorrevoli
  - Pagina 272: Schema Installazione

### C721 (2 occorrenze)
  - Pagina 112-113: Automazioni per cancelli scorrevoli
  - Pagina 274: Schema Installazione

### C851 (2 occorrenze)
  - Pagina 130-132: Automazioni per porte sezionali
  - Pagina 276: Schema Installazione

### D1000 (2 occorrenze)
  - Pagina 138-139: Automazioni per porte sezionali
  - Pagina 278: Schema Installazione

### D600 (2 occorrenze)
  - Pagina 134-135: Automazioni per porte sezionali
  - Pagina 277: Schema Installazione

### D700 HS (2 occorrenze)
  - Pagina 136-137: Automazioni per porte sezionali
  - Pagina 277: Schema Installazione

### DELTA 2 kit (2 occorrenze)
  - Pagina 37: PERFECT KIT
  - Pagina 55: CLASSIC KIT

### DELTA 3 kit (2 occorrenze)
  - Pagina 38: PERFECT KIT
  - Pagina 56: CLASSIC KIT

### ECO kit (2 occorrenze)
  - Pagina 32: PERFECT KIT
  - Pagina 49: CLASSIC KIT

### HANDY kit (2 occorrenze)
  - Pagina 31: PERFECT KIT
  - Pagina 48: CLASSIC KIT

### LEADER kit (2 occorrenze)
  - Pagina 28: PERFECT KIT
  - Pagina 44: CLASSIC KIT

### MASTER kit 230V (2 occorrenze)
  - Pagina 29: PERFECT KIT
  - Pagina 46: CLASSIC KIT

### MASTER kit 24V (2 occorrenze)
  - Pagina 30: PERFECT KIT
  - Pagina 47: CLASSIC KIT

### POWER kit 230V (2 occorrenze)
  - Pagina 34: PERFECT KIT
  - Pagina 52: CLASSIC KIT

### POWER kit 24V (2 occorrenze)
  - Pagina 35: PERFECT KIT
  - Pagina 53: CLASSIC KIT

### PRATICO C kit (2 occorrenze)
  - Pagina 36: PERFECT KIT
  - Pagina 54: CLASSIC KIT

### RAPID kit (2 occorrenze)
  - Pagina 39: PERFECT KIT
  - Pagina 57: CLASSIC KIT

### RH200B (2 occorrenze)
  - Pagina 242-243: Automazioni per serrande avvolgibili
  - Pagina 284: Schema Installazione

### RH240 (2 occorrenze)
  - Pagina 244-245: Automazioni per serrande avvolgibili
  - Pagina 285: Schema Installazione

### RL200 (2 occorrenze)
  - Pagina 240-241: Automazioni per serrande avvolgibili
  - Pagina 284: Schema Installazione

### S2500I (2 occorrenze)
  - Pagina 096-097: Automazioni per ante a battente con moto
  - Pagina 273: Schema Installazione

### S418 (2 occorrenze)
  - Pagina 072-073: Automazioni per ante a battente esterno
  - Pagina 266: Schema Installazione

### S450H (2 occorrenze)
  - Pagina 092-094: Automazioni per ante a battente con moto
  - Pagina 267: Schema Installazione

### S800 ENC (2 occorrenze)
  - Pagina 104-106: automazioni per cancelli scorrevoli
  - Pagina 270: Schema Installazione

### S800H ENC (2 occorrenze)
  - Pagina 102-103: Automazioni per ante a battente con moto
  - Pagina 269: Schema Installazione


## 5. ANALISI DETTAGLIATA DISCREPANZE

Confronto Elena (riferimento) vs estrazione FAAC per prodotti comuni:


### Prodotto: 390 230V

**Dati Elena:**
  - Categoria: Automazioni per ante a battente esterno
  - Pagina: 82-83
  - Titolo: Attuatore elettromeccanico a braccio articolato 230V
  - Codici Modelli: 104570.0

**Estrazione FAAC (3 voci):**
  Voce 1 [✓ Principale]: Pagina 082-083 - Automazioni per ante a battente esterno
  Voce 2 [✓ Principale]: Pagina 154-155 - Automazioni per porte a libro
  Voce 3 [⚠️ PAGINA SI]: Pagina 263 - Schema Installazione

**Verifica IDML (082-083_390_230V.idml):**
  ✓ SKU confermati: ['104570']
  ✓ Parole chiave titolo trovate: ['attuatore', 'elettromeccanico', 'braccio', 'articolato']

### Prodotto: 392 C

**Dati Elena:**
  - Categoria: Automazioni per ante a battente esterno
  - Pagina: 84-85
  - Titolo: Attuatore elettromeccanico a braccio articolato 24V
  - Codici Modelli: 104583;104584

**Estrazione FAAC (2 voci):**
  Voce 1 [✓ Principale]: Pagina 084-085 - Automazioni per ante a battente esterno
  Voce 2 [⚠️ PAGINA SI]: Pagina 263 - Schema Installazione

**Verifica IDML (084-085_392_C.idml):**
  ✓ SKU confermati: ['104583', '104584']
  ✓ Parole chiave titolo trovate: ['attuatore', 'elettromeccanico', 'braccio', 'articolato']

### Prodotto: 400

**Dati Elena:**
  - Categoria: Automazioni per ante a battente esterno
  - Pagina: 90-91
  - Titolo: Attuatore oleodinamico 230V
  - Codici Modelli: 104205;104206;104203;104201;104202;104220

**Estrazione FAAC (2 voci):**
  Voce 1 [✓ Principale]: Pagina 090-091 - Automazioni per ante a battente esterno
  Voce 2 [⚠️ PAGINA SI]: Pagina 268 - Schema Installazione

**Verifica IDML (090-091_400.idml):**
  ✓ SKU confermati: ['104205', '104206', '104203', '104201', '104202']
  ✓ Parole chiave titolo trovate: ['attuatore', 'oleodinamico']

### Prodotto: 402

**Dati Elena:**
  - Categoria: Automazioni per ante a battente esterno
  - Pagina: 86 - 87
  - Titolo: Attuatore oleodinamico 230V
  - Codici Modelli: 104468; 104468

**Estrazione FAAC (2 voci):**
  Voce 1 [✓ Principale]: Pagina 086-087 - Automazioni per ante a battente esterno
  Voce 2 [⚠️ PAGINA SI]: Pagina 266 - Schema Installazione

**Verifica IDML (086-087_402.idml):**
  ✓ SKU confermati: ['104468', '104468']
  ✓ Parole chiave titolo trovate: ['attuatore', 'oleodinamico']

### Prodotto: 412

**Dati Elena:**
  - Categoria: Automazioni per ante a battente esterno
  - Pagina: 74-75
  - Titolo: Attuatore elettromeccanico 230V
  - Codici Modelli: 104470; 104471

**Estrazione FAAC (2 voci):**
  Voce 1 [✓ Principale]: Pagina 074-075 - Automazioni per ante a battente esterno
  Voce 2 [⚠️ PAGINA SI]: Pagina 264 - Schema Installazione

**Verifica IDML (074-075_412.idml):**
  ✓ SKU confermati: ['104470', '104471']
  ✓ Parole chiave titolo trovate: ['attuatore', 'elettromeccanico']

### Prodotto: 413 230V

**Dati Elena:**
  - Categoria: Automazioni per ante a battente esterno
  - Pagina: 76-77
  - Titolo: Attuatore elettromeccanico 230V
  - Codici Modelli: 104413.0

**Estrazione FAAC (2 voci):**
  Voce 1 [✓ Principale]: Pagina 076-077 - Automazioni per ante a battente esterno
  Voce 2 [⚠️ PAGINA SI]: Pagina 264 - Schema Installazione

**Verifica IDML (076-077_413_230V.idml):**
  ✓ SKU confermati: ['104413']
  ✓ Parole chiave titolo trovate: ['attuatore', 'elettromeccanico']

### Prodotto: 415 230V

**Dati Elena:**
  - Categoria: Automazioni per ante a battente esterno
  - Pagina: 78-79
  - Titolo: Attuatore elettromeccanico 230V
  - Codici Modelli: 104415; 104417

**Estrazione FAAC (2 voci):**
  Voce 1 [✓ Principale]: Pagina 078-079 - Automazioni per ante a battente esterno
  Voce 2 [⚠️ PAGINA SI]: Pagina 265 - Schema Installazione

**Verifica IDML (078-079_415_230V.idml):**
  ✓ SKU confermati: ['104415', '104417']
  ✓ Parole chiave titolo trovate: ['attuatore', 'elettromeccanico']

### Prodotto: 415 24V

**Dati Elena:**
  - Categoria: Automazioni per ante a battente esterno
  - Pagina: 80-81
  - Titolo: Attuatore elettromeccanico 24V
  - Codici Modelli: 1044151; 1044171

**Estrazione FAAC (2 voci):**
  Voce 1 [✓ Principale]: Pagina 080-081 - Automazioni per ante a battente esterno
  Voce 2 [⚠️ PAGINA SI]: Pagina 265 - Schema Installazione

**Verifica IDML (080-081_415_24V.idml):**
  ✓ Parole chiave titolo trovate: ['attuatore', 'elettromeccanico']

### Prodotto: 422

**Dati Elena:**
  - Categoria: Automazioni per ante a battente esterno
  - Pagina: 88 - 89 
  - Titolo: Attuatore oleodinamico 230V
  - Codici Modelli: 104200; 104210

**Estrazione FAAC (2 voci):**
  Voce 1 [✓ Principale]: Pagina 088-089 - Automazioni per ante a battente esterno
  Voce 2 [⚠️ PAGINA SI]: Pagina 267 - Schema Installazione

**Verifica IDML (088-089_422.idml):**
  ✓ SKU confermati: ['104200', '104210']
  ✓ Parole chiave titolo trovate: ['attuatore', 'oleodinamico']

### Prodotto: 740

**Dati Elena:**
  - Categoria: Automazioni per cancelli scorrevoli
  - Pagina: 114 - 115 
  - Titolo: Motoriduttore 230V
  - Codici Modelli: 1097805.0

**Estrazione FAAC (2 voci):**
  Voce 1 [✓ Principale]: Pagina 114-115 - Automazioni per cancelli scorrevoli
  Voce 2 [⚠️ PAGINA SI]: Pagina 270 - Schema Installazione

**Verifica IDML (114-115_740.idml):**
  ✓ Parole chiave titolo trovate: ['motoriduttore']

### Prodotto: 740 C

**Dati Elena:**
  - Categoria: Automazioni per cancelli scorrevoli
  - Pagina: 116 - 117
  - Titolo: Motoriduttore 230V
  - Codici Modelli: 109600.0

**Estrazione FAAC (2 voci):**
  Voce 1 [✓ Principale]: Pagina 116-117 - Automazioni per cancelli scorrevoli
  Voce 2 [⚠️ PAGINA SI]: Pagina 271 - Schema Installazione

**Verifica IDML (116-117_740_C.idml):**
  ✓ SKU confermati: ['109600']
  ✓ Parole chiave titolo trovate: ['motoriduttore']

### Prodotto: 741

**Dati Elena:**
  - Categoria: Automazioni per cancelli scorrevoli
  - Pagina: 118 - 119 
  - Titolo: Motoriduttore 230V
  - Codici Modelli: 1097815.0

**Estrazione FAAC (2 voci):**
  Voce 1 [✓ Principale]: Pagina 118-119 - Automazioni per cancelli scorrevoli
  Voce 2 [⚠️ PAGINA SI]: Pagina 272 - Schema Installazione

**Verifica IDML (118-119_741.idml):**
  ✓ Parole chiave titolo trovate: ['motoriduttore']

### Prodotto: 741 C

**Dati Elena:**
  - Categoria: Automazioni per cancelli scorrevoli
  - Pagina: 120 - 121
  - Titolo: Motoriduttore 230V
  - Codici Modelli: 109602.0

**Estrazione FAAC (2 voci):**
  Voce 1 [✓ Principale]: Pagina 120-121 - Automazioni per cancelli scorrevoli
  Voce 2 [⚠️ PAGINA SI]: Pagina 271 - Schema Installazione

**Verifica IDML (120-121_741_C.idml):**
  ✓ SKU confermati: ['109602']
  ✓ Parole chiave titolo trovate: ['motoriduttore']

### Prodotto: 746 C

**Dati Elena:**
  - Categoria: Automazioni per cancelli scorrevoli
  - Pagina: 122 - 123
  - Titolo: Motoriduttore 230V
  - Codici Modelli: 109745; 109746

**Estrazione FAAC (2 voci):**
  Voce 1 [✓ Principale]: Pagina 122-123 - Automazioni per cancelli scorrevoli
  Voce 2 [⚠️ PAGINA SI]: Pagina 274 - Schema Installazione

**Verifica IDML (122-123_746_C.idml):**
  ✓ SKU confermati: ['109745', '109746']
  ✓ Parole chiave titolo trovate: ['motoriduttore']

### Prodotto: 770N 230V

**Dati Elena:**
  - Categoria: Automazioni per ante a battente esterno
  - Pagina: 98-99
  - Titolo: Attuatore elettromeccanico
  - Codici Modelli: 10675201

**Estrazione FAAC (2 voci):**
  Voce 1 [✓ Principale]: Pagina 098-099 - Automazioni per ante a battente con moto
  Voce 2 [⚠️ PAGINA SI]: Pagina 268 - Schema Installazione

**Verifica IDML (098-099_770N_230V.idml):**
  ✓ Parole chiave titolo trovate: ['attuatore', 'elettromeccanico']

### Prodotto: 770N 24V

**Dati Elena:**
  - Categoria: Automazioni per ante a battente con motore interrato
  - Pagina: 100 - 101
  - Titolo: Attuatore elettromeccanico interrato
  - Codici Modelli: 10675301.0

**Estrazione FAAC (2 voci):**
  Voce 1 [✓ Principale]: Pagina 100-101 - Automazioni per ante a battente con moto
  Voce 2 [⚠️ PAGINA SI]: Pagina 269 - Schema Installazione

**Verifica IDML (100-101_770N_24V.idml):**
  ✓ Parole chiave titolo trovate: ['attuatore', 'elettromeccanico', 'interrato']

### Prodotto: 844 C

**Dati Elena:**
  - Categoria: Automazioni per cancelli scorrevoli
  - Pagina: 124 - 125
  - Titolo: Motoriduttore 230V
  - Codici Modelli: 109925; 109926

**Estrazione FAAC (3 voci):**
  Voce 1 [✓ Principale]: Pagina 124-125 - Automazioni per cancelli scorrevoli
  Voce 2 [⚠️ PAGINA SI]: Pagina 275 - Schema Installazione
  Voce 3 [⚠️ PAGINA SI]: Pagina 275 - Schema Installazione

**Verifica IDML (124-125_844_C.idml):**
  ✓ SKU confermati: ['109925', '109926']
  ✓ Parole chiave titolo trovate: ['motoriduttore']

### Prodotto: B614

**Dati Elena:**
  - Categoria: Barriere automatiche
  - Pagina: 163.0
  - Titolo: Aste rettangolari
  - Codici Modelli: 428088;428089;428090;428091

**Estrazione FAAC (4 voci):**
  Voce 1 [✓ Principale]: Pagina 160-163 - Barriere automatiche
  Voce 2 [✓ Principale]: Pagina 160-163 - Barriere automatiche
  Voce 3 [✓ Principale]: Pagina 160-163 - Barriere automatiche
  Voce 4 [⚠️ PAGINA SI]: Pagina 282 - Schema Installazione

### Prodotto: C4000I

**Dati Elena:**
  - Categoria: Automazioni integrate per cancelli scorrevoli
  - Pagina: 108 - 109 
  - Titolo: Motoriduttore integrato 24V
  - Codici Modelli: 109001.0

**Estrazione FAAC (2 voci):**
  Voce 1 [✓ Principale]: Pagina 108-109 - Motoriduttore integrato 24V
  Voce 2 [⚠️ PAGINA SI]: Pagina 273 - Schema Installazione

**Verifica IDML (108-109_C4000I.idml):**
  ✓ SKU confermati: ['109001']
  ✓ Parole chiave titolo trovate: ['motoriduttore', 'integrato']

### Prodotto: C720

**Dati Elena:**
  - Categoria: Automazioni per cancelli scorrevoli
  - Pagina: 110 - 111
  - Titolo: Motoriduttore 24V in bassa tensione
  - Codici Modelli: 109320.0

**Estrazione FAAC (2 voci):**
  Voce 1 [✓ Principale]: Pagina 110-111 - Automazioni per cancelli scorrevoli
  Voce 2 [⚠️ PAGINA SI]: Pagina 272 - Schema Installazione

**Verifica IDML (110-111_C720.idml):**
  ✓ SKU confermati: ['109320']
  ✓ Parole chiave titolo trovate: ['motoriduttore', 'bassa', 'tensione']

### Prodotto: C721

**Dati Elena:**
  - Categoria: Automazioni per cancelli scorrevoli
  - Pagina: 112-113
  - Titolo: Motoriduttore 24V in bassa tensione
  - Codici Modelli: 109321.0

**Estrazione FAAC (2 voci):**
  Voce 1 [✓ Principale]: Pagina 112-113 - Automazioni per cancelli scorrevoli
  Voce 2 [⚠️ PAGINA SI]: Pagina 274 - Schema Installazione

**Verifica IDML (112-113_C721.idml):**
  ✓ SKU confermati: ['109321']
  ✓ Parole chiave titolo trovate: ['motoriduttore', 'bassa', 'tensione']

### Prodotto: C851

**Dati Elena:**
  - Categoria: Automazioni per cancelli scorrevoli
  - Pagina: 130 - 131
  - Titolo: Motoriduttore 230V
  - Codici Modelli: 109903.0

**Estrazione FAAC (2 voci):**
  Voce 1 [✓ Principale]: Pagina 130-132 - Automazioni per porte sezionali
  Voce 2 [⚠️ PAGINA SI]: Pagina 276 - Schema Installazione

**Verifica IDML (130-132_C851.idml):**
  ✓ SKU confermati: ['109903']
  ✓ Parole chiave titolo trovate: ['motoriduttore']

### Prodotto: D1000

**Dati Elena:**
  - Categoria: Automazioni per porte sezionali
  - Pagina: 138 - 139
  - Titolo: Attuatore elettromeccanico 24V a traino
  - Codici Modelli: 110601.0

**Estrazione FAAC (2 voci):**
  Voce 1 [✓ Principale]: Pagina 138-139 - Automazioni per porte sezionali
  Voce 2 [⚠️ PAGINA SI]: Pagina 278 - Schema Installazione

**Verifica IDML (138-139_D1000.idml):**
  ✓ SKU confermati: ['110601']
  ✓ Parole chiave titolo trovate: ['attuatore', 'elettromeccanico', 'traino']

### Prodotto: D600

**Dati Elena:**
  - Categoria: Automazioni per porte sezionali
  - Pagina: 134 -135
  - Titolo: Attuatore elettromeccanico 24V a traino
  - Codici Modelli: 110600.0

**Estrazione FAAC (2 voci):**
  Voce 1 [✓ Principale]: Pagina 134-135 - Automazioni per porte sezionali
  Voce 2 [⚠️ PAGINA SI]: Pagina 277 - Schema Installazione

**Verifica IDML (134-135_D600.idml):**
  ✓ SKU confermati: ['110600']
  ✓ Parole chiave titolo trovate: ['attuatore', 'elettromeccanico', 'traino']

### Prodotto: D700 HS

**Dati Elena:**
  - Categoria: Automazioni per porte sezionali
  - Pagina: 136 - 137 
  - Titolo: Attuatore elettromeccanico 24V a traino
  - Codici Modelli: 110602.0

**Estrazione FAAC (2 voci):**
  Voce 1 [✓ Principale]: Pagina 136-137 - Automazioni per porte sezionali
  Voce 2 [⚠️ PAGINA SI]: Pagina 277 - Schema Installazione

**Verifica IDML (136-137_D700_HS.idml):**
  ✓ SKU confermati: ['110602']
  ✓ Parole chiave titolo trovate: ['attuatore', 'elettromeccanico', 'traino']

### Prodotto: S2500I

**Dati Elena:**
  - Categoria: Automazioni per ante a battente con motore integrato
  - Pagina: 96-97
  - Titolo: Attuatore elettromeccanico 24V
  - Codici Modelli: 104250.0

**Estrazione FAAC (2 voci):**
  Voce 1 [✓ Principale]: Pagina 096-097 - Automazioni per ante a battente con moto
  Voce 2 [⚠️ PAGINA SI]: Pagina 273 - Schema Installazione

**Verifica IDML (096-097_S2500I.idml):**
  ✓ SKU confermati: ['104250']
  ✓ Parole chiave titolo trovate: ['attuatore', 'elettromeccanico']

### Prodotto: S418

**Dati Elena:**
  - Categoria: Automazioni per ante a battente esterno
  - Pagina: 72-73
  - Titolo: Attuatore elettromeccanico 24V
  - Codici Modelli: 104301.0

**Estrazione FAAC (2 voci):**
  Voce 1 [✓ Principale]: Pagina 072-073 - Automazioni per ante a battente esterno
  Voce 2 [⚠️ PAGINA SI]: Pagina 266 - Schema Installazione

**Verifica IDML (072-073_S418.idml):**
  ✓ SKU confermati: ['104301']
  ✓ Parole chiave titolo trovate: ['attuatore', 'elettromeccanico']

### Prodotto: S450H

**Dati Elena:**
  - Categoria: Automazioni per ante a battente esterno
  - Pagina: 92 - 93 
  - Titolo: Attuatore oleodinamico 24V
  - Codici Modelli: 104100; 104101

**Estrazione FAAC (2 voci):**
  Voce 1 [✓ Principale]: Pagina 092-094 - Automazioni per ante a battente con moto
  Voce 2 [⚠️ PAGINA SI]: Pagina 267 - Schema Installazione

**Verifica IDML (092-094_S450H.idml):**
  ✓ SKU confermati: ['104100', '104101']
  ✓ Parole chiave titolo trovate: ['attuatore', 'oleodinamico']

### Prodotto: S800 ENC

**Dati Elena:**
  - Categoria: Automazioni per ante a battente con motore interrato
  - Pagina: 104 - 105 
  - Titolo: Attuatore oleodinamico 230V interrato
  - Codici Modelli: 108800; 108801; 108802; 108803

**Estrazione FAAC (2 voci):**
  Voce 1 [✓ Principale]: Pagina 104-106 - automazioni per cancelli scorrevoli
  Voce 2 [⚠️ PAGINA SI]: Pagina 270 - Schema Installazione

**Verifica IDML (104-106_S800_ENC.idml):**
  ✓ SKU confermati: ['108800', '108801', '108802', '108803']
  ✓ Parole chiave titolo trovate: ['attuatore', 'oleodinamico', 'interrato']

### Prodotto: S800H ENC

**Dati Elena:**
  - Categoria: Automazioni per ante a battente con motore interrato
  - Pagina: 102 - 103 
  - Titolo: Attuatore oleodinamico 24V interrato
  - Codici Modelli: 108720; 108724; 108722; 108725

**Estrazione FAAC (2 voci):**
  Voce 1 [✓ Principale]: Pagina 102-103 - Automazioni per ante a battente con moto
  Voce 2 [⚠️ PAGINA SI]: Pagina 269 - Schema Installazione

**Verifica IDML (102-103_S800H_ENC.idml):**
  ✓ SKU confermati: ['108720', '108724', '108722', '108725']
  ✓ Parole chiave titolo trovate: ['attuatore', 'oleodinamico', 'interrato']

### Prodotto: XTO

**Dati Elena:**
  - Categoria: Trasmittenti e riceventi
  - Pagina: 204.0
  - Titolo: Sistema 868MHz SLH-DS
  - Codici Modelli: 787030;787031

**Estrazione FAAC (1 voci):**
  Voce 1 [✓ Principale]: Pagina 204-205 - Trasmittenti e riceventi

**Verifica IDML (204-205_XTO_-_Sistema_868MHz_SLH-DS.idml):**
  ✓ SKU confermati: ['787030', '787031']
  ✓ Parole chiave titolo trovate: ['sistema', '868mhz', 'slh-ds']


## 6. FILE SCHEMA INSTALLAZIONE (Da escludere)

  - 263_390_230V_SI.idml
  - 263_392_C_SI.idml
  - 264_412_SI.idml
  - 264_413_230V_SI.idml
  - 265_415_230V_SI.idml
  - 265_415_24V_SI.idml
  - 266_402_SI.idml
  - 266_S418_SI.idml
  - 267_422_SI.idml
  - 267_S450H_SI.idml
  - 268_400_SI.idml
  - 268_770N_230V_SI.idml
  - 269_770N_24V_SI.idml
  - 269_S800H_ENC_SI.idml
  - 270_740_SI.idml
  - 270_S800_ENC_SI.idml
  - 271_740_C_SI.idml
  - 271_741_C_SI.idml
  - 272_741_SI.idml
  - 272_C720_SI.idml
  - 273_C4000I_SI.idml
  - 273_S2500I_SI.idml
  - 274_746_C_SI.idml
  - 274_C721_SI.idml
  - 275_844_C_3PH_SI.idml
  - 275_844_C_SI.idml
  - 276_884_MC_3PH_SI.idml
  - 276_C851_SI.idml
  - 277_D600_SI.idml
  - 277_D700_HS_SI.idml
  - 278_540_SI.idml
  - 278_D1000_SI.idml
  - 279_541_3PH_SI.idml
  - 279_541_SI.idml
  - 280_550_SI.idml
  - 280_593_SI.idml
  - 281_580_SI.idml
  - 281_B680H_SI.idml
  - 282_615BPR_SI.idml
  - 282_B614_SI.idml
  - 283_620_Rapida_SI.idml
  - 283_620_Standard_SI.idml
  - 284_RH200B_SI.idml
  - 284_RL200_SI.idml
  - 285_RH240B_SI.idml
  - 285_RH240_SI.idml


## 7. SOLUZIONE CONSIGLIATA


In scripts/extract_all_idml.py, aggiungere filtro per saltare i file Schema Installazione:

```python
for idml_path in idml_files:
    # Salta i file Schema Installazione
    if idml_path.stem.endswith('_SI'):
        continue
    # ... resto dell'estrazione
```

Questo permetterà di:
- Rimuovere 46 voci prodotto duplicate
- Mantenere solo i dati della pagina prodotto principale
- Allinearsi ai dati di riferimento di Elena
