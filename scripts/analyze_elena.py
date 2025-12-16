#!/usr/bin/env python3
"""
Detailed analysis of Elena P's file compared to others
"""

import pandas as pd
from pathlib import Path

EXTRACTED_DIR = "/home/user/checkimport/input/processing/extracted_data"

# Read all files
data_files = sorted(Path(EXTRACTED_DIR).glob("*.xlsx"))
all_data = {}

for filepath in data_files:
    xl = pd.ExcelFile(filepath)
    sheets = {}
    for sheet in xl.sheet_names:
        sheets[sheet] = pd.read_excel(xl, sheet_name=sheet)
    all_data[filepath.name] = sheets

elena = all_data.get("Data Elena P.xlsx", {})
elena_prodotti = elena.get('prodotti', pd.DataFrame())
elena_sku = elena.get('sku', pd.DataFrame())

print("=" * 80)
print("ELENA P's FILE - DETAILED COMPARISON")
print("=" * 80)

# Compare row counts
print("\n### ROW COUNTS COMPARISON ###\n")
print(f"{'File':<25} {'Prodotti':<12} {'SKU':<12}")
print("-" * 50)

for filename, sheets in sorted(all_data.items()):
    p_rows = len(sheets.get('prodotti', pd.DataFrame()))
    s_rows = len(sheets.get('sku', pd.DataFrame()))
    marker = " <-- ELENA" if "Elena" in filename else ""
    print(f"{filename:<25} {p_rows:<12} {s_rows:<12}{marker}")

print("\n" + "=" * 80)
print("ELENA P's UNIQUE CHARACTERISTICS")
print("=" * 80)

# Elena's prodotti analysis
print(f"\n### PRODOTTI SHEET ({len(elena_prodotti)} rows) ###\n")

# Count unique products
if 'nome_prodotto' in elena_prodotti.columns:
    unique_products = elena_prodotti['nome_prodotto'].nunique()
    total_products = len(elena_prodotti['nome_prodotto'].dropna())
    print(f"Unique products: {unique_products}")
    print(f"Total entries: {total_products}")
    print(f"Duplicates: {total_products - unique_products}")

# List all products Elena worked on
if 'nome_prodotto' in elena_prodotti.columns:
    print(f"\nProducts Elena entered:")
    for prod in elena_prodotti['nome_prodotto'].dropna().unique():
        print(f"  - {prod}")

# Elena's SKU analysis
print(f"\n### SKU SHEET ({len(elena_sku)} rows) ###\n")

# Check if Elena added new SKUs
print("SKU columns in Elena's file:")
for col in elena_sku.columns[:10]:
    filled = elena_sku[col].notna().sum()
    print(f"  {col}: {filled}/{len(elena_sku)} filled")

# Compare column structure
print("\n" + "=" * 80)
print("COLUMN STRUCTURE COMPARISON")
print("=" * 80)

# Get Elena's columns
elena_p_cols = set(elena_prodotti.columns)
elena_s_cols = set(elena_sku.columns)

# Compare with other files
print("\n### PRODOTTI COLUMNS ###\n")
for filename, sheets in sorted(all_data.items()):
    if "Elena" in filename:
        continue
    other_p = sheets.get('prodotti', pd.DataFrame())
    other_cols = set(other_p.columns)

    elena_only = elena_p_cols - other_cols
    other_only = other_cols - elena_p_cols

    if elena_only or other_only:
        print(f"\nCompared to {filename}:")
        if elena_only:
            print(f"  Elena has: {elena_only}")
        if other_only:
            print(f"  Other has: {other_only}")

print("\n### SKU COLUMNS ###\n")
for filename, sheets in sorted(all_data.items()):
    if "Elena" in filename:
        continue
    other_s = sheets.get('sku', pd.DataFrame())
    other_cols = set(other_s.columns)

    elena_only = elena_s_cols - other_cols
    other_only = other_cols - elena_s_cols

    if elena_only or other_only:
        print(f"\nCompared to {filename}:")
        if elena_only:
            print(f"  Elena has: {elena_only}")
        if other_only:
            print(f"  Other has: {other_only}")

# Check what makes Elena's file different
print("\n" + "=" * 80)
print("WHAT MAKES ELENA's FILE DIFFERENT")
print("=" * 80)

# 1. More prodotti rows
avg_prodotti = sum(len(d.get('prodotti', pd.DataFrame())) for d in all_data.values()) / len(all_data)
print(f"\n1. PRODOTTI ROWS:")
print(f"   Elena: {len(elena_prodotti)} rows")
print(f"   Average: {avg_prodotti:.1f} rows")
print(f"   Elena entered {len(elena_prodotti) - avg_prodotti:.1f} more rows than average")

# 2. More SKU rows
avg_sku = sum(len(d.get('sku', pd.DataFrame())) for d in all_data.values()) / len(all_data)
print(f"\n2. SKU ROWS:")
print(f"   Elena: {len(elena_sku)} rows")
print(f"   Average: {avg_sku:.1f} rows")
print(f"   Elena entered {len(elena_sku) - avg_sku:.1f} more rows than average")

# 3. Check completeness by column
print(f"\n3. PRODOTTI COMPLETENESS BY KEY COLUMN:")
key_cols = ['titolo_prodotto', 'descrizione_prodotto', 'codici_modelli', 'immagine_principale']
for col in key_cols:
    if col in elena_prodotti.columns:
        elena_fill = elena_prodotti[col].notna().sum() / len(elena_prodotti) * 100

        # Average for others
        other_fills = []
        for fname, sheets in all_data.items():
            if "Elena" in fname:
                continue
            p_df = sheets.get('prodotti', pd.DataFrame())
            if col in p_df.columns and len(p_df) > 0:
                other_fills.append(p_df[col].notna().sum() / len(p_df) * 100)

        avg_fill = sum(other_fills) / len(other_fills) if other_fills else 0
        diff = elena_fill - avg_fill
        print(f"   {col}: Elena {elena_fill:.1f}% vs Others {avg_fill:.1f}% (diff: {diff:+.1f}%)")

# 4. Check if Elena has missing codice_sku
print(f"\n4. SKU ISSUES:")
if 'codice_sku' in elena_sku.columns:
    print(f"   codice_sku column EXISTS in Elena's file")
    filled = elena_sku['codice_sku'].notna().sum()
    print(f"   Filled: {filled}/{len(elena_sku)} ({filled/len(elena_sku)*100:.1f}%)")
else:
    print(f"   *** codice_sku column MISSING in Elena's file! ***")
    # Check what column might be the SKU
    print(f"   Available columns: {list(elena_sku.columns)[:5]}")

# 5. Products coverage
print(f"\n5. PRODUCT CATEGORIES COVERED:")
if 'categoria_prodotto' in elena_prodotti.columns:
    categories = elena_prodotti['categoria_prodotto'].value_counts()
    for cat, count in categories.items():
        print(f"   {cat}: {count} products")
