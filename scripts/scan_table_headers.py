#!/usr/bin/env python3
"""
Scan all IDML tables and categorize their headers.
Outputs JSON data for HTML report generation.
"""
import os
import re
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict, Counter

IDML_DIR = '/home/user/checkimport/input/processing/IDML_unzipped'
OUTPUT_JSON = '/home/user/checkimport/output/v2/table_headers_analysis.json'


def extract_page_from_folder(folder_name):
    """Extract page number(s) from folder name."""
    match = re.match(r'^(\d{3})(?:-(\d{3}))?_', folder_name)
    if match:
        return match.group(1), match.group(2) or match.group(1)
    match = re.match(r'^pages_(\d{3})(?:-(\d{3}))?_', folder_name)
    if match:
        return match.group(1), match.group(2) or match.group(1)
    return None, None


def get_cell_text(cell):
    """Extract text content from a cell element."""
    texts = []
    for content in cell.iter():
        if content.tag == 'Content' and content.text:
            texts.append(content.text.strip())
    return ' '.join(texts).strip()


def parse_table_headers(table_elem):
    """Parse table and extract header row."""
    cells = {}
    for cell in table_elem.findall('.//Cell'):
        name = cell.get('Name', '')
        if ':' in name:
            col, row = name.split(':')
            col, row = int(col), int(row)
            if row == 0:  # Header row
                text = get_cell_text(cell)
                cells[col] = text

    # Build header string
    if cells:
        max_col = max(cells.keys())
        headers = [cells.get(i, '') for i in range(max_col + 1)]
        return ' | '.join(h if h else '[empty]' for h in headers)
    return None


def guess_table_type(header_str):
    """Guess table type based on header pattern."""
    header_lower = header_str.lower()

    # Price tables
    if 'codice articolo' in header_lower and 'prezzo' in header_lower:
        if 'descrizione' in header_lower:
            return 'PRICE_TABLE_WITH_DESC'
        elif 'lunghezza' in header_lower or 'lung.' in header_lower:
            return 'PRICE_TABLE_LENGTHS'
        elif 'frequenza' in header_lower:
            return 'PRICE_TABLE_RADIO'
        elif header_str.startswith('[empty]'):
            return 'PRICE_TABLE_WITH_IMAGE'
        else:
            return 'PRICE_TABLE_STANDARD'

    # Kit contents
    if 'kit' in header_lower or 'contenuto' in header_lower:
        return 'KIT_CONTENTS'

    # Technical specs
    if 'caratteristiche' in header_lower or 'dati tecnici' in header_lower:
        return 'TECH_SPECS'

    # Compatibility
    if 'compatibil' in header_lower:
        return 'COMPATIBILITY_TABLE'

    # Dimensions
    if 'dimensioni' in header_lower or 'misure' in header_lower:
        return 'DIMENSIONS'

    # Installation
    if 'installazione' in header_lower or 'schema' in header_lower:
        return 'INSTALLATION'

    # Layout/formatting tables
    if header_str == '[empty]' or all(h in ['[empty]', ''] for h in header_str.split(' | ')):
        return 'LAYOUT_TABLE'

    return 'OTHER'


def main():
    all_tables = []
    header_counts = Counter()
    type_counts = Counter()
    tables_by_type = defaultdict(list)

    idml_folders = sorted(os.listdir(IDML_DIR))

    for folder_name in idml_folders:
        folder_path = Path(IDML_DIR) / folder_name
        if not folder_path.is_dir():
            continue

        page_start, page_end = extract_page_from_folder(folder_name)
        if not page_start:
            continue

        stories_dir = folder_path / 'Stories'
        if not stories_dir.exists():
            continue

        for story_file in stories_dir.glob('*.xml'):
            try:
                tree = ET.parse(story_file)
                root = tree.getroot()
            except ET.ParseError:
                continue

            for table in root.iter('Table'):
                header_str = parse_table_headers(table)
                if header_str:
                    table_type = guess_table_type(header_str)
                    header_counts[header_str] += 1
                    type_counts[table_type] += 1

                    table_info = {
                        'folder': folder_name,
                        'page_start': page_start,
                        'page_end': page_end,
                        'header': header_str,
                        'type': table_type,
                        'column_count': len(header_str.split(' | '))
                    }
                    all_tables.append(table_info)
                    tables_by_type[table_type].append(table_info)

    # Prepare output data
    output = {
        'summary': {
            'total_tables': len(all_tables),
            'unique_headers': len(header_counts),
            'types': dict(type_counts.most_common())
        },
        'header_patterns': [
            {'header': h, 'count': c, 'type': guess_table_type(h)}
            for h, c in header_counts.most_common()
        ],
        'tables_by_type': {
            t: tables[:10]  # Sample of first 10 per type
            for t, tables in tables_by_type.items()
        },
        'price_tables': [t for t in all_tables if t['type'].startswith('PRICE_TABLE')]
    }

    # Write JSON
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Total tables found: {len(all_tables)}")
    print(f"Unique header patterns: {len(header_counts)}")
    print(f"\nTable types:")
    for t, c in type_counts.most_common():
        print(f"  {t}: {c}")

    return output


if __name__ == '__main__':
    main()
