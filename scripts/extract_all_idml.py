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
# COLUMN DEFINITIONS - MATCHING Data.xlsx EXACTLY
# ============================================================================

# Prodotti columns: (field_name, italian_label) - 35 columns from Data.xlsx
PRODOTTI_COLUMNS = [
    ('categoria_prodotto', 'Categoria'),
    ('nome_prodotto', 'Prodotto'),
    ('nome_asta', 'Nome Asta'),  # For barriers: asta tonda, asta rettangolare
    ('pagina_catalogo', 'Page'),
    ('tipo_layout', 'Layout'),
    ('immagine_principale', 'Prodotto Immagine'),
    ('codici_modelli', 'Modelli'),
    ('titolo_prodotto', 'Titolo'),
    ('descrizione_prodotto', 'Descrizione'),
    ('intensita_transito', 'Transito (Basso;Medio;Alto)'),
    ('caratteristica_primaria', 'Prodotto Caratteristica Label 1'),
    ('valore_primario', 'Prodotto Caratteristica Value 1'),
    ('caratteristica_secondaria', 'Prodotto Caratteristica Label 2'),
    ('valore_secondario', 'Prodotto Caratteristica Value 2'),
    ('novita', 'New'),
    ('veloce', 'Fast'),
    ('solare', 'Solar'),
    ('brevetto_faac', 'FAAC Patent'),
    ('badge_sistemi', 'Icone'),
    ('codice_qr', 'QRCode'),
    ('certificazioni', 'Certificazioni'),
    ('descrizione_categoria', 'Categoria Descrizione Intestazione Prodotto'),
    ('contenuto_confezione', 'Confezioni'),
    ('schema_installazione', 'Schema Installazione'),
    ('immagine_schema', 'Schema Immagine'),
    ('componenti_kit', 'Kit'),
    ('immagine_kit', 'Kit Immagine'),
    ('sku_correlati', 'SKU Correlate'),
    ('prodotti_correlati', 'Prodotti Correlati'),
    ('note_prodotto', 'Note'),
    ('quote_installazione', 'Quote'),
    ('grafico_tecnico', 'Grafico'),
    ('tabella_molle', 'Tabella Numero Molle'),
    ('accessori_disponibili', 'Altri Accessori'),
    ('prototipo', 'Prototype'),
]

# SKU columns: (field_name, italian_label) - 61 columns from Data.xlsx
SKU_COLUMNS = [
    ('codice_sku', 'SKU'),
    ('quantita', 'COUNTIF'),
    ('immagine_sku', 'SKU Immagine'),
    ('ordine_tipo_componente', 'Ordine Tipo'),
    ('tipo_componente', 'Tipo'),
    ('nome_modello', 'Nome Modello'),
    ('modelli_correlati', 'Modelli Correlati'),
    ('descrizione_breve', 'Descrizione Breve'),
    ('tensione_alimentazione', 'Tensione di alimentazione di rete'),
    ('corrente_assorbita', 'Corrente assorbita'),
    ('tipo_motore', 'Motore elettrico'),
    ('potenza_massima', 'Potenza max'),
    ('coppia_massima', 'Coppia max'),
    ('materiale', 'Tipo di materiale'),
    ('trattamento_superficiale', 'Tipo di trattamento'),
    ('forza_spinta', 'Forza max di spinta'),
    ('rapporto_riduzione', 'Rapporto di riduzione'),
    ('numero_max_schede_collegabili', 'Numero max schede di decodifica collegabili'),
    ('velocita_angolare', 'Velocità angolare max'),
    ('velocita_anta', "Velocità dell'anta"),
    ('lunghezza_anta_max', 'Lunghezza max anta'),
    ('lunghezza_asta_max', 'Lunghezza max asta'),
    ('spazio_fermata', 'Spazio di fermata'),
    ('controllo_motore', 'Regolazione velocità e controllo motore'),
    ('tipo_finecorsa', 'Finecorsa'),
    ('pignone', 'Pignone'),
    ('regolazione_forza', 'Regolazione della forza'),
    ('peso_anta_max', 'Peso max anta'),
    ('angolo_apertura_max', 'Angolo max apertura anta'),
    ('temperatura_esercizio', 'Temperatura ambiente di esercizio'),
    ('termoprotezione', 'Termoprotezione'),
    ('grado_protezione_ip', 'Grado di protezione'),
    ('peso_unita', 'Peso'),
    ('frequenza_utilizzo', 'Frequenza di utilizzo'),
    ('larghezza_anta_max', 'Larghezza max anta'),
    ('dimensioni', 'Dimensioni (LxPxH)'),
    ('scheda_elettronica', 'Apparecchiatura elettronica'),
    ('arresti_meccanici', 'Arresti meccanici integrati in apertura e chiusura'),
    ('tempo_utilizzo_continuo', 'Tempo di utilizzo continuo (ROT)'),
    ('tempo_apertura', 'Tempo di apertura'),
    ('encoder', 'Encoder'),
    ('tipo_rallentamento', 'Tipo di rallentamento'),
    ('tipo_asta', 'Tipo di asta'),
    ('dimensione_pilastro', 'Dimensione del pilastro a sezione quadrata'),
    ('dispositivo_sblocco', 'Dispositivo di sblocco'),
    ('condensatore_spunto', 'Condensatore di spunto'),
    ('lunghezza_mm', 'Lunghezza (mm)'),
    ('unita_misura_prezzo', 'Unità Misura Prezzo'),
    ('icona_badge', 'Icona 1'),
    ('decodifica_radio', 'Decodifica'),
    ('memoria_codici_radio', 'Memoria codici radio'),
    ('collegamento', 'Collegamento'),
    ('note_tecniche', 'Note'),
    ('corsa_stelo', 'Corsa dello stelo'),
    ('dimensioni_colonna', 'Dimensioni colonna'),
    ('peso_anta_cantilever', 'Peso max anta cantilever'),
    ('portata_pompa', 'Portata gruppo motore-pompa'),
    ('staffe_fissaggio', 'Staffe di fissaggio'),
    ('tipo_olio', 'Tipo di olio'),
    ('tipo_utilizzo', 'Tipo di utilizzo'),
    ('velocita_stelo', 'Velocità max stelo'),
]

