#!/usr/bin/env python3
"""
Create FAAC_master_data_v2.xlsx by enhancing v1 with:
- Tech_Spec_Master_v1.csv data
- Sku_Notes_Master_v1.csv data
"""

import pandas as pd
from pathlib import Path

# Paths
BASE = Path('/home/user/checkimport/output')
MASTER_V1 = BASE / 'FAAC_master_data_v1.xlsx'
TECH_SPEC = BASE / 'Tech_Spec_Master_v1.csv'
SKU_NOTES = BASE / 'Sku_Notes_Master_v1.csv'
MASTER_V2 = BASE / 'FAAC_master_data_v2.xlsx'

# Mapping from Tech_Spec labels to SKU sheet columns
SPEC_TO_COLUMN = {
    'Tensione di alimentazione di rete': 'tensione_alimentazione',
    'Corrente assorbita': 'corrente_assorbita',
    'Motore elettrico': 'tipo_motore',
    'Potenza max': 'potenza_massima',
    'Coppia max': 'coppia_massima',
    'Forza max di spinta': 'forza_spinta',
    'Rapporto di riduzione': 'rapporto_riduzione',
    'Velocità angolare max': 'velocita_angolare',
    'Velocità dell\'anta': 'velocita_anta',
    'Lunghezza max anta': 'lunghezza_anta_max',
    'Lunghezza max asta': 'lunghezza_asta_max',
    'Spazio di fermata': 'spazio_fermata',
    'Regolazione velocità e controllo motore': 'controllo_motore',
    'Finecorsa': 'tipo_finecorsa',
    'Pignone': 'pignone',
    'Regolazione della forza': 'regolazione_forza',
    'Peso max anta': 'peso_anta_max',
    'Angolo max apertura anta': 'angolo_apertura_max',
    'Temperatura ambiente di esercizio': 'temperatura_esercizio',
    'Termoprotezione': 'termoprotezione',
    'Grado di protezione': 'grado_protezione_ip',
    'Peso': 'peso_unita',
    'Frequenza di utilizzo': 'frequenza_utilizzo',
    'Larghezza max anta': 'larghezza_anta_max',
    'Dimensioni (LxPxH)': 'dimensioni',
    'Apparecchiatura elettronica': 'scheda_elettronica',
    'Arresti meccanici integrati in apertura e chiusura': 'arresti_meccanici',
    'Tempo di utilizzo continuo (ROT)': 'tempo_utilizzo_continuo',
    'Tempo di apertura': 'tempo_apertura',
    'Encoder': 'encoder',
    'Tipo di rallentamento': 'tipo_rallentamento',
    'Tipo di asta': 'tipo_asta',
    'Dimensione del pilastro a sezione quadrata': 'dimensione_pilastro',
    'Dispositivo di sblocco': 'dispositivo_sblocco',
    'Condensatore di spunto': 'condensatore_spunto',
    'Corsa dello stelo': 'corsa_stelo',
    'Velocità max stelo': 'velocita_stelo',
    'Staffe di fissaggio': 'staffe_fissaggio',
    'Tipo di olio': 'tipo_olio',
    'Dimensioni colonna': 'dimensioni_colonna',
    'Peso max anta cantilever': 'peso_anta_cantilever',
    'Portata gruppo motore-pompa': 'portata_pompa',
}

def transform_tech_specs_to_sku_centric(tech_df):
    """Transform tech specs from row-per-spec to row-per-SKU format."""
    sku_specs = {}

    for _, row in tech_df.iterrows():
        spec_label = row['Spec_Label']
        if spec_label not in SPEC_TO_COLUMN:
            continue

        column_name = SPEC_TO_COLUMN[spec_label]

        # Process each model column (1-11)
        for i in range(1, 12):
            sku_col = f'Model_{i}_SKU'
            val_col = f'Value_{i}'

            if pd.notna(row.get(sku_col)) and pd.notna(row.get(val_col)):
                sku = str(int(row[sku_col])) if isinstance(row[sku_col], float) else str(row[sku_col])
                value = row[val_col]

                if sku not in sku_specs:
                    sku_specs[sku] = {}

                # Only set if not already set (first value wins)
                if column_name not in sku_specs[sku]:
                    sku_specs[sku][column_name] = value

    return sku_specs

