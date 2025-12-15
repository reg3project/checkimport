================================================================================
DISCREPANCY REPORT: Data Elena P.xlsx vs FAAC_master_data_v1.xlsx
Generated: 2025-12-15 21:56:48
================================================================================

## 1. FILE OVERVIEW

| File | Products | Unique Names | SKUs |
|------|----------|--------------|------|
| Data Elena P.xlsx | 33 rows | 33 | 298 |
| FAAC_master_data_v1.xlsx | 149 rows | 86 | 511 |

## 2. IDML SOURCE FILES

| Type | Count | Description |
|------|-------|-------------|
| Main Product Pages | 64 | Correct product data source |
| Schema Installazione (*_SI) | 46 | Installation diagrams - SHOULD SKIP |
| Kit Pages | 31 | Handled by kit.xlsx |
| **Total** | 141 | |

## 3. ROOT CAUSE

The FAAC extraction processes Schema Installazione (SI) files as separate products,
creating duplicate entries with WRONG metadata:
- Wrong categoria: "Schema Installazione" instead of actual category
- Wrong page numbers: SI pages (263-285) instead of product pages
- Wrong SKUs: Kit reference codes instead of model codes
- Wrong titles: Often picks up unrelated text


## 4. DUPLICATE PRODUCTS IN FAAC_master_data_v1.xlsx

Products appearing multiple times:


### 390 230V (3 occurrences)
  - Page 082-083: Automazioni per ante a battente esterno
  - Page 154-155: Automazioni per porte a libro
  - Page 263: Schema Installazione

### 392 C (2 occurrences)
  - Page 084-085: Automazioni per ante a battente esterno
  - Page 263: Schema Installazione

### 400 (2 occurrences)
  - Page 090-091: Automazioni per ante a battente esterno
  - Page 268: Schema Installazione

### 402 (2 occurrences)
  - Page 086-087: Automazioni per ante a battente esterno
  - Page 266: Schema Installazione

### 412 (2 occurrences)
  - Page 074-075: Automazioni per ante a battente esterno
  - Page 264: Schema Installazione

### 413 230V (2 occurrences)
  - Page 076-077: Automazioni per ante a battente esterno
  - Page 264: Schema Installazione

### 415 230V (2 occurrences)
  - Page 078-079: Automazioni per ante a battente esterno
  - Page 265: Schema Installazione

### 415 24V (2 occurrences)
  - Page 080-081: Automazioni per ante a battente esterno
  - Page 265: Schema Installazione

### 422 (2 occurrences)
  - Page 088-089: Automazioni per ante a battente esterno
  - Page 267: Schema Installazione

### 433 (3 occurrences)
  - Page 200-201: Trasmittenti e riceventi
  - Page 202-203: Trasmittenti e riceventi
  - Page 206-207: Trasmittenti e riceventi

### 541 (2 occurrences)
  - Page 279: Schema Installazione
  - Page 279: Schema Installazione

### 550 (2 occurrences)
  - Page 148-149: Automazioni per porte basculanti
  - Page 280: Schema Installazione

### 580 (2 occurrences)
  - Page 150-152: Automazioni per porte a libro
  - Page 281: Schema Installazione

### 620 (8 occurrences)
  - Page 168-171: Barriere automatiche
  - Page 168-171: Barriere automatiche
  - Page 168-171: Barriere automatiche
  - Page 172-175: Barriere automatiche
  - Page 172-175: Barriere automatiche
  - Page 172-175: Barriere automatiche
  - Page 283: Schema Installazione
  - Page 283: Schema Installazione

### 740 (2 occurrences)
  - Page 114-115: Automazioni per cancelli scorrevoli
  - Page 270: Schema Installazione

### 740 C (2 occurrences)
  - Page 116-117: Automazioni per cancelli scorrevoli
  - Page 271: Schema Installazione

### 741 (2 occurrences)
  - Page 118-119: Automazioni per cancelli scorrevoli
  - Page 272: Schema Installazione

### 741 C (2 occurrences)
  - Page 120-121: Automazioni per cancelli scorrevoli
  - Page 271: Schema Installazione

### 746 C (2 occurrences)
  - Page 122-123: Automazioni per cancelli scorrevoli
  - Page 274: Schema Installazione

