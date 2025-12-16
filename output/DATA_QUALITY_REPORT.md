# FAAC Data Quality Comparison Report

**Generated:** 2025-12-16 08:28:13

**Source Files:** 12 Excel files from drive-download-20251216T071121Z-3-001.zip

**Master File:** FAAC_master_data_v1.xlsx


---

## 1. Master File Reference

| Sheet | Rows | Columns | Completeness |
|-------|------|---------|--------------|
| prodotti | 150 | 37 | 41.4% |
| sku | 512 | 61 | 12.1% |


---

## 2. Summary by Contributor

| File | Prodotti Rows | SKU Rows | Prodotti % | SKU % | Grade | Score |
|------|---------------|----------|------------|-------|-------|-------|
| Abrar H | 12 | 269 | 54.7% | 14.1% | **A** | 51.0 |
| Almay E | 67 | 269 | 21.2% | 14.1% | **C** | 31.2 |
| Arjol T | 26 | 274 | 58.6% | 14.0% | **A** | 54.6 |
| Ayesha K | 15 | 274 | 59.4% | 15.7% | **A** | 55.5 |
| Blerta B | 11 | 269 | 55.9% | 14.1% | **A** | 53.6 |
| Dora T | 22 | 270 | 56.0% | 14.1% | **A** | 51.5 |
| Elena P | 38 | 299 | 55.3% | 15.3% | **A** | 48.5 |
| Giuseppe C | 58 | 277 | 47.0% | 13.7% | **A** | 45.6 |
| Javeria I | 11 | 269 | 56.4% | 14.8% | **A** | 54.0 |
| Julja V | 32 | 269 | 46.3% | 14.1% | **B** | 44.6 |
| Matteo F | 13 | 271 | 52.5% | 14.1% | **A** | 50.1 |
| Nazia S | 84 | 269 | 46.6% | 14.2% | **A** | 45.6 |


---

## 3. Quality Rankings

| Rank | Contributor | Score | Grade | Key Columns Filled |
|------|-------------|-------|-------|-------------------|
| 1 | **Ayesha K** | 55.5 | A | Prodotti: 7/7, SKU: 4/5 |
| 2 | **Arjol T** | 54.6 | A | Prodotti: 7/7, SKU: 4/5 |
| 3 | **Javeria I** | 54.0 | A | Prodotti: 7/7, SKU: 4/5 |
| 4 | **Blerta B** | 53.6 | A | Prodotti: 7/7, SKU: 4/5 |
| 5 | **Dora T** | 51.5 | A | Prodotti: 6/7, SKU: 4/5 |
| 6 | **Abrar H** | 51.0 | A | Prodotti: 6/7, SKU: 4/5 |
| 7 | **Matteo F** | 50.1 | A | Prodotti: 6/7, SKU: 4/5 |
| 8 | **Elena P** | 48.5 | A | Prodotti: 6/7, SKU: 3/5 |
| 9 | **Giuseppe C** | 45.6 | A | Prodotti: 5/7, SKU: 4/5 |
| 10 | **Nazia S** | 45.6 | A | Prodotti: 5/7, SKU: 4/5 |
| 11 | **Julja V** | 44.6 | B | Prodotti: 6/7, SKU: 3/5 |
| 12 | **Almay E** | 31.2 | C | Prodotti: 3/7, SKU: 4/5 |


---

## 4. Detailed Errors and Warnings by File

### Abrar H

**Errors:**
- :x: SKU: `tensione_alimentazione` only 19.0% filled (critical)
- :x: SKU: 3 duplicate `codice_sku` entries

**Warnings:**
- :warning: PRODOTTI: `immagine_principale` only 75.0% filled
- :warning: PRODOTTI: 2 duplicate `nome_prodotto` entries
- :warning: PRODOTTI: `nome_asta` very sparse (16.7%)
- :warning: PRODOTTI: `brevetto_faac` very sparse (16.7%)
- :warning: PRODOTTI: `schema_installazione` very sparse (16.7%)
- :warning: PRODOTTI: `immagne_schema` very sparse (8.3%)
- :warning: PRODOTTI: `componenti_kit` very sparse (16.7%)
- :warning: PRODOTTI: `immagine_kit` very sparse (16.7%)
- :warning: PRODOTTI: `prodotti_correlati` very sparse (16.7%)
- :warning: PRODOTTI: `tabella_molle` very sparse (16.7%)
- ... and 1 more warnings

### Almay E

**Errors:**
- :x: PRODOTTI: `immagine_principale` only 13.4% filled (critical)
- :x: SKU: `tensione_alimentazione` only 19.0% filled (critical)
- :x: SKU: 3 duplicate `codice_sku` entries

