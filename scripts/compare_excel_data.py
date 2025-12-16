#!/usr/bin/env python3
"""
Excel Data Quality Comparison Script
Compares data files with FAAC_master_data_v1.xlsx
"""

import pandas as pd
import os
from pathlib import Path
import json

# Paths
MASTER_FILE = "/home/user/checkimport/output/FAAC_master_data_v1.xlsx"
EXTRACTED_DIR = "/home/user/checkimport/input/processing/extracted_data"

def read_excel_sheets(filepath):
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

def analyze_dataframe(df, name):
    """Analyze a dataframe for quality metrics"""
    if df is None or df.empty:
        return {"empty": True, "rows": 0, "cols": 0}

    analysis = {
        "rows": len(df),
        "cols": len(df.columns),
        "columns": list(df.columns),
        "null_counts": df.isnull().sum().to_dict(),
        "total_nulls": int(df.isnull().sum().sum()),
        "total_cells": int(df.size),
        "completeness_pct": round((1 - df.isnull().sum().sum() / df.size) * 100, 2) if df.size > 0 else 0,
        "dtypes": {str(k): str(v) for k, v in df.dtypes.to_dict().items()}
    }
    return analysis

def compare_with_master(data_df, master_df, data_file):
    """Compare a data file with master data"""
    errors = []
    warnings = []

    # Check column alignment
    data_cols = set(data_df.columns)
    master_cols = set(master_df.columns)

    missing_cols = master_cols - data_cols
    extra_cols = data_cols - master_cols

    if missing_cols:
        errors.append(f"Missing columns compared to master: {missing_cols}")
    if extra_cols:
        warnings.append(f"Extra columns not in master: {extra_cols}")

    # Check for common columns
    common_cols = data_cols & master_cols

    return {
        "missing_columns": list(missing_cols),
        "extra_columns": list(extra_cols),
        "common_columns": list(common_cols),
        "errors": errors,
        "warnings": warnings
    }

print("=" * 80)
print("EXCEL DATA QUALITY COMPARISON REPORT")
print("=" * 80)

# Read master file
print("\n" + "=" * 40)
print("MASTER FILE ANALYSIS")
print("=" * 40)
master_sheets = read_excel_sheets(MASTER_FILE)

if "error" in master_sheets:
    print(f"ERROR reading master file: {master_sheets['error']}")
else:
    print(f"\nMaster file: {os.path.basename(MASTER_FILE)}")
    print(f"Number of sheets: {len(master_sheets)}")
    for sheet_name, df in master_sheets.items():
        print(f"\n  Sheet: '{sheet_name}'")
        analysis = analyze_dataframe(df, sheet_name)
        print(f"    Rows: {analysis['rows']}")
        print(f"    Columns: {analysis['cols']}")
        print(f"    Completeness: {analysis['completeness_pct']}%")
        print(f"    Total null cells: {analysis['total_nulls']}")
        print(f"    Column names: {analysis['columns'][:10]}{'...' if len(analysis['columns']) > 10 else ''}")

# Read all data files
print("\n" + "=" * 80)
print("INDIVIDUAL DATA FILES ANALYSIS")
print("=" * 80)

data_files = sorted(Path(EXTRACTED_DIR).glob("*.xlsx"))
all_results = {}

