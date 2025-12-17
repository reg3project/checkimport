#!/usr/bin/env python3
"""
Create product CSV with columns:
- categoria_prodotto
- nome_prodotto
- titolo_prodotto
- tipo_layout (only: "kit special", "automazione", "accessori", "barriera", "asta")
- descrizione_categoria
- codici_modelli (lista sku)
- prodotti_correlati (lista nome_prodotto)

Data sources:
- FAAC_Lista_Attivita_annotato.xlsx - Data Entry.csv (categories, products, pages, SKUs)
- Model_Codes_Master.csv (SKUs, prices)
- FAAC_Complete_v2_Modello_Codice_Pagina_QuiteGood.csv (cross-reference)
- barriere_skus.csv (barrier-specific data)
"""

import csv
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional

# Paths
BASE_DIR = Path("/home/user/checkimport")
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
LEARNING_DIR = INPUT_DIR / "learning"

# Category to tipo_layout mapping
TIPO_LAYOUT_MAPPING = {
    # Kit categories -> "kit special"
    "PERFECT KIT": "kit special",
    "CLASSIC KIT": "kit special",
    "TM2K KIT MINI": "kit special",
    "N2D kit": "kit special",
    "K3 kit": "kit special",

    # Automazione categories
    "Automazioni per ante a battente esterno": "automazione",
    "Automazioni per ante a battente con motore interrato": "automazione",
    "Automazioni per cancelli scorrevoli": "automazione",
    "Automazioni per porte sezionali": "automazione",
    "Automazioni per porte basculanti": "automazione",
    "Automazioni per porte a libro": "automazione",
    "Automazioni per serrande avvolgibili": "automazione",

    # Barriere -> "barriera"
    "Barriere automatiche": "barriera",

    # Accessori
    "Accessori per automazioni": "accessori",
    "Apparecchiature elettroniche di comando": "accessori",
}

# Category descriptions (Italian)
DESCRIZIONE_CATEGORIA = {
    "PERFECT KIT": "Kit di automazione serie PERFECT 60",
    "CLASSIC KIT": "Kit di automazione classici",
    "TM2K KIT MINI": "Kit motori tubolari TM2K",
    "N2D kit": "Kit N2D",
    "K3 kit": "Kit K3",
    "Automazioni per ante a battente esterno": "Operatori per cancelli a battente montaggio esterno",
    "Automazioni per ante a battente con motore interrato": "Operatori per cancelli a battente con motore interrato",
    "Automazioni per cancelli scorrevoli": "Operatori per cancelli scorrevoli",
    "Automazioni per porte sezionali": "Operatori per porte sezionali",
    "Automazioni per porte basculanti": "Operatori per porte basculanti",
    "Automazioni per porte a libro": "Operatori per porte a libro",
    "Automazioni per serrande avvolgibili": "Operatori per serrande avvolgibili",
    "Barriere automatiche": "Barriere automatiche per controllo accessi",
    "Accessori per automazioni": "Accessori per sistemi di automazione",
    "Apparecchiature elettroniche di comando": "Apparecchiature elettroniche e schede di controllo",
}


def load_data_entry_csv() -> List[Dict]:
    """Load the main Data Entry CSV with categories, products, and SKUs"""
    csv_path = LEARNING_DIR / "FAAC_Lista_Attivita_annotato.xlsx - Data Entry.csv"
    rows = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip rows marked for deletion
            note = row.get('Note_Antonella', '').strip()
            if 'ELIMINAR' in note.upper():
                continue

            # Skip "Schemi di installazione" category
            categoria = row.get('Categoria', '').strip()
            if 'Schemi' in categoria:
                continue

            rows.append(row)

    return rows