### 770N 230V (2 occurrences)
  - Page 098-099: Automazioni per ante a battente con moto
  - Page 268: Schema Installazione

### 770N 24V (2 occurrences)
  - Page 100-101: Automazioni per ante a battente con moto
  - Page 269: Schema Installazione

### 844 C (3 occurrences)
  - Page 124-125: Automazioni per cancelli scorrevoli
  - Page 275: Schema Installazione
  - Page 275: Schema Installazione

### 884 (2 occurrences)
  - Page 128-129: Automazioni per cancelli scorrevoli
  - Page 276: Schema Installazione

### B614 (4 occurrences)
  - Page 160-163: Barriere automatiche
  - Page 160-163: Barriere automatiche
  - Page 160-163: Barriere automatiche
  - Page 282: Schema Installazione

### B680H (3 occurrences)
  - Page 176-179: Barriere automatiche
  - Page 176-179: Barriere automatiche
  - Page 281: Schema Installazione

### C4000I (2 occurrences)
  - Page 108-109: Motoriduttore integrato 24V
  - Page 273: Schema Installazione

### C720 (2 occurrences)
  - Page 110-111: Automazioni per cancelli scorrevoli
  - Page 272: Schema Installazione

### C721 (2 occurrences)
  - Page 112-113: Automazioni per cancelli scorrevoli
  - Page 274: Schema Installazione

### C851 (2 occurrences)
  - Page 130-132: Automazioni per porte sezionali
  - Page 276: Schema Installazione

### D1000 (2 occurrences)
  - Page 138-139: Automazioni per porte sezionali
  - Page 278: Schema Installazione

### D600 (2 occurrences)
  - Page 134-135: Automazioni per porte sezionali
  - Page 277: Schema Installazione

### D700 HS (2 occurrences)
  - Page 136-137: Automazioni per porte sezionali
  - Page 277: Schema Installazione

### DELTA 2 kit (2 occurrences)
  - Page 37: PERFECT KIT
  - Page 55: CLASSIC KIT

### DELTA 3 kit (2 occurrences)
  - Page 38: PERFECT KIT
  - Page 56: CLASSIC KIT

### ECO kit (2 occurrences)
  - Page 32: PERFECT KIT
  - Page 49: CLASSIC KIT

### HANDY kit (2 occurrences)
  - Page 31: PERFECT KIT
  - Page 48: CLASSIC KIT

### LEADER kit (2 occurrences)
  - Page 28: PERFECT KIT
  - Page 44: CLASSIC KIT

### MASTER kit 230V (2 occurrences)
  - Page 29: PERFECT KIT
  - Page 46: CLASSIC KIT

### MASTER kit 24V (2 occurrences)
  - Page 30: PERFECT KIT
  - Page 47: CLASSIC KIT

### POWER kit 230V (2 occurrences)
  - Page 34: PERFECT KIT
  - Page 52: CLASSIC KIT

### POWER kit 24V (2 occurrences)
  - Page 35: PERFECT KIT
  - Page 53: CLASSIC KIT

### PRATICO C kit (2 occurrences)
  - Page 36: PERFECT KIT
  - Page 54: CLASSIC KIT

### RAPID kit (2 occurrences)
  - Page 39: PERFECT KIT
  - Page 57: CLASSIC KIT

### RH200B (2 occurrences)
  - Page 242-243: Automazioni per serrande avvolgibili
  - Page 284: Schema Installazione

### RH240 (2 occurrences)
  - Page 244-245: Automazioni per serrande avvolgibili
  - Page 285: Schema Installazione

### RL200 (2 occurrences)
  - Page 240-241: Automazioni per serrande avvolgibili
  - Page 284: Schema Installazione

### S2500I (2 occurrences)
  - Page 096-097: Automazioni per ante a battente con moto
  - Page 273: Schema Installazione

### S418 (2 occurrences)
  - Page 072-073: Automazioni per ante a battente esterno
  - Page 266: Schema Installazione

### S450H (2 occurrences)
  - Page 092-094: Automazioni per ante a battente con moto
  - Page 267: Schema Installazione

### S800 ENC (2 occurrences)
  - Page 104-106: automazioni per cancelli scorrevoli
  - Page 270: Schema Installazione

### S800H ENC (2 occurrences)
  - Page 102-103: Automazioni per ante a battente con moto
  - Page 269: Schema Installazione


