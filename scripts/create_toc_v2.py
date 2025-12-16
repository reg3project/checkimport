#!/usr/bin/env python3
"""
Create FAAC_Complete_v2_TOC.csv from the source Data Entry CSV.
Filters rows where IDML is not 0 and formats page numbers as 3 digits.
"""
import csv
import os

def main():
    input_file = '/home/user/checkimport/input/learning/FAAC_Lista_Attivita_annotato.xlsx - Data Entry.csv'
    output_dir = '/home/user/checkimport/output/v2'
    output_file = os.path.join(output_dir, 'FAAC_Complete_v2_TOC.csv')

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    rows_out = []

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            idml_value = row.get('IDML', '').strip()

            # Skip rows where IDML is "0"
            if idml_value == '0':
                continue

            categoria = row.get('Categoria', '').strip()
            prodotto = row.get('Prodotto', '').strip()
            pagina = row.get('Pagina', '').strip()
            pagina_fine = row.get('Pagina_fine', '').strip()

            # Skip rows without product name (category headers without products)
            if not prodotto:
                continue

            # Format page numbers as 3 digits
            try:
                page_start = f"{int(pagina):03d}" if pagina else ''
                page_finish = f"{int(pagina_fine):03d}" if pagina_fine else ''
            except ValueError:
                page_start = pagina
                page_finish = pagina_fine

            rows_out.append({
                'Categoria': categoria,
                'Prodotto': prodotto,
                'page_start': page_start,
                'page_finish': page_finish
            })

    # Write output CSV
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['Categoria', 'Prodotto', 'page_start', 'page_finish']
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(rows_out)

    print(f"Created {output_file} with {len(rows_out)} rows")

if __name__ == '__main__':
    main()
