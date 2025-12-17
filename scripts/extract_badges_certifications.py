#!/usr/bin/env python3
"""
Extract badges, certifications, and QR codes from IDML files.
Outputs CSV with HTML styling for text.
"""
import os
import re
import csv
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict
from urllib.parse import unquote

IDML_DIR = '/home/user/checkimport/input/processing/IDML_unzipped'
OUTPUT_CSV = '/home/user/checkimport/output/v2/FAAC_Complete_v2_Badges_Certifications.csv'

# Badge/certification patterns
BADGE_PATTERNS = {
    'CE': r'logo_CE',
    'Safe': r'logo_safezone',
    'Green': r'logo_greentech',
    'Omnidec': r'logo_Omnidec',
    '2Easy': r'logo_2easy',
    'Hybrid': r'logo_Hybrid',
    'Classe_II': r'logo_double_insulation|classe.*ii',
    'Wireless': r'logo_wireless',
}

QR_PATTERN = r'QR[_-]'


def extract_page_from_folder(folder_name):
    """Extract page number(s) and product name from folder name."""
    match = re.match(r'^(\d{3})(?:-(\d{3}))?_(.+)$', folder_name)
    if match:
        return match.group(1), match.group(2) or match.group(1), match.group(3).replace('_', ' ')
    return None, None, folder_name


def get_filename_from_uri(uri):
    """Extract clean filename from LinkResourceURI."""
    if not uri:
        return ''
    # Get the last part of the path
    filename = uri.split('/')[-1]
    # URL decode
    filename = unquote(filename)
    return filename


def identify_badge(filename):
    """Identify badge type from filename."""
    filename_lower = filename.lower()
    for badge_name, pattern in BADGE_PATTERNS.items():
        if re.search(pattern.lower(), filename_lower):
            return badge_name
    return None


def is_qr_code(filename):
    """Check if filename is a QR code."""
    return bool(re.search(QR_PATTERN, filename, re.IGNORECASE))


