#!/usr/bin/env python3
"""
Compare Data Elena P.xlsx with FAAC_master_data_v2.xlsx
Research differences in IDML files
Create HTML error report
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import re
import os

BASE = Path('/home/user/checkimport')
ELENA_FILE = BASE / 'input/processing/Data Elena P.xlsx'
MASTER_FILE = BASE / 'output/FAAC_master_data_v2.xlsx'
IDML_DIR = BASE / 'input/processing/IDML_unzipped'
OUTPUT_HTML = BASE / 'output/comparison_report.html'

def load_data():
    """Load both Excel files"""
    elena_prod = pd.read_excel(ELENA_FILE, sheet_name='prodotti')
    elena_sku = pd.read_excel(ELENA_FILE, sheet_name='sku')
    master_prod = pd.read_excel(MASTER_FILE, sheet_name='prodotti')
    master_sku = pd.read_excel(MASTER_FILE, sheet_name='sku')

    # Fix Elena SKU first column name
    elena_sku = elena_sku.rename(columns={elena_sku.columns[0]: 'codice_sku'})

    # Skip header rows
    elena_prod = elena_prod.iloc[1:].copy()
    elena_sku = elena_sku.iloc[1:].copy()
    master_prod = master_prod.iloc[1:].copy()
    master_sku = master_sku.iloc[1:].copy()

    return elena_prod, elena_sku, master_prod, master_sku

def find_column_errors(elena_prod, elena_sku):
    """Find column naming errors in Elena file"""
    errors = []

    # Check for typos
    if 'immagne_schema' in elena_prod.columns:
        errors.append({
            'type': 'Typo',
            'sheet': 'prodotti',
            'issue': 'Column "immagne_schema" should be "immagine_schema"',
            'severity': 'warning'
        })

    # Check first column issue
    if elena_sku.columns[0] == 'codice_sku':  # After rename
        errors.append({
            'type': 'Wrong Header',
            'sheet': 'sku',
            'issue': 'First column header was "E850S incorporata" instead of "codice_sku"',
            'severity': 'error'
        })

    return errors

def find_image_sku_mismatches(elena_sku):
    """Find SKUs with mismatched image filenames"""
    mismatches = []

    for _, row in elena_sku.iterrows():
        sku = str(row['codice_sku'])
        img = str(row.get('immagine_sku', ''))

        if pd.isna(row.get('immagine_sku')) or img == 'nan':
            continue

        # Check if SKU is in image filename
        if sku not in img and len(sku) >= 5:
            mismatches.append({
                'sku': sku,
                'image': img,
                'expected': f'{sku}.tif'
            })

    return mismatches

def find_missing_products(elena_prod, master_prod):
    """Find products missing in each file"""
    elena_products = set(str(x) for x in elena_prod['nome_prodotto'].dropna().unique() if str(x) != 'nan')
    master_products = set(str(x) for x in master_prod['nome_prodotto'].dropna().unique() if str(x) != 'nan')

    only_elena = elena_products - master_products
    only_master = master_products - elena_products
    common = elena_products & master_products

    return only_elena, only_master, common

def find_missing_skus(elena_sku, master_sku):
    """Find SKUs missing in each file"""
    elena_skus = set(str(x) for x in elena_sku['codice_sku'].dropna().unique() if str(x) != 'nan')
    master_skus = set(str(x) for x in master_sku['codice_sku'].dropna().unique() if str(x) != 'nan')

    only_elena = elena_skus - master_skus
    only_master = master_skus - elena_skus
    common = elena_skus & master_skus

    return only_elena, only_master, common

def verify_sku_in_idml(sku):
    """Check if SKU exists in IDML files"""
    for idml_dir in IDML_DIR.glob('*'):
        stories_dir = idml_dir / 'Stories'
        if stories_dir.exists():
            for story in stories_dir.glob('Story_*.xml'):
                try:
                    content = story.read_text(errors='ignore')
                    if f'<Content>{sku}</Content>' in content:
                        return True, idml_dir.name
                except:
                    pass
    return False, None

def find_value_differences(elena_sku, master_sku, common_skus):
    """Find value differences for common SKUs"""
    differences = []
    compare_cols = ['descrizione_breve', 'tipo_componente', 'nome_modello',
                    'tensione_alimentazione', 'potenza_massima']

    for sku in list(common_skus)[:50]:  # Limit for performance
        elena_row = elena_sku[elena_sku['codice_sku'].astype(str) == sku]
        master_row = master_sku[master_sku['codice_sku'].astype(str) == sku]

        if elena_row.empty or master_row.empty:
            continue

        for col in compare_cols:
            if col in elena_sku.columns and col in master_sku.columns:
                elena_val = str(elena_row[col].iloc[0]) if not elena_row[col].isna().all() else ''
                master_val = str(master_row[col].iloc[0]) if not master_row[col].isna().all() else ''

                if elena_val != master_val and elena_val != 'nan' and master_val != 'nan':
                    differences.append({
                        'sku': sku,
                        'column': col,
                        'elena_value': elena_val[:50],
                        'master_value': master_val[:50]
                    })

    return differences

def generate_html_report(errors, img_mismatches, prod_diff, sku_diff, value_diffs):
    """Generate HTML error report"""

    only_elena_prod, only_master_prod, common_prod = prod_diff
    only_elena_sku, only_master_sku, common_sku = sku_diff

    html = f'''<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FAAC Data Comparison Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        h1 {{
            color: #1a237e;
            border-bottom: 3px solid #3f51b5;
            padding-bottom: 15px;
        }}
        h2 {{
            color: #283593;
            margin-top: 30px;
            border-left: 4px solid #3f51b5;
            padding-left: 15px;
        }}
        .summary-box {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-card.warning {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        .stat-card.success {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }}
        .stat-card h3 {{
            margin: 0;
            font-size: 2em;
        }}
        .stat-card p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #3f51b5;
            color: white;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .error {{
            color: #c62828;
            background: #ffebee;
        }}
        .warning {{
            color: #f57c00;
            background: #fff3e0;
        }}
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        .badge-error {{
            background: #c62828;
            color: white;
        }}
        .badge-warning {{
            background: #f57c00;
            color: white;
        }}
        .badge-info {{
            background: #1565c0;
            color: white;
        }}
        .collapsible {{
            background: #e8eaf6;
            padding: 10px 15px;
            cursor: pointer;
            border: none;
            width: 100%;
            text-align: left;
            font-size: 1em;
            border-radius: 4px;
            margin: 5px 0;
        }}
        .collapsible:hover {{
            background: #c5cae9;
        }}
        .content {{
            padding: 0 15px;
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease-out;
            background: #fafafa;
        }}
        .content.show {{
            max-height: 500px;
            overflow-y: auto;
        }}
        .timestamp {{
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 FAAC Data Comparison Report</h1>
        <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        <p><strong>Comparing:</strong></p>
        <ul>
            <li><code>Data Elena P.xlsx</code> (input/processing/)</li>
            <li><code>FAAC_master_data_v2.xlsx</code> (output/)</li>
        </ul>

        <h2>📊 Summary</h2>
        <div class="summary-box">
            <div class="stat-card warning">
                <h3>{len(errors)}</h3>
                <p>Structure Errors</p>
            </div>
            <div class="stat-card warning">
                <h3>{len(img_mismatches)}</h3>
                <p>Image-SKU Mismatches</p>
            </div>
            <div class="stat-card">
                <h3>{len(common_prod)}</h3>
                <p>Common Products</p>
            </div>
            <div class="stat-card success">
                <h3>{len(common_sku)}</h3>
                <p>Common SKUs</p>
            </div>
        </div>

        <h2>⚠️ Structure Errors in Data Elena P.xlsx</h2>
        <table>
            <tr><th>Type</th><th>Sheet</th><th>Issue</th><th>Severity</th></tr>
'''

    for err in errors:
        badge_class = 'badge-error' if err['severity'] == 'error' else 'badge-warning'
        html += f'''
            <tr class="{err['severity']}">
                <td>{err['type']}</td>
                <td>{err['sheet']}</td>
                <td>{err['issue']}</td>
                <td><span class="badge {badge_class}">{err['severity'].upper()}</span></td>
            </tr>
'''

    html += '''
        </table>

        <h2>🖼️ Image-SKU Mismatches in Elena</h2>
        <p>SKUs where the image filename doesn't match the SKU code:</p>
'''

    if img_mismatches:
        html += '''
        <table>
            <tr><th>SKU</th><th>Current Image</th><th>Expected</th></tr>
'''
        for mm in img_mismatches[:20]:
            html += f'''
            <tr class="warning">
                <td><strong>{mm['sku']}</strong></td>
                <td>{mm['image']}</td>
                <td>{mm['expected']}</td>
            </tr>
'''
        if len(img_mismatches) > 20:
            html += f'<tr><td colspan="3"><em>...and {len(img_mismatches)-20} more</em></td></tr>'
        html += '</table>'
    else:
        html += '<p>No mismatches found.</p>'

    # Products comparison
    html += f'''
        <h2>📦 Products Comparison</h2>

        <button class="collapsible">Products only in Elena ({len(only_elena_prod)})</button>
        <div class="content">
            <ul>
'''
    for p in sorted(only_elena_prod):
        html += f'<li>{p}</li>'
    html += '''
            </ul>
        </div>

        <button class="collapsible">Products only in Master ({len(only_master_prod)})</button>
        <div class="content">
            <ul>
'''
    for p in sorted(list(only_master_prod)[:50]):
        html += f'<li>{p}</li>'
    if len(only_master_prod) > 50:
        html += f'<li><em>...and {len(only_master_prod)-50} more</em></li>'
    html += '''
            </ul>
        </div>
'''

    # SKUs comparison
    html += f'''
        <h2>🏷️ SKUs Comparison</h2>

        <button class="collapsible">SKUs only in Elena ({len(only_elena_sku)})</button>
        <div class="content">
            <ul>
'''
    for s in sorted(list(only_elena_sku)[:30]):
        html += f'<li>{s}</li>'
    if len(only_elena_sku) > 30:
        html += f'<li><em>...and {len(only_elena_sku)-30} more</em></li>'
    html += '''
            </ul>
        </div>

        <button class="collapsible">SKUs only in Master ({len(only_master_sku)})</button>
        <div class="content">
            <ul>
'''
    for s in sorted(list(only_master_sku)[:30]):
        html += f'<li>{s}</li>'
    if len(only_master_sku) > 30:
        html += f'<li><em>...and {len(only_master_sku)-30} more</em></li>'
    html += '''
            </ul>
        </div>
'''

    # Value differences
    if value_diffs:
        html += f'''
        <h2>🔄 Value Differences for Common SKUs</h2>
        <p>Different values found for the same SKU (sample):</p>
        <table>
            <tr><th>SKU</th><th>Column</th><th>Elena Value</th><th>Master Value</th></tr>
'''
        for diff in value_diffs[:30]:
            html += f'''
            <tr>
                <td>{diff['sku']}</td>
                <td>{diff['column']}</td>
                <td>{diff['elena_value']}</td>
                <td>{diff['master_value']}</td>
            </tr>
'''
        html += '</table>'

    html += '''
        <h2>💡 Recommendations</h2>
        <ul>
            <li><strong>Fix column header:</strong> Change "E850S incorporata" to "codice_sku" in Elena SKU sheet</li>
            <li><strong>Fix typo:</strong> Rename "immagne_schema" to "immagine_schema" in prodotti sheet</li>
            <li><strong>Verify image-SKU associations:</strong> Several SKUs have mismatched image filenames</li>
            <li><strong>Add missing products:</strong> {len(only_master_prod)} products in Master are not in Elena</li>
            <li><strong>Review SKU coverage:</strong> {len(only_master_sku)} SKUs in Master are not in Elena</li>
        </ul>

        <script>
            document.querySelectorAll('.collapsible').forEach(btn => {
                btn.addEventListener('click', function() {
                    this.classList.toggle('active');
                    var content = this.nextElementSibling;
                    content.classList.toggle('show');
                });
            });
        </script>
    </div>
</body>
</html>
'''

    return html

def main():
    print("Loading data...")
    elena_prod, elena_sku, master_prod, master_sku = load_data()

    print("Finding structure errors...")
    errors = find_column_errors(elena_prod, elena_sku)

    print("Finding image-SKU mismatches...")
    img_mismatches = find_image_sku_mismatches(elena_sku)
    print(f"  Found {len(img_mismatches)} mismatches")

    print("Comparing products...")
    prod_diff = find_missing_products(elena_prod, master_prod)

    print("Comparing SKUs...")
    sku_diff = find_missing_skus(elena_sku, master_sku)

    print("Finding value differences...")
    value_diffs = find_value_differences(elena_sku, master_sku, sku_diff[2])
    print(f"  Found {len(value_diffs)} differences")

    print("Generating HTML report...")
    html = generate_html_report(errors, img_mismatches, prod_diff, sku_diff, value_diffs)

    OUTPUT_HTML.write_text(html, encoding='utf-8')
    print(f"\nReport saved to: {OUTPUT_HTML}")

    # Print summary
    print("\n=== Summary ===")
    print(f"Structure errors: {len(errors)}")
    print(f"Image-SKU mismatches: {len(img_mismatches)}")
    print(f"Products only in Elena: {len(prod_diff[0])}")
    print(f"Products only in Master: {len(prod_diff[1])}")
    print(f"Common products: {len(prod_diff[2])}")
    print(f"SKUs only in Elena: {len(sku_diff[0])}")
    print(f"SKUs only in Master: {len(sku_diff[1])}")
    print(f"Common SKUs: {len(sku_diff[2])}")

if __name__ == '__main__':
    main()