# Mapping from IDML extracted field names to SKU column field names
IDML_TO_SKU_FIELD = {
    'SKU': 'codice_sku',
    'sku': 'codice_sku',
    'Nome Modello': 'nome_modello',
    'Tensione di alimentazione di rete': 'tensione_alimentazione',
    'Tensione di alimentazione': 'tensione_alimentazione',
    'Corrente assorbita': 'corrente_assorbita',
    'Motore elettrico': 'tipo_motore',
    'Potenza max': 'potenza_massima',
    'Coppia max': 'coppia_massima',
    'Tipo di materiale': 'materiale',
    'Tipo di trattamento': 'trattamento_superficiale',
    'Forza max di spinta': 'forza_spinta',
    'Rapporto di riduzione': 'rapporto_riduzione',
    'Velocità angolare max': 'velocita_angolare',
    "Velocità dell'anta": 'velocita_anta',
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
    'Dispositivo di sblocco': 'dispositivo_sblocco',
    'Condensatore di spunto': 'condensatore_spunto',
    'Corsa dello stelo': 'corsa_stelo',
    'Portata gruppo motore-pompa': 'portata_pompa',
    'Staffe di fissaggio': 'staffe_fissaggio',
    'Tipo di olio': 'tipo_olio',
    'Velocità max stelo': 'velocita_stelo',
    'Confezione': 'contenuto_confezione',
    'Note': 'note_tecniche',
    'Descrizione Breve': 'descrizione_breve',
}


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


def extract_barrier_rod_types(document) -> List[str]:
    """Extract rod types (aste) from barrier documents

    Returns list of rod type names found (e.g., ['ASTE TONDE S', 'ASTE RETTANGOLARI'])
    """
    rod_types = []
    all_text = document.all_text.lower()

    # Check for round rods (aste tonde)
    if 'aste tonde' in all_text or 'asta tonda' in all_text:
        # Look for the full name
        rod_types.append('ASTE TONDE S - Ø 75MM')

    # Check for rectangular rods (aste rettangolari)
    if 'aste rettangolari' in all_text or 'asta rettangolare' in all_text:
        rod_types.append('ASTE RETTANGOLARI')

    # Check for elliptical rods
    if 'aste ellittiche' in all_text or 'asta ellittica' in all_text:
        rod_types.append('ASTE ELLITTICHE')

    return rod_types


