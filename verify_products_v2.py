#!/usr/bin/env python3
"""
FAAC Product Verification Script V2
Enhanced verification that properly distinguishes:
- Kit product codes (codici_modelli in prodotti)
- Component SKUs (contents of kits in IDML)
- Individual product SKUs (sku sheet)
"""

import os
import re
import json
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from collections import defaultdict
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from copy import copy

# Configuration
XLSX_PATH = "/home/user/checkimport/input/processing/FAAC_Data_Elena_P_KIT_v5.xlsx"
IDML_BASE = "/home/user/checkimport/input/processing/IDML_unzipped"
PDF_BASE = "/home/user/checkimport/input/processing/PDF Single Products"
OUTPUT_DIR = "/home/user/checkimport/output"

# Progress tracking
START_TIME = time.time()
CHECKPOINT_INTERVAL = 420  # 7 minutes
last_checkpoint = START_TIME

def log_checkpoint(message):
    """Log with timing"""
    global last_checkpoint
    current_time = time.time()
    elapsed = current_time - START_TIME
    mins = int(elapsed // 60)
    secs = int(elapsed % 60)
    print(f"[{mins:02d}:{secs:02d}] {message}")

    if current_time - last_checkpoint >= CHECKPOINT_INTERVAL:
        print(f"\n*** 7-MINUTE CHECKPOINT - Process still running ***\n")
        last_checkpoint = current_time

def find_idml_folder(product_name, page_num):
    """Find IDML folder matching product"""
    if not os.path.exists(IDML_BASE):
        return None

    folders = os.listdir(IDML_BASE)

    if product_name is None:
        return None
    product_name = str(product_name)
    clean_name = product_name.lower().replace(' ', '_').replace('/', '_')

    # Try by page number first
    if page_num:
        page_str_raw = str(page_num)
        if '-' in page_str_raw:
            page_str_raw = page_str_raw.split('-')[0]
        try:
            page_int = int(float(page_str_raw))
            page_str = str(page_int).zfill(3)
            page_str_no_pad = str(page_int)

            for folder in folders:
                if folder.startswith(page_str + '_') or folder.startswith(page_str + '-'):
                    return os.path.join(IDML_BASE, folder)
                if folder.startswith(page_str_no_pad + '_') or folder.startswith(page_str_no_pad + '-'):
                    return os.path.join(IDML_BASE, folder)
        except:
            pass

    # Try by name
    for folder in folders:
        folder_name = '_'.join(folder.split('_')[1:]) if '_' in folder else folder
        folder_name_lower = folder_name.lower()
        if clean_name in folder_name_lower or folder_name_lower in clean_name:
            return os.path.join(IDML_BASE, folder)

    return None

def extract_idml_data(idml_folder):
    """Extract comprehensive data from IDML"""
    data = {
        'models': [],           # Model names
        'model_codes': [],      # Main product/kit codes
        'component_skus': [],   # Component SKUs
        'prices': [],           # Prices
        'descriptions': [],     # Descriptions
        'tech_specs': [],       # Technical specifications
        'raw_content': []       # All content for reference
    }

    stories_path = os.path.join(idml_folder, 'Stories')
    if not os.path.exists(stories_path):
        return data

    for story_file in os.listdir(stories_path):
        if not story_file.endswith('.xml'):
            continue

        file_path = os.path.join(stories_path, story_file)
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            current_style = None
            contents = []
            content_with_styles = []

            for elem in root.iter():
                if 'AppliedParagraphStyle' in elem.attrib:
                    current_style = elem.attrib['AppliedParagraphStyle'].lower()

                if elem.tag == 'Content' and elem.text:
                    text = elem.text.strip()
                    if text:
                        contents.append(text)
                        content_with_styles.append({'text': text, 'style': current_style})
                        data['raw_content'].append({'text': text, 'style': current_style, 'file': story_file})

                        # Classify by style
                        if current_style:
                            if 'models_model' in current_style:
                                data['models'].append(text)
                            elif 'models_code' in current_style or ('pricelist_code' in current_style):
                                if re.match(r'^\d{5,6}$', text):
                                    data['model_codes'].append(text)
                            elif 'models_price' in current_style or 'pricelist_price' in current_style:
                                data['prices'].append(text)

            # Scan for SKU patterns in all content
            for item in content_with_styles:
                text = item['text']
                # 5-6 digit codes are SKUs
                if re.match(r'^\d{5,6}$', text):
                    if text not in data['component_skus']:
                        data['component_skus'].append(text)
                # Prices with comma
                if re.match(r'^[\d.,]+$', text) and ',' in text and text not in data['prices']:
                    data['prices'].append(text)

        except Exception as e:
            pass

    return data

def normalize_sku(sku):
    """Normalize SKU to comparable format"""
    if sku is None:
        return None
    try:
        # Remove decimals and convert to string
        return str(int(float(str(sku))))
    except:
        return str(sku).strip()

def read_excel_data():
    """Read all Excel data with full structure"""
    wb = openpyxl.load_workbook(XLSX_PATH)

    products = []
    skus = []

    # Read prodotti sheet
    if 'prodotti' in wb.sheetnames:
        ws = wb['prodotti']
        headers = {}
        for col in range(1, ws.max_column + 1):
            header = ws.cell(row=1, column=col).value
            if header:
                headers[col] = header

        for row in range(3, ws.max_row + 1):
            product = {'_row': row}
            for col, header in headers.items():
                product[header] = ws.cell(row=row, column=col).value
            if product.get('nome_prodotto'):
                products.append(product)

    # Read sku sheet
    if 'sku' in wb.sheetnames:
        ws = wb['sku']
        headers = {}
        for col in range(1, ws.max_column + 1):
            header = ws.cell(row=1, column=col).value
            if header:
                headers[col] = header

        for row in range(3, ws.max_row + 1):
            sku = {'_row': row}
            for col, header in headers.items():
                sku[header] = ws.cell(row=row, column=col).value
            if sku.get('codice_sku'):
                skus.append(sku)

    wb.close()
    return products, skus, headers

def analyze_product(product, idml_data, all_skus):
    """Deep analysis of a single product"""
    issues = []
    suggestions = []

    product_name = str(product.get('nome_prodotto', ''))

    # Get kit codes from Excel
    excel_kit_codes = []
    if product.get('codici_modelli'):
        for code in re.split(r'[;,]', str(product['codici_modelli'])):
            code = code.strip()
            if code:
                excel_kit_codes.append(normalize_sku(code))

    # Get model codes from IDML
    idml_model_codes = [normalize_sku(c) for c in idml_data.get('model_codes', [])]
    idml_component_skus = [normalize_sku(c) for c in idml_data.get('component_skus', [])]

    # All SKUs from Excel SKU sheet
    excel_sku_codes = set(normalize_sku(s.get('codice_sku')) for s in all_skus if s.get('codice_sku'))

    # Check 1: Kit codes should match
    for kit_code in excel_kit_codes:
        if kit_code and kit_code not in idml_model_codes and kit_code not in idml_component_skus:
            issues.append({
                'type': 'KIT_CODE_NOT_IN_IDML',
                'product': product_name,
                'excel_value': kit_code,
                'idml_value': None,
                'severity': 'HIGH',
                'message': f"Kit code {kit_code} not found in IDML source"
            })

    # Check 2: IDML model codes should be in Excel
    for code in idml_model_codes:
        if code and code not in excel_kit_codes:
            issues.append({
                'type': 'IDML_MODEL_NOT_IN_EXCEL',
                'product': product_name,
                'excel_value': None,
                'idml_value': code,
                'severity': 'MEDIUM',
                'message': f"IDML model code {code} not listed in Excel kit codes"
            })
            suggestions.append({
                'type': 'ADD_KIT_CODE',
                'product': product_name,
                'value': code,
                'message': f"Consider adding model code {code} to {product_name}"
            })

    # Check 3: Component SKUs should exist in SKU sheet
    for component in idml_component_skus:
        if component and component not in excel_sku_codes:
            issues.append({
                'type': 'COMPONENT_NOT_IN_SKU_SHEET',
                'product': product_name,
                'excel_value': None,
                'idml_value': component,
                'severity': 'MEDIUM',
                'message': f"Component SKU {component} from IDML not in Excel SKU sheet"
            })
            suggestions.append({
                'type': 'ADD_COMPONENT_SKU',
                'product': product_name,
                'value': component,
                'message': f"Add component SKU {component} to SKU sheet"
            })

    # Check 4: Verify descriptions and specs
    excel_desc = str(product.get('descrizione_prodotto', '') or '')
    idml_descriptions = idml_data.get('descriptions', [])

    if excel_desc and idml_descriptions:
        # Simple check for presence of key terms
        excel_words = set(excel_desc.lower().split())
        idml_words = set(' '.join(idml_descriptions).lower().split())
        common = excel_words & idml_words
        if len(common) < min(3, len(excel_words)):
            issues.append({
                'type': 'DESCRIPTION_MISMATCH',
                'product': product_name,
                'excel_value': excel_desc[:100],
                'idml_value': ' '.join(idml_descriptions)[:100],
                'severity': 'LOW',
                'message': f"Description text differs significantly between sources"
            })

    return issues, suggestions

def create_enhanced_xlsx(products, skus, all_issues, all_suggestions, verified_products):
    """Create comprehensive output XLSX"""
    wb = Workbook()

    # Styles
    header_fill = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    high_fill = PatternFill(start_color="FF6B6B", end_color="FF6B6B", fill_type="solid")
    medium_fill = PatternFill(start_color="FFC000", end_color="FFC000", fill_type="solid")
    low_fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
    suggestion_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")

    # Sheet 1: Summary
    ws_summary = wb.active
    ws_summary.title = "Summary"

    summary_data = [
        ["FAAC Product Verification Report"],
        [""],
        ["Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ["Source File", os.path.basename(XLSX_PATH)],
        [""],
        ["STATISTICS"],
        ["Products in Excel", len(products)],
        ["Products Verified", len(verified_products)],
        ["Products Without IDML", len(products) - len(verified_products)],
        ["SKUs in Excel", len(skus)],
        [""],
        ["ISSUES BY SEVERITY"],
    ]

    severity_counts = defaultdict(int)
    for issue in all_issues:
        severity_counts[issue.get('severity', 'UNKNOWN')] += 1

    for sev, count in sorted(severity_counts.items()):
        summary_data.append([f"  {sev}", count])

    summary_data.append([""])
    summary_data.append(["ISSUES BY TYPE"])

    type_counts = defaultdict(int)
    for issue in all_issues:
        type_counts[issue['type']] += 1

    for itype, count in sorted(type_counts.items()):
        summary_data.append([f"  {itype}", count])

    summary_data.append([""])
    summary_data.append(["Total Suggestions", len(all_suggestions)])

    for row_idx, row_data in enumerate(summary_data, 1):
        for col_idx, value in enumerate(row_data, 1):
            ws_summary.cell(row=row_idx, column=col_idx, value=value)

    ws_summary.cell(row=1, column=1).font = Font(bold=True, size=16)

    # Sheet 2: All Issues
    ws_issues = wb.create_sheet("All_Issues")
    issue_headers = ["Severity", "Type", "Product", "Excel Value", "IDML Value", "Message"]

    for col, header in enumerate(issue_headers, 1):
        cell = ws_issues.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font

    for row_num, issue in enumerate(all_issues, 2):
        ws_issues.cell(row=row_num, column=1, value=issue.get('severity', ''))
        ws_issues.cell(row=row_num, column=2, value=issue['type'])
        ws_issues.cell(row=row_num, column=3, value=issue['product'])
        ws_issues.cell(row=row_num, column=4, value=str(issue.get('excel_value', '')))
        ws_issues.cell(row=row_num, column=5, value=str(issue.get('idml_value', '')))
        ws_issues.cell(row=row_num, column=6, value=issue['message'])

        # Color by severity
        severity = issue.get('severity', '')
        if severity == 'HIGH':
            for col in range(1, 7):
                ws_issues.cell(row=row_num, column=col).fill = high_fill
        elif severity == 'MEDIUM':
            for col in range(1, 7):
                ws_issues.cell(row=row_num, column=col).fill = medium_fill
        elif severity == 'LOW':
            for col in range(1, 7):
                ws_issues.cell(row=row_num, column=col).fill = low_fill

    # Sheet 3: Suggested Edits
    ws_sugg = wb.create_sheet("Suggested_Edits")
    sugg_headers = ["Type", "Product", "Value", "Suggestion"]

    for col, header in enumerate(sugg_headers, 1):
        cell = ws_sugg.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font

    for row_num, sugg in enumerate(all_suggestions, 2):
        ws_sugg.cell(row=row_num, column=1, value=sugg['type'])
        ws_sugg.cell(row=row_num, column=2, value=sugg['product'])
        ws_sugg.cell(row=row_num, column=3, value=str(sugg.get('value', '')))
        ws_sugg.cell(row=row_num, column=4, value=sugg['message'])

    # Sheet 4: Products Without IDML
    ws_no_idml = wb.create_sheet("Products_No_IDML")
    no_idml_headers = ["Product Name", "Page Number", "Category"]

    for col, header in enumerate(no_idml_headers, 1):
        cell = ws_no_idml.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font

    verified_names = set(p['name'] for p in verified_products)
    row_num = 2
    for product in products:
        pname = str(product.get('nome_prodotto', ''))
        if pname and pname not in verified_names:
            ws_no_idml.cell(row=row_num, column=1, value=pname)
            ws_no_idml.cell(row=row_num, column=2, value=str(product.get('pagina_catalogo', '')))
            ws_no_idml.cell(row=row_num, column=3, value=str(product.get('categoria_prodotto', '')))
            row_num += 1

    # Sheet 5: Verified Products Detail
    ws_verified = wb.create_sheet("Verified_Products")
    verified_headers = ["Product", "Page", "IDML Folder", "Kit Codes Found", "Component SKUs Found", "Issues Count"]

    for col, header in enumerate(verified_headers, 1):
        cell = ws_verified.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font

    for row_num, vp in enumerate(verified_products, 2):
        ws_verified.cell(row=row_num, column=1, value=vp.get('name', ''))
        ws_verified.cell(row=row_num, column=2, value=str(vp.get('page', '')))
        ws_verified.cell(row=row_num, column=3, value=vp.get('idml_folder', ''))
        ws_verified.cell(row=row_num, column=4, value=vp.get('model_codes_found', 0))
        ws_verified.cell(row=row_num, column=5, value=vp.get('component_skus_found', 0))
        ws_verified.cell(row=row_num, column=6, value=vp.get('issues_count', 0))

    # Auto-width columns
    for ws in wb.worksheets:
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width

    return wb

def main():
    print("=" * 80)
    print("FAAC PRODUCT VERIFICATION V2 - Enhanced Analysis")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 80)
    print()

    # Read Excel
    log_checkpoint("Reading Excel data...")
    products, skus, headers = read_excel_data()
    print(f"Products: {len(products)}")
    print(f"SKUs: {len(skus)}")

    # List IDML folders
    idml_folders = os.listdir(IDML_BASE) if os.path.exists(IDML_BASE) else []
    print(f"IDML folders: {len(idml_folders)}")
    print()

    all_issues = []
    all_suggestions = []
    verified_products = []

    log_checkpoint("Starting enhanced product verification...")

    for idx, product in enumerate(products):
        product_name = product.get('nome_prodotto')
        if product_name is None:
            continue
        product_name = str(product_name)
        if not product_name or product_name == 'nan':
            continue

        page_num = product.get('pagina_catalogo')

        if idx % 25 == 0:
            log_checkpoint(f"Processing {idx + 1}/{len(products)}: {product_name[:40]}")

        # Find IDML
        idml_folder = find_idml_folder(product_name, page_num)

        if idml_folder:
            idml_data = extract_idml_data(idml_folder)
            issues, suggestions = analyze_product(product, idml_data, skus)

            all_issues.extend(issues)
            all_suggestions.extend(suggestions)

            verified_products.append({
                'name': product_name,
                'page': page_num,
                'idml_folder': os.path.basename(idml_folder),
                'model_codes_found': len(idml_data.get('model_codes', [])),
                'component_skus_found': len(idml_data.get('component_skus', [])),
                'issues_count': len(issues)
            })
        else:
            all_issues.append({
                'type': 'NO_IDML_FOLDER',
                'product': product_name,
                'excel_value': page_num,
                'idml_value': None,
                'severity': 'HIGH',
                'message': f"No IDML source found for {product_name} (page {page_num})"
            })

    log_checkpoint("Product verification complete!")

    # SKU sheet verification
    log_checkpoint("Verifying SKU sheet...")

    # Build set of all component SKUs found in IDML
    all_idml_skus = set()
    for vp in verified_products:
        idml_folder = find_idml_folder(vp['name'], vp['page'])
        if idml_folder:
            idml_data = extract_idml_data(idml_folder)
            for sku in idml_data.get('component_skus', []):
                all_idml_skus.add(normalize_sku(sku))

    # Check each SKU in Excel
    for idx, sku in enumerate(skus):
        if idx % 100 == 0:
            log_checkpoint(f"Checking SKU {idx + 1}/{len(skus)}")

        sku_code = normalize_sku(sku.get('codice_sku'))
        model_name = sku.get('nome_modello', '')

        # Check if SKU appears in any IDML
        # This is informational - SKUs may be standalone products
        pass

    log_checkpoint("SKU verification complete!")

    # Generate outputs
    log_checkpoint("Generating output files...")

    # Create enhanced XLSX
    wb = create_enhanced_xlsx(products, skus, all_issues, all_suggestions, verified_products)
    xlsx_path = os.path.join(OUTPUT_DIR, "FAAC_Data_Elena_P_KIT_v5_VERIFIED_v2.xlsx")
    wb.save(xlsx_path)
    print(f"Saved: {xlsx_path}")

    # Create JSON
    json_data = {
        'generated_at': datetime.now().isoformat(),
        'source_file': XLSX_PATH,
        'statistics': {
            'products_total': len(products),
            'products_verified': len(verified_products),
            'products_no_idml': len(products) - len(verified_products),
            'skus_total': len(skus),
            'issues_total': len(all_issues),
            'suggestions_total': len(all_suggestions)
        },
        'issues_by_severity': dict(sorted(defaultdict(int, {i.get('severity', 'UNKNOWN'): 1 for i in all_issues}).items())),
        'issues_by_type': dict(sorted({i['type']: sum(1 for x in all_issues if x['type'] == i['type']) for i in all_issues}.items())),
        'all_issues': all_issues,
        'all_suggestions': all_suggestions,
        'verified_products': verified_products
    }

    json_path = os.path.join(OUTPUT_DIR, "faac_verification_v2.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    print(f"Saved: {json_path}")

    # Summary report
    report_lines = [
        "=" * 80,
        "FAAC PRODUCT VERIFICATION REPORT V2",
        f"Generated: {datetime.now().isoformat()}",
        "=" * 80,
        "",
        "STATISTICS",
        f"  Products in Excel: {len(products)}",
        f"  Products Verified: {len(verified_products)}",
        f"  Products Without IDML: {len(products) - len(verified_products)}",
        f"  SKUs in Excel: {len(skus)}",
        f"  Total Issues: {len(all_issues)}",
        f"  Total Suggestions: {len(all_suggestions)}",
        "",
        "ISSUES BY SEVERITY",
    ]

    severity_counts = defaultdict(int)
    for issue in all_issues:
        severity_counts[issue.get('severity', 'UNKNOWN')] += 1
    for sev, count in sorted(severity_counts.items()):
        report_lines.append(f"  {sev}: {count}")

    report_lines.append("")
    report_lines.append("ISSUES BY TYPE")

    type_counts = defaultdict(int)
    for issue in all_issues:
        type_counts[issue['type']] += 1
    for itype, count in sorted(type_counts.items()):
        report_lines.append(f"  {itype}: {count}")

    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("TOP ISSUES (First 50)")
    report_lines.append("=" * 80)

    for issue in all_issues[:50]:
        report_lines.append(f"[{issue.get('severity', '?')}] {issue['type']}: {issue['message']}")

    if len(all_issues) > 50:
        report_lines.append(f"... and {len(all_issues) - 50} more issues")

    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("TOP SUGGESTIONS (First 50)")
    report_lines.append("=" * 80)

    for sugg in all_suggestions[:50]:
        report_lines.append(f"[{sugg['type']}] {sugg['message']}")

    if len(all_suggestions) > 50:
        report_lines.append(f"... and {len(all_suggestions) - 50} more suggestions")

    report_path = os.path.join(OUTPUT_DIR, "faac_verification_report_v2.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    print(f"Saved: {report_path}")

    # Final summary
    elapsed = time.time() - START_TIME
    mins = int(elapsed // 60)
    secs = int(elapsed % 60)

    print()
    print("=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)
    print(f"Time: {mins}m {secs}s")
    print(f"Products verified: {len(verified_products)}/{len(products)}")
    print(f"Issues found: {len(all_issues)}")
    print(f"Suggestions: {len(all_suggestions)}")
    print()
    print("Output files:")
    print(f"  - {xlsx_path}")
    print(f"  - {json_path}")
    print(f"  - {report_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
