#!/usr/bin/env python3
"""
Extract icon/badge marks from IDML files.
Finds Innovation_Marks captions with Highlight (bold) styling.
"""

import os
import re
from pathlib import Path
import csv

IDML_DIR = Path('/home/user/checkimport/input/processing/IDML_unzipped')
OUTPUT_CSV = Path('/home/user/checkimport/output/Icon_Marks_Master_v1.csv')

def extract_page_from_dirname(dirname):
    """Extract page number from directory name"""
    match = re.search(r'^(\d+)(?:-\d+)?_', dirname)
    if match:
        return match.group(1)
    match = re.search(r'pages_(\d+)', dirname)
    if match:
        return match.group(1)
    return None

def extract_product_from_dirname(dirname):
    """Extract product name from directory name"""
    parts = dirname.split('_', 1)
    if len(parts) > 1 and parts[0].replace('-', '').replace('pages', '').isdigit():
        return parts[1].replace('_', ' ')
    return dirname.replace('_', ' ')

def read_story(path):
    """Read story XML content"""
    try:
        return path.read_text(encoding='utf-8', errors='ignore')
    except:
        return ''

def extract_icon_marks(stories_dir):
    """Extract icon mark captions from Innovation_Marks paragraphs"""
    marks = []

    # Pattern for Innovation_Marks captions
    mark_styles = [
        'Innovation_Marks_gruppo%3aMain_Mark_S',  # SAFEzone
        'Innovation_Marks_gruppo%3aMain_Mark_G',  # GREENtech
        'Innovation_Marks_gruppo%3aMain_Mark',    # Generic
    ]

    for story_file in Path(stories_dir).glob('Story_*.xml'):
        content = read_story(story_file)

        for style in mark_styles:
            if style not in content:
                continue

            # Determine mark type
            if 'Mark_S' in style:
                mark_type = 'Safe'
            elif 'Mark_G' in style:
                mark_type = 'Green'
            else:
                mark_type = 'Other'

            # Find caption paragraphs
            caption_pattern = rf'ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/{re.escape(style)}_gruppo%3aCaption"[^>]*>(.*?)</ParagraphStyleRange>'
            caption_matches = re.findall(caption_pattern, content, re.DOTALL)

            for caption in caption_matches:
                # Extract Highlight (bold) text
                highlight_pattern = r'CharacterStyleRange AppliedCharacterStyle="CharacterStyle/Highlight"[^>]*>\s*<Content>([^<]+)</Content>'
                highlight_matches = re.findall(highlight_pattern, caption)

                # Extract normal text
                normal_pattern = r'CharacterStyleRange AppliedCharacterStyle="CharacterStyle/\$ID/\[No character style\]"[^>]*>.*?<Content>([^<]+)</Content>'
                normal_matches = re.findall(normal_pattern, caption, re.DOTALL)

                bold_text = ' '.join(h.strip() for h in highlight_matches if h.strip())
                normal_text = ' '.join(n.strip() for n in normal_matches if n.strip())

                if bold_text:
                    marks.append({
                        'mark_type': mark_type,
                        'bold_text': bold_text,
                        'normal_text': normal_text,
                        'full_text': f"<b>{bold_text}</b><br>{normal_text}" if normal_text else f"<b>{bold_text}</b>"
                    })

    return marks

def process_all_idmls():
    """Process all IDML directories"""
    results = []

    for idml_dir in sorted(IDML_DIR.iterdir()):
        if not idml_dir.is_dir():
            continue

        stories_dir = idml_dir / 'Stories'
        if not stories_dir.exists():
            continue

        page = extract_page_from_dirname(idml_dir.name)
        product = extract_product_from_dirname(idml_dir.name)

        if not page:
            continue

        marks = extract_icon_marks(stories_dir)

        if marks:
            # Combine marks into badge_sistemi format
            badge_parts = []
            for m in marks:
                badge_parts.append(f"{m['mark_type']}|{m['full_text']}")

            badge_sistemi = ' '.join(badge_parts)

            results.append({
                'page': page,
                'product': product,
                'dirname': idml_dir.name,
                'marks': marks,
                'badge_sistemi': badge_sistemi
            })

    return results

def main():
    print("Extracting icon marks from IDMLs...")
    results = process_all_idmls()

    print(f"\nFound icon marks in {len(results)} IDMLs")

    # Save to CSV
    rows = []
    for r in results:
        for m in r['marks']:
            rows.append({
                'page': r['page'],
                'product': r['product'],
                'mark_type': m['mark_type'],
                'bold_text': m['bold_text'],
                'normal_text': m['normal_text'],
                'full_html': m['full_text']
            })

    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['page', 'product', 'mark_type', 'bold_text', 'normal_text', 'full_html'], delimiter=';')
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} icon mark entries to {OUTPUT_CSV}")

    # Show sample
    print("\n=== Sample Results ===")
    for r in results[:10]:
        print(f"\nPage {r['page']}: {r['product']}")
        print(f"  badge_sistemi: {r['badge_sistemi'][:100]}...")

if __name__ == '__main__':
    main()
