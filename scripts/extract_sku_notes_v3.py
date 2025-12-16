#!/usr/bin/env python3
"""
Extract SKU notes and product notes from IDML files.
Creates:
- Sku_Notes_Master_v1.csv (notes with diamond markers for SKUs)
- Product_Notes_Master_v1.csv (notes without diamonds for products)
"""

import os
import re
import zipfile
import csv
from pathlib import Path
from collections import defaultdict

def extract_page_from_filename(filename):
    """Extract page number(s) from IDML filename"""
    base = os.path.basename(filename)
    match = re.search(r'^(\d+)(?:-\d+)?_', base)
    if match:
        return match.group(1)
    match = re.search(r'pages_(\d+)', base)
    if match:
        return match.group(1)
    return None

def extract_product_name_from_filename(filename):
    """Extract product name from IDML filename"""
    base = os.path.basename(filename).replace('.idml', '')
    # Remove page numbers prefix
    parts = base.split('_', 1)
    if len(parts) > 1 and parts[0].replace('-', '').isdigit():
        return parts[1].replace('_', ' ')
    return base.replace('_', ' ')

def color_to_name(color_code):
    """Convert CMYK color code to human-readable name"""
    color_map = {
        'C=0 M=0 Y=0 K=60': 'grigio',
        'C=0 M=100 Y=0 K=0': 'magenta',
        'C=100 M=0 Y=0 K=0': 'ciano',
        'C=0 M=0 Y=100 K=0': 'giallo',
        'default': 'nero',
        'unknown': 'sconosciuto'
    }
    return color_map.get(color_code, color_code)

def get_text_content(xml_content):
    """Extract all text content from XML"""
    contents = re.findall(r'<Content>([^<]*)</Content>', xml_content)
    return ' '.join(contents).strip()

def find_ref_notes(xml_content):
    """Find __logo__RefNote[N]__ markers and return note numbers"""
    notes = re.findall(r'__logo__RefNote(\d+)__', xml_content)
    return [int(n) for n in notes]

def get_diamond_color(xml_content):
    """Extract diamond color from Wingdings marker story"""
    color_match = re.search(r'FillColor="Color/([^"]+)"', xml_content)
    if color_match:
        return color_match.group(1)
    return 'default'

def extract_sku_codes(xml_content):
    """Extract SKU codes from table cell stories"""
    if 'infoblock_code_pgf' in xml_content:
        codes = re.findall(r'<Content>(\d{5,7})</Content>', xml_content)
        return codes
    return []

def extract_product_descriptions(xml_content):
    """Extract product descriptions and their note references"""
    results = []
    if 'Description_gruppo%3aDescription' in xml_content:
        text = get_text_content(xml_content)
        ref_notes = find_ref_notes(xml_content)
        if text and ref_notes:
            results.append({
                'description': text,
                'ref_notes': ref_notes
            })
    return results

def extract_accessory_notes(xml_content):
    """Extract accessory notes (with diamond markers)"""
    notes = []
    if 'Accessories_gruppo%3aNote' in xml_content:
        pattern = r'ParentStory="(u[a-f0-9]+)".*?</TextFrame>\s*<Content>([^<]+)</Content>'
        matches = re.findall(pattern, xml_content, re.DOTALL)
        for parent_story, text in matches:
            text = text.strip()
            if text:
                notes.append({
                    'parent_story': parent_story,
                    'text': text
                })
    return notes

def extract_product_notes(xml_content):
    """Extract product-level notes (no diamond markers)"""
    notes = []
    # Images_gruppo:Note style is used for product-level notes
    if 'Images_gruppo%3aNote' in xml_content:
        pattern = r'ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/Images_gruppo%3aNote"[^>]*>.*?<Content>([^<]+)</Content>'
        matches = re.findall(pattern, xml_content, re.DOTALL)
        for text in matches:
            text = text.strip()
            if text:
                notes.append(text)
    return notes

def process_idml(idml_path):
    """Process a single IDML file and extract notes data"""
    page = extract_page_from_filename(idml_path)
    product = extract_product_name_from_filename(idml_path)
    if not page:
        return None

    stories = {}
    descriptions = []
    sku_codes = []
    accessory_notes = []
    product_notes = []
    diamond_stories = {}

    try:
        with zipfile.ZipFile(idml_path, 'r') as zf:
            for name in zf.namelist():
                if name.startswith('Stories/') and name.endswith('.xml'):
                    content = zf.read(name).decode('utf-8', errors='ignore')
                    story_id = re.search(r'Story Self="(u[a-f0-9]+)"', content)
                    if story_id:
                        stories[story_id.group(1)] = content

            for story_id, content in stories.items():
                descs = extract_product_descriptions(content)
                for d in descs:
                    d['story_id'] = story_id
                descriptions.extend(descs)

                codes = extract_sku_codes(content)
                for code in codes:
                    sku_codes.append({'code': code, 'story_id': story_id})

                acc_notes = extract_accessory_notes(content)
                accessory_notes.extend(acc_notes)

                prod_notes = extract_product_notes(content)
                product_notes.extend(prod_notes)

                if 'Wingdings' in content and '<Content>t</Content>' in content:
                    color = get_diamond_color(content)
                    diamond_stories[story_id] = color

    except Exception as e:
        print(f"Error processing {idml_path}: {e}")
        return None

    # Assign colors to accessory notes
    for note in accessory_notes:
        parent = note.get('parent_story', '')
        color = diamond_stories.get(parent, 'unknown')
        note['color'] = color

    return {
        'page': page,
        'product': product,
        'file': os.path.basename(idml_path),
        'descriptions': descriptions,
        'sku_codes': [s['code'] for s in sku_codes],
        'accessory_notes': accessory_notes,
        'product_notes': product_notes
    }

