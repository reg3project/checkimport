"""
Table Extractor - Extract technical specifications from IDML tables

Handles various table formats:
- Two-column tables (attribute, value)
- Multi-column tables (attribute, value1, value2, ... for multiple SKUs)
- Merged cells and complex layouts
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import logging

from .idml_parser import IDMLDocument, Table, TableCell

logger = logging.getLogger(__name__)


@dataclass
class TechnicalSpec:
    """A single technical specification"""
    attribute: str
    value: str
    sku: str = ""
    unit: str = ""
    raw_value: str = ""

    def __post_init__(self):
        # Parse unit from value if present
        if not self.unit and self.value:
            self.unit, self.value = self._extract_unit(self.value)
        if not self.raw_value:
            self.raw_value = self.value

    def _extract_unit(self, value: str) -> Tuple[str, str]:
        """Extract unit from value string"""
        # Common units in technical specs
        unit_patterns = [
            r'(\d+(?:[.,]\d+)?)\s*(V|W|A|Hz|kg|g|mm|cm|m|°C|°|%|dB|Nm|rpm|s|ms)$',
            r'(\d+(?:[.,]\d+)?)\s*(Volt|Watt|Ampere|kilogram|gram|millimeter|centimeter|meter)s?$',
        ]
        for pattern in unit_patterns:
            match = re.search(pattern, value, re.IGNORECASE)
            if match:
                return match.group(2), match.group(1)
        return "", value


@dataclass
class SKUSpecs:
    """Technical specifications for a single SKU"""
    sku: str
    specs: Dict[str, TechnicalSpec] = field(default_factory=dict)

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

    def __init__(self, document: IDMLDocument):
        self.document = document
        self.extracted_specs: List[SKUSpecs] = []

    def extract_all(self) -> List[SKUSpecs]:
        """Extract specs from all tables in document"""
        for table in self.document.tables:
            specs = self._extract_from_table(table)
            self.extracted_specs.extend(specs)
        return self.extracted_specs

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
        specs = SKUSpecs(sku="")

        for row in range(table.rows):
            attr_cell = table.get_cell(row, 0)
            val_cell = table.get_cell(row, 1)

            if attr_cell and val_cell:
                attribute = self._normalize_attribute(attr_cell.content)
                value = self._clean_value(val_cell.content)

                if attribute and value:
                    specs.add_spec(attribute, value)

        return [specs] if specs.specs else []

    def _extract_multi_column(self, table: Table) -> List[SKUSpecs]:
        """Extract from multi-column table (attribute, val1, val2, ...)"""
        # First row typically contains SKU codes
        skus = []
        for col in range(1, table.cols):
            header_cell = table.get_cell(0, col)
            if header_cell:
                sku = self._extract_sku(header_cell.content)
                skus.append(sku if sku else f"SKU_{col}")

        # Create SKUSpecs for each column
        specs_list = [SKUSpecs(sku=sku) for sku in skus]

        # Extract values for each attribute row
        for row in range(1, table.rows):
            attr_cell = table.get_cell(row, 0)
            if not attr_cell:
                continue

            attribute = self._normalize_attribute(attr_cell.content)
            if not attribute:
                continue

            for col_idx, col in enumerate(range(1, table.cols)):
                if col_idx >= len(specs_list):
                    break

                val_cell = table.get_cell(row, col)
                if val_cell:
                    value = self._clean_value(val_cell.content)
                    if value:
                        specs_list[col_idx].add_spec(attribute, value)

        return [s for s in specs_list if s.specs]

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

    def _clean_value(self, raw: str) -> str:
        """Clean and normalize a value"""
        if not raw:
            return ""

        # Remove extra whitespace
        clean = raw.strip()
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


def extract_specs_from_idml(idml_path: Path) -> List[SKUSpecs]:
    """Extract specs directly from an IDML file"""
    from .idml_parser import parse_idml
    document = parse_idml(idml_path)
    return extract_specs_from_document(document)