## 5. DETAILED DISCREPANCY ANALYSIS

Comparing Elena (reference) vs FAAC extraction for common products:


### Product: 390 230V

**Elena Data:**
  - categoria_prodotto: Automazioni per ante a battente esterno
  - pagina_catalogo: 82-83
  - titolo_prodotto: Attuatore elettromeccanico a braccio articolato 230V
  - codici_modelli: 104570.0

**FAAC Extraction (3 entries):**
  Entry 1 [✓ Main]: Page 082-083 - Automazioni per ante a battente esterno
  Entry 2 [✓ Main]: Page 154-155 - Automazioni per porte a libro
  Entry 3 [⚠️ SI PAGE]: Page 263 - Schema Installazione

**IDML Verification (082-083_390_230V.idml):**
  ✓ SKUs confirmed: ['104570']
  ✓ Title keywords found: ['attuatore', 'elettromeccanico', 'braccio', 'articolato']

### Product: 392 C

**Elena Data:**
  - categoria_prodotto: Automazioni per ante a battente esterno
  - pagina_catalogo: 84-85
  - titolo_prodotto: Attuatore elettromeccanico a braccio articolato 24V
  - codici_modelli: 104583;104584

**FAAC Extraction (2 entries):**
  Entry 1 [✓ Main]: Page 084-085 - Automazioni per ante a battente esterno
  Entry 2 [⚠️ SI PAGE]: Page 263 - Schema Installazione

**IDML Verification (084-085_392_C.idml):**
  ✓ SKUs confirmed: ['104583', '104584']
  ✓ Title keywords found: ['attuatore', 'elettromeccanico', 'braccio', 'articolato']

### Product: 400

**Elena Data:**
  - categoria_prodotto: Automazioni per ante a battente esterno
  - pagina_catalogo: 90-91
  - titolo_prodotto: Attuatore oleodinamico 230V
  - codici_modelli: 104205;104206;104203;104201;104202;104220

**FAAC Extraction (2 entries):**
  Entry 1 [✓ Main]: Page 090-091 - Automazioni per ante a battente esterno
  Entry 2 [⚠️ SI PAGE]: Page 268 - Schema Installazione

**IDML Verification (090-091_400.idml):**
  ✓ SKUs confirmed: ['104205', '104206', '104203', '104201', '104202']
  ✓ Title keywords found: ['attuatore', 'oleodinamico']

### Product: 402

**Elena Data:**
  - categoria_prodotto: Automazioni per ante a battente esterno
  - pagina_catalogo: 86 - 87
  - titolo_prodotto: Attuatore oleodinamico 230V
  - codici_modelli: 104468; 104468

**FAAC Extraction (2 entries):**
  Entry 1 [✓ Main]: Page 086-087 - Automazioni per ante a battente esterno
  Entry 2 [⚠️ SI PAGE]: Page 266 - Schema Installazione

**IDML Verification (086-087_402.idml):**
  ✓ SKUs confirmed: ['104468', '104468']
  ✓ Title keywords found: ['attuatore', 'oleodinamico']

### Product: 412

**Elena Data:**
  - categoria_prodotto: Automazioni per ante a battente esterno
  - pagina_catalogo: 74-75
  - titolo_prodotto: Attuatore elettromeccanico 230V
  - codici_modelli: 104470; 104471

**FAAC Extraction (2 entries):**
  Entry 1 [✓ Main]: Page 074-075 - Automazioni per ante a battente esterno
  Entry 2 [⚠️ SI PAGE]: Page 264 - Schema Installazione

**IDML Verification (074-075_412.idml):**
  ✓ SKUs confirmed: ['104470', '104471']
  ✓ Title keywords found: ['attuatore', 'elettromeccanico']

### Product: 413 230V

**Elena Data:**
  - categoria_prodotto: Automazioni per ante a battente esterno
  - pagina_catalogo: 76-77
  - titolo_prodotto: Attuatore elettromeccanico 230V
  - codici_modelli: 104413.0

**FAAC Extraction (2 entries):**
  Entry 1 [✓ Main]: Page 076-077 - Automazioni per ante a battente esterno
  Entry 2 [⚠️ SI PAGE]: Page 264 - Schema Installazione

