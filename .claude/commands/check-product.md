# Check Product Data Integrity

Validate product data by comparing source files (IDML/PDF) against CSV output files.

## CRITICAL: Source-First Workflow

**ALWAYS start from source files. NEVER use memory or start from CSV.**

The source files are the SOURCE OF TRUTH:
1. **Extracted JSON** (preferred if exists) - `input/processing/extracted/{product}.json`
2. **IDML files** (if no JSON) - `input/processing/IDML_unzipped/`
3. **PDF files** (visual cross-check) - `input/processing/PDF Single Products/`

---

## Step 1: Ask for Product Name

Ask the user:
**"Which product do you want to check? (e.g., 746 C, 560, 844 C, S450H, etc.)"**

Wait for response before proceeding.

---

## Step 2: Load Product Data

### 2.1 Check for Extracted JSON (Fast Path)
```bash
ls input/processing/extracted/{product}*.json
```

**If JSON exists:** Read it and skip to Step 4 (validation).

**If no JSON:** Continue to Step 2.2 to extract from IDML.

### 2.2 Locate IDML Source Files (if no JSON)

#### Find the IDML Folder
```bash
ls input/processing/IDML_unzipped/ | grep -i "{product_name}"
```

#### List ALL Story Files
```bash
ls input/processing/IDML_unzipped/{folder}/Stories/
```

#### READ EACH Story File NOW

**YOU MUST read each Story_*.xml file using the Read tool.** Do not skip this step or use values from memory.

For each Story file, extract:

**A) Model/SKU Table (usually in one Story file)**
Look for table with:
- `models_model_pgf` style → Model names (e.g., "560 CBAC", "560 SB")
- `models_code_pgf` style → SKU codes (e.g., "104561", "104562")
- `models_price_pgf` style → Prices

**B) Technical Specifications Table**
Look for table with:
- `techspec_param_pgf` style → Parameter names (Italian labels)
- `techspec_value_pgf` style → Parameter values
- **ColumnSpan="2"** → Value is SHARED across all models
- **ColumnSpan="1"** → Value is specific to one model

**C) All Other Text Content**
Extract any `<Content>` tags that contain:
- Product descriptions
- Feature lists
- Notes
- Any other text

---

## Step 3: Build Complete Data Map from IDML

After reading ALL Story files, create these tables:

### 3.1 SKUs and Models Found
```
| SKU | Model Name | Price |
|-----|------------|-------|
```

### 3.2 Technical Specifications (COMPLETE LIST)
```
| # | IDML Attribute (Italian) | Model 1 Value | Model 2 Value | Shared? |
|---|--------------------------|---------------|---------------|---------|
| 1 | [attr from IDML]         | [value]       | [value]       | Yes/No  |
| 2 | [attr from IDML]         | [value]       | [value]       | Yes/No  |
| ...                                                                     |
```

**List EVERY attribute found. Do not skip any.**

### 3.3 Other Text Content
```
| Content Type | Text Found |
|--------------|------------|
| Description  | [text]     |
| Notes        | [text]     |
| ...          | ...        |
```

---

## Step 4: Map Attributes to CSV Columns

**(If using JSON, the `csv_column` mapping is already included)**

### 4.1 Read CSV Headers
Read first 2 rows of `output/FAAC_Data_Elena_P_KIT_v4.xlsx - sku.csv`:
- Row 1: Technical column names (e.g., `frequenza_utilizzo`)
- Row 2: Italian display labels (e.g., `Frequenza di utilizzo`)

### 4.2 Create Mapping Table
For EACH IDML attribute, find the matching CSV column:

```
| IDML Attribute | CSV Column Name | Match Type |
|----------------|-----------------|------------|
| [Italian text] | [column_name]   | Exact/Partial/None |
```

---

## Step 5: Validate CSV Data

