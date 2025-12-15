#!/usr/bin/env python3
"""
Extract all IDML files and create a mega Excel with double headers

Output structure:
- Sheet "prodotti": Product-level data with double header (field/label)
- Sheet "sku": SKU-level technical specs with double header (field/label)

Features:
- Duplicate SKUs with different descriptions are preserved
- Double header: row 1 = field name, row 2 = Italian label
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.idml_parser import parse_idml
from src.table_extractor import extract_all_from_document, SKUSpecs, ProductTableData
from src.text_extractor import extract_product_info, ProductInfo

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
    from openpyxl.utils import get_column_letter
except ImportError:
    print("Error: openpyxl required. Install with: pip install openpyxl")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ============================================================================
# COLUMN DEFINITIONS WITH ITALIAN LABELS
# ============================================================================

# Prodotti columns: (field_name, italian_label)
PRODOTTI_COLUMNS = [
    ('source_file', 'File Sorgente'),
    ('pagina_catalogo', 'Pagina Catalogo'),
    ('nome_prodotto', 'Nome Prodotto'),
    ('titolo_prodotto', 'Titolo Prodotto'),
    ('categoria_prodotto', 'Categoria'),
    ('tipo_layout', 'Tipo Layout'),
    ('descrizione_prodotto', 'Descrizione'),
    ('descrizione_breve', 'Descrizione Breve'),
    ('caratteristica_primaria', 'Caratteristica Primaria'),
    ('valore_primario', 'Valore Primario'),
    ('caratteristica_secondaria', 'Caratteristica Secondaria'),
    ('valore_secondario', 'Valore Secondario'),
    ('intensita_transito', 'Intensità Transito'),
    ('badge_sistemi', 'Badge Sistemi'),
    ('certificazioni', 'Certificazioni'),
    ('codici_modelli', 'Codici Modelli'),
    ('componenti_kit', 'Componenti Kit'),
    ('sku_correlati', 'SKU Correlati'),
    ('note_prodotto', 'Note Prodotto'),
    ('immagini', 'Immagini'),
    ('accessori', 'Accessori'),
]

# SKU columns: (field_name, italian_label)
SKU_COLUMNS = [
    ('source_file', 'File Sorgente'),
    ('pagina_catalogo', 'Pagina Catalogo'),
    ('nome_prodotto', 'Nome Prodotto'),
    ('SKU', 'SKU'),
    ('Nome Modello', 'Nome Modello'),
    ('Descrizione Breve', 'Descrizione Breve'),
    ('Confezione', 'Confezione'),
    ('Note', 'Note'),
    # Electrical specs
    ('Tensione di alimentazione di rete', 'Tensione Alimentazione'),
    ('Corrente assorbita', 'Corrente Assorbita'),
    ('Motore elettrico', 'Motore Elettrico'),
    ('Potenza max', 'Potenza Max'),
    ('Coppia max', 'Coppia Max'),
    # Mechanical specs
    ('Forza max di spinta', 'Forza Max Spinta'),
    ('Rapporto di riduzione', 'Rapporto Riduzione'),
    ('Velocità angolare max', 'Velocità Angolare Max'),
    ("Velocità dell'anta", 'Velocità Anta'),
    ('Velocità max stelo', 'Velocità Max Stelo'),
    ('Corsa dello stelo', 'Corsa Stelo'),
    ('Angolo max apertura anta', 'Angolo Max Apertura'),
    # Dimensions
    ('Lunghezza max anta', 'Lunghezza Max Anta'),
    ('Lunghezza max asta', 'Lunghezza Max Asta'),
    ('Larghezza max anta', 'Larghezza Max Anta'),
    ('Peso max anta', 'Peso Max Anta'),
    ('Peso', 'Peso'),
    ('Dimensioni (LxPxH)', 'Dimensioni (LxPxH)'),
    # Environment
    ('Temperatura ambiente di esercizio', 'Temperatura Esercizio'),
    ('Termoprotezione', 'Termoprotezione'),
    ('Grado di protezione', 'Grado Protezione IP'),
    # Usage
    ('Frequenza di utilizzo', 'Frequenza Utilizzo'),
    ('Tempo di utilizzo continuo (ROT)', 'Tempo Utilizzo Continuo'),
    # Control
    ('Apparecchiatura elettronica', 'Apparecchiatura Elettronica'),
    ('Finecorsa', 'Finecorsa'),
    ('Encoder', 'Encoder'),
    ('Regolazione velocità e controllo motore', 'Regolazione Velocità'),
    ('Regolazione della forza', 'Regolazione Forza'),
    # Other
    ('Tipo di materiale', 'Tipo Materiale'),
    ('Tipo di trattamento', 'Tipo Trattamento'),
    ('Tipo di rallentamento', 'Tipo Rallentamento'),
    ('Tipo di asta', 'Tipo Asta'),
    ('Dispositivo di sblocco', 'Dispositivo Sblocco'),
    ('Pignone', 'Pignone'),
    ('Condensatore di spunto', 'Condensatore Spunto'),
    # Hydraulic
    ('Portata gruppo motore-pompa', 'Portata Pompa'),
    ('Tipo di olio', 'Tipo Olio'),
    ('Staffe di fissaggio', 'Staffe Fissaggio'),
    # Misc
    ('Arresti meccanici integrati in apertura e chiusura', 'Arresti Meccanici'),
    ('Spazio di fermata', 'Spazio Fermata'),
    ('Tempo di apertura', 'Tempo Apertura'),
]


class MegaExcelWriter:
    """Write extraction results to a mega Excel file with double headers"""

    HEADER_FILL = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    LABEL_FILL = PatternFill(start_color="8FAADC", end_color="8FAADC", fill_type="solid")
    HEADER_FONT = Font(bold=True, color="FFFFFF")
    LABEL_FONT = Font(bold=True, color="000000")
    BORDER = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    def __init__(self, output_path: Path):
        self.output_path = Path(output_path)
        self.workbook = Workbook()

    def write(self, prodotti_data: List[Dict], sku_data: List[Dict]) -> Path:
        """Write data to Excel file"""
        # Remove default sheet
        if 'Sheet' in self.workbook.sheetnames:
            del self.workbook['Sheet']

        # Create sheets
        self._write_prodotti_sheet(prodotti_data)
        self._write_sku_sheet(sku_data)

        # Save
        self.workbook.save(self.output_path)
        logger.info(f"Wrote Excel to: {self.output_path}")
        return self.output_path

    def _write_prodotti_sheet(self, data: List[Dict]):
        """Write prodotti sheet with double header"""
        ws = self.workbook.create_sheet("prodotti")

        # Row 1: Field names
        for col, (field, label) in enumerate(PRODOTTI_COLUMNS, 1):
            cell = ws.cell(row=1, column=col, value=field)
            cell.fill = self.HEADER_FILL
            cell.font = self.HEADER_FONT
            cell.border = self.BORDER
            cell.alignment = Alignment(horizontal='center')

        # Row 2: Italian labels
        for col, (field, label) in enumerate(PRODOTTI_COLUMNS, 1):
            cell = ws.cell(row=2, column=col, value=label)
            cell.fill = self.LABEL_FILL
            cell.font = self.LABEL_FONT
            cell.border = self.BORDER
            cell.alignment = Alignment(horizontal='center')

        # Data rows starting from row 3
        for row_idx, row_data in enumerate(data, 3):
            for col, (field, _) in enumerate(PRODOTTI_COLUMNS, 1):
                value = row_data.get(field, "")
                cell = ws.cell(row=row_idx, column=col, value=value)
                cell.border = self.BORDER

        # Freeze panes (first 2 rows)
        ws.freeze_panes = 'A3'
        self._adjust_column_widths(ws)

    def _write_sku_sheet(self, data: List[Dict]):
        """Write SKU sheet with double header"""
        ws = self.workbook.create_sheet("sku")

        # Row 1: Field names
        for col, (field, label) in enumerate(SKU_COLUMNS, 1):
            cell = ws.cell(row=1, column=col, value=field)
            cell.fill = self.HEADER_FILL
            cell.font = self.HEADER_FONT
            cell.border = self.BORDER
            cell.alignment = Alignment(horizontal='center')

        # Row 2: Italian labels
        for col, (field, label) in enumerate(SKU_COLUMNS, 1):
            cell = ws.cell(row=2, column=col, value=label)
            cell.fill = self.LABEL_FILL
            cell.font = self.LABEL_FONT
            cell.border = self.BORDER
            cell.alignment = Alignment(horizontal='center')

        # Data rows starting from row 3
        for row_idx, row_data in enumerate(data, 3):
            for col, (field, _) in enumerate(SKU_COLUMNS, 1):
                value = row_data.get(field, "")
                cell = ws.cell(row=row_idx, column=col, value=value)
                cell.border = self.BORDER

        # Freeze panes
        ws.freeze_panes = 'A3'
        self._adjust_column_widths(ws)

    def _adjust_column_widths(self, ws):
        """Auto-adjust column widths"""
        for column in ws.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)

            for cell in column:
                try:
                    cell_length = len(str(cell.value or ""))
                    if cell_length > max_length:
                        max_length = cell_length
                except:
                    pass

            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = max(adjusted_width, 10)


def extract_from_idml(idml_path: Path) -> Tuple[Dict, List[Dict]]:
    """Extract product and SKU data from a single IDML file"""
    try:
        # Parse IDML
        document = parse_idml(idml_path)

        # Extract product info
        product_info = extract_product_info(document)

        # Extract table data (specs + product data like confezioni)
        sku_specs_list, product_table_data = extract_all_from_document(document)

        # Build product row
        product_row = {
            'source_file': idml_path.name,
            'pagina_catalogo': product_info.pagina_catalogo,
            'nome_prodotto': product_info.name,
            'titolo_prodotto': product_info.titolo_prodotto,
            'categoria_prodotto': product_info.category,
            'tipo_layout': product_info.tipo_layout,
            'descrizione_prodotto': product_info.description,
            'descrizione_breve': product_info.short_description,
            'caratteristica_primaria': product_info.caratteristica_primaria,
            'valore_primario': product_info.valore_primario,
            'caratteristica_secondaria': product_info.caratteristica_secondaria,
            'valore_secondario': product_info.valore_secondario,
            'intensita_transito': product_info.intensita_transito,
            'badge_sistemi': '; '.join(product_info.badge_sistemi),
            'certificazioni': '; '.join(product_info.certifications),
            'codici_modelli': product_info.codici_modelli or '; '.join(product_info.sku_codes),
            'componenti_kit': product_table_data.get_componenti_kit() if product_table_data else '',
            'sku_correlati': product_table_data.get_sku_correlati() if product_table_data else '',
            'note_prodotto': product_table_data.get_product_notes() if product_table_data else '',
            'immagini': '; '.join(product_info.images),
            'accessori': '; '.join(product_info.accessories),
        }

        # Build SKU rows
        sku_rows = []
        for sku_spec in sku_specs_list:
            sku_row = {
                'source_file': idml_path.name,
                'pagina_catalogo': product_info.pagina_catalogo,
                'nome_prodotto': product_info.name,
            }

            # Add all specs from sku_spec.to_dict()
            specs_dict = sku_spec.to_dict()
            sku_row.update(specs_dict)

            # Ensure SKU field is populated
            if not sku_row.get('SKU'):
                sku_row['SKU'] = sku_spec.sku

            sku_rows.append(sku_row)

        return product_row, sku_rows

    except Exception as e:
        logger.error(f"Error extracting {idml_path.name}: {e}")
        return None, []


def main():
    # Input/output paths
    idml_dir = Path("/home/user/checkimport/input/processing/IDML")
    output_dir = Path("/home/user/checkimport/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"mega_extraction_{timestamp}.xlsx"

    # Get all IDML files
    idml_files = sorted(idml_dir.glob("*.idml"))
    logger.info(f"Found {len(idml_files)} IDML files to process")

    # Extract from all files
    all_prodotti = []
    all_sku = []

    for i, idml_path in enumerate(idml_files, 1):
        logger.info(f"[{i}/{len(idml_files)}] Processing: {idml_path.name}")

        product_row, sku_rows = extract_from_idml(idml_path)

        if product_row:
            all_prodotti.append(product_row)

        if sku_rows:
            all_sku.extend(sku_rows)

    logger.info(f"\nExtraction complete:")
    logger.info(f"  - Products: {len(all_prodotti)}")
    logger.info(f"  - SKUs: {len(all_sku)}")

    # Write to Excel
    writer = MegaExcelWriter(output_file)
    writer.write(all_prodotti, all_sku)

    logger.info(f"\nOutput saved to: {output_file}")

    # Summary stats
    unique_skus = len(set(row.get('SKU', '') for row in all_sku if row.get('SKU')))
    logger.info(f"  - Unique SKUs: {unique_skus}")
    logger.info(f"  - Duplicate SKU entries: {len(all_sku) - unique_skus}")


if __name__ == "__main__":
    main()
