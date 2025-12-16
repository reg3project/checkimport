#!/usr/bin/env python3
"""
Detailed Excel Data Quality Analysis
Comprehensive comparison of data files with FAAC_master_data_v1.xlsx
"""

import pandas as pd
import os
from pathlib import Path
from collections import defaultdict
import re

# Paths
MASTER_FILE = "/home/user/checkimport/output/FAAC_master_data_v1.xlsx"
EXTRACTED_DIR = "/home/user/checkimport/input/processing/extracted_data"

def read_excel_all_sheets(filepath):
    """Read all sheets from an Excel file"""
    try:
        xl = pd.ExcelFile(filepath)
        sheets = {}
        for sheet in xl.sheet_names:
            df = pd.read_excel(xl, sheet_name=sheet)
            sheets[sheet] = df
        return sheets
    except Exception as e:
        return {"error": str(e)}

# Read master file
print("Loading master file...")
master_sheets = read_excel_all_sheets(MASTER_FILE)
master_prodotti = master_sheets.get('prodotti', pd.DataFrame())
master_sku = master_sheets.get('sku', pd.DataFrame())

print(f"Master prodotti: {len(master_prodotti)} rows, {len(master_prodotti.columns)} columns")
print(f"Master sku: {len(master_sku)} rows, {len(master_sku.columns)} columns")

# Expected columns
PRODOTTI_KEY_COLUMNS = [
    'categoria_prodotto', 'nome_prodotto', 'pagina_catalogo', 'titolo_prodotto',
    'descrizione_prodotto', 'codici_modelli', 'immagine_principale'
]
SKU_KEY_COLUMNS = [
    'codice_sku', 'nome_modello', 'descrizione_breve', 'tipo_componente',
    'tensione_alimentazione', 'prezzo_listino'
]

# Read all data files
print("\nLoading data files...")
data_files = sorted(Path(EXTRACTED_DIR).glob("*.xlsx"))
all_data = {}

for filepath in data_files:
    sheets = read_excel_all_sheets(str(filepath))
    all_data[filepath.name] = sheets

print(f"Loaded {len(all_data)} files")

# Detailed Analysis
print("\n" + "=" * 100)
print("DETAILED DATA QUALITY ANALYSIS REPORT")
print("=" * 100)

# Create detailed results structure
detailed_results = {}

