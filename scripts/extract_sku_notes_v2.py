#!/usr/bin/env python3
"""
Extract SKU notes with diamond markers from IDML files.
Creates Sku_Notes_Master_v1.csv
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
    # Match patterns like "080-081" or "080"
    match = re.search(r'^(\d+)(?:-\d+)?_', base)
    if match:
        return match.group(1)
    # Try pages_XXX format
    match = re.search(r'pages_(\d+)', base)
    if match:
        return match.group(1)
    return None

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

def extract_notes_from_story(xml_content):
    """Extract notes (text after diamond markers)"""
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

def process_idml(idml_path):
    """Process a single IDML file and extract notes data"""
    page = extract_page_from_filename(idml_path)
    if not page:
        return []

    stories = {}
    descriptions = []
    sku_codes = []
    notes = []
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

                note_list = extract_notes_from_story(content)
                notes.extend(note_list)

                if 'Wingdings' in content and '<Content>t</Content>' in content:
                    color = get_diamond_color(content)
                    diamond_stories[story_id] = color

    except Exception as e:
        print(f"Error processing {idml_path}: {e}")
        return []

    # Assign colors to notes
    for note in notes:
        parent = note.get('parent_story', '')
        color = diamond_stories.get(parent, 'unknown')
        note['color'] = color

    return {
        'page': page,
        'file': os.path.basename(idml_path),
        'descriptions': descriptions,
        'sku_codes': [s['code'] for s in sku_codes],
        'notes': notes
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
    all_results.sort(key=lambda x: x['page'] or '0')

    # Remove duplicates (same page from both dirs)
    seen_pages = set()
    unique_results = []
    for r in all_results:
        key = (r['page'], r['file'])
        if key not in seen_pages:
            seen_pages.add(key)
            unique_results.append(r)

    # Build output CSV
    output_path = '/home/user/checkimport/output/Sku_Notes_Master_v1.csv'
    rows = []

    for result in unique_results:
        page = result['page']
        notes = result['notes']
        descriptions = result['descriptions']
        skus = result['sku_codes']

        if not notes:
            continue

        # For each note, find the associated description and SKU
        for note in notes:
            note_text = note['text'].replace('&apos;', "'")
            color = color_to_name(note.get('color', 'unknown'))

            # Find descriptions with RefNote markers
            for desc in descriptions:
                if desc['ref_notes']:
                    desc_text = desc['description'].replace('&apos;', "'")
                    # Find first SKU associated with this description
                    # (In reality, we'd need to trace the layout hierarchy)
                    sku = ''
                    if skus:
                        sku = skus[0]  # Simplified - take first SKU on page

                    rows.append({
                        'page': page,
                        'tipo_componente': 'ACCESSORI',
                        'descrizione_breve': desc_text[:80] if len(desc_text) > 80 else desc_text,
                        'sku': sku,
                        'nota': note_text,
                        'colore_rombo': color
                    })

    # Deduplicate rows by (page, nota, colore_rombo)
    seen = set()
    unique_rows = []
    for row in rows:
        key = (row['page'], row['nota'], row['colore_rombo'])
        if key not in seen:
            seen.add(key)
            unique_rows.append(row)

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f,
            fieldnames=['page', 'tipo_componente', 'descrizione_breve', 'sku', 'nota', 'colore_rombo'],
            delimiter=';')
        writer.writeheader()
        for row in unique_rows:
            writer.writerow(row)

    print(f"Extracted {len(unique_rows)} note entries to {output_path}")

    # Also create a summary of all unique notes
    unique_notes = defaultdict(list)
    for result in unique_results:
        for note in result['notes']:
            text = note['text'].replace('&apos;', "'")
            color = color_to_name(note.get('color', 'unknown'))
            unique_notes[(text, color)].append(result['page'])

    summary_path = '/home/user/checkimport/output/sku_notes_summary.txt'
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("=== UNIQUE NOTES WITH DIAMOND MARKERS ===\n\n")
        for (text, color), pages in sorted(unique_notes.items(), key=lambda x: x[0][0]):
            f.write(f"[{color}] {text}\n")
            f.write(f"   Pages: {', '.join(sorted(set(pages)))}\n\n")

    print(f"Summary saved to {summary_path}")

if __name__ == '__main__':
    main()
