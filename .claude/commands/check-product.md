# Check Product Data Integrity

Validate that all product information from source files (IDML/PDF) is correctly transferred to CSV output files.

## Step 1: Ask for Product Name

First, ask the user:
**"Which product do you want to check? (e.g., 746 C, 844 C, 741 C, S450H, etc.)"**

Wait for the user's response before proceeding.

---

## Step 2: Analyze Source Files (IDML + PDF)

### 2.1 Find IDML Source
Search for the product's IDML folder:
```
input/processing/IDML_unzipped/*{product_name}*/
```

Example: For "746 C" → `input/processing/IDML_unzipped/122-123_746_C/`

### 2.2 Extract Data from IDML

Read the Stories/*.xml files to extract:

**A) Product Info (for prodotti.csv)**
- Product name and category
- Page numbers (from folder name, e.g., "122-123")
- Product description
- Product image references
- SKU codes listed
- Accessories and related products
- Certifications and badges

**B) Technical Specifications Table (for sku.csv)**
Search for table content with patterns:
```bash
grep -r "Content>" Stories/*.xml | grep -v "ParagraphStyle\|CharacterStyle"
```

Extract the technical specs table:
| Attribute | Column in sku.csv |
|-----------|-------------------|
| Modello | nome_modello |
| Codice articolo | SKU (first column) |
| Tensione di alimentazione di rete | tensione_alimentazione |
| Potenza max | potenza_massima |
| Pignone | pignone |
| Forza max di spinta | forza_spinta |
| Peso max anta | peso_anta_max |
| Temperatura ambiente di esercizio | temperatura_esercizio |
| Termoprotezione | termoprotezione |
| Grado di protezione | grado_protezione_ip |
| Peso | peso_unita |
| Frequenza di utilizzo | frequenza_utilizzo |
| Spazio di fermata | spazio_fermata |
| Velocità max | velocita_max |
| Velocità dell'anta | velocita_anta |
| Dimensioni (LxPxH) | dimensioni |
| Lunghezza max anta | lunghezza_anta_max |
| Condensatore di spunto | condensatore_spunto |
| Apparecchiatura elettronica | scheda_elettronica |
| Encoder | encoder |

**Important IDML parsing rules:**
- `ColumnSpan="2"` means value applies to ALL model variants
- `ColumnSpan="1"` means value is specific to ONE model variant
- Model names are in row 0 of the table
- First column contains attribute labels

### 2.3 Check PDF (if available)
Look for PDF files in:
```
input/processing/*.pdf
input/*.pdf
```

Use PDF to visually verify:
- Product images match
- Page layout matches IDML
- Any handwritten annotations or corrections

---

## Step 3: Check CSV Files

### 3.1 Check prodotti.csv

File: `output/FAAC_Data_Elena_P_KIT_v4.xlsx - prodotti.csv`

Find the product row and verify:

| Field | Check |
|-------|-------|
| nome_prodotto | Matches IDML product name |
| pagina_catalogo | Matches IDML folder page numbers |
| immagine_principale | Image file exists |
| 720118 (SKU column) | Contains ALL SKUs from IDML |
| titolo_prodotto | Matches IDML title |
| descrizione_prodotto | Contains IDML description text |
| caratteristica_primaria/valore_primario | Matches IDML main specs |
| certificazioni | Matches IDML certifications |
| sku_correlati | Lists related SKUs |

### 3.2 Check sku.csv

File: `output/FAAC_Data_Elena_P_KIT_v4.xlsx - sku.csv`

For EACH SKU found in IDML:
1. Find the SKU row in sku.csv
2. Compare EVERY technical attribute
3. Flag any missing or different values

**Critical checks:**
- All SKUs from IDML exist in CSV
- nome_modello matches IDML model name
- ALL technical specs have values (no empty cells for attributes that exist in IDML)
- Values match exactly (including units like "Kg", "mm", "W", "N")

---

## Step 4: Report Findings

### Format your report as:

```
# Product Check Report: [PRODUCT NAME]

## Source Files Analyzed
- IDML: [folder path]
- PDF: [file path or "Not found"]
- Pages: [page numbers]

## SKUs Found in IDML
| SKU | Model Name |
|-----|------------|
| XXXXXX | Model A |
| YYYYYY | Model B |

## prodotti.csv Check
- [ ] Product row found
- [ ] All SKUs listed
- [ ] Description complete
- [ ] Images referenced
- [ ] Certifications correct

Issues found:
- [list any issues]

## sku.csv Check

### SKU: XXXXXX (Model A)
| Attribute | IDML Value | CSV Value | Status |
|-----------|------------|-----------|--------|
| tensione_alimentazione | 220-240V~ | 220-240V~ | ✓ |
| spazio_fermata | 30 mm | 30 mm | ✓ |
| ... | ... | ... | ... |

### SKU: YYYYYY (Model B)
| Attribute | IDML Value | CSV Value | Status |
|-----------|------------|-----------|--------|
| tensione_alimentazione | 220-240V~ | 220-240V~ | ✓ |
| spazio_fermata | 30 mm | (empty) | ❌ MISSING |
| ... | ... | ... | ... |

## Summary
- Total attributes checked: X
- Correct: X
- Missing: X
- Incorrect: X

## Errors to Fix
1. **SKU YYYYYY**: Missing `spazio_fermata` - should be "30 mm"
2. [other errors...]
```

---

## Quick Reference: File Locations

```
Source Files:
├── input/processing/IDML_unzipped/{page}_{product}/
│   └── Stories/Story_*.xml          <- Technical specs here
└── input/processing/*.pdf            <- Visual reference

Output Files:
├── output/FAAC_Data_Elena_P_KIT_v4.xlsx - prodotti.csv
└── output/FAAC_Data_Elena_P_KIT_v4.xlsx - sku.csv
```

---

## Example Session

**Claude:** Which product do you want to check?

**User:** 746 C

**Claude:**
1. Finding IDML source... Found: `122-123_746_C/`
2. Extracting technical specs from IDML...
3. Found 2 SKUs: 109745 (746 C Z16), 109746 (746 C Z20)
4. Checking prodotti.csv... ✓ Product found
5. Checking sku.csv...

[Detailed comparison table]

**Error Found:**
- SKU 109746 (746 C Z20): Missing `spazio_fermata` - should be "30 mm"