def load_model_codes_master() -> Dict[str, Dict]:
    """Load Model_Codes_Master.csv for SKU/price data, keyed by (page, product_name)"""
    csv_path = OUTPUT_DIR / "Model_Codes_Master.csv"
    data = defaultdict(list)

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            page = row.get('page', '').strip()
            product = row.get('product_name', '').strip()
            model_sku = row.get('model_sku', '').strip()
            model_name = row.get('model_name', '').strip()
            price = row.get('price', '').strip()

            if page and product and model_sku:
                key = (page, product)
                data[key].append({
                    'sku': model_sku,
                    'model_name': model_name,
                    'price': price
                })

    return data


def load_quite_good_csv() -> Tuple[Dict[str, List[Dict]], Dict[str, List[str]]]:
    """Load FAAC_Complete_v2_Modello_Codice_Pagina_QuiteGood.csv for cross-reference

    Returns:
        Tuple of (product_data, page_to_models)
        - product_data: keyed by product_name, list of models with SKU
        - page_to_models: keyed by page, list of model names on that page
    """
    csv_path = LEARNING_DIR / "FAAC_Complete_v2_Modello_Codice_Pagina_QuiteGood.csv"
    data = defaultdict(list)
    page_models = defaultdict(list)

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            product_name = row.get('Product_Name', '').strip()
            modello = row.get('Modello', '').strip()
            codice = row.get('Codice_articolo', '').strip()
            page_start = row.get('page_start', '').strip()
            confidence = row.get('Confidence', '0')

            if product_name and codice:
                data[product_name].append({
                    'modello': modello,
                    'codice': codice,
                    'page': page_start,
                    'confidence': float(confidence) if confidence else 0
                })

            # Build page to model name mapping
            if page_start and modello:
                if modello not in page_models[page_start]:
                    page_models[page_start].append(modello)

    return data, page_models


def load_barriere_skus() -> Dict[str, Dict]:
    """Load barriere_skus.csv for barrier and arm data

    Handles various SKU types:
    - 'Barrier': Main barrier unit
    - 'Barrier Config', 'Barrier Config DX', 'Barrier Config SX': Configuration SKUs
    - 'Arm': Barrier arms (aste)
    """
    csv_path = OUTPUT_DIR / "barriere_skus.csv"
    data = defaultdict(lambda: {'barrier_skus': [], 'arm_skus': []})

    if not csv_path.exists():
        return data

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            product = row.get('Product', '').strip()
            sku_type = row.get('SKU_Type', '').strip()
            sku = row.get('Codice_SKU', '').strip()

            if product and sku:
                # Barrier types include main barrier and configurations
                if sku_type.startswith('Barrier'):
                    if sku not in data[product]['barrier_skus']:
                        data[product]['barrier_skus'].append(sku)
                elif sku_type == 'Arm':
                    if sku not in data[product]['arm_skus']:
                        data[product]['arm_skus'].append(sku)

    return data


def parse_skus_from_string(skus_str: str) -> List[str]:
    """Parse SKUs from semicolon-separated string, preserving order"""
    if not skus_str:
        return []

    skus = []
    for sku in skus_str.split(';'):
        sku = sku.strip()
        if sku and sku not in skus:
            skus.append(sku)
    return skus


def get_tipo_layout(categoria: str, product_name: str = '') -> str:
    """Determine tipo_layout based on category and product name"""
    # Direct category mapping
    if categoria in TIPO_LAYOUT_MAPPING:
        return TIPO_LAYOUT_MAPPING[categoria]

    # Check if it's a kit product
    if 'kit' in categoria.lower() or 'kit' in product_name.lower():
        return "kit special"

    # Check for automazione keywords
    if 'Automazioni' in categoria or 'automazioni' in categoria:
        return "automazione"

    # Check for barriers
    if 'Barriere' in categoria or 'barriera' in categoria.lower():
        return "barriera"

    # Default to accessori for remaining products
    return "accessori"


def get_descrizione_categoria(categoria: str) -> str:
    """Get category description"""
    return DESCRIZIONE_CATEGORIA.get(categoria, categoria)


