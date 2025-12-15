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
# CSV REFERENCE DATA LOADING
# ============================================================================

def load_csv_reference_data() -> Tuple[Dict[str, set], set, Dict[int, List[str]]]:
    """Load reference data from CSV files

    Returns:
        Tuple of (product_to_skus mapping, set of deleted SKUs, page_to_images mapping)
    """
    import csv
    from pathlib import Path

    csv_dir = Path("/home/user/checkimport/input/learning")

    product_to_skus = {}
    deleted_skus = set()
    page_to_images = {}

    # Load Data Entry CSV for product-to-SKU mapping
    data_entry_csv = csv_dir / "FAAC_Lista_Attivita_annotato.xlsx - Data Entry.csv"
    if data_entry_csv.exists():
        with open(data_entry_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                prodotto = row.get('Prodotto', '').strip()
                skus_str = row.get('SKU_presenti_nel_prodotto', '')
                if prodotto and skus_str:
                    skus = set(s.strip() for s in skus_str.split(';') if s.strip())
                    product_to_skus[prodotto] = skus
        logger.info(f"Loaded {len(product_to_skus)} product-SKU mappings from CSV")

    # Load SKU CSV to identify deleted SKUs
    sku_csv = csv_dir / "FAAC_Lista_Attivita_annotato.xlsx - SKU.csv"
    if sku_csv.exists():
        with open(sku_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                codice = row.get('Codice', '').strip()
                eliminato = row.get('eliminato?', '').strip()
                if codice and eliminato and 'SI' in eliminato.upper():
                    deleted_skus.add(codice)
        logger.info(f"Found {len(deleted_skus)} deleted SKUs in CSV")

    # Load Images CSV for page-to-image mapping
    images_csv = csv_dir / "FAAC_Lista_Attivita_annotato.xlsx - immagini_catalogo_FAAC.csv"
    if images_csv.exists():
        with open(images_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get('Name', '').strip()
                page_str = row.get('Page', '').strip()
                if name and page_str:
                    try:
                        page = int(page_str)
                        if page not in page_to_images:
                            page_to_images[page] = []
                        page_to_images[page].append(name)
                    except ValueError:
                        pass
        logger.info(f"Loaded images for {len(page_to_images)} catalog pages")

    return product_to_skus, deleted_skus, page_to_images


def get_main_product_image(page_num: int, product_name: str, page_to_images: Dict[int, List[str]]) -> str:
    """Get the main product image for a catalog page

    Filters out logos and decorative elements, preferring product images.
    """
    images = page_to_images.get(page_num, [])
    if not images:
        return ''

    # Patterns to exclude (logos, decorative elements)
    exclude_patterns = ['logo_', 'untitled', 'loghi', 'qr_', 'cert_', 'artboard',
                        'screenshot', 'background', 'design']

    # Filter to product images only
    product_images = []
    for img in images:
        img_lower = img.lower()
        # Skip excluded patterns
        if any(pat in img_lower for pat in exclude_patterns):
            continue
        # Prefer .tif, .jpg, .png files (actual product images)
        if img_lower.endswith(('.tif', '.jpg', '.png', '.eps')):
            product_images.append(img)

    if not product_images:
        return ''

    # Try to find image matching product name
    product_name_lower = product_name.lower().replace(' ', '_') if product_name else ''
    for img in product_images:
        if product_name_lower and product_name_lower in img.lower():
            return img

    # Return first product image (usually the main one)
    return product_images[0]


# Global reference data (loaded once)
CSV_PRODUCT_SKUS, CSV_DELETED_SKUS, CSV_PAGE_IMAGES = load_csv_reference_data()


# ============================================================================
# KIT.XLSX REFERENCE DATA - Use as-is for kit products
# ============================================================================

def load_kit_xlsx_data() -> Tuple[List[Dict], List[Dict], set]:
    """Load kit products and SKUs from kit.xlsx

    Returns:
        Tuple of (kit_prodotti_rows, kit_sku_rows, kit_product_names)
    """
    from openpyxl import load_workbook

    kit_xlsx = Path("/home/user/checkimport/input/learning/kit.xlsx")
    if not kit_xlsx.exists():
        logger.warning("kit.xlsx not found - skipping kit data")
        return [], [], set()

    wb = load_workbook(kit_xlsx)

    # Load prodotti sheet (row 1 = fields, row 2 = labels, row 3+ = data)
    ws_prod = wb['prodotti']
    prod_headers = [cell.value for cell in ws_prod[1]]

    kit_prodotti = []
    kit_product_names = set()
    for row in ws_prod.iter_rows(min_row=3, values_only=True):
        row_dict = {}
        for i, val in enumerate(row):
            if i < len(prod_headers) and prod_headers[i]:
                row_dict[prod_headers[i]] = val if val else ''
        if row_dict.get('nome_prodotto'):
            kit_prodotti.append(row_dict)
            kit_product_names.add(row_dict['nome_prodotto'])

    # Load sku sheet (row 1 = empty, row 2 = fields, row 3 = labels, row 4+ = data)
    ws_sku = wb['sku']
    # SKU headers are in row 2
    sku_headers = [cell.value for cell in ws_sku[2]]

    kit_skus = []
    for row in ws_sku.iter_rows(min_row=4, values_only=True):
        row_dict = {}
        for i, val in enumerate(row):
            if i < len(sku_headers) and sku_headers[i]:
                row_dict[sku_headers[i]] = val if val else ''
        if row_dict.get('codice_sku'):
            kit_skus.append(row_dict)

    logger.info(f"Loaded {len(kit_prodotti)} kit products and {len(kit_skus)} kit SKUs from kit.xlsx")
    return kit_prodotti, kit_skus, kit_product_names


# Load kit data
KIT_PRODOTTI, KIT_SKUS, KIT_PRODUCT_NAMES = load_kit_xlsx_data()


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
    ('caratteristica_terziaria', 'Prodotto Caratteristica Label 3'),
    ('valore_terziario', 'Prodotto Caratteristica Value 3'),
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


def extract_notes_from_text(document) -> str:
    """Extract notes from document text

    Looks for patterns like "Nota:", "ATTENZIONE:", "N.B.:", etc.
    """
    import re
    all_text = document.all_text

    notes = []

    # Excluded patterns (section headers, not real notes)
    excluded = ['quote', 'dimensioni', 'installazione', 'configurazioni', 'caratteristiche']

    # Pattern: "Nota" or "ATTENZIONE" followed by content
    patterns = [
        r'Nota[:\s]+([^\n]{20,200})',
        r'ATTENZIONE[:\s]+([^\n]{20,200})',
        r'N\.B\.[:\s]+([^\n]{20,200})',
        r'Importante[:\s]+([^\n]{20,200})',
        r'Avvertenza[:\s]+([^\n]{20,200})',
        r'(?:bracci|tubi|non compresi)[^\n]{10,150}',  # Common note patterns
    ]

    for pattern in patterns:
        matches = re.findall(pattern, all_text, re.IGNORECASE)
        for match in matches:
            note = match.strip()
            # Skip if too short
            if len(note) < 20:
                continue
            # Skip if it looks like a section header
            if any(ex in note.lower() for ex in excluded):
                continue
            # Skip if it looks like a spec value (just numbers/units)
            if re.match(r'^[\d\s.,]+\s*(?:kg|mm|m|V|W|N|°|μF)?$', note):
                continue
            # Skip if it contains (*) - usually spec values
            if '(*)' in note and len(note) < 30:
                continue
            notes.append(note)

    # Remove duplicates and join
    unique_notes = list(dict.fromkeys(notes))
    return '; '.join(unique_notes[:3])  # Limit to 3 notes


def extract_confezione_from_text(document, product_name: str) -> str:
    """Extract package/confezione content from document text

    Looks for patterns like "740 comprende:" or "MODEL comprende:"
    """
    import re
    all_text = document.all_text

    # Pattern: "MODEL comprende:" followed by description
    patterns = [
        rf'{re.escape(product_name)}\s+comprende\s*:\s*(.+?)(?:\n\n|\n[A-Z]|\n\d{{3}}|$)',
        rf'{re.escape(product_name)}\s+include\s*:\s*(.+?)(?:\n\n|\n[A-Z]|\n\d{{3}}|$)',
        r'comprende\s*:\s*(.+?)(?:\n\n|\n[A-Z]|\n\d{3}|$)',
    ]

    for pattern in patterns:
        match = re.search(pattern, all_text, re.IGNORECASE | re.DOTALL)
        if match:
            content = match.group(1).strip()
            # Clean up: remove excessive newlines, normalize spacing
            content = re.sub(r'\n+', '; ', content)
            content = re.sub(r'\s+', ' ', content)
            return content[:500]  # Limit length

    return ''


def extract_badges_from_text(document) -> Dict[str, bool]:
    """Extract product badges from document text

    Returns dict with badge flags: novita, veloce, solare, brevetto_faac
    """
    import re
    all_text = document.all_text.lower()

    # Check for badge words - standalone or as part of larger text
    # Use word boundaries to avoid false matches
    badges = {
        'novita': bool(re.search(r'\b(nuovo|new|novità)\b', all_text)),
        'veloce': bool(re.search(r'\b(veloce|fast|rapido|rapida)\b', all_text)),
        'solare': bool(re.search(r'\b(solare|solar|fotovoltaico)\b', all_text)),
        'brevetto_faac': bool(re.search(r'\b(brevetto|patent)\b', all_text)),
    }

    return badges


def extract_prodotti_correlati(document) -> str:
    """Extract related products/kits from document text

    Looks for patterns like "Questo prodotto è disponibile anche in kit:"
    """
    import re
    all_text = document.all_text

    related = []

    # Pattern: "Questo prodotto è disponibile anche in kit:" followed by kit names
    kit_pattern = r'(?:disponibile anche in kit|disponibile in kit)[:\s]*([^\n]+(?:\n(?:PERFECT|CLASSIC|cod\.|Info)[^\n]*)*)'
    matches = re.findall(kit_pattern, all_text, re.IGNORECASE)
    for match in matches:
        # Extract kit references
        kit_refs = re.findall(r'((?:PERFECT|CLASSIC)\s*\d*|cod\.\s*[\d]+)', match)
        related.extend(kit_refs)

    # Also look for "Info a pag." patterns with kit codes
    info_pattern = r'(cod\.\s*[\d]+)\s*Info a pag'
    info_matches = re.findall(info_pattern, all_text)
    for match in info_matches:
        if match not in related:
            related.append(match)

    # Clean up and join
    cleaned = []
    for r in related:
        r = r.strip()
        if r and r not in cleaned:
            cleaned.append(r)

    return '; '.join(cleaned[:5])  # Limit to 5 related products


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

        # Enrich with CSV reference data
        product_name = product_info.name
        if product_name:
            # Try exact match first
            csv_skus = CSV_PRODUCT_SKUS.get(product_name, set())
            # Try partial match if no exact match
            if not csv_skus:
                for csv_name, skus in CSV_PRODUCT_SKUS.items():
                    if product_name.lower() in csv_name.lower() or csv_name.lower() in product_name.lower():
                        csv_skus = skus
                        break
            # Add CSV SKUs to related SKUs (filter deleted ones)
            for sku in csv_skus:
                if sku not in CSV_DELETED_SKUS and sku not in all_related_skus:
                    all_related_skus.append(sku)

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

        # Extract badges from text
        badges = extract_badges_from_text(document)

        # Extract related products (kit references)
        prodotti_correlati_str = extract_prodotti_correlati(document)

        # Extract confezione from product table data or text
        confezione_str = ''
        if product_table_data and product_table_data.confezioni:
            # confezioni is a dict like {'model': 'description'}
            confezione_parts = []
            for model, desc in product_table_data.confezioni.items():
                if desc:
                    confezione_parts.append(f"{model}: {desc}" if model else desc)
            confezione_str = '; '.join(confezione_parts)

        # If no confezione from table, try extracting from text
        if not confezione_str:
            confezione_str = extract_confezione_from_text(document, product_info.name)

        # Extract notes - combine table notes with text notes
        table_notes = product_table_data.get_product_notes() if product_table_data else ''
        text_notes = extract_notes_from_text(document)
        # Use text notes if table notes are too short or look like spec values
        if len(table_notes) < 20 or table_notes.count('(*)') > 0:
            notes_str = text_notes if text_notes else table_notes
        else:
            notes_str = table_notes
            if text_notes:
                notes_str = f"{table_notes}; {text_notes}"

        # Extract page number from IDML filename (e.g., "028_LEADER_kit.idml" -> 28)
        import re
        page_match = re.match(r'^(\d+)', idml_path.stem)
        page_num = int(page_match.group(1)) if page_match else 0

        # Get main product image from CSV (by page number)
        csv_image = get_main_product_image(page_num, product_info.name, CSV_PAGE_IMAGES)
        # Fall back to IDML-extracted images if no CSV image
        immagine_principale = csv_image if csv_image else '; '.join(product_info.images)

        # Build main product row
        product_row = {
            'categoria_prodotto': product_info.category,
            'nome_prodotto': product_info.name,
            'nome_asta': '',  # Empty for non-barrier products
            'pagina_catalogo': product_info.pagina_catalogo,
            'tipo_layout': product_info.tipo_layout,
            'immagine_principale': immagine_principale,
            'codici_modelli': product_info.codici_modelli or '; '.join(product_info.sku_codes),
            'titolo_prodotto': product_info.titolo_prodotto,
            'descrizione_prodotto': product_info.description,
            'intensita_transito': product_info.intensita_transito,
            'caratteristica_primaria': product_info.caratteristica_primaria,
            'valore_primario': product_info.valore_primario,
            'caratteristica_secondaria': product_info.caratteristica_secondaria,
            'valore_secondario': product_info.valore_secondario,
            'novita': 'Sì' if badges.get('novita') else '',
            'veloce': 'Sì' if badges.get('veloce') else '',
            'solare': 'Sì' if badges.get('solare') else '',
            'brevetto_faac': 'Sì' if badges.get('brevetto_faac') else '',
            'badge_sistemi': '; '.join(product_info.badge_sistemi),
            'codice_qr': '',
            'certificazioni': '; '.join(product_info.certifications),
            'descrizione_categoria': product_info.descrizione_categoria if hasattr(product_info, 'descrizione_categoria') else '',
            'contenuto_confezione': confezione_str,
            'schema_installazione': '',
            'immagine_schema': '',
            'componenti_kit': product_table_data.get_componenti_kit() if product_table_data else '',
            'immagine_kit': '',
            'sku_correlati': '; '.join(all_related_skus),
            'prodotti_correlati': prodotti_correlati_str,
            'note_prodotto': notes_str,
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

            # These are main product models - set tipo_componente to Modello
            sku_row['tipo_componente'] = 'Modello'
            sku_row['ordine_tipo_componente'] = 0  # Modello has highest priority

            # Set descrizione_breve from product title if not already set
            if not sku_row.get('descrizione_breve') and product_info.titolo_prodotto:
                sku_row['descrizione_breve'] = product_info.titolo_prodotto

            sku_rows.append(sku_row)

        # Build SKU-to-description mapping from kit_components and pricing
        sku_descriptions = {}
        if product_table_data:
            # From kit components (has description field)
            for comp in product_table_data.kit_components:
                if comp.code and comp.description:
                    sku_descriptions[comp.code] = comp.description
            # From pricing (model field often contains description)
            for pricing in product_table_data.pricing:
                if pricing.code and pricing.model and pricing.code not in sku_descriptions:
                    sku_descriptions[pricing.code] = pricing.model

        # Also extract descriptions from document text for accessory codes
        # Pattern: Description followed by code, or code followed by description
        import re
        text = document.all_text
        # Pattern: description (line) + code (line)
        desc_code_matches = re.findall(r'([A-Za-z][^\n€]{10,80})\n(\d{6})\n', text)
        for desc, code in desc_code_matches:
            if code not in sku_descriptions:
                sku_descriptions[code] = desc.strip()
        # Pattern: code + euro price + description (same line or next)
        code_price_desc = re.findall(r'(\d{6})\s*€?\s*[\d.,]+\s*\n([A-Za-z][^\n€]{10,80})', text)
        for code, desc in code_price_desc:
            if code not in sku_descriptions:
                sku_descriptions[code] = desc.strip()

        # Also add SKU rows for all related SKUs (accessories) from sku_price tables
        # These are single SKU-price pairs that don't have full specs
        seen_skus = {row.get('codice_sku') for row in sku_rows}
        for related_sku in all_related_skus:
            if related_sku and related_sku not in seen_skus:
                desc = sku_descriptions.get(related_sku, '')
                sku_rows.append({
                    'codice_sku': related_sku,
                    'nome_modello': '',
                    'tipo_componente': 'accessorio',
                    'descrizione_breve': desc,
                })
                seen_skus.add(related_sku)

        # Filter out invalid SKU rows (headers, empty values, model names, deleted SKUs)
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
            # Skip deleted SKUs (from CSV reference)
            if sku in CSV_DELETED_SKUS:
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

    # Start with kit.xlsx data (use as-is, perfect quality)
    all_prodotti = list(KIT_PRODOTTI)  # Copy kit products
    all_sku = list(KIT_SKUS)  # Copy kit SKUs
    logger.info(f"Loaded {len(all_prodotti)} products and {len(all_sku)} SKUs from kit.xlsx")

    # Get all IDML files
    idml_files = sorted(idml_dir.glob("*.idml"))
    logger.info(f"Found {len(idml_files)} IDML files to process")

    # Extract from IDML files (skip kit products already loaded from kit.xlsx)
    skipped_kit_count = 0
    for i, idml_path in enumerate(idml_files, 1):
        # Check if this is a kit IDML (skip - already have from kit.xlsx)
        filename_lower = idml_path.stem.lower()
        is_kit_idml = '_kit' in filename_lower or 'kit_' in filename_lower

        if is_kit_idml:
            skipped_kit_count += 1
            logger.info(f"[{i}/{len(idml_files)}] Skipping kit IDML (using kit.xlsx): {idml_path.name}")
            continue

        logger.info(f"[{i}/{len(idml_files)}] Processing: {idml_path.name}")

        product_rows, sku_rows = extract_from_idml(idml_path)

        if product_rows:
            all_prodotti.extend(product_rows)

        if sku_rows:
            all_sku.extend(sku_rows)

    logger.info(f"\nExtraction complete:")
    logger.info(f"  - Kit products from kit.xlsx: {len(KIT_PRODOTTI)}")
    logger.info(f"  - Kit SKUs from kit.xlsx: {len(KIT_SKUS)}")
    logger.info(f"  - Skipped kit IDMLs: {skipped_kit_count}")
    logger.info(f"  - Total Products: {len(all_prodotti)}")
    logger.info(f"  - Total SKUs: {len(all_sku)}")

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