**IDML Verification (076-077_413_230V.idml):**
  ✓ SKUs confirmed: ['104413']
  ✓ Title keywords found: ['attuatore', 'elettromeccanico']

### Product: 415 230V

**Elena Data:**
  - categoria_prodotto: Automazioni per ante a battente esterno
  - pagina_catalogo: 78-79
  - titolo_prodotto: Attuatore elettromeccanico 230V
  - codici_modelli: 104415; 104417

**FAAC Extraction (2 entries):**
  Entry 1 [✓ Main]: Page 078-079 - Automazioni per ante a battente esterno
  Entry 2 [⚠️ SI PAGE]: Page 265 - Schema Installazione

**IDML Verification (078-079_415_230V.idml):**
  ✓ SKUs confirmed: ['104415', '104417']
  ✓ Title keywords found: ['attuatore', 'elettromeccanico']

### Product: 415 24V

**Elena Data:**
  - categoria_prodotto: Automazioni per ante a battente esterno
  - pagina_catalogo: 80-81
  - titolo_prodotto: Attuatore elettromeccanico 24V
  - codici_modelli: 1044151; 1044171

**FAAC Extraction (2 entries):**
  Entry 1 [✓ Main]: Page 080-081 - Automazioni per ante a battente esterno
  Entry 2 [⚠️ SI PAGE]: Page 265 - Schema Installazione

**IDML Verification (080-081_415_24V.idml):**
  ✓ Title keywords found: ['attuatore', 'elettromeccanico']

### Product: 422

**Elena Data:**
  - categoria_prodotto: Automazioni per ante a battente esterno
  - pagina_catalogo: 88 - 89 
  - titolo_prodotto: Attuatore oleodinamico 230V
  - codici_modelli: 104200; 104210

**FAAC Extraction (2 entries):**
  Entry 1 [✓ Main]: Page 088-089 - Automazioni per ante a battente esterno
  Entry 2 [⚠️ SI PAGE]: Page 267 - Schema Installazione

**IDML Verification (088-089_422.idml):**
  ✓ SKUs confirmed: ['104200', '104210']
  ✓ Title keywords found: ['attuatore', 'oleodinamico']

### Product: 740

**Elena Data:**
  - categoria_prodotto: Automazioni per cancelli scorrevoli
  - pagina_catalogo: 114 - 115 
  - titolo_prodotto: Motoriduttore 230V
  - codici_modelli: 1097805.0

**FAAC Extraction (2 entries):**
  Entry 1 [✓ Main]: Page 114-115 - Automazioni per cancelli scorrevoli
  Entry 2 [⚠️ SI PAGE]: Page 270 - Schema Installazione

**IDML Verification (114-115_740.idml):**
  ✓ Title keywords found: ['motoriduttore']

### Product: 740 C

**Elena Data:**
  - categoria_prodotto: Automazioni per cancelli scorrevoli
  - pagina_catalogo: 116 - 117
  - titolo_prodotto: Motoriduttore 230V
  - codici_modelli: 109600.0

**FAAC Extraction (2 entries):**
  Entry 1 [✓ Main]: Page 116-117 - Automazioni per cancelli scorrevoli
  Entry 2 [⚠️ SI PAGE]: Page 271 - Schema Installazione

**IDML Verification (116-117_740_C.idml):**
  ✓ SKUs confirmed: ['109600']
  ✓ Title keywords found: ['motoriduttore']

### Product: 741

**Elena Data:**
  - categoria_prodotto: Automazioni per cancelli scorrevoli
  - pagina_catalogo: 118 - 119 
  - titolo_prodotto: Motoriduttore 230V
  - codici_modelli: 1097815.0

**FAAC Extraction (2 entries):**
  Entry 1 [✓ Main]: Page 118-119 - Automazioni per cancelli scorrevoli
  Entry 2 [⚠️ SI PAGE]: Page 272 - Schema Installazione

**IDML Verification (118-119_741.idml):**
  ✓ Title keywords found: ['motoriduttore']

### Product: 741 C

**Elena Data:**
  - categoria_prodotto: Automazioni per cancelli scorrevoli
  - pagina_catalogo: 120 - 121
  - titolo_prodotto: Motoriduttore 230V
  - codici_modelli: 109602.0

**FAAC Extraction (2 entries):**
  Entry 1 [✓ Main]: Page 120-121 - Automazioni per cancelli scorrevoli
  Entry 2 [⚠️ SI PAGE]: Page 271 - Schema Installazione