def build_page_to_products_map(data_entry_rows: List[Dict]) -> Dict[int, List[str]]:
    """Build mapping of pages to product names for prodotti_correlati"""
    page_products = defaultdict(list)

    for row in data_entry_rows:
        prodotto = row.get('Prodotto', '').strip()
        if not prodotto:
            continue

        try:
            page_start = int(row.get('Pagina', 0))
            page_end = int(row.get('Pagina_fine', page_start) or page_start)
        except ValueError:
            continue

        for page in range(page_start, page_end + 1):
            if prodotto not in page_products[page]:
                page_products[page].append(prodotto)

    return page_products


def find_related_products_from_models(product_name: str, page_start: int, page_end: int,
                                      page_models: Dict[str, List[str]],
                                      quite_good_data: Dict[str, List[Dict]],
                                      main_product_skus: Set[str]) -> List[str]:
    """Find related product model names on the same pages

    For accessory pages like XTO, related products are the receivers/interface modules
    that are listed on the same page but are not the main transmitter models.

    Returns list of model names (not product names), e.g., ['XF 868 MHz', 'RP 868 SLH-DS']
    """
    related = []

    # Get models from QuiteGood data for this product
    product_data = quite_good_data.get(product_name, [])

    # Also try stripped product name (e.g., "XTO" from "XTO - Sistema 868MHz SLH-DS")
    short_name = product_name.split(' - ')[0].strip() if ' - ' in product_name else product_name
    if short_name != product_name:
        product_data.extend(quite_good_data.get(short_name, []))

    # Collect model names that are NOT in main_product_skus
    for item in product_data:
        modello = item.get('modello', '').strip()
        codice = item.get('codice', '').strip()

        if modello and codice and codice not in main_product_skus:
            # This is a related product (receiver, interface, etc.)
            if modello not in related:
                related.append(modello)

    return related


def get_main_product_skus(product_name: str, page_start: int, page_end: int,
                          model_codes: Dict, quite_good_data: Dict) -> List[str]:
    """Get the main product SKUs (the first few rows in the price table)

    For most products, this is all SKUs. For accessory pages with multiple
    product types (transmitters + receivers), this should be just the main
    product SKUs (e.g., XTO transmitters, not receivers).

    For radio/accessory products, we take the first 2 SKUs as the "main" product,
    since these are typically the transmitter models.
    """
    main_skus = []

    # Try to get from Model Codes Master - first entries are typically main product
    for page in range(page_start, page_end + 1):
        key = (str(page), product_name)
        if key in model_codes:
            items = model_codes[key]
            # Take first 2 items as main SKUs for accessory products
            # These are typically the transmitter/main product models
            for item in items[:2]:
                sku = item.get('sku', '')
                if sku and sku not in main_skus:
                    main_skus.append(sku)
            break

    # Also try short name (e.g., "XTO" from "XTO - Sistema...")
    short_name = product_name.split(' - ')[0].strip() if ' - ' in product_name else None
    if short_name and not main_skus:
        for page in range(page_start, page_end + 1):
            key = (str(page), short_name)
            if key in model_codes:
                items = model_codes[key]
                for item in items[:2]:
                    sku = item.get('sku', '')
                    if sku and sku not in main_skus:
                        main_skus.append(sku)
                break

    return main_skus


def find_related_products(product_name: str, page_start: int, page_end: int,
                         page_products: Dict[int, List[str]],
                         quite_good_data: Dict[str, List[Dict]]) -> List[str]:
    """Find related products on the same pages (legacy function for compatibility)"""
    related = set()

    # Get products from page mapping
    for page in range(page_start, page_end + 1):
        for other_product in page_products.get(page, []):
            if other_product != product_name:
                related.add(other_product)

    return sorted(list(related))