for filename, sheets in all_data.items():
    print(f"\n\n{'#' * 100}")
    print(f"FILE: {filename}")
    print('#' * 100)

    if "error" in sheets:
        print(f"ERROR: Could not read file - {sheets['error']}")
        continue

    file_report = {
        "prodotti": {"errors": [], "warnings": [], "stats": {}},
        "sku": {"errors": [], "warnings": [], "stats": {}},
        "precision_score": 0,
        "completeness_score": 0
    }

    # Analyze PRODOTTI sheet
    print("\n" + "-" * 80)
    print("PRODOTTI SHEET ANALYSIS")
    print("-" * 80)

    prodotti_df = sheets.get('prodotti', pd.DataFrame())
    if prodotti_df.empty:
        print("  ERROR: No 'prodotti' sheet found or sheet is empty")
        file_report["prodotti"]["errors"].append("Missing or empty prodotti sheet")
    else:
        rows = len(prodotti_df)
        cols = len(prodotti_df.columns)

        print(f"\n  Dimensions: {rows} rows x {cols} columns")

        # Column analysis
        print(f"\n  COLUMNS PRESENT ({cols}):")
        for col in prodotti_df.columns:
            non_null = prodotti_df[col].notna().sum()
            fill_pct = (non_null / rows * 100) if rows > 0 else 0
            empty_pct = 100 - fill_pct

            status = "OK" if fill_pct >= 80 else "WARNING" if fill_pct >= 50 else "ERROR"
            marker = "" if status == "OK" else " **" if status == "WARNING" else " ***"

            print(f"    {col:<40} {non_null:>4}/{rows:<4} ({fill_pct:>5.1f}% filled){marker}")

            if status == "ERROR":
                file_report["prodotti"]["errors"].append(f"Column '{col}' only {fill_pct:.1f}% filled ({non_null}/{rows})")
            elif status == "WARNING":
                file_report["prodotti"]["warnings"].append(f"Column '{col}' only {fill_pct:.1f}% filled")

        # Check for key columns
        print(f"\n  KEY COLUMNS CHECK:")
        for key_col in PRODOTTI_KEY_COLUMNS:
            if key_col in prodotti_df.columns:
                non_null = prodotti_df[key_col].notna().sum()
                fill_pct = (non_null / rows * 100) if rows > 0 else 0
                status = "OK" if fill_pct >= 80 else "MISSING DATA"
                print(f"    {key_col:<35} - {status} ({fill_pct:.1f}%)")
            else:
                print(f"    {key_col:<35} - COLUMN MISSING")
                file_report["prodotti"]["errors"].append(f"Key column '{key_col}' is missing")

        # Data quality checks
        print(f"\n  DATA QUALITY CHECKS:")

        # Check for duplicate rows
        if 'nome_prodotto' in prodotti_df.columns:
            duplicates = prodotti_df['nome_prodotto'].dropna().duplicated().sum()
            if duplicates > 0:
                print(f"    - Duplicate nome_prodotto entries: {duplicates} ***")
                file_report["prodotti"]["warnings"].append(f"{duplicates} duplicate product names found")
            else:
                print(f"    - No duplicate product names: OK")

        # Check pagina_catalogo format
        if 'pagina_catalogo' in prodotti_df.columns:
            invalid_pages = 0
            for val in prodotti_df['pagina_catalogo'].dropna():
                if not isinstance(val, (int, float)) and not str(val).replace('-', '').replace(' ', '').isdigit():
                    invalid_pages += 1
            if invalid_pages > 0:
                print(f"    - Invalid page number formats: {invalid_pages} **")
                file_report["prodotti"]["warnings"].append(f"{invalid_pages} invalid page number formats")
            else:
                print(f"    - Page number formats: OK")

        # Calculate stats
        total_cells = rows * cols
        filled_cells = prodotti_df.notna().sum().sum()
        file_report["prodotti"]["stats"] = {
            "rows": rows,
            "columns": cols,
            "filled_cells": int(filled_cells),
            "total_cells": total_cells,
            "completeness": round(filled_cells / total_cells * 100, 2) if total_cells > 0 else 0
        }

    # Analyze SKU sheet
    print("\n" + "-" * 80)
    print("SKU SHEET ANALYSIS")
    print("-" * 80)

    sku_df = sheets.get('sku', pd.DataFrame())
    if sku_df.empty:
        print("  ERROR: No 'sku' sheet found or sheet is empty")
        file_report["sku"]["errors"].append("Missing or empty sku sheet")
    else:
        rows = len(sku_df)
        cols = len(sku_df.columns)

        print(f"\n  Dimensions: {rows} rows x {cols} columns")

        # Count filled vs empty columns
        filled_columns = []
        sparse_columns = []
        empty_columns = []

        for col in sku_df.columns:
            non_null = sku_df[col].notna().sum()
            fill_pct = (non_null / rows * 100) if rows > 0 else 0

            if fill_pct >= 50:
                filled_columns.append((col, fill_pct, non_null))
            elif fill_pct > 0:
                sparse_columns.append((col, fill_pct, non_null))
            else:
                empty_columns.append(col)

        print(f"\n  COLUMN SUMMARY:")
        print(f"    - Well-filled columns (>=50%): {len(filled_columns)}")
        print(f"    - Sparse columns (>0% <50%): {len(sparse_columns)}")
        print(f"    - Empty columns (0%): {len(empty_columns)}")

        print(f"\n  WELL-FILLED COLUMNS ({len(filled_columns)}):")
        for col, pct, count in sorted(filled_columns, key=lambda x: -x[1]):
            print(f"    {col:<40} {count:>4}/{rows:<4} ({pct:>5.1f}%)")

        if sparse_columns:
            print(f"\n  SPARSE COLUMNS ({len(sparse_columns)}):")
            for col, pct, count in sorted(sparse_columns, key=lambda x: -x[1])[:15]:  # Top 15
                print(f"    {col:<40} {count:>4}/{rows:<4} ({pct:>5.1f}%)")
                file_report["sku"]["warnings"].append(f"Column '{col}' only {pct:.1f}% filled")
            if len(sparse_columns) > 15:
                print(f"    ... and {len(sparse_columns) - 15} more sparse columns")

        if empty_columns:
            print(f"\n  EMPTY COLUMNS ({len(empty_columns)}):")
            for col in empty_columns[:10]:
                print(f"    {col}")
                file_report["sku"]["errors"].append(f"Column '{col}' is completely empty")
            if len(empty_columns) > 10:
                print(f"    ... and {len(empty_columns) - 10} more empty columns")

        # Key columns check
        print(f"\n  KEY COLUMNS CHECK:")
        for key_col in SKU_KEY_COLUMNS:
            if key_col in sku_df.columns:
                non_null = sku_df[key_col].notna().sum()
                fill_pct = (non_null / rows * 100) if rows > 0 else 0
                status = "OK" if fill_pct >= 50 else "MISSING DATA"
                print(f"    {key_col:<35} - {status} ({fill_pct:.1f}%)")
            else:
                print(f"    {key_col:<35} - COLUMN MISSING")
                file_report["sku"]["errors"].append(f"Key column '{key_col}' is missing")

        # Data quality checks
        print(f"\n  DATA QUALITY CHECKS:")

        # Check for duplicate SKUs
        if 'codice_sku' in sku_df.columns:
            sku_values = sku_df['codice_sku'].dropna()
            duplicates = sku_values.duplicated().sum()
            if duplicates > 0:
                print(f"    - Duplicate codice_sku entries: {duplicates} ***")
                file_report["sku"]["errors"].append(f"{duplicates} duplicate SKU codes found")
            else:
                print(f"    - No duplicate SKU codes: OK")

            # Check SKU format
            invalid_skus = 0
            for sku in sku_values:
                if not isinstance(sku, str):
                    continue
                # SKUs should match patterns like numbers or alphanumeric codes
                if len(str(sku).strip()) < 3:
                    invalid_skus += 1
            if invalid_skus > 0:
                print(f"    - Short/invalid SKU codes: {invalid_skus} **")

        # Calculate stats
        total_cells = rows * cols
        filled_cells = sku_df.notna().sum().sum()
        file_report["sku"]["stats"] = {
            "rows": rows,
            "columns": cols,
            "filled_cells": int(filled_cells),
            "total_cells": total_cells,
            "completeness": round(filled_cells / total_cells * 100, 2) if total_cells > 0 else 0,
            "filled_columns": len(filled_columns),
            "sparse_columns": len(sparse_columns),
            "empty_columns": len(empty_columns)
        }

    # Calculate overall scores
    prodotti_completeness = file_report["prodotti"]["stats"].get("completeness", 0)
    sku_completeness = file_report["sku"]["stats"].get("completeness", 0)

    # Weight prodotti more heavily (it's usually more complete)
    weighted_completeness = (prodotti_completeness * 0.6 + sku_completeness * 0.4)

    # Adjust for errors and warnings
    error_penalty = len(file_report["prodotti"]["errors"]) * 5 + len(file_report["sku"]["errors"]) * 3
    warning_penalty = (len(file_report["prodotti"]["warnings"]) + len(file_report["sku"]["warnings"])) * 0.5

    final_score = max(0, min(100, weighted_completeness - error_penalty - warning_penalty))

    file_report["completeness_score"] = round(weighted_completeness, 1)
    file_report["final_score"] = round(final_score, 1)

    detailed_results[filename] = file_report

