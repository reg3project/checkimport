#!/usr/bin/env python3
"""
Extract schema_installazione from IDML _SI files
Format: posizione|quantità|codice_sku;posizione|quantità|codice_sku;...
"""

import os
import re
import csv
from pathlib import Path

IDML_DIR = Path("/home/user/checkimport/input/processing/IDML_unzipped")
OUTPUT_CSV = Path("/home/user/checkimport/output/Schema_Installazione_Master.csv")

def extract_content_from_stories(idml_folder):
    """Extract all <Content> values from Stories/*.xml"""
    stories_dir = idml_folder / "Stories"
    if not stories_dir.exists():
        return []

    contents = []
    for xml_file in stories_dir.glob("*.xml"):
        with open(xml_file, 'r', encoding='utf-8') as f:
            text = f.read()
            # Extract all <Content>...</Content>
            matches = re.findall(r'<Content>([^<]*)</Content>', text)
            contents.extend(matches)

    return contents

def parse_schema_table(contents):
    """
    Parse the installation schema table.
    Pattern: Rif, Q.tà, Descrizione, Cod., Prezzo
    Returns list of (rif, qta, cod) tuples
    """
    results = []
    i = 0

    # Skip header and find table start
    in_table = False

    while i < len(contents):
        val = contents[i].strip()

        # Skip headers
        if val in ['Rif', 'Q.tà', 'Descrizione materiale', 'Cod.', 'Prezzo €']:
            in_table = True
            i += 1
            continue

        # Skip non-table content
        if val.startswith('ATTENZIONE') or val.startswith('TOTALE') or val.startswith('Esempio'):
            in_table = False
            i += 1
            continue

        if val.startswith('Tubazioni') or val.startswith('cavo'):
            i += 1
            continue

        if not in_table:
            i += 1
            continue

        # Try to parse table row: Rif, Q.tà, Descrizione, Cod, Prezzo
        # Rif can be number or empty space
        if i + 4 < len(contents):
            rif = contents[i].strip()
            qta = contents[i+1].strip()
            desc = contents[i+2].strip()
            cod = contents[i+3].strip()
            prezzo = contents[i+4].strip()

            # Validate: rif should be digit or space, qta should be digit, cod should be numeric
            rif_valid = rif.isdigit() or rif == '' or rif == ' '
            qta_valid = qta.isdigit()
            cod_valid = cod.replace(' ', '').isdigit() and len(cod) >= 5
            prezzo_valid = ',' in prezzo or prezzo.replace('.', '').replace(',', '').isdigit()

            if qta_valid and cod_valid:
                # Use previous rif if current is empty
                if rif == '' or rif == ' ':
                    rif = results[-1][0] if results else '0'
                results.append((rif, qta, cod))
                i += 5
                continue

        i += 1

    return results

def format_schema(rows):
    """Format as posizione|quantità|codice;..."""
    return ';'.join([f"{r[0]}|{r[1]}|{r[2]}" for r in rows])

def save_to_csv(results):
    """Save results to CSV file"""
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['page', 'product_name', 'schema_installazione'])
        for (page, product_name), schema in sorted(results.items()):
            writer.writerow([page, product_name, schema])
    print(f"Saved to {OUTPUT_CSV}")

def main():
    # Find all _SI folders
    si_folders = sorted([f for f in IDML_DIR.iterdir() if f.name.endswith('_SI')])

    print(f"Found {len(si_folders)} _SI folders")
    print()

    results = {}

    for folder in si_folders:
        # Extract product name from folder name (e.g., "263_392_C_SI" -> "392 C")
        name_parts = folder.name.replace('_SI', '').split('_')
        page = name_parts[0]
        product_name = ' '.join(name_parts[1:]).replace('_', ' ')

        contents = extract_content_from_stories(folder)
        rows = parse_schema_table(contents)

        if rows:
            schema = format_schema(rows)
            results[(page, product_name)] = schema
            print(f"Page {page} - {product_name}:")
            print(f"  {len(rows)} items: {schema[:100]}...")
            print()

    # Save to CSV
    save_to_csv(results)

    return results

if __name__ == "__main__":
    main()