def create_product_rows() -> List[Dict]:
    """Create product rows for the CSV"""
    # Load all data sources
    print("Loading data sources...")
    data_entry_rows = load_data_entry_csv()
    model_codes = load_model_codes_master()
    quite_good_data, page_models = load_quite_good_csv()
    barriere_data = load_barriere_skus()

    print(f"  - Data Entry: {len(data_entry_rows)} rows")
    print(f"  - Model Codes: {len(model_codes)} product/page combinations")
    print(f"  - QuiteGood: {len(quite_good_data)} products")
    print(f"  - Page Models: {len(page_models)} pages with model names")
    print(f"  - Barriere: {len(barriere_data)} barrier products")

    # Build page to products mapping for prodotti_correlati
    page_products = build_page_to_products_map(data_entry_rows)

    products = []
    seen_products = set()

    current_categoria = ""

    for row in data_entry_rows:
        # Update current category
        categoria = row.get('Categoria', '').strip()
        if categoria:
            current_categoria = categoria

        prodotto = row.get('Prodotto', '').strip()
        if not prodotto:
            continue

        # Skip duplicates
        product_key = (current_categoria, prodotto)
        if product_key in seen_products:
            continue
        seen_products.add(product_key)

        # Parse page range
        try:
            page_start = int(row.get('Pagina', 0))
            page_end = int(row.get('Pagina_fine', page_start) or page_start)
        except ValueError:
            page_start = page_end = 0

        # Get SKUs from Data Entry
        skus_str = row.get('SKU_presenti_nel_prodotto', '')
        skus = parse_skus_from_string(skus_str)

        # Get tipo_layout
        tipo_layout = get_tipo_layout(current_categoria, prodotto)

        # Get descrizione_categoria
        descrizione = get_descrizione_categoria(current_categoria)

        # For accessory products, find related models and main SKUs
        related_models = []
        main_skus = skus  # Default: use all SKUs

        if tipo_layout == "accessori":
            # For accessory products (radio systems, sensors, etc.),
            # identify main product SKUs and related product model names
            main_skus = get_main_product_skus(prodotto, page_start, page_end,
                                              model_codes, quite_good_data)

            # If we found main SKUs, use them; otherwise fall back to all SKUs
            if main_skus:
                main_skus_set = set(main_skus)
                related_models = find_related_products_from_models(
                    prodotto, page_start, page_end, page_models,
                    quite_good_data, main_skus_set
                )
            else:
                main_skus = skus

        elif tipo_layout == "barriera":
            # For barriers, separate barrier SKUs from arm SKUs
            if prodotto in barriere_data:
                barrier_skus = barriere_data[prodotto]['barrier_skus']
                if barrier_skus:
                    main_skus = barrier_skus

        else:
            # For other products (automazione, kit), use all SKUs
            main_skus = skus

        # Find related products (other products on same pages)
        related_products = find_related_products(prodotto, page_start, page_end,
                                                 page_products, quite_good_data)

        # Combine related models and related products
        all_related = []
        if related_models:
            all_related.extend(related_models)
        if related_products:
            for rp in related_products:
                if rp not in all_related:
                    all_related.append(rp)

        # Create product row
        product_row = {
            'categoria_prodotto': current_categoria,
            'nome_prodotto': prodotto,
            'titolo_prodotto': prodotto,  # Same as nome_prodotto for now
            'tipo_layout': tipo_layout,
            'descrizione_categoria': descrizione,
            'codici_modelli': ';'.join(main_skus) if main_skus else '',
            'prodotti_correlati': ';'.join(all_related) if all_related else ''
        }

        products.append(product_row)

        # For barriers, also create "asta" entries if they have arm SKUs
        if tipo_layout == "barriera" and prodotto in barriere_data:
            arm_skus = barriere_data[prodotto]['arm_skus']
            if arm_skus:
                asta_row = {
                    'categoria_prodotto': current_categoria,
                    'nome_prodotto': f"Aste {prodotto}",
                    'titolo_prodotto': f"Aste per barriera {prodotto}",
                    'tipo_layout': "asta",
                    'descrizione_categoria': f"Aste per barriera {prodotto}",
                    'codici_modelli': ';'.join(arm_skus),
                    'prodotti_correlati': prodotto
                }
                products.append(asta_row)

    return products


