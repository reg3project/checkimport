#!/usr/bin/env python3
"""
Create consolidated TOC with product names and SKU codes.
Merges FAAC_Complete_v2_TOC.csv with approved SKU-to-Product mapping.
"""
import csv
import re
from collections import defaultdict
from difflib import SequenceMatcher

TOC_FILE = '/home/user/checkimport/output/v2/FAAC_Complete_v2_TOC.csv'
APPROVED_FILE = '/tmp/approved.csv'
OUTPUT_FILE = '/home/user/checkimport/output/v2/FAAC_Complete_v2_TOC_with_SKUs.csv'


def normalize_name(name):
    """Normalize product name for matching."""
    # Remove common suffixes, lowercase, remove extra spaces
    name = name.lower()
    name = re.sub(r'\s*(perfect\s*60|kit)\s*', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name


def similarity(a, b):
    """Calculate text similarity."""
    return SequenceMatcher(None, normalize_name(a), normalize_name(b)).ratio()


def find_best_match(prodotto, product_names):
    """Find best matching product name for a TOC Prodotto."""
    if not product_names:
        return None, 0

    best_match = None
    best_score = 0

    for product_name in product_names:
        score = similarity(prodotto, product_name)
        if score > best_score:
            best_score = score
            best_match = product_name

    return best_match, best_score


def pages_overlap(toc_start, toc_end, csv_start, csv_end):
    """Check if two page ranges overlap."""
    try:
        t_start, t_end = int(toc_start), int(toc_end)
        c_start, c_end = int(csv_start), int(csv_end)
        return not (t_end < c_start or c_end < t_start)
    except ValueError:
        return False


def main():
    # Read approved CSV - store all entries with page ranges
    approved_entries = []

    with open(APPROVED_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            page_start = row['page_start'].zfill(3)
            page_end = row['page_end'].zfill(3)
            product_name = row['Product_Name'].strip()
            codice = row['Codice_articolo'].strip()

            if codice:
                approved_entries.append({
                    'page_start': page_start,
                    'page_end': page_end,
                    'product_name': product_name,
                    'codice': codice
                })

    # Build page_product_skus with overlapping range support
    def get_products_for_page_range(toc_start, toc_end):
        """Find all products/SKUs that overlap with given page range."""
        result = defaultdict(set)
        for entry in approved_entries:
            if pages_overlap(toc_start, toc_end, entry['page_start'], entry['page_end']):
                if entry['product_name']:
                    result[entry['product_name']].add(entry['codice'])
        return result

    # Read TOC
    toc_rows = []
    with open(TOC_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            toc_rows.append(row)

    # Build output rows
    output_rows = []

    for toc_row in toc_rows:
        categoria = toc_row['Categoria']
        prodotto = toc_row['Prodotto']
        page_start = toc_row['page_start']
        page_finish = toc_row['page_finish']

        # Get all product names and SKUs for this page range (with overlap support)
        products_on_page = get_products_for_page_range(page_start, page_finish)

        if not products_on_page:
            # No SKUs found - try to find in nearby pages
            all_skus = set()
            output_rows.append({
                'Categoria': categoria,
                'Prodotto': prodotto,
                'nome_prodotto': '',
                'page_start': page_start,
                'page_finish': page_finish,
                'codici_modelli': ''
            })
        elif len(products_on_page) == 1:
            # Single product on page - use it
            product_name = list(products_on_page.keys())[0]
            skus = products_on_page[product_name]
            output_rows.append({
                'Categoria': categoria,
                'Prodotto': prodotto,
                'nome_prodotto': product_name,
                'page_start': page_start,
                'page_finish': page_finish,
                'codici_modelli': ';'.join(sorted(skus))
            })
        else:
            # Multiple products - find best match for this TOC Prodotto
            best_match, score = find_best_match(prodotto, products_on_page.keys())
            if best_match and score > 0.3:
                skus = products_on_page[best_match]
                output_rows.append({
                    'Categoria': categoria,
                    'Prodotto': prodotto,
                    'nome_prodotto': best_match,
                    'page_start': page_start,
                    'page_finish': page_finish,
                    'codici_modelli': ';'.join(sorted(skus))
                })
            else:
                # No good match - collect all SKUs from page
                all_skus = set()
                for skus in products_on_page.values():
                    all_skus.update(skus)
                output_rows.append({
                    'Categoria': categoria,
                    'Prodotto': prodotto,
                    'nome_prodotto': '',
                    'page_start': page_start,
                    'page_finish': page_finish,
                    'codici_modelli': ';'.join(sorted(all_skus))
                })

    # Write output
    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['Categoria', 'Prodotto', 'nome_prodotto', 'page_start', 'page_finish', 'codici_modelli']
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Created {OUTPUT_FILE}")
    print(f"  - Input TOC rows: {len(toc_rows)}")
    print(f"  - Output rows: {len(output_rows)}")

    # Show sample
    print("\nSample output (first 15 rows):")
    for row in output_rows[:15]:
        print(f"  {row['Prodotto']} | {row['nome_prodotto']} | {row['codici_modelli'][:50]}...")


if __name__ == '__main__':
    main()