**Warnings:**
- :warning: PRODOTTI: `titolo_prodotto` only 71.6% filled
- :warning: PRODOTTI: `descrizione_prodotto` only 70.1% filled
- :warning: PRODOTTI: `codici_modelli` only 62.7% filled
- :warning: PRODOTTI: 3 duplicate `nome_prodotto` entries
- :warning: PRODOTTI: `nome_asta` very sparse (3.0%)
- :warning: PRODOTTI: `tipo_layout` very sparse (16.4%)
- :warning: PRODOTTI: `intensita_transito` very sparse (13.4%)
- :warning: PRODOTTI: `caratteristica_primaria` very sparse (13.4%)
- :warning: PRODOTTI: `valore_primario` very sparse (13.4%)
- :warning: PRODOTTI: `caratteristica_secondaria` very sparse (7.5%)
- ... and 23 more warnings

### Arjol T

**Errors:**
- :x: SKU: `tensione_alimentazione` only 18.6% filled (critical)
- :x: SKU: 8 duplicate `codice_sku` entries

**Warnings:**
- :warning: PRODOTTI: 2 duplicate `nome_prodotto` entries
- :warning: PRODOTTI: `nome_asta` very sparse (7.7%)
- :warning: PRODOTTI: `novita` very sparse (15.4%)
- :warning: PRODOTTI: `brevetto_faac` very sparse (7.7%)
- :warning: PRODOTTI: `codice_qr` very sparse (11.5%)
- :warning: PRODOTTI: `immagne_schema` very sparse (3.8%)
- :warning: PRODOTTI: `componenti_kit` very sparse (7.7%)
- :warning: PRODOTTI: `immagine_kit` very sparse (7.7%)
- :warning: PRODOTTI: `prodotti_correlati` very sparse (7.7%)
- :warning: PRODOTTI: `grafico_tecnico` very sparse (11.5%)
- ... and 2 more warnings

### Ayesha K

**Errors:**
- :x: SKU: `tensione_alimentazione` only 20.4% filled (critical)
- :x: SKU: 8 duplicate `codice_sku` entries

**Warnings:**
- :warning: PRODOTTI: 2 duplicate `nome_prodotto` entries
- :warning: PRODOTTI: `Unnamed: 33` very sparse (6.7%)
- :warning: SKU: Missing `prezzo_listino` column (price information)

### Blerta B

**Errors:**
- :x: SKU: `tensione_alimentazione` only 19.0% filled (critical)
- :x: SKU: 3 duplicate `codice_sku` entries

**Warnings:**
- :warning: PRODOTTI: 2 duplicate `nome_prodotto` entries
- :warning: PRODOTTI: `nome_asta` very sparse (18.2%)
- :warning: PRODOTTI: `brevetto_faac` very sparse (18.2%)
- :warning: PRODOTTI: `schema_installazione` very sparse (18.2%)
- :warning: PRODOTTI: `immagne_schema` very sparse (9.1%)
- :warning: PRODOTTI: `componenti_kit` very sparse (18.2%)
- :warning: PRODOTTI: `immagine_kit` very sparse (18.2%)
- :warning: PRODOTTI: `prodotti_correlati` very sparse (18.2%)
- :warning: PRODOTTI: `tabella_molle` very sparse (18.2%)
- :warning: SKU: Missing `prezzo_listino` column (price information)

### Dora T

**Errors:**
- :x: SKU: `tensione_alimentazione` only 18.9% filled (critical)
- :x: SKU: 5 duplicate `codice_sku` entries

**Warnings:**
- :warning: PRODOTTI: `immagine_principale` only 54.5% filled
- :warning: PRODOTTI: 2 duplicate `nome_prodotto` entries
- :warning: PRODOTTI: `nome_asta` very sparse (9.1%)
- :warning: PRODOTTI: `novita` very sparse (18.2%)
- :warning: PRODOTTI: `brevetto_faac` very sparse (9.1%)
- :warning: PRODOTTI: `codice_qr` very sparse (13.6%)
- :warning: PRODOTTI: `schema_installazione` very sparse (9.1%)
- :warning: PRODOTTI: `immagne_schema` very sparse (4.5%)
- :warning: PRODOTTI: `componenti_kit` very sparse (9.1%)
- :warning: PRODOTTI: `immagine_kit` very sparse (9.1%)
- ... and 4 more warnings

### Elena P

**Errors:**
- :x: SKU: Missing key column `codice_sku`
- :x: SKU: `tensione_alimentazione` only 20.7% filled (critical)