**IDML Verification (120-121_741_C.idml):**
  ✓ SKUs confirmed: ['109602']
  ✓ Title keywords found: ['motoriduttore']

### Product: 746 C

**Elena Data:**
  - categoria_prodotto: Automazioni per cancelli scorrevoli
  - pagina_catalogo: 122 - 123
  - titolo_prodotto: Motoriduttore 230V
  - codici_modelli: 109745; 109746

**FAAC Extraction (2 entries):**
  Entry 1 [✓ Main]: Page 122-123 - Automazioni per cancelli scorrevoli
  Entry 2 [⚠️ SI PAGE]: Page 274 - Schema Installazione

**IDML Verification (122-123_746_C.idml):**
  ✓ SKUs confirmed: ['109745', '109746']
  ✓ Title keywords found: ['motoriduttore']

### Product: 770N 230V

**Elena Data:**
  - categoria_prodotto: Automazioni per ante a battente esterno
  - pagina_catalogo: 98-99
  - titolo_prodotto: Attuatore elettromeccanico
  - codici_modelli: 10675201

**FAAC Extraction (2 entries):**
  Entry 1 [✓ Main]: Page 098-099 - Automazioni per ante a battente con moto
  Entry 2 [⚠️ SI PAGE]: Page 268 - Schema Installazione

**IDML Verification (098-099_770N_230V.idml):**
  ✓ Title keywords found: ['attuatore', 'elettromeccanico']

### Product: 770N 24V

**Elena Data:**
  - categoria_prodotto: Automazioni per ante a battente con motore interrato
  - pagina_catalogo: 100 - 101
  - titolo_prodotto: Attuatore elettromeccanico interrato
  - codici_modelli: 10675301.0

**FAAC Extraction (2 entries):**
  Entry 1 [✓ Main]: Page 100-101 - Automazioni per ante a battente con moto
  Entry 2 [⚠️ SI PAGE]: Page 269 - Schema Installazione

**IDML Verification (100-101_770N_24V.idml):**
  ✓ Title keywords found: ['attuatore', 'elettromeccanico', 'interrato']

### Product: 844 C

**Elena Data:**
  - categoria_prodotto: Automazioni per cancelli scorrevoli
  - pagina_catalogo: 124 - 125
  - titolo_prodotto: Motoriduttore 230V
  - codici_modelli: 109925; 109926

**FAAC Extraction (3 entries):**
  Entry 1 [✓ Main]: Page 124-125 - Automazioni per cancelli scorrevoli
  Entry 2 [⚠️ SI PAGE]: Page 275 - Schema Installazione
  Entry 3 [⚠️ SI PAGE]: Page 275 - Schema Installazione

**IDML Verification (124-125_844_C.idml):**
  ✓ SKUs confirmed: ['109925', '109926']
  ✓ Title keywords found: ['motoriduttore']

### Product: B614

**Elena Data:**
  - categoria_prodotto: Barriere automatiche
  - pagina_catalogo: 163.0
  - titolo_prodotto: Aste rettangolari
  - codici_modelli: 428088;428089;428090;428091

**FAAC Extraction (4 entries):**
  Entry 1 [✓ Main]: Page 160-163 - Barriere automatiche
  Entry 2 [✓ Main]: Page 160-163 - Barriere automatiche
  Entry 3 [✓ Main]: Page 160-163 - Barriere automatiche
  Entry 4 [⚠️ SI PAGE]: Page 282 - Schema Installazione

### Product: C4000I

**Elena Data:**
  - categoria_prodotto: Automazioni integrate per cancelli scorrevoli
  - pagina_catalogo: 108 - 109 
  - titolo_prodotto: Motoriduttore integrato 24V
  - codici_modelli: 109001.0

**FAAC Extraction (2 entries):**
  Entry 1 [✓ Main]: Page 108-109 - Motoriduttore integrato 24V
  Entry 2 [⚠️ SI PAGE]: Page 273 - Schema Installazione

**IDML Verification (108-109_C4000I.idml):**
  ✓ SKUs confirmed: ['109001']
  ✓ Title keywords found: ['motoriduttore', 'integrato']

### Product: C720

