#!/usr/bin/env python3
"""
Extract SKU notes and product notes from pre-unzipped IDML files.
Creates:
- Sku_Notes_Master_v1.csv (notes with diamond markers for SKUs)
- Product_Notes_Master_v1.csv (notes without diamonds for products)

Key insight: Descriptions with __logo__RefNote labels have ParentStory
pointing to diamond marker stories. The diamond color links to the note.
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

def extract_page_from_dirname(dirname):
    """Extract page number(s) from IDML directory name"""
    match = re.search(r'^(\d+)(?:-\d+)?_', dirname)
    if match:
        return match.group(1)
    match = re.search(r'pages_(\d+)', dirname)
    if match:
        return match.group(1)
    return None

def extract_product_name_from_dirname(dirname):
    """Extract product name from IDML directory name"""
    parts = dirname.split('_', 1)
    if len(parts) > 1 and parts[0].replace('-', '').replace('pages', '').isdigit():
        return parts[1].replace('_', ' ')
    return dirname.replace('_', ' ')

def color_to_name(color_code):
    """Convert CMYK color code to human-readable name"""
    if not color_code or color_code == 'default':
        return 'nero'
    color_map = {
        'C=0 M=0 Y=0 K=60': 'grigio',
        'C=0 M=100 Y=0 K=0': 'magenta',
        'C=100 M=0 Y=0 K=0': 'ciano',
        'C=0 M=0 Y=100 K=0': 'giallo',
        'C=0 M=0 Y=0 K=100': 'nero',
        'Black': 'nero',
    }
    return color_map.get(color_code, 'nero')

def read_story(story_path):
    """Read and return story XML content"""
    try:
        with open(story_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except:
        return ''

def get_story_id(content):
    """Extract Story Self ID from content"""
    match = re.search(r'Story Self="(u[a-f0-9]+)"', content)
    return match.group(1) if match else None

def find_diamond_stories(stories_dir):
    """Find all diamond marker stories (Wingdings 't') and their colors"""
    diamonds = {}  # story_id -> color

    for story_file in Path(stories_dir).glob('Story_*.xml'):
        content = read_story(story_file)
        if 'Wingdings' in content and '<Content>t</Content>' in content:
            story_id = get_story_id(content)
            if story_id:
                # Get color from FillColor
                color_match = re.search(r'FillColor="Color/([^"]+)"', content)
                if color_match:
                    diamonds[story_id] = color_match.group(1)
                else:
                    diamonds[story_id] = 'default'

    return diamonds

def find_accessory_notes(stories_dir):
    """Find all accessory notes (with ParentStory to diamond markers)"""
    notes = []  # list of {parent_story, text}

    note_styles = [
        'Accessories_gruppo%3aNote',
        'Accessories_1_gruppo%3aNote'
    ]

    for story_file in Path(stories_dir).glob('Story_*.xml'):
        content = read_story(story_file)

        for style in note_styles:
            if f'Infoblocks_gruppo%3a{style}' not in content:
                continue

            # Find ParentStory references within note paragraphs
            para_pattern = rf'ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/Infoblocks_gruppo%3a{re.escape(style)}"[^>]*>(.*?)</ParagraphStyleRange>'
            para_matches = re.findall(para_pattern, content, re.DOTALL)

            for para in para_matches:
                # Get ParentStory from embedded TextFrame
                parent_match = re.search(r'ParentStory="(u[a-f0-9]+)"', para)
                parent_story = parent_match.group(1) if parent_match else None

                # Get note text
                contents = re.findall(r'<Content>([^<]*)</Content>', para)
                text = ' '.join(c.strip() for c in contents if c.strip())

                if text and parent_story:
                    notes.append({
                        'parent_story': parent_story,
                        'text': text.replace('&apos;', "'")
                    })

    return notes

def find_descriptions_with_diamonds(stories_dir):
    """Find descriptions that have __logo__RefNote labels (diamond markers)"""
    descriptions = []  # list of {description, parent_story, story_id}

    desc_style = 'Description_gruppo%3aDescription'

    for story_file in Path(stories_dir).glob('Story_*.xml'):
        content = read_story(story_file)

        if desc_style not in content:
            continue

        # Check if this description has a RefNote label
        if '__logo__RefNote' not in content:
            continue

        story_id = get_story_id(content)

        # Get ParentStory from the RefNote TextFrame
        parent_match = re.search(r'Label.*?__logo__RefNote\d+__.*?ParentStory="(u[a-f0-9]+)"', content, re.DOTALL)
        if not parent_match:
            # Try reverse order (ParentStory before Label)
            parent_match = re.search(r'ParentStory="(u[a-f0-9]+)"[^>]*>.*?__logo__RefNote', content, re.DOTALL)

        parent_story = parent_match.group(1) if parent_match else None

        # Get description text
        contents = re.findall(r'<Content>([^<]*)</Content>', content)
        text = ' '.join(c.strip() for c in contents if c.strip())

        if text and parent_story:
            descriptions.append({
                'description': text.replace('&apos;', "'"),
                'parent_story': parent_story,
                'story_id': story_id
            })

    return descriptions

def find_skus_with_descriptions(stories_dir):
    """Find SKUs from image links AND their associated description ParentStory.

    Key insight: Stories containing image links (SKU.tif) also have TextFrames
    that reference the description story via ParentStory attribute.
    """
    sku_desc_map = []  # list of {sku, description_story_id, image_story_id}

    for story_file in Path(stories_dir).glob('Story_*.xml'):
        content = read_story(story_file)

        # Look for image links with SKU numbers in filename
        sku_match = re.search(r'LinkResourceURI="[^"]*[/\\](\d{5,7})\.tif"', content)
        if not sku_match:
            continue

        sku = sku_match.group(1)
        story_id = get_story_id(content)

        # Find the description ParentStory in the same story
        # The TextFrame with AppliedObjectStyle containing "Description" references the description
        desc_pattern = r'TextFrame[^>]*ParentStory="(u[a-f0-9]+)"[^>]*AppliedObjectStyle="[^"]*Description[^"]*"'
        desc_match = re.search(desc_pattern, content)

        if desc_match:
            desc_story_id = desc_match.group(1)
            sku_desc_map.append({
                'sku': sku,
                'description_story_id': desc_story_id,
                'image_story_id': story_id
            })

    return sku_desc_map

def find_skus_from_tables(stories_dir):
    """Find SKUs from table cells (infoblock_code_pgf style)"""
    skus = []  # list of {sku, story_id}

    for story_file in Path(stories_dir).glob('Story_*.xml'):
        content = read_story(story_file)

        if 'infoblock_code_pgf' not in content:
            continue

        story_id = get_story_id(content)
        codes = re.findall(r'<Content>(\d{5,7})</Content>', content)

        for code in codes:
            skus.append({'sku': code, 'story_id': story_id})

    return skus

def find_product_notes(stories_dir):
    """Find product-level notes (no diamond markers)"""
    notes = []

    note_styles = [
        'Images_gruppo%3aNote',
        'Special_Content_gruppo%3aWarning',
        'Technical_Specifications_gruppo%3aNote'
    ]

    for story_file in Path(stories_dir).glob('Story_*.xml'):
        content = read_story(story_file)

        for style in note_styles:
            if style not in content:
                continue

            pattern = rf'ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/{re.escape(style)}"[^>]*>(.*?)</ParagraphStyleRange>'
            matches = re.findall(pattern, content, re.DOTALL)

            for match in matches:
                contents = re.findall(r'<Content>([^<]+)</Content>', match)
                text = ' '.join(c.strip() for c in contents if c.strip())

                if text:
                    note_type = 'warning' if 'Warning' in style else 'note'
                    notes.append({
                        'text': text.replace('&apos;', "'"),
                        'type': note_type
                    })

    return notes

def process_idml_dir(idml_dir):
    """Process a single pre-unzipped IDML directory"""
    dirname = os.path.basename(idml_dir)
    page = extract_page_from_dirname(dirname)
    product = extract_product_name_from_dirname(dirname)

    if not page:
        return None

    stories_dir = os.path.join(idml_dir, 'Stories')
    if not os.path.exists(stories_dir):
        return None

    # Collect all data
    diamonds = find_diamond_stories(stories_dir)
    acc_notes = find_accessory_notes(stories_dir)
    descriptions = find_descriptions_with_diamonds(stories_dir)
    sku_desc_map = find_skus_with_descriptions(stories_dir)
    prod_notes = find_product_notes(stories_dir)

    # Build description_story_id -> SKU mapping
    desc_to_sku = {}
    for mapping in sku_desc_map:
        desc_to_sku[mapping['description_story_id']] = mapping['sku']

    # Build description_story_id -> description text mapping
    desc_text_map = {}
    for desc in descriptions:
        desc_text_map[desc['story_id']] = desc

    # Match: SKU -> Description -> Diamond -> Note
    sku_note_entries = []

    for desc in descriptions:
        desc_story_id = desc['story_id']
        diamond_story_id = desc['parent_story']  # Points to diamond marker

        # Get diamond color
        color = diamonds.get(diamond_story_id, 'unknown')
        color_name = color_to_name(color)

        # Get SKU for this description
        sku = desc_to_sku.get(desc_story_id, '')

        # Find notes that reference the same diamond OR have same color
        matched_notes = []

        for note in acc_notes:
            note_diamond = note['parent_story']
            note_color = diamonds.get(note_diamond, 'unknown')

            # Match by same diamond reference
            if note_diamond == diamond_story_id:
                matched_notes.append(note)
            # OR match by same color
            elif color_to_name(note_color) == color_name:
                matched_notes.append(note)

        # Deduplicate notes
        seen_texts = set()
        unique_notes = []
        for note in matched_notes:
            if note['text'] not in seen_texts:
                seen_texts.add(note['text'])
                unique_notes.append(note)

        for note in unique_notes:
            sku_note_entries.append({
                'page': page,
                'tipo_componente': 'ACCESSORI',
                'descrizione_breve': desc['description'][:80],
                'sku': sku,
                'nota': note['text'],
                'colore_rombo': color_name
            })

    return {
        'page': page,
        'product': product,
        'dirname': dirname,
        'sku_notes': sku_note_entries,
        'product_notes': prod_notes
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

    # === Build SKU Notes CSV ===
    sku_notes_path = '/home/user/checkimport/output/Sku_Notes_Master_v1.csv'
    all_sku_rows = []

    for result in unique_results:
        all_sku_rows.extend(result['sku_notes'])

    # Deduplicate by (page, sku, nota)
    seen = set()
    unique_sku_rows = []
    for row in all_sku_rows:
        key = (row['page'], row['sku'], row['nota'][:50])
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

    # === Build Product Notes CSV ===
    product_notes_path = '/home/user/checkimport/output/Product_Notes_Master_v1.csv'
    all_product_rows = []

    for result in unique_results:
        page = result['page']
        product = result['product']
        for note in result['product_notes']:
            all_product_rows.append({
                'page': page,
                'nome_prodotto': product,
                'tipo_nota': note.get('type', 'note'),
                'note_prodotto': note['text']
            })

    # Deduplicate
    seen = set()
    unique_product_rows = []
    for row in all_product_rows:
        key = (row['page'], row['note_prodotto'][:50])
        if key not in seen:
            seen.add(key)
            unique_product_rows.append(row)

    with open(product_notes_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f,
            fieldnames=['page', 'nome_prodotto', 'tipo_nota', 'note_prodotto'],
            delimiter=';')
        writer.writeheader()
        for row in unique_product_rows:
            writer.writerow(row)

    print(f"Extracted {len(unique_product_rows)} product note entries to {product_notes_path}")

    # === Summary ===
    summary_path = '/home/user/checkimport/output/notes_summary.txt'
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("=== SKU NOTES (con rombi colorati) ===\n\n")

        by_note = defaultdict(list)
        for row in unique_sku_rows:
            by_note[(row['nota'][:60], row['colore_rombo'])].append(f"{row['page']}:{row['sku']}")

        for (text, color), refs in sorted(by_note.items()):
            f.write(f"[{color}] {text}...\n")
            f.write(f"   Refs: {', '.join(refs)}\n\n")

        f.write("\n=== PRODUCT NOTES (senza rombi) ===\n\n")
        for row in sorted(unique_product_rows, key=lambda x: int(x['page'])):
            f.write(f"Page {row['page']}: {row['nome_prodotto']}\n")
            f.write(f"   [{row['tipo_nota']}] {row['note_prodotto'][:100]}...\n\n")

    print(f"Summary saved to {summary_path}")

if __name__ == '__main__':
    main()