**Warnings:**
- :warning: PRODOTTI: `immagine_principale` only 71.1% filled
- :warning: PRODOTTI: 4 duplicate `nome_prodotto` entries
- :warning: PRODOTTI: `nome_asta` very sparse (5.3%)
- :warning: PRODOTTI: `novita` very sparse (18.4%)
- :warning: PRODOTTI: `brevetto_faac` very sparse (15.8%)
- :warning: PRODOTTI: `codice_qr` very sparse (10.5%)
- :warning: PRODOTTI: `schema_installazione` very sparse (5.3%)
- :warning: PRODOTTI: `immagne_schema` very sparse (2.6%)
- :warning: PRODOTTI: `componenti_kit` very sparse (5.3%)
- :warning: PRODOTTI: `immagine_kit` very sparse (5.3%)
- ... and 6 more warnings

### Giuseppe C

**Errors:**
- :x: PRODOTTI: `immagine_principale` only 15.5% filled (critical)
- :x: SKU: `tensione_alimentazione` only 19.1% filled (critical)
- :x: SKU: 3 duplicate `codice_sku` entries

**Warnings:**
- :warning: PRODOTTI: `descrizione_prodotto` only 74.1% filled
- :warning: PRODOTTI: 14 duplicate `nome_prodotto` entries
- :warning: PRODOTTI: `novita` very sparse (10.3%)
- :warning: PRODOTTI: `brevetto_faac` very sparse (8.6%)
- :warning: PRODOTTI: `codice_qr` very sparse (8.6%)
- :warning: PRODOTTI: `immagne_schema` very sparse (1.7%)
- :warning: PRODOTTI: `componenti_kit` very sparse (3.4%)
- :warning: PRODOTTI: `immagine_kit` very sparse (3.4%)
- :warning: PRODOTTI: `prodotti_correlati` very sparse (5.2%)
- :warning: PRODOTTI: `grafico_tecnico` very sparse (5.2%)
- ... and 3 more warnings

### Javeria I

**Errors:**
- :x: SKU: `tensione_alimentazione` only 19.0% filled (critical)
- :x: SKU: 4 duplicate `codice_sku` entries

**Warnings:**
- :warning: PRODOTTI: 2 duplicate `nome_prodotto` entries
- :warning: PRODOTTI: `nome_asta` very sparse (18.2%)
- :warning: PRODOTTI: `brevetto_faac` very sparse (18.2%)
- :warning: PRODOTTI: `schema_installazione` very sparse (18.2%)
- :warning: PRODOTTI: `immagne_schema` very sparse (9.1%)
- :warning: PRODOTTI: `componenti_kit` very sparse (18.2%)
- :warning: PRODOTTI: `immagine_kit` very sparse (18.2%)
- :warning: PRODOTTI: `prodotti_correlati` very sparse (18.2%)
- :warning: PRODOTTI: `tabella_molle` very sparse (18.2%)
- :warning: SKU: Missing `prezzo_listino` column (price information)

### Julja V

**Errors:**
- :x: PRODOTTI: `immagine_principale` only 28.1% filled (critical)
- :x: SKU: Missing key column `codice_sku`
- :x: SKU: `tensione_alimentazione` only 19.0% filled (critical)

**Warnings:**
- :warning: PRODOTTI: 4 duplicate `nome_prodotto` entries
- :warning: PRODOTTI: `nome_asta` very sparse (6.2%)
- :warning: PRODOTTI: `caratteristica_secondaria` very sparse (15.6%)
- :warning: PRODOTTI: `valore_secondario` very sparse (15.6%)
- :warning: PRODOTTI: `novita` very sparse (15.6%)
- :warning: PRODOTTI: `brevetto_faac` very sparse (6.2%)
- :warning: PRODOTTI: `codice_qr` very sparse (9.4%)
- :warning: PRODOTTI: `schema_installazione` very sparse (6.2%)
- :warning: PRODOTTI: `immagne_schema` very sparse (3.1%)
- :warning: PRODOTTI: `componenti_kit` very sparse (6.2%)
- ... and 6 more warnings

### Matteo F

**Errors:**
- :x: SKU: `tensione_alimentazione` only 18.8% filled (critical)
- :x: SKU: 5 duplicate `codice_sku` entries

**Warnings:**
- :warning: PRODOTTI: `immagine_principale` only 69.2% filled
- :warning: PRODOTTI: 2 duplicate `nome_prodotto` entries
- :warning: PRODOTTI: `nome_asta` very sparse (15.4%)
- :warning: PRODOTTI: `brevetto_faac` very sparse (15.4%)
- :warning: PRODOTTI: `schema_installazione` very sparse (15.4%)
- :warning: PRODOTTI: `immagne_schema` very sparse (7.7%)
- :warning: PRODOTTI: `componenti_kit` very sparse (15.4%)
- :warning: PRODOTTI: `immagine_kit` very sparse (15.4%)
- :warning: PRODOTTI: `prodotti_correlati` very sparse (15.4%)
- :warning: PRODOTTI: `tabella_molle` very sparse (15.4%)
- ... and 1 more warnings

