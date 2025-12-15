"""
Table Extractor - Extract technical specifications from IDML tables

Handles various table formats:
- Two-column tables (attribute, value)
- Multi-column tables (attribute, value1, value2, ... for multiple SKUs)
- Merged cells and complex layouts
- Empty cells (inherit from previous column)
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import logging

from .idml_parser import IDMLDocument, Table, TableCell

logger = logging.getLogger(__name__)


# Italian attribute names found in FAAC IDML files
ITALIAN_ATTRIBUTE_NAMES = [
    'Tensione di alimentazione di rete',
    'Corrente assorbita',
    'Motore elettrico',
    'Potenza max',
    'Coppia max',
    'Forza max di spinta',
    'Velocità max stelo',
    'Velocità angolare max',
    "Velocità dell'anta",
    'Portata gruppo motore-pompa',
    'Corsa dello stelo',
    'Angolo max apertura anta',
    'Temperatura ambiente di esercizio',
    'Termoprotezione',
    'Grado di protezione',
    'Peso',
    'Frequenza di utilizzo',
    'Larghezza max anta',
    'Lunghezza max anta',
    'Peso max anta',
    'Tipo di olio',
    'Staffe di fissaggio',
    'Dimensioni (LxPxH)',
    'Apparecchiatura elettronica',
    'Dispositivo di sblocco',
    'Finecorsa',
    'Encoder',
]


@dataclass
class TechnicalSpec:
    """A single technical specification"""
    attribute: str
    value: str
    sku: str = ""
    unit: str = ""
    raw_value: str = ""

    def __post_init__(self):
        # Store raw value before any processing
        if not self.raw_value:
            self.raw_value = self.value
        # Extract unit but DON'T modify the original value
        # The value should remain intact for comparison
        if not self.unit and self.value:
            self.unit = self._extract_unit(self.value)

    def _extract_unit(self, value: str) -> str:
        """Extract unit from value string (without modifying value)"""
        # Common units in technical specs
        unit_patterns = [
            r'\d+(?:[.,]\d+)?\s*(V|W|A|Hz|kg|g|mm|cm|m|°C|°|%|dB|Nm|rpm|s|ms|μF)(?:\s|$)',
            r'\d+(?:[.,]\d+)?\s*(Volt|Watt|Ampere|kilogram|gram|millimeter|centimeter|meter)s?(?:\s|$)',
        ]
        for pattern in unit_patterns:
            match = re.search(pattern, value, re.IGNORECASE)
            if match:
                return match.group(1)
        return ""


@dataclass
class SKUSpecs:
    """Technical specifications for a single SKU"""
    sku: str
    specs: Dict[str, TechnicalSpec] = field(default_factory=dict)
    confezione: str = ""  # Package contents for this SKU
    notes: str = ""  # SKU-specific notes

    def add_spec(self, attribute: str, value: str, unit: str = ""):
        """Add a specification"""
        spec = TechnicalSpec(
            attribute=attribute,
            value=value,
            sku=self.sku,
            unit=unit
        )
        self.specs[attribute] = spec

    def get(self, attribute: str) -> Optional[str]:
        """Get a specification value"""
        spec = self.specs.get(attribute)
        return spec.value if spec else None

    def to_dict(self) -> Dict[str, str]:
        """Convert to flat dictionary"""
        result = {'sku': self.sku}
        for attr, spec in self.specs.items():
            result[attr] = spec.value
        # Add confezione and notes if present
        if self.confezione:
            result['Confezione'] = self.confezione
        if self.notes:
            result['Note'] = self.notes
        return result


@dataclass
class KitComponent:
    """A single kit component"""
    quantity: str
    description: str
    code: str

    def to_format(self) -> str:
        """Format as Q|SKU for componenti_kit column"""
        return f"{self.quantity}|{self.code}"


@dataclass
class PricingInfo:
    """Pricing information for a model"""
    model: str
    code: str
    price: str


@dataclass
class NoteInfo:
    """Represents a note extracted from tables or text"""
    note_text: str
    note_type: str = ""  # 'technical', 'product', 'accessory', 'general'
    related_sku: str = ""

    def get_formatted(self, include_bold: bool = True) -> str:
        """Get note text, preserving any <b> tags if present"""
        return self.note_text


@dataclass
class ConfezioneInfo:
    """Package contents for a SKU"""
    sku: str
    contents: str  # May contain <b> tags for bold text


@dataclass
class ProductTableData:
    """Product-level data extracted from tables"""
    kit_components: List[KitComponent] = field(default_factory=list)
    pricing: List[PricingInfo] = field(default_factory=list)
    related_skus: List[str] = field(default_factory=list)
    # Notes handling
    product_notes: List[NoteInfo] = field(default_factory=list)
    technical_notes: List[NoteInfo] = field(default_factory=list)
    accessory_notes: List[NoteInfo] = field(default_factory=list)
    # Confezioni per SKU
    confezioni: Dict[str, str] = field(default_factory=dict)

    def get_componenti_kit(self) -> str:
        """Format kit components as Q|SKU;Q|SKU;..."""
        return ";".join(c.to_format() for c in self.kit_components)

    def get_sku_correlati(self) -> str:
        """Format related SKUs as semicolon-separated list"""
        return ";".join(self.related_skus)

    def get_product_notes(self) -> str:
        """Get formatted product notes"""
        return "; ".join(n.get_formatted() for n in self.product_notes)

    def get_technical_notes(self) -> str:
        """Get formatted technical notes"""
        return "; ".join(n.get_formatted() for n in self.technical_notes)

    def get_accessory_notes(self) -> str:
        """Get formatted accessory notes"""
        return "; ".join(n.get_formatted() for n in self.accessory_notes)

    def get_confezione_for_sku(self, sku: str) -> str:
        """Get package contents for a specific SKU"""
        return self.confezioni.get(sku, "")

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for product-level fields"""
        result = {}
        if self.kit_components:
            result['componenti_kit'] = self.get_componenti_kit()
        if self.related_skus:
            result['sku_correlati'] = self.get_sku_correlati()
        if self.pricing:
            # Store first pricing as main product
            result['codice_articolo'] = self.pricing[0].code if self.pricing else ""
            result['prezzo'] = self.pricing[0].price if self.pricing else ""
        if self.product_notes:
            result['note_prodotto'] = self.get_product_notes()
        if self.technical_notes:
            result['note_tecniche'] = self.get_technical_notes()
        if self.accessory_notes:
            result['note_accessori'] = self.get_accessory_notes()
        return result


