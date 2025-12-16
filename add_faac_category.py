#!/usr/bin/env python3
"""
Add FAAC category column to Model_Codes_Master.csv
"""

import csv

# Read FAAC Data Entry to build category mappings
faac_categories = []
with open('input/learning/FAAC_Lista_Attivita_annotato.xlsx - Data Entry.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        categoria = row.get('Categoria', '').strip()
        prodotto = row.get('Prodotto', '').strip()
        pagina = row.get('Pagina', '').strip()
        pagina_fine = row.get('Pagina_fine', '').strip()

        if categoria and pagina:
            try:
                page_start = int(pagina)
                page_end = int(pagina_fine) if pagina_fine else page_start
                faac_categories.append({
                    'categoria': categoria,
                    'prodotto': prodotto,
                    'page_start': page_start,
                    'page_end': page_end
                })
            except ValueError:
                pass

def find_category(page, product_name):
    """Find category based on page number and product name"""
    try:
        page_num = int(page)
    except (ValueError, TypeError):
        return ''

    # First try to match by page range and product name
    for entry in faac_categories:
        if entry['page_start'] <= page_num <= entry['page_end']:
            # If prodotto matches, return the category
            if entry['prodotto'] and product_name:
                if entry['prodotto'].lower() in product_name.lower() or product_name.lower() in entry['prodotto'].lower():
                    return entry['categoria']

    # If no product match, just match by page range
    for entry in faac_categories:
        if entry['page_start'] <= page_num <= entry['page_end']:
            if entry['categoria']:
                return entry['categoria']

    return ''

# Read Model_Codes_Master and add category column
input_file = 'output/Model_Codes_Master.csv'
output_file = 'output/Model_Codes_Master.csv'

rows = []
with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter=';')
    header = next(reader)
    rows.append(header)

    for row in rows[1:]:
        pass  # Already have header

    for row in reader:
        rows.append(row)

# Add category to each row
new_rows = []
# Double header: first row has column names, add categoria_prodotto
new_header = rows[0] + ['categoria_prodotto']
new_rows.append(new_header)

# Add second header row with "Categoria"
second_header = [''] * len(rows[0]) + ['Categoria']
new_rows.append(second_header)

# Process data rows
for row in rows[1:]:
    if len(row) >= 2:
        page = row[0]  # page column
        product_name = row[1]  # product_name column
        categoria = find_category(page, product_name)
        new_row = row + [categoria]
        new_rows.append(new_row)
    else:
        new_rows.append(row + [''])

# Write output
with open(output_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerows(new_rows)

print(f"Added category column to {output_file}")
print(f"Total rows: {len(new_rows)}")

# Show sample
print("\nFirst 10 rows:")
for row in new_rows[:10]:
    print(';'.join(row))