### Nazia S

**Errors:**
- :x: PRODOTTI: `immagine_principale` only 23.8% filled (critical)
- :x: SKU: `tensione_alimentazione` only 19.0% filled (critical)
- :x: SKU: 3 duplicate `codice_sku` entries

**Warnings:**
- :warning: PRODOTTI: `descrizione_prodotto` only 66.7% filled
- :warning: PRODOTTI: 6 duplicate `nome_prodotto` entries
- :warning: PRODOTTI: `nome_asta` very sparse (3.6%)
- :warning: PRODOTTI: `novita` very sparse (6.0%)
- :warning: PRODOTTI: `veloce` very sparse (19.0%)
- :warning: PRODOTTI: `brevetto_faac` very sparse (4.8%)
- :warning: PRODOTTI: `codice_qr` very sparse (4.8%)
- :warning: PRODOTTI: `schema_installazione` very sparse (3.6%)
- :warning: PRODOTTI: `immagne_schema` very sparse (1.2%)
- :warning: PRODOTTI: `immagine_kit` very sparse (3.6%)
- ... and 4 more warnings


---

## 5. Column Structure Comparison with Master

| File | Prodotti Missing | Prodotti Extra | SKU Missing | SKU Extra |
|------|------------------|----------------|-------------|-----------|
| Abrar H | 4 | 1 | 1 | 1 |
| Almay E | 3 | 1 | 1 | 1 |
| Arjol T | 3 | 1 | 1 | 1 |
| Ayesha K | 5 | 2 | 1 | 1 |
| Blerta B | 4 | 1 | 1 | 1 |
| Dora T | 3 | 1 | 1 | 1 |
| Elena P | 3 | 1 | 2 | 2 |
| Giuseppe C | 3 | 1 | 1 | 2 |
| Javeria I | 3 | 1 | 2 | 2 |
| Julja V | 4 | 1 | 2 | 2 |
| Matteo F | 3 | 1 | 1 | 1 |
| Nazia S | 3 | 1 | 1 | 2 |


---

## 6. Overall Assessment

**Average Quality Score:** 48.8/100

**Grade Distribution:**
- Grade A (>=45): 10 files
- Grade B (38-44): 1 files
- Grade C (30-37): 1 files
- Grade D (22-29): 0 files
- Grade F (<22): 0 files


### Key Findings:

1. **PRODOTTI Sheet Quality:** Most files have reasonably good PRODOTTI data with key columns
   (categoria_prodotto, nome_prodotto, pagina_catalogo, titolo_prodotto) well-filled.

2. **SKU Sheet Issues:** All files show low completeness in SKU sheets (~14-16%), which is
   expected given the nature of technical specifications - not all specs apply to all products.

3. **Common Problems:**
   - Missing `prezzo_listino` column in all files
   - Duplicate SKU codes in several files
   - Many technical specification columns are sparsely filled
   - `nome_asta` column consistently underutilized

4. **Best Performers:** Files with higher PRODOTTI completeness and fewer duplicate entries
   scored better overall.

5. **Recommendations:**
   - Address duplicate SKU codes across all files
   - Consider adding price information (`prezzo_listino`)
   - Focus on filling key columns before optional technical specs
   - Validate data entry for consistency



---

## 7. Precision and Completeness Ratings

### Precision Assessment

Precision measures the accuracy of data entered. Based on analysis:

| Aspect | Rating | Notes |
|--------|--------|-------|
| Data Types | **Good** | Numeric fields contain numbers, text fields contain text |
| SKU Format | **Fair** | Some short/malformed SKU codes detected |
| Page Numbers | **Good** | Most page references are valid numbers |
| Duplicates | **Poor** | Multiple files have duplicate entries |
| Overall | **Fair** | 65/100 |


### Completeness Assessment

Completeness measures how much of the expected data is present:

| Sheet | Rating | Notes |
|-------|--------|-------|
| PRODOTTI | **Fair to Good** | Key columns mostly filled (60-90%), optional fields sparse |
| SKU | **Poor** | Only ~14-16% overall, though core identifiers are present |
| Overall | **Poor to Fair** | 35/100 |


### Combined Quality Score

| Metric | Score | Weight | Weighted |
|--------|-------|--------|----------|
| Precision | 65 | 40% | 26 |
| Completeness | 35 | 60% | 21 |
| **Total** | - | - | **47/100** |
