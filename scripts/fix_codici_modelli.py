#!/usr/bin/env python3
"""
Fix codici_modelli in FAAC_master_data_v2.xlsx by replacing with correct
model codes from Model_Codes_Master.csv.

The issue: codici_modelli was populated with ALL SKU codes (models + accessories)
The fix: Use only model SKUs from Models_gruppo tables
"""

import pandas as pd
from pathlib import Path

# Paths
BASE = Path('/home/user/checkimport/output')
MASTER_V2 = BASE / 'FAAC_master_data_v2.xlsx'
MODEL_CODES_CSV = BASE / 'Model_Codes_Master.csv'
MASTER_V3 = BASE / 'FAAC_master_data_v3.xlsx'


def main():
    print("Loading data...")

    # Load master v2
    prodotti_df = pd.read_excel(MASTER_V2, sheet_name='prodotti')
    sku_df = pd.read_excel(MASTER_V2, sheet_name='sku')

    print(f"  prodotti: {len(prodotti_df)} rows")
    print(f"  sku: {len(sku_df)} rows")

    # Load model codes
    model_codes_df = pd.read_csv(MODEL_CODES_CSV, sep=';')
    print(f"  model_codes: {len(model_codes_df)} rows")

    # Build page -> codici_modelli mapping
    page_to_models = {}
    for _, row in model_codes_df.iterrows():
        page = str(row['page'])
        codici = row['codici_modelli']
        if page not in page_to_models:
            page_to_models[page] = codici

    print(f"\nFound model codes for {len(page_to_models)} pages")

    # Update prodotti sheet
    print("\nUpdating codici_modelli...")
    updated = 0
    not_found = 0

    for idx, row in prodotti_df.iterrows():
        page = str(row['pagina_catalogo']).split('-')[0]  # Handle "100-101" -> "100"

        # Skip pages without model codes (likely kit or accessory pages)
        if page in page_to_models:
            old_value = row['codici_modelli']
            new_value = page_to_models[page]

            if old_value != new_value:
                prodotti_df.at[idx, 'codici_modelli'] = new_value
                updated += 1

                # Show some updates for verification
                if updated <= 10:
                    product = row['nome_prodotto']
                    print(f"  Page {page} ({product})")
                    print(f"    OLD: {str(old_value)[:60]}...")
                    print(f"    NEW: {new_value}")
        else:
            not_found += 1

    print(f"\nUpdated {updated} rows")
    print(f"Skipped {not_found} rows (no model codes found)")

    # Save to v3
    print(f"\nSaving to {MASTER_V3}...")
    with pd.ExcelWriter(MASTER_V3, engine='openpyxl') as writer:
        prodotti_df.to_excel(writer, sheet_name='prodotti', index=False)
        sku_df.to_excel(writer, sheet_name='sku', index=False)

    print("Done!")

    # Verify 770N 24V
    print("\n=== Verification: 770N 24V ===")
    for _, row in prodotti_df.iterrows():
        if '770N 24V' in str(row['nome_prodotto']):
            print(f"Product: {row['nome_prodotto']}")
            print(f"Page: {row['pagina_catalogo']}")
            print(f"codici_modelli: {row['codici_modelli']}")
            break


if __name__ == '__main__':
    main()