def write_csv(products: List[Dict], output_path: Path):
    """Write products to CSV file"""
    fieldnames = [
        'categoria_prodotto',
        'nome_prodotto',
        'titolo_prodotto',
        'tipo_layout',
        'descrizione_categoria',
        'codici_modelli',
        'prodotti_correlati'
    ]

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(products)

    print(f"\nWrote {len(products)} products to {output_path}")


def create_materials_report(output_path: Path, products: List[Dict]):
    """Create a comprehensive report of all materials used and data quality"""
    from datetime import datetime

    report = []
    report.append("=" * 80)
    report.append("MATERIALS REPORT - Product CSV Generation")
    report.append("=" * 80)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")

    # Summary statistics
    report.append("## SUMMARY")
    report.append("")
    report.append(f"Total products generated: {len(products)}")

    tipo_counts = defaultdict(int)
    cat_counts = defaultdict(int)
    products_with_skus = 0
    products_with_related = 0

    for p in products:
        tipo_counts[p['tipo_layout']] += 1
        cat_counts[p['categoria_prodotto']] += 1
        if p['codici_modelli']:
            products_with_skus += 1
        if p['prodotti_correlati']:
            products_with_related += 1

    report.append(f"Products with SKUs: {products_with_skus}")
    report.append(f"Products with related products: {products_with_related}")
    report.append("")

    report.append("Products by tipo_layout:")
    for tipo, count in sorted(tipo_counts.items()):
        report.append(f"  - {tipo}: {count}")
    report.append("")

    # List all input files used
    report.append("## INPUT FILES USED")
    report.append("")

    input_files = [
        ("Data Entry CSV (primary source)", LEARNING_DIR / "FAAC_Lista_Attivita_annotato.xlsx - Data Entry.csv"),
        ("Model Codes Master (SKU/price reference)", OUTPUT_DIR / "Model_Codes_Master.csv"),
        ("QuiteGood Reference (cross-check)", LEARNING_DIR / "FAAC_Complete_v2_Modello_Codice_Pagina_QuiteGood.csv"),
        ("Barriere SKUs (barrier/arm data)", OUTPUT_DIR / "barriere_skus.csv"),
        ("Tech Spec Master (technical specs)", OUTPUT_DIR / "Tech_Spec_Master_v1.csv"),
        ("SKU Consolidated (detailed attributes)", OUTPUT_DIR / "sku_consolidated.csv"),
    ]

    for name, path in input_files:
        exists = "EXISTS" if path.exists() else "NOT FOUND"
        size = path.stat().st_size if path.exists() else 0
        lines = 0
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                lines = sum(1 for _ in f)
        report.append(f"- {name}")
        report.append(f"  Path: {path}")
        report.append(f"  Status: {exists}, {lines} lines, {size:,} bytes")
        report.append("")

    report.append("## IDML FILES AVAILABLE (Source Documents)")
    report.append("")

    idml_dirs = [
        ("Processing IDML", INPUT_DIR / "processing" / "IDML"),
        ("Learning IDML", INPUT_DIR / "learning" / "IDML"),
    ]

    total_idml = 0
    for dir_name, idml_dir in idml_dirs:
        if idml_dir.exists():
            idml_files = sorted(list(idml_dir.glob("*.idml")))
            total_idml += len(idml_files)
            report.append(f"### {dir_name}: {idml_dir}")
            report.append(f"Total files: {len(idml_files)} IDML files")
            report.append("")

            # Group by category
            kits = [f.name for f in idml_files if 'kit' in f.name.lower()]
            barriers = [f.name for f in idml_files if 'B6' in f.name or '620' in f.name or '615' in f.name]
            motors = [f.name for f in idml_files if any(x in f.name for x in ['S418', 'S450', 'S800', '412', '413', '415', '400', '422', '770', 'C720', 'C721', 'C851'])]
            radio = [f.name for f in idml_files if any(x in f.name for x in ['XTO', 'FDS', 'MHz', 'Sistema'])]
            accessories = [f.name for f in idml_files if any(x in f.name for x in ['Fotocell', 'Costa', 'Sensor', 'Lampeggia', 'Contenitor'])]

            if kits:
                report.append(f"Kit IDMLs: {len(kits)} files")
                for k in kits[:5]:
                    report.append(f"  - {k}")
                if len(kits) > 5:
                    report.append(f"  ... and {len(kits) - 5} more")

            if motors:
                report.append(f"Motor/Operator IDMLs: {len(motors)} files")
                for m in motors[:5]:
                    report.append(f"  - {m}")
                if len(motors) > 5:
                    report.append(f"  ... and {len(motors) - 5} more")

            if barriers:
                report.append(f"Barrier IDMLs: {len(barriers)} files")
                for b in barriers[:5]:
                    report.append(f"  - {b}")
                if len(barriers) > 5:
                    report.append(f"  ... and {len(barriers) - 5} more")

            if radio:
                report.append(f"Radio System IDMLs: {len(radio)} files")
                for r in radio[:5]:
                    report.append(f"  - {r}")
                if len(radio) > 5:
                    report.append(f"  ... and {len(radio) - 5} more")

            report.append("")

    report.append(f"Total IDML files: {total_idml}")
    report.append("")

    report.append("## TIPO_LAYOUT MAPPING RULES")
    report.append("")
    report.append("tipo_layout values (restricted to 5 types):")
    report.append("  - kit special: Kit products (PERFECT KIT, CLASSIC KIT, etc.)")
    report.append("  - automazione: Automation operators (gates, doors, shutters)")
    report.append("  - barriera: Automatic barriers (B614, 615BPR, 620, B680H)")
    report.append("  - asta: Barrier arms/bars (428xxx SKUs)")
    report.append("  - accessori: Accessories, electronics, radio systems")
    report.append("")

    report.append("Category to tipo_layout mapping:")
    for categoria, tipo in sorted(TIPO_LAYOUT_MAPPING.items()):
        report.append(f"  - {categoria} -> {tipo}")
    report.append("")

    report.append("## OUTPUT FILES GENERATED")
    report.append("")
    report.append(f"- Product CSV: {OUTPUT_DIR / 'FAAC_products.csv'}")
    report.append(f"- This report: {output_path}")
    report.append("")

    report.append("## DATA QUALITY NOTES")
    report.append("")
    report.append("1. SKU ordering: SKUs are listed with upper (first in table) going first")
    report.append("2. prodotti_correlati: For accessory products, related products are model names")
    report.append("   found on the same page but not the main product SKUs")
    report.append("3. Barrier products: Main barrier SKUs separated from arm (asta) SKUs")
    report.append("4. Excluded: 'Schemi Installazione' documents were not processed")
    report.append("")

    report.append("## PRODUCTS BY CATEGORY")
    report.append("")
    for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
        report.append(f"  - {cat}: {count} products")
    report.append("")

    report.append("=" * 80)
    report.append("END OF REPORT")
    report.append("=" * 80)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))

    print(f"Wrote materials report to {output_path}")


def main():
    """Main function"""
    print("Creating Product CSV...")
    print("=" * 60)

    # Create product rows
    products = create_product_rows()

    # Write CSV
    output_csv = OUTPUT_DIR / "FAAC_products.csv"
    write_csv(products, output_csv)

    # Create materials report
    report_path = OUTPUT_DIR / "reports" / "product_csv_materials_report.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    create_materials_report(report_path, products)

    # Print summary statistics
    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS")
    print("=" * 60)

    tipo_counts = defaultdict(int)
    cat_counts = defaultdict(int)

    for p in products:
        tipo_counts[p['tipo_layout']] += 1
        cat_counts[p['categoria_prodotto']] += 1

    print("\nProducts by tipo_layout:")
    for tipo, count in sorted(tipo_counts.items()):
        print(f"  {tipo}: {count}")

    print("\nProducts by category:")
    for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

    print("\nDone!")


if __name__ == '__main__':
    main()
