#!/usr/bin/env python3
"""
Scan all IDML files for badge and certification images.
Generates JSON data for HTML report.
"""
import os
import re
import json
from pathlib import Path
from collections import defaultdict, Counter

IDML_DIR = '/home/user/checkimport/input/processing/IDML_unzipped'
OUTPUT_JSON = '/home/user/checkimport/output/v2/badges_certifications_analysis.json'

# Known badge/certification file patterns
BADGE_PATTERNS = {
    'CE': r'logo_CE',
    'Safe': r'logo_safezone',
    'Green': r'logo_greentech',
    'Omnidec': r'logo_Omnidec',
    '2Easy': r'logo_2easy',
    'Hybrid': r'logo_Hybrid',
    'Double_Insulation': r'logo_double_insulation',
    'Wireless': r'logo_wireless',
}


def extract_page_from_folder(folder_name):
    """Extract page number(s) from folder name."""
    match = re.match(r'^(\d{3})(?:-(\d{3}))?_(.+)$', folder_name)
    if match:
        return match.group(1), match.group(2) or match.group(1), match.group(3)
    return None, None, folder_name


def scan_idml_for_links(folder_path):
    """Scan IDML folder for all linked resources."""
    links = []
    spreads_dir = folder_path / 'Spreads'
    master_dir = folder_path / 'MasterSpreads'

    for search_dir in [spreads_dir, master_dir]:
        if search_dir.exists():
            for xml_file in search_dir.glob('*.xml'):
                try:
                    content = xml_file.read_text(encoding='utf-8')
                    # Extract all LinkResourceURI values
                    for match in re.finditer(r'LinkResourceURI="([^"]+)"', content):
                        links.append(match.group(1))
                except Exception:
                    pass
    return links


def identify_badges(links):
    """Identify badges from link list."""
    badges = set()
    badge_files = []

    for link in links:
        filename = link.split('/')[-1].lower()
        for badge_name, pattern in BADGE_PATTERNS.items():
            if re.search(pattern.lower(), filename):
                badges.add(badge_name)
                badge_files.append((badge_name, link.split('/')[-1]))
                break

    return sorted(badges), badge_files


def main():
    all_pages = []
    badge_usage = Counter()
    pages_by_badge = defaultdict(list)
    pages_missing_badges = []

    idml_folders = sorted(os.listdir(IDML_DIR))

    for folder_name in idml_folders:
        folder_path = Path(IDML_DIR) / folder_name
        if not folder_path.is_dir():
            continue

        page_start, page_end, product_name = extract_page_from_folder(folder_name)
        if not page_start:
            continue

        # Scan for links
        links = scan_idml_for_links(folder_path)
        badges, badge_files = identify_badges(links)

        page_info = {
            'folder': folder_name,
            'page_start': page_start,
            'page_end': page_end,
            'product': product_name.replace('_', ' '),
            'badges': badges,
            'badge_files': badge_files,
            'has_ce': 'CE' in badges,
            'has_safe': 'Safe' in badges,
            'has_green': 'Green' in badges,
        }
        all_pages.append(page_info)

        for badge in badges:
            badge_usage[badge] += 1
            pages_by_badge[badge].append(f"{page_start}-{page_end}")

        # Track pages without any badges
        if not badges:
            pages_missing_badges.append(page_info)

    # Find specific issues (like 770N)
    issues = []
    for page in all_pages:
        if '770N' in page['product']:
            if not page['badges']:
                issues.append({
                    'page': f"{page['page_start']}-{page['page_end']}",
                    'product': page['product'],
                    'issue': 'Missing all badges (should have Safe, Green, CE)',
                    'severity': 'HIGH'
                })

    # Prepare output
    output = {
        'summary': {
            'total_pages': len(all_pages),
            'pages_with_badges': len([p for p in all_pages if p['badges']]),
            'pages_without_badges': len(pages_missing_badges),
            'badge_usage': dict(badge_usage.most_common()),
        },
        'all_pages': all_pages,
        'pages_missing_badges': pages_missing_badges[:50],  # First 50
        'issues': issues,
        'badge_files_reference': {
            'CE': 'logo_CE_bw.ai',
            'Safe': 'logo_safezone_cmyk.ai',
            'Green': 'logo_greentech_cmyk.ai',
            'Omnidec': 'logo_Omnidec_bw.ai',
            '2Easy': 'logo_2easy_bw.ai',
            'Hybrid': 'logo_Hybrid_bw.ai',
            'Double_Insulation': 'logo_double_insulation.ai',
            'Wireless': 'logo_wireless.tif',
        }
    }

    # Write JSON
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Total pages scanned: {len(all_pages)}")
    print(f"Pages with badges: {len([p for p in all_pages if p['badges']])}")
    print(f"Pages without badges: {len(pages_missing_badges)}")
    print(f"\nBadge usage:")
    for badge, count in badge_usage.most_common():
        print(f"  {badge}: {count}")
    print(f"\nIssues found: {len(issues)}")

    return output


if __name__ == '__main__':
    main()
