"""
XLSX Loader - Load reference XLSX files for comparison and learning

Handles XLSX files with the standard structure:
- Sheet "prodotti": Product-level metadata (36 columns)
- Sheet "sku": SKU-level technical specs (66 columns)
"""

from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import logging

try:
    import openpyxl
    from openpyxl import Workbook
    from openpyxl.worksheet.worksheet import Worksheet
except ImportError:
    openpyxl = None

logger = logging.getLogger(__name__)


# Standard column definitions
PRODOTTI_COLUMNS = [
    'id', 'category', 'subcategory', 'name', 'page', 'description',
    'short_description', 'features', 'badges', 'certifications',
    'warranty', 'brand', 'manufacturer', 'origin', 'weight_unit',
    'dimension_unit', 'currency', 'price_type', 'availability',
    'lead_time', 'min_order', 'keywords', 'seo_title', 'seo_description',
    'images', 'documents', 'videos', 'related_products', 'accessories',
    'spare_parts', 'installation_type', 'application', 'environment',
    'notes', 'status', 'last_updated'
]

SKU_COLUMNS = [
    'sku', 'product_id', 'variant_name', 'voltage', 'voltage_unit',
    'frequency', 'frequency_unit', 'power', 'power_unit', 'current',
    'current_unit', 'motor_type', 'motor_power', 'motor_power_unit',
    'speed', 'speed_unit', 'torque', 'torque_unit', 'duty_cycle',
    'duty_cycle_unit', 'ip_rating', 'temperature_min', 'temperature_max',
    'temperature_unit', 'weight', 'weight_unit', 'length', 'width',
    'height', 'depth', 'dimension_unit', 'capacity', 'capacity_unit',
    'stroke', 'stroke_unit', 'force', 'force_unit', 'cycles',
    'cycles_unit', 'opening_time', 'closing_time', 'time_unit',
    'noise_level', 'noise_unit', 'material', 'color', 'finish',
    'mounting_type', 'connection_type', 'protocol', 'compatibility',
    'included_accessories', 'optional_accessories', 'certifications',
    'price', 'currency', 'availability', 'lead_time', 'min_order',
    'ean', 'upc', 'mpn', 'notes', 'status', 'last_updated'
]


@dataclass
class XLSXData:
    """Data loaded from an XLSX file"""
    path: Path
    prodotti: List[Dict[str, Any]] = field(default_factory=list)
    sku: List[Dict[str, Any]] = field(default_factory=list)
    prodotti_columns: List[str] = field(default_factory=list)
    sku_columns: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_product_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get product by name"""
        name_lower = name.lower()
        for prod in self.prodotti:
            if prod.get('name', '').lower() == name_lower:
                return prod
        return None

    def get_sku_by_code(self, sku_code: str) -> Optional[Dict[str, Any]]:
        """Get SKU by code"""
        for sku in self.sku:
            if sku.get('sku', '') == sku_code:
                return sku
        return None

    def get_skus_for_product(self, product_id: str) -> List[Dict[str, Any]]:
        """Get all SKUs for a product"""
        return [s for s in self.sku if s.get('product_id') == product_id]


class XLSXLoader:
    """Load XLSX reference files"""

    def __init__(self, xlsx_path: Path):
        if openpyxl is None:
            raise ImportError("openpyxl is required. Install with: pip install openpyxl")
        self.xlsx_path = Path(xlsx_path)
        self.data = XLSXData(path=self.xlsx_path)

    def load(self) -> XLSXData:
        """Load and parse the XLSX file"""
        if not self.xlsx_path.exists():
            raise FileNotFoundError(f"XLSX file not found: {self.xlsx_path}")

        wb = openpyxl.load_workbook(self.xlsx_path, data_only=True)

        # Load prodotti sheet
        if 'prodotti' in wb.sheetnames:
            self._load_sheet(wb['prodotti'], 'prodotti')
        elif len(wb.sheetnames) > 0:
            # Try first sheet
            self._load_sheet(wb.worksheets[0], 'prodotti')

        # Load sku sheet
        if 'sku' in wb.sheetnames:
            self._load_sheet(wb['sku'], 'sku')
        elif len(wb.sheetnames) > 1:
            # Try second sheet
            self._load_sheet(wb.worksheets[1], 'sku')

        wb.close()
        return self.data

    def _load_sheet(self, sheet: 'Worksheet', sheet_type: str):
        """Load data from a worksheet"""
        rows = list(sheet.iter_rows(values_only=True))
        if not rows:
            return

        # First row is headers (keep original case for Italian column names)
        headers = [str(h).strip() if h else f'col_{i}' for i, h in enumerate(rows[0])]

        # Store columns
        if sheet_type == 'prodotti':
            self.data.prodotti_columns = headers
        else:
            self.data.sku_columns = headers

        # Load data rows (skip template/placeholder rows)
        for row_idx, row in enumerate(rows[1:], start=2):
            if not any(row):  # Skip empty rows
                continue

            # Skip placeholder row in prodotti sheet (row 2 typically has "Categoria", "Prodotto", etc.)
            if sheet_type == 'prodotti':
                first_val = str(row[0]).strip() if row[0] else ""
                if first_val in ('Categoria', 'Category'):
                    logger.debug(f"Skipping placeholder row {row_idx} in prodotti sheet")
                    continue

            # Skip placeholder row in sku sheet (row 2 often has template SKU '104250445')
            if sheet_type == 'sku' and row_idx == 2:
                first_val = str(row[0]).strip() if row[0] else ""
                if first_val == '104250445':
                    logger.debug(f"Skipping placeholder row {row_idx} in sku sheet")
                    continue

            row_dict = {}
            for i, value in enumerate(row):
                if i < len(headers):
                    col_name = headers[i]
                    row_dict[col_name] = self._clean_value(value)

            if sheet_type == 'prodotti':
                self.data.prodotti.append(row_dict)
            else:
                self.data.sku.append(row_dict)

    def _clean_value(self, value: Any) -> str:
        """Clean and normalize a cell value"""
        if value is None:
            return ""
        if isinstance(value, (int, float)):
            # Avoid scientific notation
            if isinstance(value, float) and value.is_integer():
                return str(int(value))
            return str(value)
        return str(value).strip()


def load_xlsx(xlsx_path: Path) -> XLSXData:
    """Convenience function to load an XLSX file"""
    loader = XLSXLoader(xlsx_path)
    return loader.load()


def get_xlsx_columns() -> Tuple[List[str], List[str]]:
    """Get standard column definitions"""
    return PRODOTTI_COLUMNS.copy(), SKU_COLUMNS.copy()


def validate_xlsx_structure(xlsx_path: Path) -> Dict[str, Any]:
    """Validate XLSX file structure against expected schema"""
    data = load_xlsx(xlsx_path)

    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'prodotti_count': len(data.prodotti),
        'sku_count': len(data.sku),
    }

    # Check for required sheets
    if not data.prodotti:
        result['warnings'].append("No 'prodotti' data found")

    if not data.sku:
        result['warnings'].append("No 'sku' data found")

    # Check for expected columns
    missing_prodotti = set(PRODOTTI_COLUMNS[:10]) - set(data.prodotti_columns)
    if missing_prodotti:
        result['warnings'].append(f"Missing prodotti columns: {missing_prodotti}")

    missing_sku = set(SKU_COLUMNS[:10]) - set(data.sku_columns)
    if missing_sku:
        result['warnings'].append(f"Missing sku columns: {missing_sku}")

    return result
