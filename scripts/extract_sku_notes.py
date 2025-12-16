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

def extract_page_from_filename(filename):
    """Extract page number(s) from IDML filename"""
    match = re.search(r'^(\d+)', os.path.basename(filename))
    if match:
        return match.group(1)
    # Try pages_XXX format
    match = re.search(r'pages_(\d+)', os.path.basename(filename))
    if match:
        return match.group(1)
    return None

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
    # Look for FillColor in CharacterStyleRange
    color_match = re.search(r'FillColor="Color/([^"]+)"', xml_content)
    if color_match:
        return color_match.group(1)
    return 'default'

def extract_sku_codes(xml_content):
    """Extract SKU codes from table cell stories"""
    # Look for 6-digit codes in infoblock_code_pgf paragraphs
    if 'infoblock_code_pgf' in xml_content:
        codes = re.findall(r'<Content>(\d{5,7})</Content>', xml_content)
        return codes
    return []

def extract_product_descriptions(xml_content):
    """Extract product descriptions and their note references"""
    results = []
    # Check if this is a description story
    if 'Description_gruppo%3aDescription' in xml_content:
        text = get_text_content(xml_content)
        ref_notes = find_ref_notes(xml_content)
        if text:
            results.append({
                'description': text,
                'ref_notes': ref_notes
            })
    return results

def extract_notes_from_story(xml_content):
    """Extract notes (text after diamond markers)"""
    notes = []
    # Look for note style paragraphs
    if 'Accessories_gruppo%3aNote' in xml_content:
        # Find all content after potential diamond markers
        # The structure is: TextFrame (diamond) + Content (note text)
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

def process_idml(idml_path, output_dir):
    """Process a single IDML file and extract notes data"""
    page = extract_page_from_filename(idml_path)
    if not page:
        return []

    results = []
    stories = {}
    descriptions = []
    sku_codes = []
    notes = []
    diamond_stories = {}

    try:
        with zipfile.ZipFile(idml_path, 'r') as zf:
            # Read all stories
            for name in zf.namelist():
                if name.startswith('Stories/') and name.endswith('.xml'):
                    content = zf.read(name).decode('utf-8', errors='ignore')
                    story_id = re.search(r'Story Self="(u[a-f0-9]+)"', content)
                    if story_id:
                        stories[story_id.group(1)] = content

            # Extract different types of content
            for story_id, content in stories.items():
                # Extract product descriptions with ref notes
                descs = extract_product_descriptions(content)
                for d in descs:
                    d['story_id'] = story_id
                descriptions.extend(descs)

                # Extract SKU codes
                codes = extract_sku_codes(content)
                for code in codes:
                    sku_codes.append({'code': code, 'story_id': story_id})

                # Extract notes
                note_list = extract_notes_from_story(content)
                notes.extend(note_list)

                # Check for Wingdings diamond stories
                if 'Wingdings' in content and '<Content>t</Content>' in content:
                    color = get_diamond_color(content)
                    diamond_stories[story_id] = color

    except Exception as e:
        print(f"Error processing {idml_path}: {e}")
        return []

    # Build results linking descriptions to notes and SKUs
    # This is complex because we need to match by layout proximity
    # For now, we'll output what we find for manual verification

    for note in notes:
        parent = note.get('parent_story', '')
        color = diamond_stories.get(parent, 'unknown')
        note['color'] = color

    return {
        'page': page,
        'file': os.path.basename(idml_path),
        'descriptions': descriptions,
        'sku_codes': sku_codes,
        'notes': notes,
        'diamond_colors': diamond_stories
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
                result = process_idml(os.path.join(idml_dir, f), '/tmp/idml_notes')
                if result:
                    all_results.append(result)

    # Output CSV with found notes
    output_path = '/home/user/checkimport/output/Sku_Notes_Master_v1.csv'

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['page', 'tipo_componente', 'descrizione_breve', 'sku', 'nota', 'colore_rombo'])

        for result in all_results:
            page = result['page']
            notes = result['notes']
            descriptions = result['descriptions']
            skus = result['sku_codes']

            # For each note found, try to output with associated info
            for note in notes:
                note_text = note['text']
                color = note.get('color', 'unknown')

                # Find descriptions that reference this note
                for desc in descriptions:
                    if desc['ref_notes']:
                        desc_text = desc['description']
                        # Get first associated SKU (simplified)
                        sku = skus[0]['code'] if skus else ''
                        writer.writerow([
                            page,
                            'ACCESSORI',  # Default, would need more parsing
                            desc_text[:50] if len(desc_text) > 50 else desc_text,
                            sku,
                            note_text,
                            color
                        ])

    print(f"Extracted notes to {output_path}")

    # Also output raw data for analysis
    raw_path = '/home/user/checkimport/output/sku_notes_raw.txt'
    with open(raw_path, 'w', encoding='utf-8') as f:
        for result in sorted(all_results, key=lambda x: x['page'] or '0'):
            f.write(f"\n=== Page {result['page']} ({result['file']}) ===\n")

            f.write("Descriptions with notes:\n")
            for d in result['descriptions']:
                if d['ref_notes']:
                    f.write(f"  - {d['description'][:80]}... refs: {d['ref_notes']}\n")

            f.write("SKU codes:\n")
            for s in result['sku_codes']:
                f.write(f"  - {s['code']}\n")

            f.write("Notes:\n")
            for n in result['notes']:
                f.write(f"  - [{n.get('color', '?')}] {n['text']}\n")

    print(f"Raw data saved to {raw_path}")

if __name__ == '__main__':
    main()