### 5.1 Read CSV Rows for Each SKU
For each SKU found in IDML:
```bash
grep "^{SKU}," "output/FAAC_Data_Elena_P_KIT_v4.xlsx - sku.csv"
```

### 5.2 Compare EVERY Attribute
For each attribute in your IDML data map:
1. Find the corresponding CSV column
2. Extract the CSV value for this SKU
3. Compare: IDML value vs CSV value
4. Mark as: ✓ Match, ❌ Missing, ⚠ Wrong

**Check ALL attributes, not just a subset.**

### 5.3 Check prodotti.csv
Verify product exists with correct SKU list:
```bash
grep "{product_name}" "output/FAAC_Data_Elena_P_KIT_v4.xlsx - prodotti.csv"
```

---

## Step 6: Report Findings

```
# Product Check Report: [PRODUCT NAME]

## Source Files Analyzed
- IDML Folder: input/processing/IDML_unzipped/[folder]/
- Story files read: [list each file]
- PDF: [path or "Not found"]

## Data Extracted from IDML

### Models & SKUs
| SKU | Model Name | Price |
|-----|------------|-------|

### Technical Specifications (X attributes found)
| # | Attribute | Model 1 | Model 2 | Shared |
|---|-----------|---------|---------|--------|
| 1 | [name]    | [val]   | [val]   | Yes/No |
| 2 | [name]    | [val]   | [val]   | Yes/No |
...

## Validation Results

### SKU: [SKU1] - [Model Name]
| # | Attribute | IDML Value | CSV Column | CSV Value | Status |
|---|-----------|------------|------------|-----------|--------|
| 1 | [attr]    | [value]    | [col]      | [value]   | ✓/❌/⚠ |
| 2 | [attr]    | [value]    | [col]      | [value]   | ✓/❌/⚠ |
...

### SKU: [SKU2] - [Model Name]
| # | Attribute | IDML Value | CSV Column | CSV Value | Status |
|---|-----------|------------|------------|-----------|--------|
...

## Errors Found

1. **[SKU]**: Missing `[csv_column]` - IDML says "[value]"
2. **[SKU]**: Wrong `[csv_column]` - IDML: "[correct]", CSV: "[wrong]"

## Summary
- Total attributes in IDML: X
- ✓ Correct: X
- ❌ Missing: X
- ⚠ Incorrect: X
```

---

## Key Rules

1. **READ IDML FILES FRESH** - Never rely on previous reads or memory
2. **EXTRACT EVERYTHING** - All attributes, all text, all values
3. **BUILD DATA MAP FIRST** - Complete the IDML analysis before touching CSV
4. **CHECK ColumnSpan** - "2" means shared value for all models
5. **VERIFY EVERY ATTRIBUTE** - Don't skip any discovered attributes
6. **REPORT ALL DISCREPANCIES** - Missing, wrong, or mismatched values

---

## File Locations

```
Source of Truth (check in this order):
│
├── input/processing/extracted/{product}.json   ← FAST: Pre-extracted data
│
├── input/processing/IDML_unzipped/{pages}_{product}/
│   └── Stories/Story_*.xml   ← FULL: Read each file
│
└── input/processing/PDF Single Products/
    └── pages_{pages}_{product}.pdf   ← VISUAL: Cross-check

Output to Validate (CSV):
├── output/FAAC_Data_Elena_P_KIT_v4.xlsx - prodotti.csv
└── output/FAAC_Data_Elena_P_KIT_v4.xlsx - sku.csv
```

### Extracted JSON Format
If `{product}.json` exists, it contains:
- `models[]` - SKUs, names, prices
- `tech_specs[]` - All attributes with `csv_column` mapping
- `discrepancies[]` - Any IDML vs PDF differences

Use `/extract-product {name}` to create/update JSON files.

### PDF Naming Convention
PDFs follow pattern: `pages_{page-range}_{category}_{product}.pdf`
Example: `pages_156-157_Automazioni_per_porte_a_libro_560.pdf`
