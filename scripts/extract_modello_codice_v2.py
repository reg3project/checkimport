#!/usr/bin/env python3
"""
Extract Modello and Codice articolo from IDML price tables.
Finds tables with headers: Modello | Codice articolo | Prezzo €
Extracts data rows and saves with page number.
"""
import os
import re
import csv
import xml.etree.ElementTree as ET
from pathlib import Path

IDML_DIR = '/home/user/checkimport/input/processing/IDML_unzipped'
OUTPUT_FILE = '/home/user/checkimport/output/v2/FAAC_Complete_v2_Modello_Codice_Pagina.csv'


def extract_page_from_folder(folder_name):
    """Extract page number(s) from folder name like '034_POWER_kit' or '039-040_RAPID' or 'pages_062-063_TM2K'."""
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

    # Get table dimensions
    body_row_count = int(table_elem.get('BodyRowCount', 0))
    header_row_count = int(table_elem.get('HeaderRowCount', 0))
    column_count = int(table_elem.get('ColumnCount', 0))

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

    return rows_data, header_row_count, column_count


def is_price_table(rows_data):
    """Check if this is a Modello/Codice articolo/Prezzo table."""
    if 0 not in rows_data:
        return False

    header_row = rows_data[0]
    # Check for expected headers
    has_modello = any('Modello' in str(v) for v in header_row.values())
    has_codice = any('Codice' in str(v) for v in header_row.values())

    return has_modello and has_codice


def extract_from_story(story_path, page_start, page_end):
    """Extract table data from a story XML file."""
    results = []

    try:
        tree = ET.parse(story_path)
        root = tree.getroot()
    except ET.ParseError:
        return results

    # Find all tables
    for table in root.iter('Table'):
        rows_data, header_count, col_count = parse_table(table)

        if not is_price_table(rows_data):
            continue

        # Identify column indices for Modello and Codice
        header_row = rows_data.get(0, {})
        modello_col = None
        codice_col = None

        for col, text in header_row.items():
            if 'Modello' in str(text):
                modello_col = col
            elif 'Codice' in str(text):
                codice_col = col

        if modello_col is None or codice_col is None:
            continue

        # Extract data rows (skip header row 0)
        for row_num in sorted(rows_data.keys()):
            if row_num == 0:  # Skip header
                continue

            row = rows_data[row_num]
            modello = row.get(modello_col, '').strip()
            codice = row.get(codice_col, '').strip()

            if modello and codice:
                results.append({
                    'Modello': modello,
                    'Codice_articolo': codice,
                    'page_start': page_start,
                    'page_end': page_end
                })

    return results


def main():
    all_results = []

    # Process each IDML folder
    idml_folders = sorted(os.listdir(IDML_DIR))

    for folder_name in idml_folders:
        folder_path = Path(IDML_DIR) / folder_name
        if not folder_path.is_dir():
            continue

        page_start, page_end = extract_page_from_folder(folder_name)
        if not page_start:
            print(f"Skipping {folder_name} - no page number found")
            continue

        stories_dir = folder_path / 'Stories'
        if not stories_dir.exists():
            continue

        # Process each story file
        for story_file in stories_dir.glob('*.xml'):
            results = extract_from_story(story_file, page_start, page_end)
            all_results.extend(results)

    # Remove duplicates while preserving order
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
        fieldnames = ['Modello', 'Codice_articolo', 'page_start', 'page_end']
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(unique_results)

    print(f"Extracted {len(unique_results)} rows to {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
