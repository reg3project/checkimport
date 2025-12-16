#!/usr/bin/env python3
"""
Parse IDML files to extract raw table data:
1. CARATTERISTICHE TECNICHE (Technical Specifications) table
2. MODELLI FAMIGLIA (Models/Family) table with SKU and prices
"""

import os
import re
import csv
import zipfile
from pathlib import Path
from collections import defaultdict


def extract_tables_from_idml(idml_path):
    """
    Extract tables from an IDML file.
    Returns dict with 'tech_specs' and 'modelli' tables.
    """
    tech_specs_tables = []
    modelli_tables = []

    try:
        with zipfile.ZipFile(idml_path, 'r') as zf:
            story_files = [f for f in zf.namelist() if f.startswith('Stories/Story_') and f.endswith('.xml')]

            for story_file in story_files:
                try:
                    content = zf.read(story_file).decode('utf-8', errors='ignore')

                    # Skip files without tables
                    if '<Cell ' not in content:
                        continue

                    # Check for table type based on cell style
                    is_tech_spec = 'Technical_Specifications' in content or 'techspec_cell' in content
                    is_models = 'Models_gruppo' in content or 'models_cell' in content
                    is_price_list = 'Price_List_gruppo' in content or 'pricelist_cell' in content

                    if not is_tech_spec and not is_models and not is_price_list:
                        continue

                    # Parse cells - extract cell name and content
                    cells = {}

                    # Pattern to match Cell with its Content
                    # Cell elements contain the Name attribute (col:row) and Content elements have the text
                    cell_pattern = re.compile(
                        r'<Cell[^>]*Name="(\d+:\d+)"[^>]*>.*?<Content>([^<]*)</Content>',
                        re.DOTALL
                    )

                    # Alternative: match each Cell block and extract Name and Content
                    cell_blocks = re.findall(r'<Cell[^>]*Name="(\d+:\d+)"[^>]*>.*?</Cell>', content, re.DOTALL)

                    for match in re.finditer(r'<Cell[^>]*Name="(\d+:\d+)"[^>]*>(.*?)</Cell>', content, re.DOTALL):
                        cell_name = match.group(1)  # e.g., "0:0", "1:0"
                        cell_content = match.group(2)

                        # Extract Content text
                        content_match = re.search(r'<Content>([^<]*)</Content>', cell_content)
                        if content_match:
                            text = content_match.group(1).strip()
                            if text:
                                cells[cell_name] = text

                    if not cells:
                        continue

                    # Organize into rows
                    # Cell name format is "column:row"
                    table_data = defaultdict(dict)
                    max_col = 0
                    max_row = 0

                    for cell_name, text in cells.items():
                        parts = cell_name.split(':')
                        col = int(parts[0])
                        row = int(parts[1])
                        table_data[row][col] = text
                        max_col = max(max_col, col)
                        max_row = max(max_row, row)

                    # Convert to list of rows
                    table_rows = []
                    for row_idx in range(max_row + 1):
                        row_data = []
                        for col_idx in range(max_col + 1):
                            row_data.append(table_data[row_idx].get(col_idx, ''))
                        table_rows.append(row_data)

                    if is_tech_spec and table_rows:
                        tech_specs_tables.append(table_rows)
                    elif (is_models or is_price_list) and table_rows:
                        modelli_tables.append(table_rows)

                except Exception as e:
                    print(f"  Error parsing {story_file}: {e}")
                    continue

    except Exception as e:
        print(f"Error opening {idml_path}: {e}")

    return {
        'tech_specs': tech_specs_tables,
        'modelli': modelli_tables
    }


def get_product_name_from_filename(filename):
    """Extract product name from IDML filename."""
    # Remove page numbers and extension
    name = Path(filename).stem
    # Remove page prefix like "098-099_"
    name = re.sub(r'^\d+[-_]\d+[-_]', '', name)
    name = re.sub(r'^\d+[-_]', '', name)
    # Remove _SI suffix
    name = re.sub(r'_SI$', '', name)
    # Replace underscores with spaces
    name = name.replace('_', ' ')
    return name


