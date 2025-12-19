# Validate Product Data - Error Detection Prompt

Analyze product data for errors by cross-referencing multiple source files.

## Task
Find data inconsistencies and missing attributes in product/SKU CSV files by comparing them against IDML source files and PDF catalogs.

## Source Files to Check

### 1. CSV Files (Data Output)
- `output/FAAC_Data_Elena_P_KIT_v4.xlsx - prodotti.csv` - Product definitions
- `output/FAAC_Data_Elena_P_KIT_v4.xlsx - sku.csv` - SKU technical specifications

### 2. IDML Unzipped Files (Source of Truth)
- Location: `input/processing/IDML_unzipped/`
- Key content in: `Stories/Story_*.xml` files
- Contains: Technical specifications tables, SKU codes, model names

### 3. PDF Files (Visual Reference)
- Location: `input/processing/` or similar
- Use for visual verification when needed

## Validation Steps

### Step 1: Identify the Product
When given a product name (e.g., "746 C"):
1. Find the corresponding IDML folder: `IDML_unzipped/*_{product_name}/`
2. Locate the product in `prodotti.csv`
3. Find all related SKUs in `sku.csv`

### Step 2: Extract IDML Technical Specifications
Search the IDML Stories folder for:
```
- SKU codes (e.g., grep for 6-digit numbers like "109745")
- Model names (e.g., "746 C Z16", "746 C Z20")
- Technical specs: Look for patterns like <Content>value</Content>
```

Key technical attributes to extract:
- Tensione di alimentazione (voltage)
- Potenza max (max power)
- Forza max di spinta (max thrust force)
- Peso max anta (max door weight)
- Pignone (pinion type)
- Temperatura ambiente di esercizio (operating temperature)
- Grado di protezione (IP rating)
- Peso (weight)
- Frequenza di utilizzo (usage frequency)
- Spazio di fermata (stopping space)
- Velocità (speed)
- Dimensioni (dimensions)

### Step 3: Cross-Reference CSV Data
For each SKU found in IDML:
1. Locate the SKU row in `sku.csv`
2. Compare EACH technical attribute from IDML against CSV columns
3. Check for:
   - **Missing values**: Attribute exists in IDML but empty in CSV
   - **Wrong values**: Value differs between IDML and CSV
   - **Missing SKUs**: SKU in IDML not present in CSV
   - **Extra SKUs**: SKU in CSV not in IDML (possible mislabeling)

### Step 4: Validate Product-SKU Relationship
Check `prodotti.csv`:
1. Verify all IDML SKUs are listed in the product's SKU column
2. Check for orphan SKUs (in CSV but not linked to product)
3. Verify product specifications match IDML header info

## CSV Column Reference (sku.csv)

Key columns to validate:
| Column Name | Italian Label | Description |
|-------------|---------------|-------------|
| tensione_alimentazione | Tensione di alimentazione di rete | Power supply voltage |
| potenza_massima | Potenza max | Maximum power |
| forza_spinta | Forza max di spinta | Maximum thrust force |
| peso_anta_max | Peso max anta | Maximum door weight |
| pignone | Pignone | Pinion type |
| temperatura_esercizio | Temperatura ambiente di esercizio | Operating temperature |
| grado_protezione_ip | Grado di protezione | IP protection rating |
| peso_unita | Peso | Unit weight |
| frequenza_utilizzo | Frequenza di utilizzo | Usage frequency |
| spazio_fermata | Spazio di fermata | Stopping space |
| velocita_max | Velocità max | Maximum speed |
| dimensioni | Dimensioni (LxPxH) | Dimensions |

## IDML Parsing Tips

1. **ColumnSpan attribute**: When `ColumnSpan="2"`, the value applies to BOTH model variants
2. **Table structure**: Values follow the pattern:
   - Row 0: Model headers (e.g., "746 C Z16", "746 C Z20")
   - Row 1+: Parameter name in column 0, values in columns 1-2

3. **Search patterns**:
```bash
# Find SKU codes
grep -r "109745\|109746" Stories/

# Find model names
grep -r "Z16\|Z20" Stories/

# Find specific attributes
grep -r "Spazio di fermata\|Peso max" Stories/
```

## Output Format

Report findings as:

```
## Product: [Product Name]

### SKUs Found
| SKU | Model | Status |
|-----|-------|--------|
| XXXXXX | Model Name | ✓ OK / ❌ Issues |

### Errors Found

#### 1. Missing Attribute
- **SKU**: XXXXXX
- **Attribute**: [column_name]
- **Expected Value**: [value from IDML]
- **Current Value**: (empty)

#### 2. Incorrect Value
- **SKU**: XXXXXX
- **Attribute**: [column_name]
- **IDML Value**: [correct value]
- **CSV Value**: [wrong value]

#### 3. Missing SKU
- **SKU**: XXXXXX not found in sku.csv

### Summary
- Total errors: X
- Missing attributes: X
- Incorrect values: X
- Missing SKUs: X
```

## Example Usage

User: "Check product 746 C for errors"

1. Find IDML: `IDML_unzipped/122-123_746_C/`
2. Extract specs from Stories/*.xml
3. Find SKUs 109745, 109746 in sku.csv
4. Compare each attribute
5. Report any discrepancies
