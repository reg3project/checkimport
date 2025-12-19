# Extract Product Data to JSON

Extract ALL data from IDML and PDF sources into a structured JSON file for fast searching and validation.

## Usage
```
/extract-product 560
/extract-product 746 C
```

## Output
Creates: `input/processing/extracted/{product}.json`

---

## Step 1: Parse Product Argument

Product name is provided as argument: `$ARGUMENTS`

---

## Step 2: Locate Source Files

### 2.1 Find IDML Folder
```bash
ls input/processing/IDML_unzipped/ | grep -i "{product}"
```

### 2.2 Find PDF File
```bash
ls "input/processing/PDF Single Products/" | grep -i "{product}"
```

---

## Step 3: Extract from IDML (Primary Source)

### 3.1 List and Read ALL Story Files
```bash
ls input/processing/IDML_unzipped/{folder}/Stories/
```

**READ EACH Story_*.xml file** and extract:

**A) Models Table**
- Look for `models_model_pgf` → Model name
- Look for `models_code_pgf` → SKU code
- Look for `models_price_pgf` → Price

**B) Technical Specs Table**
- Look for `techspec_param_pgf` → Attribute name (Italian)
- Look for `techspec_value_pgf` → Value
- Check `ColumnSpan="2"` → Shared across all models
- Check `ColumnSpan="1"` → Model-specific

**C) Other Content**
- Product descriptions
- Notes, footnotes
- Any other `<Content>` text

---

## Step 4: Extract from PDF (Visual Verification)

Read the PDF file to:
- Verify values match IDML
- Capture any data that might be in images (not text)
- Note any discrepancies between IDML and PDF

---

## Step 5: Map to CSV Columns

Read CSV headers to find column mappings:
```bash
head -2 "output/FAAC_Data_Elena_P_KIT_v4.xlsx - sku.csv"
```

For each IDML attribute, find matching CSV column:
- Row 2 contains Italian labels
- Row 1 contains technical column names

---

## Step 6: Build JSON Output

Create JSON following the schema in `input/processing/extracted/schema.json`:

```json
{
  "product_name": "{product}",
  "catalog_pages": "{pages}",
  "sources": {
    "idml_folder": "input/processing/IDML_unzipped/{folder}/",
    "pdf_file": "input/processing/PDF Single Products/{pdf_file}",
    "story_files": ["Story_xxx.xml", ...]
  },
  "extracted_at": "{ISO timestamp}",
  "models": [
    { "sku": "...", "name": "...", "price": "..." }
  ],
  "tech_specs": [
    {
      "attribute_it": "Italian name",
      "csv_column": "column_name",
      "values": { "sku1": "value1", "sku2": "value2" },
      "shared": true/false,
      "source": "idml"
    }
  ],
  "descriptions": [...],
  "notes": [...],
  "discrepancies": [
    { "attribute": "...", "idml_value": "...", "pdf_value": "..." }
  ]
}
```

---

## Step 7: Write JSON File

Write to: `input/processing/extracted/{product_name}.json`

Use product name with underscores for spaces (e.g., `746_C.json`)

---

## Key Rules

1. **Read IDML files fresh** - Don't use cached values
2. **Include ALL attributes** - Don't skip any specs found
3. **Map to CSV columns** - Include `csv_column` for validation
4. **Note discrepancies** - If PDF differs from IDML, record it
5. **Use exact values** - Copy text exactly as it appears

---

## After Extraction

The JSON can be used for:
- Fast validation with `/check-product`
- Quick lookups without re-parsing XML
- Cross-referencing IDML vs PDF
- Building validation reports