def get_page_from_filename(filename):
    """Extract page number from IDML filename."""
    name = Path(filename).stem
    match = re.match(r'^(\d+(?:[-_]\d+)?)', name)
    if match:
        return match.group(1).replace('_', '-')
    return ''


def main():
    idml_dir = Path('input/learning/IDML')
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)

    # Collect all data
    all_tech_specs = []
    all_modelli = []

    # Get all IDML files (exclude _SI files - Schema Installazione)
    idml_files = sorted([f for f in idml_dir.glob('*.idml') if not f.stem.endswith('_SI')])

    print(f"Processing {len(idml_files)} IDML files...")

    for idml_file in idml_files:
        filename = idml_file.name
        page = get_page_from_filename(filename)
        product = get_product_name_from_filename(filename)

        print(f"  {filename}...")

        tables = extract_tables_from_idml(idml_file)

        # Process tech specs tables
        for table in tables['tech_specs']:
            if len(table) < 2:  # Need header + at least 1 data row
                continue

            # First row is header - typically "Modello" in col 0, model names in col 1+
            header = table[0]
            num_models = len(header) - 1  # Exclude first column (spec label)

            # Get model names from header row
            model_names = header[1:] if len(header) > 1 else ['']

            # Process each spec row - one row per spec with all models
            for row in table[1:]:  # Skip header
                if not row or not row[0]:
                    continue

                spec_label = row[0]

                # Create one row with all model columns
                row_data = {
                    'Page': page,
                    'Product': product,
                    'Spec_Label': spec_label,
                }

                for i, model_name in enumerate(model_names):
                    value = row[i + 1] if len(row) > i + 1 else ''
                    row_data[f'Model_{i+1}'] = model_name
                    row_data[f'Value_{i+1}'] = value

                all_tech_specs.append(row_data)

        # Process modelli tables
        for table in tables['modelli']:
            if len(table) < 2:
                continue

            # First row is header: Modello, Codice articolo, Prezzo €
            for row in table[1:]:  # Skip header
                if len(row) >= 3:
                    modello = row[0].strip() if row[0] else ''
                    codice = row[1].strip() if row[1] else ''
                    prezzo = row[2].strip() if row[2] else ''

                    # Only include rows with valid SKU codes (numeric)
                    # Filter out description rows that end up in the table
                    if codice and codice.replace('.', '').isdigit():
                        all_modelli.append({
                            'Page': page,
                            'Product': product,
                            'Modello': modello,
                            'Codice_SKU': codice,
                            'Prezzo': prezzo
                        })

    # Write tech specs CSV
    tech_specs_file = output_dir / 'caratteristiche_tecniche_raw.csv'
    if all_tech_specs:
        # Determine all columns needed
        max_models = 1
        for row in all_tech_specs:
            for key in row:
                if key.startswith('Model_'):
                    num = int(key.replace('Model_', ''))
                    max_models = max(max_models, num)

        fieldnames = ['Page', 'Product', 'Spec_Label']
        for i in range(1, max_models + 1):
            fieldnames.extend([f'Model_{i}', f'Value_{i}'])

        with open(tech_specs_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_tech_specs)

        print(f"\nWritten {len(all_tech_specs)} tech spec rows to {tech_specs_file}")
    else:
        print("\nNo tech specs data found!")

    # Write modelli CSV
    modelli_file = output_dir / 'modelli_famiglia_raw.csv'
    if all_modelli:
        fieldnames = ['Page', 'Product', 'Modello', 'Codice_SKU', 'Prezzo']
        with open(modelli_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_modelli)

        print(f"Written {len(all_modelli)} modelli rows to {modelli_file}")
    else:
        print("No modelli data found!")

    return len(all_tech_specs), len(all_modelli)


if __name__ == '__main__':
    tech_count, modelli_count = main()
    print(f"\nSummary: {tech_count} tech specs, {modelli_count} modelli")