# Summary Table
print("\n\n" + "=" * 100)
print("FINAL SUMMARY")
print("=" * 100)

print("\n{:<25} {:>10} {:>10} {:>12} {:>12} {:>8} {:>8} {:>10}".format(
    "File", "Prodotti", "SKU", "Prodotti %", "SKU %", "Errors", "Warns", "Score"))
print("-" * 100)

rankings = []
for filename, report in sorted(detailed_results.items()):
    p_rows = report["prodotti"]["stats"].get("rows", 0)
    s_rows = report["sku"]["stats"].get("rows", 0)
    p_pct = report["prodotti"]["stats"].get("completeness", 0)
    s_pct = report["sku"]["stats"].get("completeness", 0)
    errors = len(report["prodotti"]["errors"]) + len(report["sku"]["errors"])
    warnings = len(report["prodotti"]["warnings"]) + len(report["sku"]["warnings"])
    score = report.get("final_score", 0)

    print(f"{filename:<25} {p_rows:>10} {s_rows:>10} {p_pct:>11.1f}% {s_pct:>11.1f}% {errors:>8} {warnings:>8} {score:>9.1f}")
    rankings.append((filename, score, p_pct, s_pct, errors, warnings))

# Rankings
print("\n\n" + "=" * 100)
print("QUALITY RANKINGS (Best to Worst)")
print("=" * 100)