def scan_xml_for_links(xml_path):
    """Scan XML file for all linked images."""
    links = []
    try:
        with open(xml_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find all LinkResourceURI
        for match in re.finditer(r'LinkResourceURI="([^"]+)"', content):
            uri = match.group(1)
            filename = get_filename_from_uri(uri)
            links.append({
                'uri': uri,
                'filename': filename
            })
    except Exception as e:
        pass
    return links


def extract_styled_text_from_story(xml_path):
    """Extract text with styling information from Story XML."""
    styled_texts = []
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Find all CharacterStyleRange elements
        for csr in root.iter('CharacterStyleRange'):
            style = csr.get('AppliedCharacterStyle', '')
            font_style = csr.get('FontStyle', '')

            # Check for bold
            is_bold = 'Bold' in font_style or 'bold' in style.lower()

            # Get text content
            for content in csr.iter('Content'):
                if content.text:
                    text = content.text.strip()
                    if text:
                        styled_texts.append({
                            'text': text,
                            'style': style,
                            'font_style': font_style,
                            'is_bold': is_bold
                        })
    except Exception:
        pass
    return styled_texts


def format_text_with_html(text, is_bold):
    """Format text with HTML tags based on styling."""
    if is_bold:
        return f"<b>{text}</b>"
    return text


def scan_idml_folder(folder_path):
    """Scan an IDML folder for badges, certifications, and QR codes."""
    result = {
        'badges': [],
        'qr_codes': [],
        'styled_texts': []
    }

    # Scan Spreads
    spreads_dir = folder_path / 'Spreads'
    if spreads_dir.exists():
        for xml_file in spreads_dir.glob('*.xml'):
            links = scan_xml_for_links(xml_file)
            for link in links:
                badge = identify_badge(link['filename'])
                if badge:
                    result['badges'].append({
                        'type': badge,
                        'file': link['filename'],
                        'source': 'Spreads'
                    })
                elif is_qr_code(link['filename']):
                    result['qr_codes'].append({
                        'file': link['filename'],
                        'source': 'Spreads'
                    })

    # Scan Stories
    stories_dir = folder_path / 'Stories'
    if stories_dir.exists():
        for xml_file in stories_dir.glob('*.xml'):
            # Check for badge/QR links
            links = scan_xml_for_links(xml_file)
            for link in links:
                badge = identify_badge(link['filename'])
                if badge:
                    # Check if already added from Spreads
                    existing = [b for b in result['badges'] if b['type'] == badge]
                    if not existing:
                        result['badges'].append({
                            'type': badge,
                            'file': link['filename'],
                            'source': 'Stories'
                        })
                elif is_qr_code(link['filename']):
                    existing = [q for q in result['qr_codes'] if q['file'] == link['filename']]
                    if not existing:
                        result['qr_codes'].append({
                            'file': link['filename'],
                            'source': 'Stories'
                        })

            # Extract styled text
            styled = extract_styled_text_from_story(xml_file)
            result['styled_texts'].extend(styled)

    # Scan MasterSpreads
    master_dir = folder_path / 'MasterSpreads'
    if master_dir.exists():
        for xml_file in master_dir.glob('*.xml'):
            links = scan_xml_for_links(xml_file)
            for link in links:
                badge = identify_badge(link['filename'])
                if badge:
                    existing = [b for b in result['badges'] if b['type'] == badge]
                    if not existing:
                        result['badges'].append({
                            'type': badge,
                            'file': link['filename'],
                            'source': 'MasterSpreads'
                        })

    return result


def main():
    all_products = []

    idml_folders = sorted(os.listdir(IDML_DIR))

    for folder_name in idml_folders:
        folder_path = Path(IDML_DIR) / folder_name
        if not folder_path.is_dir():
            continue

        page_start, page_end, product_name = extract_page_from_folder(folder_name)
        if not page_start:
            continue

        # Scan folder
        result = scan_idml_folder(folder_path)

        # Organize badges
        badges_list = sorted(set(b['type'] for b in result['badges']))
        badge_files = {b['type']: b['file'] for b in result['badges']}

        # QR codes
        qr_files = [q['file'] for q in result['qr_codes']]

        # Check for badge-related styled text (text near badges)
        # Look for text that might be labels or descriptions
        badge_texts = []
        for st in result['styled_texts']:
            text_lower = st['text'].lower()
            # Check if text relates to badges/certifications
            if any(kw in text_lower for kw in ['ce', 'safe', 'green', 'omnidec', '2easy', 'hybrid', 'classe', 'wireless', 'certificat']):
                formatted = format_text_with_html(st['text'], st['is_bold'])
                if formatted not in badge_texts:
                    badge_texts.append(formatted)

        product_data = {
            'page_start': page_start,
            'page_end': page_end,
            'product': product_name,
            'folder': folder_name,
            'CE': 'logo_CE_bw.ai' if 'CE' in badges_list else '',
            'Safe': 'logo_safezone_cmyk.ai' if 'Safe' in badges_list else '',
            'Green': 'logo_greentech_cmyk.ai' if 'Green' in badges_list else '',
            'Omnidec': 'logo_Omnidec_bw.ai' if 'Omnidec' in badges_list else '',
            '2Easy': 'logo_2easy_bw.ai' if '2Easy' in badges_list else '',
            'Hybrid': 'logo_Hybrid_bw.ai' if 'Hybrid' in badges_list else '',
            'Classe_II': 'logo_double_insulation.ai' if 'Classe_II' in badges_list else '',
            'Wireless': 'logo_wireless.tif' if 'Wireless' in badges_list else '',
            'all_badges': ';'.join(badges_list),
            'badge_files': ';'.join(badge_files.values()),
            'qr_code': qr_files[0] if qr_files else '',
            'qr_codes_all': ';'.join(qr_files),
            'badge_texts_styled': ';'.join(badge_texts[:5]) if badge_texts else ''  # First 5 relevant texts
        }

        all_products.append(product_data)

    # Write CSV
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

    fieldnames = [
        'page_start', 'page_end', 'product', 'folder',
        'CE', 'Safe', 'Green', 'Omnidec', '2Easy', 'Hybrid', 'Classe_II', 'Wireless',
        'all_badges', 'badge_files', 'qr_code', 'qr_codes_all', 'badge_texts_styled'
    ]

    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(all_products)

    # Summary stats
    print(f"Total products scanned: {len(all_products)}")

    badge_counts = defaultdict(int)
    for p in all_products:
        for badge in ['CE', 'Safe', 'Green', 'Omnidec', '2Easy', 'Hybrid', 'Classe_II', 'Wireless']:
            if p[badge]:
                badge_counts[badge] += 1

    print("\nBadge counts:")
    for badge, count in sorted(badge_counts.items(), key=lambda x: -x[1]):
        print(f"  {badge}: {count}")

    qr_count = sum(1 for p in all_products if p['qr_code'])
    print(f"\nProducts with QR codes: {qr_count}")

    print(f"\nCSV saved to: {OUTPUT_CSV}")


if __name__ == '__main__':
    main()