class TableExtractor:
    """Extract technical specifications from IDML tables"""

    # Known attribute names for FAAC products
    KNOWN_ATTRIBUTES = {
        # Electrical
        'tensione': 'voltage',
        'alimentazione': 'power_supply',
        'potenza': 'power',
        'corrente': 'current',
        'frequenza': 'frequency',

        # Mechanical
        'peso': 'weight',
        'dimensioni': 'dimensions',
        'larghezza': 'width',
        'altezza': 'height',
        'profondità': 'depth',
        'lunghezza': 'length',

        # Motor
        'motore': 'motor_type',
        'velocità': 'speed',
        'coppia': 'torque',
        'cicli': 'duty_cycle',

        # Protection
        'grado protezione': 'ip_rating',
        'ip': 'ip_rating',
        'temperatura': 'temperature_range',

        # Performance
        'portata': 'capacity',
        'corsa': 'stroke',
        'forza': 'force',
    }

    # Kit component table headers
    KIT_HEADERS = ['q.tà', 'q', 'quantità', 'qty']
    KIT_CODE_HEADERS = ['codice', 'code', 'cod']
    KIT_DESC_HEADERS = ['descrizione', 'description', 'desc']

    # Pricing table headers
    PRICING_HEADERS = ['prezzo', 'price', '€']
    PRICING_CODE_HEADERS = ['codice articolo', 'codice', 'code']
    PRICING_MODEL_HEADERS = ['modello', 'model']

    # Notes detection patterns
    NOTE_MARKERS = ['nota', 'note', '(*)']
    TECHNICAL_NOTE_MARKERS = ['nota tecnica', 'note tecniche', 'specifiche']

    # Confezione table headers
    CONFEZIONE_HEADERS = ['confezione', 'contenuto', 'package', 'kit']

    def __init__(self, document: IDMLDocument):
        self.document = document
        self.extracted_specs: List[SKUSpecs] = []
        self.product_data = ProductTableData()

    def extract_all(self) -> List[SKUSpecs]:
        """Extract specs from all tables in document"""
        for table in self.document.tables:
            # First check for special table types
            table_type = self._identify_table_type(table)

            if table_type == 'kit_components':
                self._extract_kit_components(table)
            elif table_type == 'pricing':
                self._extract_pricing(table)
            elif table_type == 'sku_price':
                self._extract_sku_price(table)
            elif table_type == 'confezione':
                self._extract_confezione(table)
            else:
                # Regular specs table - also check for notes
                specs = self._extract_from_table(table)
                self.extracted_specs.extend(specs)
                # Extract any notes from this specs table
                self._extract_notes_from_table(table)

        # Assign confezioni to individual SKUSpecs
        self.assign_confezioni_to_skus()

        return self.extracted_specs

    def get_product_data(self) -> ProductTableData:
        """Get extracted product-level data"""
        return self.product_data

    def assign_confezioni_to_skus(self):
        """Assign confezioni from product_data to each matching SKUSpecs"""
        if not self.product_data.confezioni:
            return

        for sku_spec in self.extracted_specs:
            sku = sku_spec.sku
            # Direct match
            if sku in self.product_data.confezioni:
                sku_spec.confezione = self.product_data.confezioni[sku]
            else:
                # Try matching by model name (Nome Modello spec)
                model_name = sku_spec.get('Nome Modello')
                if model_name and model_name in self.product_data.confezioni:
                    sku_spec.confezione = self.product_data.confezioni[model_name]

    def _identify_table_type(self, table: Table) -> str:
        """Identify the type of table based on headers"""
        if table.rows < 1:
            return 'unknown'

        # Get first row headers
        headers = []
        for col in range(table.cols):
            cell = table.get_cell(0, col)
            if cell:
                headers.append(cell.content.strip().lower())
            else:
                headers.append('')

        # Check for kit component table (Q.tà, Descrizione, Codice)
        has_qty = any(any(kh in h for kh in self.KIT_HEADERS) for h in headers)
        has_code = any(any(ch in h for ch in self.KIT_CODE_HEADERS) for h in headers)
        has_desc = any(any(dh in h for dh in self.KIT_DESC_HEADERS) for h in headers)

        if has_qty and has_code:
            return 'kit_components'

        # Check for pricing table (Modello, Codice articolo, Prezzo €)
        has_price = any(any(ph in h for ph in self.PRICING_HEADERS) for h in headers)
        has_model = any(any(mh in h for mh in self.PRICING_MODEL_HEADERS) for h in headers)

        if has_price and (has_code or has_model):
            return 'pricing'

        # Check for confezione table
        has_confezione = any(any(ch in h for ch in self.CONFEZIONE_HEADERS) for h in headers)
        if has_confezione and (has_code or has_model):
            return 'confezione'

        # Check for simple 2-col SKU price table (SKU, €price)
        if table.cols == 2 and table.rows == 1:
            cell0 = table.get_cell(0, 0)
            cell1 = table.get_cell(0, 1)
            if cell0 and cell1:
                # Check if first looks like SKU and second like price
                if re.match(r'^\d{5,}$', cell0.content.strip()):
                    if '€' in cell1.content or re.match(r'^\d+[.,]\d+$', cell1.content.strip()):
                        return 'sku_price'

        return 'specs'

    def _extract_kit_components(self, table: Table):
        """Extract kit component data from table"""
        # Find column indices
        headers = []
        for col in range(table.cols):
            cell = table.get_cell(0, col)
            headers.append(cell.content.strip().lower() if cell else '')

        qty_col = None
        code_col = None
        desc_col = None

        for i, h in enumerate(headers):
            if any(kh in h for kh in self.KIT_HEADERS):
                qty_col = i
            if any(ch in h for ch in self.KIT_CODE_HEADERS):
                code_col = i
            if any(dh in h for dh in self.KIT_DESC_HEADERS):
                desc_col = i

        if qty_col is None or code_col is None:
            return

        # Extract rows
        for row in range(1, table.rows):
            qty_cell = table.get_cell(row, qty_col)
            code_cell = table.get_cell(row, code_col)
            desc_cell = table.get_cell(row, desc_col) if desc_col is not None else None

            if qty_cell and code_cell:
                qty = qty_cell.content.strip()
                code = code_cell.content.strip()
                desc = desc_cell.content.strip() if desc_cell else ""

                if qty and code:
                    component = KitComponent(quantity=qty, description=desc, code=code)
                    self.product_data.kit_components.append(component)
                    # Also add to related SKUs
                    if code not in self.product_data.related_skus:
                        self.product_data.related_skus.append(code)

    def _extract_pricing(self, table: Table):
        """Extract pricing data from table"""
        headers = []
        for col in range(table.cols):
            cell = table.get_cell(0, col)
            headers.append(cell.content.strip().lower() if cell else '')

        model_col = None
        code_col = None
        price_col = None

        for i, h in enumerate(headers):
            if any(mh in h for mh in self.PRICING_MODEL_HEADERS):
                model_col = i
            if any(ch in h for ch in self.PRICING_CODE_HEADERS):
                code_col = i
            if any(ph in h for ph in self.PRICING_HEADERS):
                price_col = i

        # Extract rows
        for row in range(1, table.rows):
            model = ""
            code = ""
            price = ""

            if model_col is not None:
                cell = table.get_cell(row, model_col)
                model = cell.content.strip() if cell else ""

            if code_col is not None:
                cell = table.get_cell(row, code_col)
                code = cell.content.strip() if cell else ""

            if price_col is not None:
                cell = table.get_cell(row, price_col)
                price = cell.content.strip() if cell else ""
                # Clean price format
                price = price.replace('€', '').replace(',', '.').strip()

            if code:
                pricing = PricingInfo(model=model, code=code, price=price)
                self.product_data.pricing.append(pricing)
                if code not in self.product_data.related_skus:
                    self.product_data.related_skus.append(code)

    def _extract_sku_price(self, table: Table):
        """Extract simple SKU-price pairs from 2-column tables"""
        cell0 = table.get_cell(0, 0)
        cell1 = table.get_cell(0, 1)

        if cell0 and cell1:
            code = cell0.content.strip()
            price = cell1.content.strip()
            price = price.replace('€', '').replace(',', '.').strip()

            if code and code not in self.product_data.related_skus:
                self.product_data.related_skus.append(code)

    def _extract_confezione(self, table: Table):
        """Extract package contents (confezione) per SKU from table"""
        headers = []
        for col in range(table.cols):
            cell = table.get_cell(0, col)
            headers.append(cell.content.strip().lower() if cell else '')

        # Find relevant columns
        model_col = None
        code_col = None
        confezione_col = None

        for i, h in enumerate(headers):
            if any(mh in h for mh in self.PRICING_MODEL_HEADERS):
                model_col = i
            if any(ch in h for ch in self.KIT_CODE_HEADERS):
                code_col = i
            if any(ch in h for ch in self.CONFEZIONE_HEADERS):
                confezione_col = i

        if confezione_col is None:
            return

        # Extract confezione for each SKU
        for row in range(1, table.rows):
            sku = ""
            if code_col is not None:
                cell = table.get_cell(row, code_col)
                sku = cell.content.strip() if cell else ""
            if not sku and model_col is not None:
                cell = table.get_cell(row, model_col)
                sku = cell.content.strip() if cell else ""

            confezione_cell = table.get_cell(row, confezione_col)
            if confezione_cell and sku:
                # Use get_formatted_content to preserve bold tags
                confezione_text = confezione_cell.content  # Already has <b> tags if bold
                self.product_data.confezioni[sku] = confezione_text

    def _extract_notes_from_table(self, table: Table):
        """Extract notes from technical specs tables"""
        for row in range(table.rows):
            for col in range(table.cols):
                cell = table.get_cell(row, col)
                if not cell:
                    continue

                content_lower = cell.content.lower()

                # Check if this cell contains a note
                is_note = any(marker in content_lower for marker in self.NOTE_MARKERS)
                is_technical_note = any(marker in content_lower for marker in self.TECHNICAL_NOTE_MARKERS)

                if is_note or is_technical_note:
                    # Get the note content (may be this cell or next cell)
                    note_text = cell.content

                    # If this is just a "Nota:" header, get text from next column
                    if len(note_text) < 20 and col + 1 < table.cols:
                        next_cell = table.get_cell(row, col + 1)
                        if next_cell:
                            note_text = next_cell.content

                    note = NoteInfo(
                        note_text=note_text,
                        note_type='technical' if is_technical_note else 'general'
                    )

                    if is_technical_note:
                        self.product_data.technical_notes.append(note)
                    else:
                        self.product_data.product_notes.append(note)

    def _extract_from_table(self, table: Table) -> List[SKUSpecs]:
        """Extract specs from a single table"""
        if table.cols < 2:
            return []

        # Determine table type
        if table.cols == 2:
            return self._extract_two_column(table)
        else:
            return self._extract_multi_column(table)

    def _extract_two_column(self, table: Table) -> List[SKUSpecs]:
        """Extract from two-column (attribute, value) table"""
        sku_name = ""

        # Check first row for model name
        first_attr = table.get_cell(0, 0)
        first_val = table.get_cell(0, 1)
        if first_attr and first_val:
            attr_lower = first_attr.content.strip().lower()
            if attr_lower == 'modello' or attr_lower == 'model':
                sku_name = first_val.content.strip()

        specs = SKUSpecs(sku=sku_name)

        # If we found a model name, add it as Nome Modello spec
        if sku_name:
            specs.specs['Nome Modello'] = TechnicalSpec(
                attribute='Nome Modello',
                value=sku_name,
                sku=sku_name
            )

        for row in range(table.rows):
            attr_cell = table.get_cell(row, 0)
            val_cell = table.get_cell(row, 1)

            if attr_cell and val_cell:
                # Keep original Italian attribute name for technical specs
                original_attr = attr_cell.content.strip()
                value = self._clean_value(val_cell.content)

                if original_attr and value:
                    # Store with original Italian attribute name
                    specs.add_spec(original_attr, value)

        return [specs] if specs.specs else []

    def _extract_multi_column(self, table: Table) -> List[SKUSpecs]:
        """Extract from multi-column table (attribute, val1, val2, ...)"""
        # First row typically contains model names (SKU codes or model names)
        models = []
        for col in range(1, table.cols):
            header_cell = table.get_cell(0, col)
            if header_cell:
                model_name = header_cell.content.strip()
                models.append(model_name if model_name else f"Model_{col}")
            else:
                models.append(f"Model_{col}")

        # Create SKUSpecs for each column using model name as identifier
        specs_list = [SKUSpecs(sku=model) for model in models]

        # Also store the original Italian attribute name
        for spec in specs_list:
            spec.specs['Nome Modello'] = TechnicalSpec(
                attribute='Nome Modello',
                value=spec.sku,
                sku=spec.sku
            )

        # Extract values for each attribute row
        for row in range(1, table.rows):
            attr_cell = table.get_cell(row, 0)
            if not attr_cell:
                continue

            # Keep original Italian attribute name
            original_attribute = attr_cell.content.strip()
            if not original_attribute:
                continue

            # Track the last non-empty value for inheritance
            last_value = None

            for col_idx, col in enumerate(range(1, table.cols)):
                if col_idx >= len(specs_list):
                    break

                val_cell = table.get_cell(row, col)
                value = ""

                if val_cell:
                    value = self._clean_value(val_cell.content)

                # If empty, inherit from previous column (FAAC table convention)
                if not value and last_value:
                    value = last_value

                if value:
                    last_value = value
                    # Store with original Italian attribute name
                    specs_list[col_idx].add_spec(original_attribute, value)

        return [s for s in specs_list if len(s.specs) > 1]  # More than just model name

    def _normalize_attribute(self, raw: str) -> str:
        """Normalize attribute name"""
        if not raw:
            return ""

        # Clean and lowercase
        clean = raw.strip().lower()
        clean = re.sub(r'\s+', ' ', clean)
        clean = re.sub(r'[:\-]$', '', clean)

        # Map to standard name if known
        for pattern, standard in self.KNOWN_ATTRIBUTES.items():
            if pattern in clean:
                return standard

        # Convert to snake_case
        clean = re.sub(r'[^a-z0-9\s]', '', clean)
        clean = re.sub(r'\s+', '_', clean)

        return clean

    def _clean_value(self, raw: str, strip_bold: bool = True) -> str:
        """Clean and normalize a value

        Args:
            raw: Raw value string
            strip_bold: If True, removes <b> tags (default for technical specs)
                       Set to False for fields that should preserve bold (Confezione, Notes)
        """
        if not raw:
            return ""

        clean = raw.strip()

        # Strip bold tags for technical specs (not for Confezione, Notes, Badges)
        if strip_bold:
            clean = re.sub(r'</?b>', '', clean)

        # Remove extra whitespace
        clean = re.sub(r'\s+', ' ', clean)

        # Normalize numbers
        clean = clean.replace(',', '.')

        return clean

    def _extract_sku(self, text: str) -> str:
        """Extract SKU code from text"""
        if not text:
            return ""

        # Look for common SKU patterns
        patterns = [
            r'\b(\d{6,})\b',  # 6+ digit codes
            r'\b([A-Z]{1,3}\d{4,})\b',  # Letter prefix + digits
            r'\b(\d+[A-Z]+\d+)\b',  # Mixed pattern
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        return text.strip()

    def find_table_by_attribute(self, attribute: str) -> Optional[Table]:
        """Find table containing specific attribute"""
        attr_lower = attribute.lower()
        for table in self.document.tables:
            for row in range(table.rows):
                cell = table.get_cell(row, 0)
                if cell and attr_lower in cell.content.lower():
                    return table
        return None


def extract_specs_from_document(document: IDMLDocument) -> List[SKUSpecs]:
    """Convenience function to extract all specs from a document"""
    extractor = TableExtractor(document)
    return extractor.extract_all()


def extract_all_from_document(document: IDMLDocument) -> Tuple[List[SKUSpecs], ProductTableData]:
    """Extract both SKU specs and product-level table data"""
    extractor = TableExtractor(document)
    specs = extractor.extract_all()
    product_data = extractor.get_product_data()
    return specs, product_data


def extract_specs_from_idml(idml_path: Path) -> List[SKUSpecs]:
    """Extract specs directly from an IDML file"""
    from .idml_parser import parse_idml
    document = parse_idml(idml_path)
    return extract_specs_from_document(document)
