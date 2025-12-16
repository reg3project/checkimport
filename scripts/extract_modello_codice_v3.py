#!/usr/bin/env python3
"""
Extract Modello/Descrizione and Codice articolo from IDML price tables.
Adds Product_Name matching from IDML Product_Name style.
Finds tables with headers containing: Codice articolo | Prezzo €
Excludes Schemi di installazione pages (263-285).
"""
import os
import re
import csv
import xml.etree.ElementTree as ET
from pathlib import Path
from difflib import SequenceMatcher

IDML_DIR = '/home/user/checkimport/input/processing/IDML_unzipped'
OUTPUT_FILE = '/home/user/checkimport/output/v2/FAAC_Complete_v2_Modello_Codice_Pagina_TEST.csv'

# Schemi di installazione pages to exclude
EXCLUDED_PAGES = set(f"{p:03d}" for p in range(263, 286))


def extract_page_from_folder(folder_name):
    """Extract page number(s) from folder name."""
    # Try standard format: 034_name or 039-040_name
    match = re.match(r'^(\d{3})(?:-(\d{3}))?_', folder_name)
    if match:
        start_page = match.group(1)
        end_page = match.group(2) if match.group(2) else start_page
        return start_page, end_page

    # Try pages_ prefix format: pages_062-063_name
    match = re.match(r'^pages_(\d{3})(?:-(\d{3}))?_', folder_name)
    if match:
        start_page = match.group(1)
        end_page = match.group(2) if match.group(2) else start_page
        return start_page, end_page

    return None, None


def extract_product_names(folder_path):
    """Extract Product_Name values from IDML stories."""
    stories_dir = folder_path / 'Stories'
    product_names = []

    for f in stories_dir.glob('*.xml'):
        try:
            content = f.read_text(encoding='utf-8')
        except:
            continue
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
    if not product_names:
        return None, 0.0

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


def get_cell_text(cell):
    """Extract text content from a cell element."""
    texts = []
    for content in cell.iter():
        if content.tag == 'Content' and content.text:
            texts.append(content.text.strip())
    return ' '.join(texts).strip()


def parse_table(table_elem):
    """Parse an IDML table element and extract rows."""
    rows_data = {}

    # Parse cells
    for cell in table_elem.findall('.//Cell'):
        name = cell.get('Name', '')  # Format: "column:row"
        if ':' in name:
            col, row = name.split(':')
            col, row = int(col), int(row)
            text = get_cell_text(cell)

            if row not in rows_data:
                rows_data[row] = {}
            rows_data[row][col] = text

    return rows_data


def is_price_table(rows_data):
    """Check if this is a table with Codice articolo and Prezzo columns."""
    if 0 not in rows_data:
        return False

    header_row = rows_data[0]
    has_codice = any('Codice' in str(v) for v in header_row.values())
    has_prezzo = any('Prezzo' in str(v) for v in header_row.values())

    return has_codice and has_prezzo


def extract_from_story(story_path, page_start, page_end):
    """Extract table data from a story XML file."""
    results = []

    try:
        tree = ET.parse(story_path)
        root = tree.getroot()
    except ET.ParseError:
        return results

    for table in root.iter('Table'):
        rows_data = parse_table(table)

        if not is_price_table(rows_data):
            continue

        header_row = rows_data.get(0, {})
        descrizione_col = None
        codice_col = None

        # Find columns by header text
        for col, text in header_row.items():
            text_str = str(text).strip()
            if 'Codice' in text_str:
                codice_col = col
            elif 'Modello' in text_str and descrizione_col is None:
                descrizione_col = col

        # If no "Modello" header, find first column with content (not Codice/Prezzo)
        if descrizione_col is None:
            for col in sorted(header_row.keys()):
                text = str(header_row.get(col, '')).strip()
                if text and 'Codice' not in text and 'Prezzo' not in text:
                    descrizione_col = col
                    break

        # Fallback to column 0
        if descrizione_col is None:
            descrizione_col = 0

        if codice_col is None:
            continue

        for row_num in sorted(rows_data.keys()):
            if row_num == 0:
                continue

            row = rows_data[row_num]
            descrizione = row.get(descrizione_col, '').strip()
            codice = row.get(codice_col, '').strip()

            if not codice or not descrizione:
                continue
            if not any(c.isdigit() for c in codice):
                continue

            results.append({
                'Modello': descrizione,
                'Codice_articolo': codice,
                'page_start': page_start,
                'page_end': page_end
            })

    return results


def main():
    all_results = []
    folder_product_names = {}  # Cache product names per folder

    idml_folders = sorted(os.listdir(IDML_DIR))

    # First pass: extract product names for all folders
    print("Extracting product names from IDML folders...")
    for folder_name in idml_folders:
        folder_path = Path(IDML_DIR) / folder_name
        if not folder_path.is_dir():
            continue

        page_start, page_end = extract_page_from_folder(folder_name)
        if not page_start or page_start in EXCLUDED_PAGES:
            continue

        product_names = extract_product_names(folder_path)
        folder_product_names[folder_name] = product_names

    # Second pass: extract SKUs and match to products
    print("Extracting SKUs and matching to products...")
    for folder_name in idml_folders:
        folder_path = Path(IDML_DIR) / folder_name
        if not folder_path.is_dir():
            continue

        page_start, page_end = extract_page_from_folder(folder_name)
        if not page_start:
            print(f"Skipping {folder_name} - no page number found")
            continue

        if page_start in EXCLUDED_PAGES:
            continue

        stories_dir = folder_path / 'Stories'
        if not stories_dir.exists():
            continue

        product_names = folder_product_names.get(folder_name, [])

        for story_file in stories_dir.glob('*.xml'):
            results = extract_from_story(story_file, page_start, page_end)

            # Add product name matching
            for r in results:
                matched_product, confidence = match_sku_to_product(r['Modello'], product_names)
                r['Product_Name'] = matched_product or ''
                r['Confidence'] = f"{confidence:.2f}"

            all_results.extend(results)

    # Remove duplicates
    seen = set()
    unique_results = []
    for r in all_results:
        key = (r['Modello'], r['Codice_articolo'], r['page_start'])
        if key not in seen:
            seen.add(key)
            unique_results.append(r)

    # Sort by page, then by Modello
    unique_results.sort(key=lambda x: (x['page_start'], x['Modello']))

    # Write CSV
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['Modello', 'Codice_articolo', 'page_start', 'page_end', 'Product_Name', 'Confidence']
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(unique_results)

    print(f"Extracted {len(unique_results)} rows to {OUTPUT_FILE}")

    # Summary stats
    with_product = sum(1 for r in unique_results if r['Product_Name'])
    high_conf = sum(1 for r in unique_results if float(r['Confidence']) > 0.5)
    print(f"  - With Product_Name: {with_product}")
    print(f"  - High confidence (>0.5): {high_conf}")


if __name__ == '__main__':
    main()