**Elena Data:**
  - categoria_prodotto: Automazioni per cancelli scorrevoli
  - pagina_catalogo: 110 - 111
  - titolo_prodotto: Motoriduttore 24V in bassa tensione
  - codici_modelli: 109320.0

**FAAC Extraction (2 entries):**
  Entry 1 [✓ Main]: Page 110-111 - Automazioni per cancelli scorrevoli
  Entry 2 [⚠️ SI PAGE]: Page 272 - Schema Installazione

**IDML Verification (110-111_C720.idml):**
  ✓ SKUs confirmed: ['109320']
  ✓ Title keywords found: ['motoriduttore', 'bassa', 'tensione']

### Product: C721

**Elena Data:**
  - categoria_prodotto: Automazioni per cancelli scorrevoli
  - pagina_catalogo: 112-113
  - titolo_prodotto: Motoriduttore 24V in bassa tensione
  - codici_modelli: 109321.0

**FAAC Extraction (2 entries):**
  Entry 1 [✓ Main]: Page 112-113 - Automazioni per cancelli scorrevoli
  Entry 2 [⚠️ SI PAGE]: Page 274 - Schema Installazione

**IDML Verification (112-113_C721.idml):**
  ✓ SKUs confirmed: ['109321']
  ✓ Title keywords found: ['motoriduttore', 'bassa', 'tensione']

### Product: C851

**Elena Data:**
  - categoria_prodotto: Automazioni per cancelli scorrevoli
  - pagina_catalogo: 130 - 131
  - titolo_prodotto: Motoriduttore 230V
  - codici_modelli: 109903.0

**FAAC Extraction (2 entries):**
  Entry 1 [✓ Main]: Page 130-132 - Automazioni per porte sezionali
  Entry 2 [⚠️ SI PAGE]: Page 276 - Schema Installazione

**IDML Verification (130-132_C851.idml):**
  ✓ SKUs confirmed: ['109903']
  ✓ Title keywords found: ['motoriduttore']

### Product: D1000

**Elena Data:**
  - categoria_prodotto: Automazioni per porte sezionali
  - pagina_catalogo: 138 - 139
  - titolo_prodotto: Attuatore elettromeccanico 24V a traino
  - codici_modelli: 110601.0

**FAAC Extraction (2 entries):**
  Entry 1 [✓ Main]: Page 138-139 - Automazioni per porte sezionali
  Entry 2 [⚠️ SI PAGE]: Page 278 - Schema Installazione

**IDML Verification (138-139_D1000.idml):**
  ✓ SKUs confirmed: ['110601']
  ✓ Title keywords found: ['attuatore', 'elettromeccanico', 'traino']

### Product: D600

**Elena Data:**
  - categoria_prodotto: Automazioni per porte sezionali
  - pagina_catalogo: 134 -135
  - titolo_prodotto: Attuatore elettromeccanico 24V a traino
  - codici_modelli: 110600.0

**FAAC Extraction (2 entries):**
  Entry 1 [✓ Main]: Page 134-135 - Automazioni per porte sezionali
  Entry 2 [⚠️ SI PAGE]: Page 277 - Schema Installazione

**IDML Verification (134-135_D600.idml):**
  ✓ SKUs confirmed: ['110600']
  ✓ Title keywords found: ['attuatore', 'elettromeccanico', 'traino']

### Product: D700 HS

**Elena Data:**
  - categoria_prodotto: Automazioni per porte sezionali
  - pagina_catalogo: 136 - 137 
  - titolo_prodotto: Attuatore elettromeccanico 24V a traino
  - codici_modelli: 110602.0

**FAAC Extraction (2 entries):**
  Entry 1 [✓ Main]: Page 136-137 - Automazioni per porte sezionali
  Entry 2 [⚠️ SI PAGE]: Page 277 - Schema Installazione

**IDML Verification (136-137_D700_HS.idml):**
  ✓ SKUs confirmed: ['110602']
  ✓ Title keywords found: ['attuatore', 'elettromeccanico', 'traino']

### Product: S2500I

**Elena Data:**
  - categoria_prodotto: Automazioni per ante a battente con motore integrato
  - pagina_catalogo: 96-97
  - titolo_prodotto: Attuatore elettromeccanico 24V
  - codici_modelli: 104250.0