def extract_from_idml(idml_path: Path) -> Tuple[List[Dict], List[Dict]]:
    """Extract product and SKU data from a single IDML file

    Returns:
        Tuple of (product_rows, sku_rows) - may have multiple products per file
    """
    try:
        # Parse IDML
        document = parse_idml(idml_path)

        # Extract product info
        product_info = extract_product_info(document)

        # Extract table data (specs + product data like confezioni)
        sku_specs_list, product_table_data = extract_all_from_document(document)

        # Build model->SKU code mapping from pricing table
        model_to_sku = {}
        model_to_price = {}
        if product_table_data and product_table_data.pricing:
            for pricing in product_table_data.pricing:
                if pricing.model and pricing.code:
                    model_to_sku[pricing.model] = pricing.code
                    model_to_price[pricing.model] = pricing.price

        # Collect all related SKUs (accessories, etc.)
        all_related_skus = []
        if product_table_data:
            all_related_skus = product_table_data.related_skus.copy()

        # Check if this is a main barrier product (needs multi-product extraction)
        # Only add aste rows for main barrier products like B614, 620, 615, etc.
        # Not for accessories within the barrier category
        is_main_barrier = (
            'barriere' in (product_info.category or '').lower() and
            product_info.name and
            # Main barrier names are typically short codes like B614, 620, 615BPR
            len(product_info.name) < 10 and
            not 'kit' in product_info.name.lower() and
            not 'adesiv' in product_info.name.lower()
        )
        rod_types = extract_barrier_rod_types(document) if is_main_barrier else []

        # Build main product row
        product_row = {
            'categoria_prodotto': product_info.category,
            'nome_prodotto': product_info.name,
            'nome_asta': '',  # Empty for non-barrier products
            'pagina_catalogo': product_info.pagina_catalogo,
            'tipo_layout': product_info.tipo_layout,
            'immagine_principale': '; '.join(product_info.images),
            'codici_modelli': product_info.codici_modelli or '; '.join(product_info.sku_codes),
            'titolo_prodotto': product_info.titolo_prodotto,
            'descrizione_prodotto': product_info.description,
            'intensita_transito': product_info.intensita_transito,
            'caratteristica_primaria': product_info.caratteristica_primaria,
            'valore_primario': product_info.valore_primario,
            'caratteristica_secondaria': product_info.caratteristica_secondaria,
            'valore_secondario': product_info.valore_secondario,
            'novita': '',
            'veloce': '',
            'solare': '',
            'brevetto_faac': '',
            'badge_sistemi': '; '.join(product_info.badge_sistemi),
            'codice_qr': '',
            'certificazioni': '; '.join(product_info.certifications),
            'descrizione_categoria': product_info.descrizione_categoria if hasattr(product_info, 'descrizione_categoria') else '',
            'contenuto_confezione': '',
            'schema_installazione': '',
            'immagine_schema': '',
            'componenti_kit': product_table_data.get_componenti_kit() if product_table_data else '',
            'immagine_kit': '',
            'sku_correlati': '; '.join(all_related_skus),
            'prodotti_correlati': '',
            'note_prodotto': product_table_data.get_product_notes() if product_table_data else '',
            'quote_installazione': '',
            'grafico_tecnico': '',
            'tabella_molle': '',
            'accessori_disponibili': '; '.join(product_info.accessories),
            'prototipo': '',
        }

        product_rows = [product_row]

        # For barriers, add additional rows for each rod type
        if is_main_barrier and rod_types:
            for rod_type in rod_types:
                rod_row = product_row.copy()
                rod_row['nome_asta'] = rod_type
                product_rows.append(rod_row)

        # Build SKU rows with proper field mapping
        sku_rows = []
        for sku_spec in sku_specs_list:
            # Get specs and map to standard column names
            specs_dict = sku_spec.to_dict()

            sku_row = {}
            # Map each extracted field to the standard column name
            for idml_field, value in specs_dict.items():
                if idml_field in IDML_TO_SKU_FIELD:
                    std_field = IDML_TO_SKU_FIELD[idml_field]
                    sku_row[std_field] = value
                else:
                    # Keep original if no mapping (might be already correct)
                    sku_row[idml_field] = value

            # Get actual SKU code from pricing table (if available)
            model_name = sku_spec.sku
            actual_sku = model_to_sku.get(model_name, model_name)

            # Set standard fields
            sku_row['codice_sku'] = actual_sku
            sku_row['nome_modello'] = model_name

            sku_rows.append(sku_row)

        # Also add SKU rows for all related SKUs (accessories) from sku_price tables
        # These are single SKU-price pairs that don't have full specs
        seen_skus = {row.get('codice_sku') for row in sku_rows}
        for related_sku in all_related_skus:
            if related_sku and related_sku not in seen_skus:
                sku_rows.append({
                    'codice_sku': related_sku,
                    'nome_modello': '',
                    'tipo_componente': 'accessorio',
                })
                seen_skus.add(related_sku)

        # Filter out invalid SKU rows (headers, empty values, model names)
        invalid_sku_patterns = ['codice', 'articolo', 'modello', 'prezzo', 'sku', 'descrizione']
        # Model name patterns (these are not SKU codes)
        model_name_patterns = ['standard', 'rapida', 'slave', 'itt', 'plus1', 'dal ', ' al ']
        filtered_sku_rows = []
        for row in sku_rows:
            sku = str(row.get('codice_sku', '')).strip()
            # Skip if empty or looks like a header
            if not sku:
                continue
            if any(pat in sku.lower() for pat in invalid_sku_patterns):
                continue
            # Skip if it doesn't contain any digits (probably a label, not a code)
            if not any(c.isdigit() for c in sku):
                continue
            # Skip model names with spaces (real SKU codes don't have spaces)
            if ' ' in sku:
                continue
            # Skip model name patterns
            if any(pat in sku.lower() for pat in model_name_patterns):
                continue
            # Skip combined models like "RH200B / RH200B EF"
            if '/' in sku:
                continue
            filtered_sku_rows.append(row)

        return product_rows, filtered_sku_rows

    except Exception as e:
        logger.error(f"Error extracting {idml_path.name}: {e}")
        import traceback
        traceback.print_exc()
        return [], []


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

        product_rows, sku_rows = extract_from_idml(idml_path)

        if product_rows:
            all_prodotti.extend(product_rows)

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
    unique_skus = len(set(row.get('codice_sku', '') for row in all_sku if row.get('codice_sku')))
    logger.info(f"  - Unique SKUs: {unique_skus}")
    logger.info(f"  - Duplicate SKU entries: {len(all_sku) - unique_skus}")


if __name__ == "__main__":
    main()
