# 844 3PH - Motoriduttore 400V Error Analysis Report

## Summary
Analysis of product "844 3PH - Motoriduttore 400V" (pages 126-127) identified TWO types of errors.

---

## Error 1: Incomplete contenuto_confezione

### Description
The product "844 3PH" has TWO model variants:
- **844 C 3PH** (SKU: 109928) - Price: €2,014.00
- **844 R 3PH** (SKU: 109904) - Price: €1,310.00

However, the `contenuto_confezione` field only describes what's included with ONE model:

> "844 C 3PH comprende: un motoriduttore predisposto per applicazione a cremagliera 
> senza pignone e con scheda elettronica E844 3PH, lamierini finecorsa per 
> assemblaggio meccanico, chiave di sblocco, carter copriviti."

**Missing**: Description for what's included with the 844 R 3PH model.

### Source
- IDML file: `/input/processing/IDML_unzipped/126-127_844_3PH/Stories/Story_u12d5.xml`
- The IDML file itself only contains the 844 C 3PH description (not an extraction error)

---

## Error 2: Missing Accessory Information

### Description
The IDML contains accessory information for the 844 R 3PH model that is NOT captured in the data:

> "Pignone Z12 cremagliera (cancello peso max 2.200 Kg) per 844 R 3PH"

This important information about compatible accessories is missing from the `accessori_disponibili` column (which is empty for this product).

### Source
- IDML file: `/input/processing/IDML_unzipped/126-127_844_3PH/Stories/Story_u179a.xml`

---

## Similar Errors Found in Other Products

### Products with Potentially Incomplete contenuto_confezione:

| Product | Models | Issue |
|---------|--------|-------|
| 844 3PH | 109928; 109904 | contenuto mentions "844 C 3PH" but product has 2 models |
| 580 - 593 | 104501; 104502; 110597 | contenuto mentions "580" but product is "580 - 593" |
| S800 ENC | 108800-108803 | Generic description, no specific model references |

---

## Comparison with 844 C (230V version)

The 230V version "844 C" (pages 124-125) has a similar pattern:
- Models: **844 C Z16** (109925) and **844** (109926)
- contenuto: "844 C Z16 , predisposta per applicazioni a cremagliera, comprende..."

This also only describes ONE model (844 C Z16), missing the plain "844" model description.

---

## Recommendations

1. **For 844 3PH**: Add contenuto_confezione description for 844 R 3PH model
2. **For 844 3PH**: Add accessory information to accessori_disponibili column
3. **For 844 C**: Add contenuto_confezione description for plain "844" model
4. **General**: Review all products with multiple SKUs to ensure complete descriptions

---

## Files Analyzed
- `/home/user/checkimport/output/v2/Data_Elena_P_KIT_v4.xlsx`
- `/home/user/checkimport/input/processing/Data Elena P.xlsx`
- `/home/user/checkimport/input/processing/IDML_unzipped/126-127_844_3PH/`
- `/home/user/checkimport/output/v2/FAAC_Complete_v2_Modello_Codice_Pagina_TEST.csv`

Generated: 2025-12-17