rankings.sort(key=lambda x: (-x[1], -x[2], -x[3], x[4]))

print("\n{:<4} {:<25} {:>10} {:>15}".format("Rank", "File", "Score", "Grade"))
print("-" * 60)

def get_grade(score):
    if score >= 45:
        return "A"
    elif score >= 35:
        return "B"
    elif score >= 25:
        return "C"
    elif score >= 15:
        return "D"
    else:
        return "F"

for i, (filename, score, p_pct, s_pct, errors, warnings) in enumerate(rankings, 1):
    grade = get_grade(score)
    print(f"{i:<4} {filename:<25} {score:>9.1f} {grade:>15}")

# Detailed error/warning report
print("\n\n" + "=" * 100)
print("DETAILED ERROR AND WARNING REPORT")
print("=" * 100)

for filename, report in sorted(detailed_results.items()):
    print(f"\n{'=' * 60}")
    print(f"FILE: {filename}")
    print("=" * 60)

    p_errors = report["prodotti"]["errors"]
    p_warnings = report["prodotti"]["warnings"]
    s_errors = report["sku"]["errors"]
    s_warnings = report["sku"]["warnings"]

    if p_errors:
        print(f"\n  PRODOTTI ERRORS ({len(p_errors)}):")
        for err in p_errors[:10]:
            print(f"    [ERROR] {err}")
        if len(p_errors) > 10:
            print(f"    ... and {len(p_errors) - 10} more errors")

    if p_warnings:
        print(f"\n  PRODOTTI WARNINGS ({len(p_warnings)}):")
        for warn in p_warnings[:5]:
            print(f"    [WARN] {warn}")
        if len(p_warnings) > 5:
            print(f"    ... and {len(p_warnings) - 5} more warnings")

    if s_errors:
        print(f"\n  SKU ERRORS ({len(s_errors)}):")
        for err in s_errors[:10]:
            print(f"    [ERROR] {err}")
        if len(s_errors) > 10:
            print(f"    ... and {len(s_errors) - 10} more errors")

    if s_warnings:
        print(f"\n  SKU WARNINGS ({len(s_warnings)}):")
        for warn in s_warnings[:5]:
            print(f"    [WARN] {warn}")
        if len(s_warnings) > 5:
            print(f"    ... and {len(s_warnings) - 5} more warnings")

# Master comparison
print("\n\n" + "=" * 100)
print("COMPARISON WITH MASTER FILE")
print("=" * 100)

print(f"\nMASTER FILE STATS:")
print(f"  Prodotti: {len(master_prodotti)} rows x {len(master_prodotti.columns)} columns")
print(f"  SKU: {len(master_sku)} rows x {len(master_sku.columns)} columns")

master_p_completeness = (master_prodotti.notna().sum().sum() / master_prodotti.size * 100) if master_prodotti.size > 0 else 0
master_s_completeness = (master_sku.notna().sum().sum() / master_sku.size * 100) if master_sku.size > 0 else 0

print(f"  Prodotti completeness: {master_p_completeness:.1f}%")
print(f"  SKU completeness: {master_s_completeness:.1f}%")

print(f"\nCOLUMN COMPARISON:")
master_p_cols = set(master_prodotti.columns)
master_s_cols = set(master_sku.columns)

for filename, sheets in all_data.items():
    if "error" in sheets:
        continue

    prodotti_df = sheets.get('prodotti', pd.DataFrame())
    sku_df = sheets.get('sku', pd.DataFrame())

    p_cols = set(prodotti_df.columns) if not prodotti_df.empty else set()
    s_cols = set(sku_df.columns) if not sku_df.empty else set()

    missing_p = master_p_cols - p_cols
    extra_p = p_cols - master_p_cols
    missing_s = master_s_cols - s_cols
    extra_s = s_cols - master_s_cols

    print(f"\n  {filename}:")
    if missing_p:
        print(f"    Prodotti - Missing columns: {len(missing_p)} - {list(missing_p)[:5]}")
    if extra_p:
        print(f"    Prodotti - Extra columns: {len(extra_p)} - {list(extra_p)[:5]}")
    if missing_s:
        print(f"    SKU - Missing columns: {len(missing_s)}")
    if extra_s:
        print(f"    SKU - Extra columns: {len(extra_s)} - {list(extra_s)[:5]}")
    if not missing_p and not extra_p and not missing_s and not extra_s:
        print(f"    Column structure matches master file")

print("\n\nReport complete!")
