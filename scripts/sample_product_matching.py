#!/usr/bin/env python3
"""
Sample script to demonstrate product name matching logic.
Analyzes pages 202-203 and 034 to show how to match SKUs to products.
"""
import re
from pathlib import Path
from difflib import SequenceMatcher

IDML_DIR = Path('/home/user/checkimport/input/processing/IDML_unzipped')


def extract_product_names(folder_path):
    """Extract Product_Name values from IDML stories."""
    stories_dir = folder_path / 'Stories'
    product_names = []

    for f in stories_dir.glob('*.xml'):
        content = f.read_text()
        if 'Product_Name' in content:
            matches = re.findall(r'Product_Name[^>]*>.*?<Content>([^<]+)</Content>', content, re.DOTALL)
            product_names.extend(matches)

    return list(set(product_names))


def similarity(a, b):
    """Calculate text similarity ratio."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def extract_key_identifiers(text):
    """Extract key identifiers like voltage (230V, 24V), model codes."""
    text_lower = text.lower()
    identifiers = set()

    # Extract voltage patterns
    voltages = re.findall(r'\d+v', text_lower)
    identifiers.update(voltages)

    # Extract model numbers
    models = re.findall(r'\b[a-z]?\d{3,}\b', text_lower)
    identifiers.update(models)

    return identifiers


def match_sku_to_product(sku_description, product_names):
    """Match SKU description to best product name using key identifiers."""
    if len(product_names) == 1:
        return product_names[0], 1.0

    sku_identifiers = extract_key_identifiers(sku_description)
    best_match = None
    best_score = 0

    for product in product_names:
        product_identifiers = extract_key_identifiers(product)

        # Check for matching key identifiers (voltage, model numbers)
        common_ids = sku_identifiers & product_identifiers
        if common_ids:
            # Bonus score for matching identifiers
            id_score = len(common_ids) / max(len(sku_identifiers), len(product_identifiers), 1)
        else:
            id_score = 0

        # Base similarity score
        text_score = similarity(sku_description, product)

        # Combined score: prioritize identifier matches
        score = (id_score * 0.7) + (text_score * 0.3)

        if score > best_score:
            best_score = score
            best_match = product

    return best_match, best_score


def analyze_page(folder_name, skus):
    """Analyze a page and match SKUs to products."""
    folder_path = IDML_DIR / folder_name
    product_names = extract_product_names(folder_path)

    print(f"\n{'='*60}")
    print(f"FOLDER: {folder_name}")
    print(f"PRODUCT NAMES FOUND: {product_names}")
    print(f"{'='*60}")

    results = []
    for sku_desc, sku_code in skus:
        matched_product, score = match_sku_to_product(sku_desc, product_names)
        results.append({
            'sku_description': sku_desc,
            'sku_code': sku_code,
            'matched_product': matched_product,
            'confidence': score
        })

        confidence_label = "HIGH" if score > 0.5 else "LOW" if score > 0.3 else "GUESS"
        print(f"\n  SKU: {sku_desc}")
        print(f"  Code: {sku_code}")
        print(f"  → Matched: '{matched_product}' [{confidence_label}: {score:.2f}]")

    return results


# ============================================================
# SAMPLE 1: Page 202-203 (Single product)
# ============================================================
print("\n" + "="*70)
print("SAMPLE 1: Pages 202-203 (Single Product)")
print("="*70)

skus_202_203 = [
    ("RP FDS 433-868", "787021"),
    ("RP2 FDS 433-868", "787022"),
    ("XF FDS 433-868", "787025"),
    ("XR2N 433-868", "787023"),
    ("XR4N 433-868", "787024"),
]

results_202 = analyze_page("202-203_Sistema_433-868MHz_FDS_BD", skus_202_203)


# ============================================================
# SAMPLE 2: Page 034 (Multi-product)
# ============================================================
print("\n" + "="*70)
print("SAMPLE 2: Page 034 (Multi-Product - POWER kit 230V & 24V)")
print("="*70)

skus_034 = [
    ("POWER 230V kit PERFECT 60", "120017"),
    ("POWER 24V kit PERFECT 60", "120018"),
    ("Gruppo encoder per 770N (confezione singola - 2 confezioni per 2 ante)", "404035"),
    ("Cassetta portante con sistema di sblocco", "490065"),
]

results_034 = analyze_page("034_POWER_kit_230V_PERFECT_60", skus_034)


# ============================================================
# OUTPUT SAMPLE CSV FORMAT
# ============================================================
print("\n" + "="*70)
print("PROPOSED CSV OUTPUT FORMAT")
print("="*70)
print("\nModello;Codice_articolo;page_start;page_end;Product_Name;Confidence")

for r in results_202:
    print(f"{r['sku_description']};{r['sku_code']};202;203;{r['matched_product']};{r['confidence']:.2f}")

for r in results_034:
    print(f"{r['sku_description']};{r['sku_code']};034;034;{r['matched_product']};{r['confidence']:.2f}")