**FAAC Extraction (2 entries):**
  Entry 1 [✓ Main]: Page 096-097 - Automazioni per ante a battente con moto
  Entry 2 [⚠️ SI PAGE]: Page 273 - Schema Installazione

**IDML Verification (096-097_S2500I.idml):**
  ✓ SKUs confirmed: ['104250']
  ✓ Title keywords found: ['attuatore', 'elettromeccanico']

### Product: S418

**Elena Data:**
  - categoria_prodotto: Automazioni per ante a battente esterno
  - pagina_catalogo: 72-73
  - titolo_prodotto: Attuatore elettromeccanico 24V
  - codici_modelli: 104301.0

**FAAC Extraction (2 entries):**
  Entry 1 [✓ Main]: Page 072-073 - Automazioni per ante a battente esterno
  Entry 2 [⚠️ SI PAGE]: Page 266 - Schema Installazione

**IDML Verification (072-073_S418.idml):**
  ✓ SKUs confirmed: ['104301']
  ✓ Title keywords found: ['attuatore', 'elettromeccanico']

### Product: S450H

**Elena Data:**
  - categoria_prodotto: Automazioni per ante a battente esterno
  - pagina_catalogo: 92 - 93 
  - titolo_prodotto: Attuatore oleodinamico 24V
  - codici_modelli: 104100; 104101

**FAAC Extraction (2 entries):**
  Entry 1 [✓ Main]: Page 092-094 - Automazioni per ante a battente con moto
  Entry 2 [⚠️ SI PAGE]: Page 267 - Schema Installazione

**IDML Verification (092-094_S450H.idml):**
  ✓ SKUs confirmed: ['104100', '104101']
  ✓ Title keywords found: ['attuatore', 'oleodinamico']

### Product: S800 ENC

**Elena Data:**
  - categoria_prodotto: Automazioni per ante a battente con motore interrato
  - pagina_catalogo: 104 - 105 
  - titolo_prodotto: Attuatore oleodinamico 230V interrato
  - codici_modelli: 108800; 108801; 108802; 108803

**FAAC Extraction (2 entries):**
  Entry 1 [✓ Main]: Page 104-106 - automazioni per cancelli scorrevoli
  Entry 2 [⚠️ SI PAGE]: Page 270 - Schema Installazione

**IDML Verification (104-106_S800_ENC.idml):**
  ✓ SKUs confirmed: ['108800', '108801', '108802', '108803']
  ✓ Title keywords found: ['attuatore', 'oleodinamico', 'interrato']

### Product: S800H ENC

**Elena Data:**
  - categoria_prodotto: Automazioni per ante a battente con motore interrato
  - pagina_catalogo: 102 - 103 
  - titolo_prodotto: Attuatore oleodinamico 24V interrato
  - codici_modelli: 108720; 108724; 108722; 108725

**FAAC Extraction (2 entries):**
  Entry 1 [✓ Main]: Page 102-103 - Automazioni per ante a battente con moto
  Entry 2 [⚠️ SI PAGE]: Page 269 - Schema Installazione

**IDML Verification (102-103_S800H_ENC.idml):**
  ✓ SKUs confirmed: ['108720', '108724', '108722', '108725']
  ✓ Title keywords found: ['attuatore', 'oleodinamico', 'interrato']

### Product: XTO

**Elena Data:**
  - categoria_prodotto: Trasmittenti e riceventi
  - pagina_catalogo: 204.0
  - titolo_prodotto: Sistema 868MHz SLH-DS
  - codici_modelli: 787030;787031

**FAAC Extraction (1 entries):**
  Entry 1 [✓ Main]: Page 204-205 - Trasmittenti e riceventi

**IDML Verification (204-205_XTO_-_Sistema_868MHz_SLH-DS.idml):**
  ✓ SKUs confirmed: ['787030', '787031']
  ✓ Title keywords found: ['sistema', '868mhz', 'slh-ds']


## 6. SCHEMA INSTALLAZIONE FILES (Should be excluded)

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


## 7. RECOMMENDED FIX


In scripts/extract_all_idml.py, add filter to skip Schema Installazione files:

```python
for idml_path in idml_files:
    # Skip Schema Installazione files
    if idml_path.stem.endswith('_SI'):
        continue
    # ... rest of extraction
```

This will:
- Remove 46 duplicate product entries
- Keep only main product page data
- Match Elena's reference data