def load_sku_notes(notes_df):
    """Load SKU notes and aggregate by SKU."""
    sku_notes = {}

    for _, row in notes_df.iterrows():
        sku = str(row['sku'])
        nota = row['nota']
        colore = row['colore_rombo']

        if sku not in sku_notes:
            sku_notes[sku] = []

        # Add note with color prefix
        note_text = f"[{colore}] {nota}"
        if note_text not in sku_notes[sku]:
            sku_notes[sku].append(note_text)

    # Join multiple notes
    return {sku: ' | '.join(notes) for sku, notes in sku_notes.items()}

def main():
    print("Loading data...")

    # Load master v1
    prodotti_df = pd.read_excel(MASTER_V1, sheet_name='prodotti')
    sku_df = pd.read_excel(MASTER_V1, sheet_name='sku')

    print(f"  prodotti: {len(prodotti_df)} rows")
    print(f"  sku: {len(sku_df)} rows")

    # Load tech specs
    tech_df = pd.read_csv(TECH_SPEC)
    print(f"  tech_specs: {len(tech_df)} rows")

    # Load SKU notes
    notes_df = pd.read_csv(SKU_NOTES, sep=';')
    print(f"  sku_notes: {len(notes_df)} rows")

    # Transform tech specs to SKU-centric
    print("\nTransforming tech specs...")
    sku_specs = transform_tech_specs_to_sku_centric(tech_df)
    print(f"  Found specs for {len(sku_specs)} SKUs")

    # Load SKU notes
    print("Loading SKU notes...")
    sku_notes = load_sku_notes(notes_df)
    print(f"  Found notes for {len(sku_notes)} SKUs")

    # Add note_accessorio column if not exists
    if 'note_accessorio' not in sku_df.columns:
        sku_df['note_accessorio'] = None

    # Update SKU sheet
    print("\nUpdating SKU sheet...")
    updated_specs = 0
    updated_notes = 0

    for idx, row in sku_df.iterrows():
        sku = str(row['codice_sku'])

        # Update tech specs (only if current value is NaN)
        if sku in sku_specs:
            for col, value in sku_specs[sku].items():
                if col in sku_df.columns and pd.isna(sku_df.at[idx, col]):
                    sku_df.at[idx, col] = value
                    updated_specs += 1

        # Update notes
        if sku in sku_notes:
            sku_df.at[idx, 'note_accessorio'] = sku_notes[sku]
            updated_notes += 1

    print(f"  Updated {updated_specs} spec values")
    print(f"  Updated {updated_notes} SKU notes")

    # Save to v2
    print(f"\nSaving to {MASTER_V2}...")
    with pd.ExcelWriter(MASTER_V2, engine='openpyxl') as writer:
        prodotti_df.to_excel(writer, sheet_name='prodotti', index=False)
        sku_df.to_excel(writer, sheet_name='sku', index=False)

    print("Done!")

    # Summary
    print("\n=== Summary ===")
    print(f"Input:  {MASTER_V1}")
    print(f"Output: {MASTER_V2}")
    print(f"  prodotti: {len(prodotti_df)} rows, {len(prodotti_df.columns)} columns")
    print(f"  sku: {len(sku_df)} rows, {len(sku_df.columns)} columns")

    # Show sample of notes added
    notes_sample = sku_df[sku_df['note_accessorio'].notna()][['codice_sku', 'descrizione_breve', 'note_accessorio']].head(5)
    if not notes_sample.empty:
        print("\nSample SKU notes added:")
        for _, r in notes_sample.iterrows():
            print(f"  {r['codice_sku']}: {r['note_accessorio'][:60]}...")

if __name__ == '__main__':
    main()
