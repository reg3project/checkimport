#!/usr/bin/env python3
"""
Add KIT rows (pages 28-63) from FAAC Data Entry to Model_Codes_Master.csv
"""

import csv

# Read FAAC Data Entry to get KIT products (pages 28-63)
kit_rows = []
with open('input/learning/FAAC_Lista_Attivita_annotato.xlsx - Data Entry.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        categoria = row.get('Categoria', '').strip()
        prodotto = row.get('Prodotto', '').strip()
        pagina = row.get('Pagina', '').strip()
        skus = row.get('SKU_presenti_nel_prodotto', '').strip()

        # Only include KIT products from pages 28-63 that have a product name
        if pagina and prodotto:
            try:
                page_num = int(pagina)
                if 28 <= page_num <= 63 and categoria:
                    kit_rows.append({
                        'page': pagina,
                        'product_name': prodotto,
                        'model_name': prodotto,  # Use product name as model name
                        'model_sku': '',  # KITs don't have single SKU
                        'price': '',  # Price not in source
                        'codici_modelli': skus,
                        'categoria_prodotto': categoria
                    })
            except ValueError:
                pass

print(f"Found {len(kit_rows)} KIT products")
for row in kit_rows:
    print(f"  Page {row['page']}: {row['product_name']} ({row['categoria_prodotto']})")

# Read existing Model_Codes_Master.csv
existing_rows = []
with open('output/Model_Codes_Master.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter=';')
    for row in reader:
        existing_rows.append(row)

# First two rows are headers
header1 = existing_rows[0]  # page;product_name;model_name;model_sku;price;codici_modelli;categoria_prodotto
header2 = existing_rows[1]  # ;;;;;;Categoria

# Data rows start from index 2
data_rows = existing_rows[2:]

# Convert kit_rows to list format
kit_data = []
for kit in kit_rows:
    kit_data.append([
        kit['page'],
        kit['product_name'],
        kit['model_name'],
        kit['model_sku'],
        kit['price'],
        kit['codici_modelli'],
        kit['categoria_prodotto']
    ])

# Combine: headers + kit rows + existing data rows
# Sort by page number
all_data = kit_data + data_rows

def get_page_num(row):
    try:
        return int(row[0])
    except (ValueError, IndexError):
        return 9999

all_data.sort(key=get_page_num)

# Write output
output_rows = [header1, header2] + all_data

with open('output/Model_Codes_Master.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerows(output_rows)

print(f"\nUpdated Model_Codes_Master.csv")
print(f"Total rows (including headers): {len(output_rows)}")

# Show first 40 rows
print("\nFirst 40 rows:")
for i, row in enumerate(output_rows[:40]):
    print(f"{i+1}: {';'.join(row[:4])}...{row[-1]}")
