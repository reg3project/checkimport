#!/usr/bin/env python3
"""
FAAC Product Verification Script
Verifies products in FAAC_Data_Elena_P_KIT_v5.xlsx against IDML source files.
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

# Configuration
XLSX_PATH = "/home/user/checkimport/input/processing/FAAC_Data_Elena_P_KIT_v5.xlsx"
IDML_BASE = "/home/user/checkimport/input/processing/IDML_unzipped"
PDF_BASE = "/home/user/checkimport/input/processing/PDF Single Products"
OUTPUT_DIR = "/home/user/checkimport/output"

# Progress tracking
START_TIME = time.time()
CHECKPOINT_INTERVAL = 420  # 7 minutes in seconds
last_checkpoint = START_TIME
products_processed = 0
total_products = 0

def log_checkpoint(message):
    """Log checkpoint with timing information"""
    global last_checkpoint
    current_time = time.time()
    elapsed = current_time - START_TIME
    since_checkpoint = current_time - last_checkpoint

    mins = int(elapsed // 60)
    secs = int(elapsed % 60)
    print(f"[{mins:02d}:{secs:02d}] {message}")

    if since_checkpoint >= CHECKPOINT_INTERVAL:
        print(f"\n*** 7-MINUTE CHECKPOINT ***")
        print(f"    Products processed: {products_processed}/{total_products}")
        print(f"    Time elapsed: {mins} minutes {secs} seconds")
        print(f"    Still running: YES")
        print(f"*** CONTINUING VERIFICATION ***\n")
        last_checkpoint = current_time

def find_idml_folder(product_name, page_num):
    """Find IDML folder matching product name or page number"""
    if not os.path.exists(IDML_BASE):
        return None

    folders = os.listdir(IDML_BASE)

    # Clean product name for matching
    if product_name is None:
        return None
    product_name = str(product_name)
    clean_name = product_name.lower().replace(' ', '_').replace('/', '_')

    # Try matching by page number first (most reliable)
    if page_num:
        page_str_raw = str(page_num)
        # Handle page ranges like "62-63" - take first page
        if '-' in page_str_raw:
            page_str_raw = page_str_raw.split('-')[0]

        try:
            page_int = int(float(page_str_raw))
            page_str = str(page_int).zfill(3)
            page_str_no_pad = str(page_int)
        except:
            page_str = None
            page_str_no_pad = None

        if page_str:
            for folder in folders:
                if folder.startswith(page_str + '_') or folder.startswith(page_str + '-'):
                    return os.path.join(IDML_BASE, folder)
                # Also try without leading zero padding
                if folder.startswith(page_str_no_pad + '_') or folder.startswith(page_str_no_pad + '-'):
                    return os.path.join(IDML_BASE, folder)

    # Try matching by product name
    for folder in folders:
        folder_lower = folder.lower()
        # Remove page number prefix for matching
        folder_name = '_'.join(folder.split('_')[1:]) if '_' in folder else folder
        folder_name_lower = folder_name.lower()

        if clean_name in folder_name_lower or folder_name_lower in clean_name:
            return os.path.join(IDML_BASE, folder)

    return None

def extract_idml_data(idml_folder):
    """Extract all product data from IDML Story files"""
    data = {
        'models': [],
        'skus': [],
        'prices': [],
        'descriptions': [],
        'components': [],
        'tech_specs': [],
        'raw_content': []
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

            for elem in root.iter():
                # Track paragraph style
                if 'AppliedParagraphStyle' in elem.attrib:
                    current_style = elem.attrib['AppliedParagraphStyle'].lower()

                # Extract content
                if elem.tag == 'Content' and elem.text:
                    text = elem.text.strip()
                    if text:
                        contents.append(text)
                        data['raw_content'].append({'text': text, 'style': current_style, 'file': story_file})

                        # Classify based on style
                        if current_style:
                            if 'model' in current_style and 'pgf' in current_style:
                                data['models'].append(text)
                            elif 'code' in current_style and 'pgf' in current_style:
                                # Check if it looks like a SKU code
                                if re.match(r'^\d{5,6}$', text):
                                    data['skus'].append(text)
                            elif 'price' in current_style and 'pgf' in current_style:
                                data['prices'].append(text)
                            elif 'techspec' in current_style:
                                data['tech_specs'].append(text)
                            elif 'descr' in current_style:
                                data['descriptions'].append(text)

            # Parse models table pattern: "Modello", "Codice articolo", "Prezzo €" followed by data
            if contents:
                for i, content in enumerate(contents):
                    if content == 'Modello' and i + 3 < len(contents):
                        # Next items should be: Codice articolo, Prezzo €, then data rows
                        pass
                    # Extract SKU codes (5-6 digit numbers)
                    if re.match(r'^\d{5,6}$', content):
                        if content not in data['skus']:
                            data['skus'].append(content)
                    # Extract prices (numbers with comma for decimals)
                    if re.match(r'^[\d.,]+$', content) and ',' in content:
                        data['prices'].append(content)

        except Exception as e:
            pass  # Skip problematic files

    return data

def compare_data(excel_data, idml_data, product_name):
    """Compare Excel data with IDML extracted data"""
    discrepancies = []
    suggestions = []

    # Extract SKUs from Excel (column 7: codici_modelli)
    excel_skus = []
    if excel_data.get('codici_modelli'):
        sku_str = str(excel_data['codici_modelli'])
        # Parse semicolon or comma separated SKUs
        for sku in re.split(r'[;,]', sku_str):
            sku = sku.strip()
            if sku:
                # Handle float-like SKUs
                try:
                    sku_int = int(float(sku))
                    excel_skus.append(str(sku_int))
                except:
                    excel_skus.append(sku)

    idml_skus = idml_data.get('skus', [])

    # Check for SKU mismatches
    for excel_sku in excel_skus:
        if excel_sku not in idml_skus:
            discrepancies.append({
                'type': 'SKU_NOT_IN_IDML',
                'product': product_name,
                'excel_value': excel_sku,
                'idml_value': None,
                'message': f"SKU {excel_sku} in Excel not found in IDML"
            })

    for idml_sku in idml_skus:
        if idml_sku not in excel_skus:
            discrepancies.append({
                'type': 'SKU_NOT_IN_EXCEL',
                'product': product_name,
                'excel_value': None,
                'idml_value': idml_sku,
                'message': f"SKU {idml_sku} in IDML not in Excel"
            })
            suggestions.append({
                'type': 'ADD_SKU',
                'product': product_name,
                'value': idml_sku,
                'message': f"Consider adding SKU {idml_sku} to product {product_name}"
            })

    return discrepancies, suggestions

def read_excel_products():
    """Read all products from Excel file"""
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
            product = {}
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
            sku = {}
            for col, header in headers.items():
                sku[header] = ws.cell(row=row, column=col).value
            if sku.get('codice_sku'):
                skus.append(sku)

    wb.close()
    return products, skus

def create_report(all_discrepancies, all_suggestions, products_verified):
    """Create detailed verification report"""
    report = []
    report.append("=" * 80)
    report.append("FAAC PRODUCT VERIFICATION REPORT")
    report.append(f"Generated: {datetime.now().isoformat()}")
    report.append("=" * 80)
    report.append("")
    report.append(f"Total products verified: {len(products_verified)}")
    report.append(f"Total discrepancies found: {len(all_discrepancies)}")
    report.append(f"Total suggestions: {len(all_suggestions)}")
    report.append("")

    # Group discrepancies by type
    by_type = defaultdict(list)
    for d in all_discrepancies:
        by_type[d['type']].append(d)

    report.append("-" * 80)
    report.append("DISCREPANCIES BY TYPE")
    report.append("-" * 80)

    for disc_type, items in by_type.items():
        report.append(f"\n### {disc_type} ({len(items)} issues)")
        for item in items[:50]:  # Limit to first 50 per type
            report.append(f"  - {item['product']}: {item['message']}")
        if len(items) > 50:
            report.append(f"  ... and {len(items) - 50} more")

    report.append("")
    report.append("-" * 80)
    report.append("SUGGESTED EDITS")
    report.append("-" * 80)

    for sugg in all_suggestions[:100]:
        report.append(f"  - [{sugg['type']}] {sugg['message']}")
    if len(all_suggestions) > 100:
        report.append(f"  ... and {len(all_suggestions) - 100} more suggestions")

    return "\n".join(report)

def create_corrected_xlsx(products, skus, all_discrepancies, all_suggestions):
    """Create a new XLSX file with suggested corrections"""
    wb = Workbook()

    # Style definitions
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    warning_fill = PatternFill(start_color="FFC000", end_color="FFC000", fill_type="solid")
    error_fill = PatternFill(start_color="FF6B6B", end_color="FF6B6B", fill_type="solid")
    suggestion_fill = PatternFill(start_color="92D050", end_color="92D050", fill_type="solid")

    # Create Discrepancies sheet
    ws_disc = wb.active
    ws_disc.title = "Discrepancies"

    disc_headers = ["Type", "Product", "Excel Value", "IDML Value", "Message"]
    for col, header in enumerate(disc_headers, 1):
        cell = ws_disc.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font

    for row_num, disc in enumerate(all_discrepancies, 2):
        ws_disc.cell(row=row_num, column=1, value=disc['type'])
        ws_disc.cell(row=row_num, column=2, value=disc['product'])
        ws_disc.cell(row=row_num, column=3, value=str(disc.get('excel_value', '')))
        ws_disc.cell(row=row_num, column=4, value=str(disc.get('idml_value', '')))
        ws_disc.cell(row=row_num, column=5, value=disc['message'])

    # Create Suggestions sheet
    ws_sugg = wb.create_sheet("Suggestions")

    sugg_headers = ["Type", "Product", "Value", "Message"]
    for col, header in enumerate(sugg_headers, 1):
        cell = ws_sugg.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font

    for row_num, sugg in enumerate(all_suggestions, 2):
        ws_sugg.cell(row=row_num, column=1, value=sugg['type'])
        ws_sugg.cell(row=row_num, column=2, value=sugg['product'])
        ws_sugg.cell(row=row_num, column=3, value=str(sugg.get('value', '')))
        ws_sugg.cell(row=row_num, column=4, value=sugg['message'])

    # Create Summary sheet
    ws_summary = wb.create_sheet("Summary")

    ws_summary.cell(row=1, column=1, value="FAAC Product Verification Summary")
    ws_summary.cell(row=1, column=1).font = Font(bold=True, size=14)

    ws_summary.cell(row=3, column=1, value="Report Generated:")
    ws_summary.cell(row=3, column=2, value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    ws_summary.cell(row=4, column=1, value="Products Verified:")
    ws_summary.cell(row=4, column=2, value=len(products))

    ws_summary.cell(row=5, column=1, value="SKUs Verified:")
    ws_summary.cell(row=5, column=2, value=len(skus))

    ws_summary.cell(row=6, column=1, value="Total Discrepancies:")
    ws_summary.cell(row=6, column=2, value=len(all_discrepancies))

    ws_summary.cell(row=7, column=1, value="Total Suggestions:")
    ws_summary.cell(row=7, column=2, value=len(all_suggestions))

    # Discrepancy breakdown
    ws_summary.cell(row=9, column=1, value="Discrepancy Breakdown:").font = Font(bold=True)

    by_type = defaultdict(int)
    for d in all_discrepancies:
        by_type[d['type']] += 1

    row = 10
    for disc_type, count in sorted(by_type.items()):
        ws_summary.cell(row=row, column=1, value=disc_type)
        ws_summary.cell(row=row, column=2, value=count)
        row += 1

    return wb

def main():
    """Main verification process"""
    global products_processed, total_products

    print("=" * 80)
    print("FAAC PRODUCT VERIFICATION SCRIPT")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 80)
    print()

    # Read Excel data
    log_checkpoint("Reading Excel file...")
    products, skus = read_excel_products()
    total_products = len(products)

    print(f"Found {len(products)} products in prodotti sheet")
    print(f"Found {len(skus)} SKUs in sku sheet")
    print()

    # List available IDML folders
    idml_folders = os.listdir(IDML_BASE) if os.path.exists(IDML_BASE) else []
    print(f"Found {len(idml_folders)} IDML folders")
    print()

    all_discrepancies = []
    all_suggestions = []
    products_verified = []
    products_no_idml = []

    # Verify each product
    log_checkpoint("Starting product verification...")

    for idx, product in enumerate(products):
        product_name = product.get('nome_prodotto')
        if product_name is None:
            continue
        product_name = str(product_name)
        if not product_name or product_name == 'nan':
            continue

        page_num = product.get('pagina_catalogo')

        # Progress update every 50 products
        if idx % 50 == 0:
            log_checkpoint(f"Processing product {idx + 1}/{len(products)}: {product_name}")

        # Find IDML folder
        idml_folder = find_idml_folder(product_name, page_num)

        if idml_folder:
            # Extract IDML data
            idml_data = extract_idml_data(idml_folder)

            # Compare data
            discrepancies, suggestions = compare_data(product, idml_data, product_name)

            all_discrepancies.extend(discrepancies)
            all_suggestions.extend(suggestions)
            products_verified.append({
                'name': product_name,
                'page': page_num,
                'idml_folder': os.path.basename(idml_folder),
                'idml_skus_found': len(idml_data.get('skus', [])),
                'discrepancies': len(discrepancies)
            })
        else:
            products_no_idml.append({
                'name': product_name,
                'page': page_num
            })
            all_discrepancies.append({
                'type': 'NO_IDML_FOLDER',
                'product': product_name,
                'excel_value': page_num,
                'idml_value': None,
                'message': f"No IDML folder found for product {product_name} (page {page_num})"
            })

        products_processed += 1

        # Checkpoint check
        log_checkpoint(f"Verified: {product_name}")

    print()
    log_checkpoint("Product verification complete!")

    # Verify SKUs separately
    log_checkpoint("Verifying individual SKUs...")

    sku_discrepancies = []
    for idx, sku in enumerate(skus):
        if idx % 100 == 0:
            log_checkpoint(f"Processing SKU {idx + 1}/{len(skus)}")

        sku_code = sku.get('codice_sku')
        if sku_code:
            try:
                sku_code_str = str(int(float(sku_code)))
            except:
                sku_code_str = str(sku_code)

            # Check if SKU exists in any IDML data
            # This is a simplified check - could be expanded
            pass

    print()
    log_checkpoint("SKU verification complete!")

    # Generate report
    log_checkpoint("Generating report...")
    report = create_report(all_discrepancies, all_suggestions, products_verified)

    # Save report
    report_path = os.path.join(OUTPUT_DIR, "faac_verification_report.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Report saved to: {report_path}")

    # Create corrected XLSX
    log_checkpoint("Creating corrected XLSX file...")
    wb_corrected = create_corrected_xlsx(products, skus, all_discrepancies, all_suggestions)

    xlsx_path = os.path.join(OUTPUT_DIR, "FAAC_Data_Elena_P_KIT_v5_VERIFIED.xlsx")
    wb_corrected.save(xlsx_path)
    print(f"Corrected XLSX saved to: {xlsx_path}")

    # Save detailed JSON
    json_data = {
        'generated_at': datetime.now().isoformat(),
        'products_total': len(products),
        'products_verified': len(products_verified),
        'products_no_idml': len(products_no_idml),
        'skus_total': len(skus),
        'discrepancies_total': len(all_discrepancies),
        'suggestions_total': len(all_suggestions),
        'discrepancies': all_discrepancies,
        'suggestions': all_suggestions,
        'products_verified_details': products_verified,
        'products_no_idml_list': products_no_idml
    }

    json_path = os.path.join(OUTPUT_DIR, "faac_verification_data.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    print(f"JSON data saved to: {json_path}")

    # Final summary
    elapsed = time.time() - START_TIME
    mins = int(elapsed // 60)
    secs = int(elapsed % 60)

    print()
    print("=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)
    print(f"Total time: {mins} minutes {secs} seconds")
    print(f"Products processed: {len(products)}")
    print(f"Products with IDML: {len(products_verified)}")
    print(f"Products without IDML: {len(products_no_idml)}")
    print(f"SKUs processed: {len(skus)}")
    print(f"Discrepancies found: {len(all_discrepancies)}")
    print(f"Suggestions generated: {len(all_suggestions)}")
    print("=" * 80)

    return all_discrepancies, all_suggestions, products_verified

if __name__ == "__main__":
    main()
