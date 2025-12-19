#!/usr/bin/env python3
"""
Create suggested XLSX with corrections applied from verification results.
"""

import os
import json
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Border, Side, Alignment
from openpyxl.comments import Comment
from copy import copy
from datetime import datetime
from collections import defaultdict

# Paths
XLSX_PATH = "/home/user/checkimport/input/processing/FAAC_Data_Elena_P_KIT_v5.xlsx"
JSON_PATH = "/home/user/checkimport/output/faac_verification_v2.json"
OUTPUT_DIR = "/home/user/checkimport/output"

def main():
    print("Creating suggested XLSX with corrections...")

    # Load verification data
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        verification = json.load(f)

    # Load original XLSX
    wb_original = openpyxl.load_workbook(XLSX_PATH)

    # Create new workbook for suggestions
    wb_new = Workbook()

    # Styles
    header_fill = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    change_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
    add_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
    error_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # Organize suggestions by product
    product_suggestions = defaultdict(list)
    for sugg in verification.get('all_suggestions', []):
        product_suggestions[sugg['product']].append(sugg)

    # Organize issues by product
    product_issues = defaultdict(list)
    for issue in verification.get('all_issues', []):
        product_issues[issue['product']].append(issue)

    # =====================
    # Sheet 1: Prodotti with Suggestions
    # =====================
    ws_prod_orig = wb_original['prodotti']
    ws_prod = wb_new.active
    ws_prod.title = "prodotti_SUGGESTED"

    # Copy headers
    for col in range(1, ws_prod_orig.max_column + 1):
        ws_prod.cell(row=1, column=col, value=ws_prod_orig.cell(row=1, column=col).value)
        ws_prod.cell(row=1, column=col).fill = header_fill
        ws_prod.cell(row=1, column=col).font = header_font

    ws_prod.cell(row=2, column=1, value="Italian Labels")
    for col in range(1, ws_prod_orig.max_column + 1):
        ws_prod.cell(row=2, column=col, value=ws_prod_orig.cell(row=2, column=col).value)

    # Add suggestion column
    sugg_col = ws_prod_orig.max_column + 1
    ws_prod.cell(row=1, column=sugg_col, value="SUGGESTED_CHANGES")
    ws_prod.cell(row=1, column=sugg_col).fill = header_fill
    ws_prod.cell(row=1, column=sugg_col).font = header_font

    # Copy data rows with suggestions
    for row in range(3, ws_prod_orig.max_row + 1):
        for col in range(1, ws_prod_orig.max_column + 1):
            orig_val = ws_prod_orig.cell(row=row, column=col).value
            ws_prod.cell(row=row, column=col, value=orig_val)

        # Get product name
        product_name = str(ws_prod_orig.cell(row=row, column=2).value or '')

        # Check for suggestions
        suggestions = product_suggestions.get(product_name, [])
        issues = product_issues.get(product_name, [])

        if suggestions or issues:
            # Build suggestion text
            sugg_texts = []

            # Kit code additions
            kit_codes_to_add = []
            for s in suggestions:
                if s['type'] == 'ADD_KIT_CODE':
                    kit_codes_to_add.append(s['value'])

            if kit_codes_to_add:
                sugg_texts.append(f"ADD kit codes: {';'.join(kit_codes_to_add)}")

            # Issues
            for issue in issues:
                if issue['type'] == 'KIT_CODE_NOT_IN_IDML':
                    sugg_texts.append(f"VERIFY: {issue['excel_value']} not in IDML")
                elif issue['type'] == 'NO_IDML_FOLDER':
                    sugg_texts.append("WARNING: No IDML source")

            if sugg_texts:
                ws_prod.cell(row=row, column=sugg_col, value=' | '.join(sugg_texts))
                ws_prod.cell(row=row, column=sugg_col).fill = change_fill

                # Highlight codici_modelli column (7) if there are kit code suggestions
                if kit_codes_to_add:
                    current_codes = ws_prod_orig.cell(row=row, column=7).value or ''
                    new_codes = str(current_codes) + ';' + ';'.join(kit_codes_to_add)
                    ws_prod.cell(row=row, column=7).fill = add_fill
                    ws_prod.cell(row=row, column=7).comment = Comment(
                        f"Suggested addition: {';'.join(kit_codes_to_add)}",
                        "Verification Script"
                    )

    # =====================
    # Sheet 2: SKU with Suggestions
    # =====================
    ws_sku_orig = wb_original['sku']
    ws_sku = wb_new.create_sheet("sku_SUGGESTED")

    # Copy headers
    for col in range(1, min(ws_sku_orig.max_column + 1, 50)):  # Limit columns
        ws_sku.cell(row=1, column=col, value=ws_sku_orig.cell(row=1, column=col).value)
        ws_sku.cell(row=1, column=col).fill = header_fill
        ws_sku.cell(row=1, column=col).font = header_font

    ws_sku.cell(row=2, column=1, value="Italian Labels")
    for col in range(1, min(ws_sku_orig.max_column + 1, 50)):
        ws_sku.cell(row=2, column=col, value=ws_sku_orig.cell(row=2, column=col).value)

    # Copy data rows
    for row in range(3, ws_sku_orig.max_row + 1):
        for col in range(1, min(ws_sku_orig.max_column + 1, 50)):
            ws_sku.cell(row=row, column=col, value=ws_sku_orig.cell(row=row, column=col).value)

    # =====================
    # Sheet 3: New SKUs to Add (from component suggestions)
    # =====================
    ws_new_skus = wb_new.create_sheet("NEW_SKUS_TO_ADD")

    new_sku_headers = ["codice_sku", "source_product", "suggestion_type", "notes"]
    for col, header in enumerate(new_sku_headers, 1):
        ws_new_skus.cell(row=1, column=col, value=header)
        ws_new_skus.cell(row=1, column=col).fill = header_fill
        ws_new_skus.cell(row=1, column=col).font = header_font

    row_num = 2
    seen_skus = set()
    for sugg in verification.get('all_suggestions', []):
        if sugg['type'] == 'ADD_COMPONENT_SKU':
            sku_val = sugg['value']
            if sku_val not in seen_skus:
                seen_skus.add(sku_val)
                ws_new_skus.cell(row=row_num, column=1, value=sku_val)
                ws_new_skus.cell(row=row_num, column=2, value=sugg['product'])
                ws_new_skus.cell(row=row_num, column=3, value=sugg['type'])
                ws_new_skus.cell(row=row_num, column=4, value=sugg['message'])
                ws_new_skus.cell(row=row_num, column=1).fill = add_fill
                row_num += 1

    # =====================
    # Sheet 4: Kit Code Updates
    # =====================
    ws_kit_updates = wb_new.create_sheet("KIT_CODE_UPDATES")

    kit_headers = ["product_name", "current_codes", "suggested_additions", "action"]
    for col, header in enumerate(kit_headers, 1):
        ws_kit_updates.cell(row=1, column=col, value=header)
        ws_kit_updates.cell(row=1, column=col).fill = header_fill
        ws_kit_updates.cell(row=1, column=col).font = header_font

    # Group kit code suggestions by product
    kit_updates = defaultdict(list)
    for sugg in verification.get('all_suggestions', []):
        if sugg['type'] == 'ADD_KIT_CODE':
            kit_updates[sugg['product']].append(sugg['value'])

    row_num = 2
    for product_name, codes in sorted(kit_updates.items()):
        # Find current codes in original
        current_codes = ""
        for row in range(3, ws_prod_orig.max_row + 1):
            if str(ws_prod_orig.cell(row=row, column=2).value or '') == product_name:
                current_codes = str(ws_prod_orig.cell(row=row, column=7).value or '')
                break

        ws_kit_updates.cell(row=row_num, column=1, value=product_name)
        ws_kit_updates.cell(row=row_num, column=2, value=current_codes)
        ws_kit_updates.cell(row=row_num, column=3, value=';'.join(codes))
        ws_kit_updates.cell(row=row_num, column=4, value="ADD to codici_modelli")
        ws_kit_updates.cell(row=row_num, column=3).fill = add_fill
        row_num += 1

    # =====================
    # Sheet 5: Issues to Review
    # =====================
    ws_issues = wb_new.create_sheet("ISSUES_TO_REVIEW")

    issue_headers = ["severity", "type", "product", "excel_value", "idml_value", "message"]
    for col, header in enumerate(issue_headers, 1):
        ws_issues.cell(row=1, column=col, value=header)
        ws_issues.cell(row=1, column=col).fill = header_fill
        ws_issues.cell(row=1, column=col).font = header_font

    # Only include HIGH severity issues
    row_num = 2
    for issue in verification.get('all_issues', []):
        if issue.get('severity') == 'HIGH':
            ws_issues.cell(row=row_num, column=1, value=issue.get('severity', ''))
            ws_issues.cell(row=row_num, column=2, value=issue['type'])
            ws_issues.cell(row=row_num, column=3, value=issue['product'])
            ws_issues.cell(row=row_num, column=4, value=str(issue.get('excel_value', '')))
            ws_issues.cell(row=row_num, column=5, value=str(issue.get('idml_value', '')))
            ws_issues.cell(row=row_num, column=6, value=issue['message'])
            ws_issues.cell(row=row_num, column=1).fill = error_fill
            row_num += 1

    # =====================
    # Sheet 6: Summary
    # =====================
    ws_summary = wb_new.create_sheet("SUMMARY", 0)  # Put at beginning

    summary_data = [
        ["FAAC DATA VERIFICATION - SUGGESTED EDITS"],
        [""],
        ["Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ["Source", os.path.basename(XLSX_PATH)],
        [""],
        ["VERIFICATION STATISTICS"],
        ["Products Verified", verification['statistics']['products_verified']],
        ["Products No IDML", verification['statistics']['products_no_idml']],
        ["Total Issues", verification['statistics']['issues_total']],
        ["Total Suggestions", verification['statistics']['suggestions_total']],
        [""],
        ["HIGH PRIORITY ITEMS"],
        ["Kit codes to verify", sum(1 for i in verification['all_issues'] if i['type'] == 'KIT_CODE_NOT_IN_IDML')],
        ["Products without IDML", sum(1 for i in verification['all_issues'] if i['type'] == 'NO_IDML_FOLDER')],
        [""],
        ["SUGGESTED ADDITIONS"],
        ["Kit codes to add", sum(1 for s in verification['all_suggestions'] if s['type'] == 'ADD_KIT_CODE')],
        ["Component SKUs to add", sum(1 for s in verification['all_suggestions'] if s['type'] == 'ADD_COMPONENT_SKU')],
        [""],
        ["SHEETS IN THIS WORKBOOK"],
        ["SUMMARY", "This overview"],
        ["prodotti_SUGGESTED", "Products sheet with suggested changes highlighted"],
        ["sku_SUGGESTED", "SKUs sheet (reference)"],
        ["NEW_SKUS_TO_ADD", "Component SKUs found in IDML not in SKU sheet"],
        ["KIT_CODE_UPDATES", "Kit codes to add to products"],
        ["ISSUES_TO_REVIEW", "HIGH severity issues requiring manual review"],
    ]

    for row_idx, row_data in enumerate(summary_data, 1):
        for col_idx, value in enumerate(row_data, 1):
            ws_summary.cell(row=row_idx, column=col_idx, value=value)

    ws_summary.cell(row=1, column=1).font = Font(bold=True, size=16)

    # Auto-width columns
    for ws in wb_new.worksheets:
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 60)
            ws.column_dimensions[column_letter].width = adjusted_width

    # Save
    output_path = os.path.join(OUTPUT_DIR, "FAAC_Data_Elena_P_KIT_v5_SUGGESTED_EDITS.xlsx")
    wb_new.save(output_path)
    print(f"Saved: {output_path}")

    wb_original.close()

    # Print summary
    print("\n" + "=" * 60)
    print("SUGGESTED EDITS SUMMARY")
    print("=" * 60)
    print(f"Kit codes to add: {len(kit_updates)} products affected")
    print(f"New component SKUs: {len(seen_skus)}")
    print(f"HIGH priority issues: {sum(1 for i in verification['all_issues'] if i.get('severity') == 'HIGH')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