for filepath in data_files:
    print(f"\n{'-' * 60}")
    print(f"FILE: {filepath.name}")
    print("-" * 60)

    sheets = read_excel_sheets(str(filepath))

    if "error" in sheets:
        print(f"  ERROR: {sheets['error']}")
        all_results[filepath.name] = {"error": sheets['error']}
        continue

    file_result = {
        "sheets": {},
        "total_rows": 0,
        "total_completeness": 0,
        "errors": [],
        "warnings": []
    }

    for sheet_name, df in sheets.items():
        print(f"\n  Sheet: '{sheet_name}'")
        analysis = analyze_dataframe(df, sheet_name)

        print(f"    Rows: {analysis['rows']}")
        print(f"    Columns: {analysis['cols']}")
        print(f"    Completeness: {analysis['completeness_pct']}%")
        print(f"    Total null cells: {analysis['total_nulls']}")

        # Check for specific issues
        if analysis['completeness_pct'] < 50:
            file_result["errors"].append(f"Sheet '{sheet_name}' has very low completeness ({analysis['completeness_pct']}%)")
            print(f"    *** ERROR: Very low completeness!")
        elif analysis['completeness_pct'] < 80:
            file_result["warnings"].append(f"Sheet '{sheet_name}' has low completeness ({analysis['completeness_pct']}%)")
            print(f"    ** WARNING: Low completeness")

        # Check for columns with high null rates
        for col, null_count in analysis['null_counts'].items():
            if analysis['rows'] > 0:
                null_pct = (null_count / analysis['rows']) * 100
                if null_pct > 50:
                    file_result["warnings"].append(f"Column '{col}' is {null_pct:.1f}% empty")

        file_result["sheets"][sheet_name] = analysis
        file_result["total_rows"] += analysis['rows']

    # Calculate average completeness
    completeness_vals = [s['completeness_pct'] for s in file_result['sheets'].values() if 'completeness_pct' in s]
    file_result["avg_completeness"] = round(sum(completeness_vals) / len(completeness_vals), 2) if completeness_vals else 0

    all_results[filepath.name] = file_result

    if file_result["errors"]:
        print(f"\n  ERRORS ({len(file_result['errors'])}):")
        for err in file_result["errors"]:
            print(f"    - {err}")

    if file_result["warnings"]:
        print(f"\n  WARNINGS ({len(file_result['warnings'])}):")
        for warn in file_result["warnings"][:5]:  # Limit to first 5
            print(f"    - {warn}")
        if len(file_result["warnings"]) > 5:
            print(f"    ... and {len(file_result['warnings']) - 5} more warnings")

# Summary and ratings
print("\n" + "=" * 80)
print("SUMMARY AND RATINGS")
print("=" * 80)

print("\n{:<30} {:>8} {:>12} {:>8} {:>8}".format("File", "Rows", "Completeness", "Errors", "Warnings"))
print("-" * 80)

ratings = {}
for filename, result in sorted(all_results.items()):
    if "error" in result:
        print(f"{filename:<30} {'ERROR':<8} {'N/A':>12} {'N/A':>8} {'N/A':>8}")
        ratings[filename] = {"score": 0, "grade": "F"}
        continue

    rows = result["total_rows"]
    completeness = result.get("avg_completeness", 0)
    errors = len(result.get("errors", []))
    warnings = len(result.get("warnings", []))

    print(f"{filename:<30} {rows:>8} {completeness:>11.1f}% {errors:>8} {warnings:>8}")

    # Calculate score
    score = completeness
    score -= errors * 10  # Heavy penalty for errors
    score -= warnings * 2  # Light penalty for warnings
    score = max(0, min(100, score))

    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    elif score >= 60:
        grade = "D"
    else:
        grade = "F"

    ratings[filename] = {"score": round(score, 1), "grade": grade, "completeness": completeness, "errors": errors, "warnings": warnings}

print("\n" + "=" * 40)
print("QUALITY RATINGS")
print("=" * 40)
print("\n{:<30} {:>8} {:>8}".format("File", "Score", "Grade"))
print("-" * 50)
for filename, rating in sorted(ratings.items(), key=lambda x: x[1]['score'], reverse=True):
    print(f"{filename:<30} {rating['score']:>7.1f} {rating['grade']:>8}")

# Save detailed results
output_file = "/home/user/checkimport/output/data_quality_report.json"
with open(output_file, 'w') as f:
    json.dump({
        "master_file": os.path.basename(MASTER_FILE),
        "files_analyzed": len(all_results),
        "results": all_results,
        "ratings": ratings
    }, f, indent=2, default=str)

print(f"\n\nDetailed results saved to: {output_file}")
