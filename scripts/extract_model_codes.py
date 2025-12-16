#!/usr/bin/env python3
"""
Extract model codes from pre-unzipped IDML files.

Model codes are in tables with style: models_code_pgf
Accessory codes are in tables with style: infoblock_code_pgf

This script extracts ONLY the main model SKUs (from Models_gruppo tables)
to populate the codici_modelli field correctly.

Output:
- Model_Codes_Master.csv: page, product_name, model_name, model_sku, price
"""

import os
import re
import csv
from pathlib import Path
from collections import defaultdict

IDML_UNZIPPED_DIRS = [
    '/home/user/checkimport/input/processing/IDML_unzipped',
    '/home/user/checkimport/input/learning/IDML_unzipped'
]

OUTPUT_CSV = '/home/user/checkimport/output/Model_Codes_Master.csv'


def extract_page_from_dirname(dirname):
    """Extract page number(s) from IDML directory name"""
    match = re.search(r'^(\d+)(?:-\d+)?_', dirname)
    if match:
        return match.group(1).lstrip('0') or '0'
    return None


def extract_product_name_from_dirname(dirname):
    """Extract product name from IDML directory name"""
    # Remove page prefix: "100-101_770N_24V" -> "770N_24V"
    parts = dirname.split('_', 1)
    if len(parts) > 1 and parts[0].replace('-', '').isdigit():
        name = parts[1]
    else:
        name = dirname
    return name.replace('_', ' ')


def read_story(story_path):
    """Read and return story XML content"""
    try:
        with open(story_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except:
        return ''


def find_model_codes_in_story(content):
    """Find model codes from Models_gruppo table in story content.

    Returns list of dicts: [{model_name, model_sku, price}, ...]
    """
    results = []

    # Check if this story has a Models_gruppo table
    if 'Models_gruppo' not in content:
        return results

    if 'models_code_pgf' not in content:
        return results

    # Extract the table content
    table_match = re.search(r'<Table[^>]*Models_gruppo[^>]*>(.*?)</Table>', content, re.DOTALL)
    if not table_match:
        return results

    table_content = table_match.group(1)

    # Parse cells - find model name, code, and price cells
    # Models are in Column 0, Codes in Column 1, Prices in Column 2

    # Find model names (models_model_pgf style)
    model_names = re.findall(
        r'models_model_pgf"[^>]*>.*?<Content>([^<]+)</Content>',
        table_content, re.DOTALL
    )

    # Find model codes (models_code_pgf style)
    model_codes = re.findall(
        r'models_code_pgf"[^>]*>.*?<Content>([^<]+)</Content>',
        table_content, re.DOTALL
    )

    # Find prices (models_price_pgf style)
    model_prices = re.findall(
        r'models_price_pgf"[^>]*>.*?<Content>([^<]+)</Content>',
        table_content, re.DOTALL
    )

    # Combine - they should be in same order (row by row)
    for i in range(len(model_codes)):
        result = {
            'model_name': model_names[i] if i < len(model_names) else '',
            'model_sku': model_codes[i].strip(),
            'price': model_prices[i] if i < len(model_prices) else ''
        }
        results.append(result)

    return results


def process_idml_dir(idml_dir):
    """Process a single pre-unzipped IDML directory"""
    dirname = os.path.basename(idml_dir)
    page = extract_page_from_dirname(dirname)
    product_name = extract_product_name_from_dirname(dirname)

    if not page:
        return None

    stories_dir = os.path.join(idml_dir, 'Stories')
    if not os.path.exists(stories_dir):
        return None

    # Find all model codes in all stories
    all_models = []

    for story_file in Path(stories_dir).glob('Story_*.xml'):
        content = read_story(story_file)
        models = find_model_codes_in_story(content)
        all_models.extend(models)

    if not all_models:
        return None

    return {
        'page': page,
        'product_name': product_name,
        'dirname': dirname,
        'models': all_models
    }


def main():
    all_results = []

    for base_dir in IDML_UNZIPPED_DIRS:
        if not os.path.exists(base_dir):
            continue

        for dirname in os.listdir(base_dir):
            idml_dir = os.path.join(base_dir, dirname)
            if os.path.isdir(idml_dir):
                result = process_idml_dir(idml_dir)
                if result:
                    all_results.append(result)

    # Sort by page number
    all_results.sort(key=lambda x: int(x['page']) if x['page'] else 0)

    # Deduplicate (same dirname)
    seen_dirs = set()
    unique_results = []
    for r in all_results:
        if r['dirname'] not in seen_dirs:
            seen_dirs.add(r['dirname'])
            unique_results.append(r)

    # Build CSV
    rows = []
    for result in unique_results:
        page = result['page']
        product_name = result['product_name']

        # Combine model SKUs into single codici_modelli field
        model_skus = [m['model_sku'] for m in result['models'] if m['model_sku']]
        codici_modelli = '; '.join(model_skus)

        for model in result['models']:
            rows.append({
                'page': page,
                'product_name': product_name,
                'model_name': model['model_name'],
                'model_sku': model['model_sku'],
                'price': model['price'],
                'codici_modelli': codici_modelli
            })

    # Write CSV
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f,
            fieldnames=['page', 'product_name', 'model_name', 'model_sku', 'price', 'codici_modelli'],
            delimiter=';')
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"Extracted {len(rows)} model entries from {len(unique_results)} products")
    print(f"Output: {OUTPUT_CSV}")

    # Show summary
    print("\n=== Sample Model Codes ===")
    for result in unique_results[:10]:
        page = result['page']
        product = result['product_name']
        models = [m['model_sku'] for m in result['models']]
        print(f"Page {page}: {product}")
        print(f"  Model SKUs: {'; '.join(models)}")

    # Verify 770N 24V
    for result in unique_results:
        if '770N' in result['product_name']:
            print(f"\n=== 770N 24V Verification ===")
            print(f"Page: {result['page']}")
            print(f"Product: {result['product_name']}")
            for model in result['models']:
                print(f"  Model: {model['model_name']} -> SKU: {model['model_sku']} @ {model['price']}€")
            break


if __name__ == '__main__':
    main()
