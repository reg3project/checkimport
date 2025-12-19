# Check Product Data Integrity

Validate that all product information from source files (IDML/PDF) is correctly transferred to CSV output files.

## Step 1: Ask for Product Name

First, ask the user:
**"Which product do you want to check? (e.g., 746 C, 844 C, 741 C, S450H, B680H, etc.)"**

Wait for the user's response before proceeding.

---

## Step 2: Find and Analyze IDML Source

### 2.1 Locate IDML Folder
```bash
# Find the product's IDML folder
ls input/processing/IDML_unzipped/ | grep -i "{product_name}"
```

### 2.2 Extract ALL Content from IDML Stories

Read through ALL Story_*.xml files to find:

**A) SKU Codes and Model Names**
```bash
# Search for SKU patterns (5-6 digit codes)
grep -roh "[0-9]\{5,6\}" Stories/*.xml | sort -u

# Search for model name patterns
grep -r "<Content>" Stories/*.xml | grep -v "ParagraphStyle"
```

**B) Technical Specifications Table**
The technical specs are in a table structure. Find ALL parameter-value pairs:

1. **Find the table Story file** - usually contains "Modello" and technical specs
2. **Extract parameter names** - these are in cells with `techspec_param_pgf` style
3. **Extract values** - these are in cells with `techspec_value_pgf` style
4. **Note ColumnSpan** - `ColumnSpan="2"` means value applies to ALL models

**DO NOT use a predefined attribute list.** Instead, dynamically discover:
- What attributes exist in THIS product's IDML
- What values are specified for each model variant
- Which values are shared (ColumnSpan="2") vs model-specific (ColumnSpan="1")

### 2.3 Build Attribute Map from IDML

Create a table of everything found:
```
| IDML Attribute Name | Model 1 Value | Model 2 Value | Shared? |
|---------------------|---------------|---------------|---------|
| [discovered attr 1] | [value]       | [value]       | Yes/No  |
| [discovered attr 2] | [value]       | [value]       | Yes/No  |
| ...                 | ...           | ...           | ...     |
```

---

## Step 3: Map IDML Attributes to CSV Columns

After discovering attributes in IDML, find the matching CSV column:

### CSV Column Header Reference (sku.csv row 1-2)
Read the first 2 rows of sku.csv to get:
- Row 1: Column technical names (e.g., `tensione_alimentazione`)
- Row 2: Column display names (e.g., `Tensione di alimentazione di rete`)

### Matching Process
For each IDML attribute found:
1. Search CSV row 2 for matching Italian label
2. Get the corresponding column name from row 1
3. If no exact match, try partial matching or ask user

---

## Step 4: Check PDF (if available)

Look for PDF files:
```bash
ls input/processing/*.pdf
ls input/*.pdf
```

Use PDF to:
- Verify page numbers match IDML folder
- Cross-check technical specs visually
- Identify any values that might be images (not text)

---

## Step 5: Validate CSV Data

### 5.1 Check prodotti.csv

File: `output/FAAC_Data_Elena_P_KIT_v4.xlsx - prodotti.csv`

```bash
grep "{product_name}" "output/FAAC_Data_Elena_P_KIT_v4.xlsx - prodotti.csv"
```

Verify:
- Product exists
- SKU codes from IDML are listed
- Description matches IDML content

### 5.2 Check sku.csv

File: `output/FAAC_Data_Elena_P_KIT_v4.xlsx - sku.csv`

For EACH SKU discovered in IDML:
```bash
grep "^{SKU}," "output/FAAC_Data_Elena_P_KIT_v4.xlsx - sku.csv"
```

Compare EVERY attribute discovered in Step 2:
- Find the CSV column that matches the IDML attribute
- Check if value exists
- Check if value matches

---

## Step 6: Report Findings

```
# Product Check Report: [PRODUCT NAME]

## Source Files
- IDML: input/processing/IDML_unzipped/[folder]/
- PDF: [path or "Not found"]
- Catalog Pages: [page numbers]

## Models & SKUs Found in IDML
| SKU | Model Name |
|-----|------------|
| ... | ...        |

## Technical Specifications from IDML

| Attribute (from IDML) | CSV Column | Model 1 | Model 2 | Shared |
|-----------------------|------------|---------|---------|--------|
| [attr name]           | [col name] | [value] | [value] | Yes/No |
| ...                   | ...        | ...     | ...     | ...    |

## Validation Results

### SKU: [SKU1] ([Model Name])
| Attribute | IDML Value | CSV Value | Status |
|-----------|------------|-----------|--------|
| [attr]    | [value]    | [value]   | ✓ / ❌ |

### SKU: [SKU2] ([Model Name])
| Attribute | IDML Value | CSV Value | Status |
|-----------|------------|-----------|--------|
| [attr]    | [value]    | [value]   | ✓ / ❌ |

## Errors Found

1. **[SKU]**: Missing `[attribute]` - should be "[value]"
2. **[SKU]**: Wrong `[attribute]` - IDML: "[correct]", CSV: "[wrong]"

## Summary
- Attributes checked: X
- ✓ Correct: X
- ❌ Missing: X
- ⚠ Incorrect: X
```

---

## File Locations

```
Source (truth):
└── input/processing/IDML_unzipped/{pages}_{product}/
    └── Stories/Story_*.xml

Output (to validate):
├── output/FAAC_Data_Elena_P_KIT_v4.xlsx - prodotti.csv
└── output/FAAC_Data_Elena_P_KIT_v4.xlsx - sku.csv
```

---

## Key Rules

1. **DO NOT assume which attributes exist** - discover them from IDML
2. **Each product is different** - specs vary by product type
3. **Check ColumnSpan** - determines if value is shared or model-specific
4. **Match by Italian label** - IDML uses Italian, match to CSV row 2
5. **Report ALL discrepancies** - missing values, wrong values, extra values