def main():
    idml_dirs = [
        '/home/user/checkimport/input/processing/IDML',
        '/home/user/checkimport/input/learning/IDML'
    ]

    all_results = []

    for idml_dir in idml_dirs:
        if not os.path.exists(idml_dir):
            continue
        for f in os.listdir(idml_dir):
            if f.endswith('.idml'):
                result = process_idml(os.path.join(idml_dir, f))
                if result:
                    all_results.append(result)

    # Sort by page number
    all_results.sort(key=lambda x: int(x['page']) if x['page'] else 0)

    # Remove duplicates (same page from both dirs)
    seen_pages = set()
    unique_results = []
    for r in all_results:
        key = (r['page'], r['file'])
        if key not in seen_pages:
            seen_pages.add(key)
            unique_results.append(r)

    # === Build SKU Notes CSV (with diamond markers) ===
    sku_notes_path = '/home/user/checkimport/output/Sku_Notes_Master_v1.csv'
    sku_rows = []

    for result in unique_results:
        page = result['page']
        accessory_notes = result['accessory_notes']
        descriptions = result['descriptions']
        skus = result['sku_codes']

        if not accessory_notes:
            continue

        for note in accessory_notes:
            note_text = note['text'].replace('&apos;', "'")
            color = color_to_name(note.get('color', 'unknown'))

            for desc in descriptions:
                if desc['ref_notes']:
                    desc_text = desc['description'].replace('&apos;', "'")
                    sku = skus[0] if skus else ''

                    sku_rows.append({
                        'page': page,
                        'tipo_componente': 'ACCESSORI',
                        'descrizione_breve': desc_text[:80] if len(desc_text) > 80 else desc_text,
                        'sku': sku,
                        'nota': note_text,
                        'colore_rombo': color
                    })

    # Deduplicate
    seen = set()
    unique_sku_rows = []
    for row in sku_rows:
        key = (row['page'], row['nota'], row['colore_rombo'])
        if key not in seen:
            seen.add(key)
            unique_sku_rows.append(row)

    with open(sku_notes_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f,
            fieldnames=['page', 'tipo_componente', 'descrizione_breve', 'sku', 'nota', 'colore_rombo'],
            delimiter=';')
        writer.writeheader()
        for row in unique_sku_rows:
            writer.writerow(row)

    print(f"Extracted {len(unique_sku_rows)} SKU note entries to {sku_notes_path}")

    # === Build Product Notes CSV (without diamond markers) ===
    product_notes_path = '/home/user/checkimport/output/Product_Notes_Master_v1.csv'
    product_rows = []

    for result in unique_results:
        page = result['page']
        product = result['product']
        product_notes = result['product_notes']

        for note in product_notes:
            note_text = note.replace('&apos;', "'")
            product_rows.append({
                'page': page,
                'nome_prodotto': product,
                'note_prodotto': note_text
            })

    # Deduplicate
    seen = set()
    unique_product_rows = []
    for row in product_rows:
        key = (row['page'], row['note_prodotto'])
        if key not in seen:
            seen.add(key)
            unique_product_rows.append(row)

    with open(product_notes_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f,
            fieldnames=['page', 'nome_prodotto', 'note_prodotto'],
            delimiter=';')
        writer.writeheader()
        for row in unique_product_rows:
            writer.writerow(row)

    print(f"Extracted {len(unique_product_rows)} product note entries to {product_notes_path}")

    # === Summary ===
    summary_path = '/home/user/checkimport/output/notes_summary.txt'
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("=== SKU NOTES (con rombi colorati) ===\n\n")

        unique_sku_notes = defaultdict(list)
        for row in unique_sku_rows:
            unique_sku_notes[(row['nota'], row['colore_rombo'])].append(row['page'])

        for (text, color), pages in sorted(unique_sku_notes.items(), key=lambda x: x[0][0]):
            f.write(f"[{color}] {text}\n")
            f.write(f"   Pages: {', '.join(sorted(set(pages), key=int))}\n\n")

        f.write("\n=== PRODUCT NOTES (senza rombi) ===\n\n")
        for row in sorted(unique_product_rows, key=lambda x: int(x['page'])):
            f.write(f"Page {row['page']}: {row['nome_prodotto']}\n")
            f.write(f"   {row['note_prodotto']}\n\n")

    print(f"Summary saved to {summary_path}")

if __name__ == '__main__':
    main()
