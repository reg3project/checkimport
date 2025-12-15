"""
Comparator - Compare extracted IDML data with reference XLSX files

Performs field-by-field comparison to:
- Find matches
- Detect mismatches
- Identify new fields (in IDML but not in XLSX schema)
- Find missing fields (expected but not in IDML)

Supports Italian field names from FAAC XLSX files.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import re
import logging
from datetime import datetime

from .xlsx_loader import XLSXData, load_xlsx
from .xlsx_writer import ExtractionResult
from .idml_parser import parse_idml
from .table_extractor import extract_specs_from_document, extract_all_from_document, SKUSpecs
from .text_extractor import extract_product_info
from .field_mapping import (
    normalize_value, values_match, find_xlsx_column_for_idml_attr,
    convert_product_dict_to_italian, get_italian_column_for_english,
    ENGLISH_TO_ITALIAN_PRODUCT, ENGLISH_TO_ITALIAN_SKU
)

logger = logging.getLogger(__name__)


@dataclass
class FieldComparison:
    """Comparison result for a single field"""
    field_name: str
    extracted_value: str
    reference_value: str
    status: str  # 'match', 'mismatch', 'new', 'missing'
    difference: Optional[float] = None  # Numeric difference if applicable
    similarity: float = 0.0  # String similarity score

    @property
    def is_match(self) -> bool:
        return self.status == 'match'


@dataclass
class ComparisonResult:
    """Complete comparison result for a file pair"""
    idml_file: str
    xlsx_file: str
    timestamp: str
    comparisons: List[FieldComparison] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def matches(self) -> List[FieldComparison]:
        return [c for c in self.comparisons if c.status == 'match']

    @property
    def mismatches(self) -> List[FieldComparison]:
        return [c for c in self.comparisons if c.status == 'mismatch']

    @property
    def new_fields(self) -> List[FieldComparison]:
        return [c for c in self.comparisons if c.status == 'new']

    @property
    def missing_fields(self) -> List[FieldComparison]:
        return [c for c in self.comparisons if c.status == 'missing']

    @property
    def accuracy(self) -> float:
        """Calculate accuracy percentage"""
        total = len(self.matches) + len(self.mismatches)
        if total == 0:
            return 0.0
        return (len(self.matches) / total) * 100

    @property
    def total_fields(self) -> int:
        return len(self.comparisons)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting"""
        return {
            'idml_file': self.idml_file,
            'xlsx_file': self.xlsx_file,
            'timestamp': self.timestamp,
            'accuracy': round(self.accuracy, 2),
            'total_fields': self.total_fields,
            'matches': len(self.matches),
            'mismatches': len(self.mismatches),
            'new_fields': len(self.new_fields),
            'missing_fields': len(self.missing_fields),
            'comparisons': [
                {
                    'field': c.field_name,
                    'extracted': c.extracted_value,
                    'reference': c.reference_value,
                    'status': c.status,
                    'similarity': round(c.similarity, 2)
                }
                for c in self.comparisons
            ]
        }


class Comparator:
    """Compare extracted data with reference data"""

    # Tolerance for numeric comparisons
    NUMERIC_TOLERANCE = 0.01
    # Minimum similarity for fuzzy match
    SIMILARITY_THRESHOLD = 0.85

    def __init__(self):
        self.results: List[ComparisonResult] = []

    def compare(
        self,
        extraction: ExtractionResult,
        reference: XLSXData
    ) -> ComparisonResult:
        """Compare extracted data with reference XLSX data"""
        result = ComparisonResult(
            idml_file=extraction.source_file,
            xlsx_file=str(reference.path.name),
            timestamp=datetime.now().isoformat()
        )

        # Compare product-level fields
        self._compare_product_fields(extraction, reference, result)

        # Compare SKU-level fields
        self._compare_sku_fields(extraction, reference, result)

        self.results.append(result)
        return result

    def _compare_product_fields(
        self,
        extraction: ExtractionResult,
        reference: XLSXData,
        result: ComparisonResult
    ):
        """Compare product-level fields"""
        # Convert extracted dict from English to Italian column names
        extracted_english = extraction.product_info.to_dict()
        extracted_dict = convert_product_dict_to_italian(extracted_english)

        # Get reference product (first one if multiple)
        ref_product = reference.prodotti[0] if reference.prodotti else {}

        # Compare each field using Italian column names
        all_fields = set(extracted_dict.keys()) | set(ref_product.keys())

        for field_name in all_fields:
            extracted_val = str(extracted_dict.get(field_name, "")).strip()
            reference_val = str(ref_product.get(field_name, "")).strip()

            comparison = self._compare_values(field_name, extracted_val, reference_val)
            result.comparisons.append(comparison)

    def _compare_sku_fields(
        self,
        extraction: ExtractionResult,
        reference: XLSXData,
        result: ComparisonResult
    ):
        """Compare SKU-level fields by matching SKU codes"""
        # Build lookup of reference SKUs by SKU code (primary key)
        ref_by_sku = {}
        for ref_sku in reference.sku:
            sku_code = str(ref_sku.get('SKU', '')).strip()
            if sku_code:
                ref_by_sku[sku_code] = ref_sku

        # Get SKU codes from codici_modelli (extracted from pricing tables)
        extracted_sku_codes = []
        if extraction.product_info.codici_modelli:
            extracted_sku_codes = [s.strip() for s in extraction.product_info.codici_modelli.split(';') if s.strip()]

        # Collect all technical specs from extraction (these apply to all SKUs)
        all_specs = {}
        for sku_specs in extraction.sku_specs:
            for field_name, spec in sku_specs.specs.items():
                if field_name not in ('sku', 'Nome Modello', 'Modello'):
                    all_specs[field_name] = spec.value

        # Compare each extracted SKU code with its reference row
        matched_skus = set()
        for sku_code in extracted_sku_codes:
            if sku_code not in ref_by_sku:
                continue

            matched_skus.add(sku_code)
            ref_sku = ref_by_sku[sku_code]

            # Compare technical specs
            for field_name, extracted_val in all_specs.items():
                extracted_val = str(extracted_val).strip()

                # Find matching reference field
                reference_val = ""
                xlsx_col = find_xlsx_column_for_idml_attr(field_name)

                if xlsx_col and xlsx_col in ref_sku:
                    reference_val = str(ref_sku.get(xlsx_col, "")).strip()
                elif field_name in ref_sku:
                    reference_val = str(ref_sku.get(field_name, "")).strip()

                comparison = self._compare_values(
                    f"{sku_code}.{field_name}",
                    extracted_val,
                    reference_val
                )
                result.comparisons.append(comparison)

            # Check for missing fields in reference
            for ref_field, ref_value in ref_sku.items():
                if ref_field in ('SKU', 'COUNTIF', 'SKU Immagine', 'Tipo', 'col_3'):
                    continue

                ref_val = str(ref_value).strip() if ref_value else ""
                if not ref_val:
                    continue

                # Check if we have this field
                found = False
                for field_name in all_specs.keys():
                    xlsx_col = find_xlsx_column_for_idml_attr(field_name)
                    if xlsx_col == ref_field or field_name == ref_field:
                        found = True
                        break

                if not found:
                    comparison = self._compare_values(
                        f"{sku_code}.{ref_field}",
                        "",
                        ref_val
                    )
                    result.comparisons.append(comparison)

        # If no SKU codes matched, fall back to model name matching
        if not matched_skus and extraction.sku_specs:
            self._compare_sku_by_model_name(extraction, reference, result, ref_by_sku)

    def _compare_sku_by_model_name(
        self,
        extraction: ExtractionResult,
        reference: XLSXData,
        result: ComparisonResult,
        ref_by_sku: dict
    ):
        """Fallback: Compare SKUs by model name when SKU codes don't match"""
        # Build lookup by model name
        ref_by_model = {}
        for ref_sku in reference.sku:
            model = ref_sku.get('Nome Modello', '')
            if model:
                ref_by_model[model.lower()] = ref_sku

        for sku_specs in extraction.sku_specs:
            extracted_dict = sku_specs.to_dict()
            model_name = sku_specs.sku

            # Find matching reference SKU by model name
            ref_sku = None
            model_lower = model_name.lower() if model_name else ""

            if model_lower and model_lower in ref_by_model:
                ref_sku = ref_by_model[model_lower]
            elif model_lower:
                # Try partial match
                for ref_model, ref_data in ref_by_model.items():
                    if model_lower in ref_model or ref_model in model_lower:
                        ref_sku = ref_data
                        break

            if not ref_sku:
                ref_sku = {}

            # Compare fields
            for field_name, field_value in extracted_dict.items():
                if field_name in ('sku', 'Nome Modello'):
                    continue

                extracted_val = str(field_value).strip()
                reference_val = ""
                xlsx_col = find_xlsx_column_for_idml_attr(field_name)

                if xlsx_col and xlsx_col in ref_sku:
                    reference_val = str(ref_sku.get(xlsx_col, "")).strip()
                elif field_name in ref_sku:
                    reference_val = str(ref_sku.get(field_name, "")).strip()

                comparison = self._compare_values(
                    f"{model_name}.{field_name}",
                    extracted_val,
                    reference_val
                )
                result.comparisons.append(comparison)

    def _compare_values(
        self,
        field_name: str,
        extracted: str,
        reference: str
    ) -> FieldComparison:
        """Compare two values and determine match status"""
        # Normalize values
        extracted_norm = self._normalize(extracted)
        reference_norm = self._normalize(reference)

        # Determine status
        if not extracted_norm and not reference_norm:
            status = 'match'
            similarity = 1.0
        elif not extracted_norm:
            status = 'missing'
            similarity = 0.0
        elif not reference_norm:
            status = 'new'
            similarity = 0.0
        elif extracted_norm == reference_norm:
            status = 'match'
            similarity = 1.0
        else:
            # Try numeric comparison
            num_match, difference = self._numeric_compare(extracted_norm, reference_norm)
            if num_match:
                status = 'match'
                similarity = 1.0
            else:
                # Try fuzzy string comparison
                similarity = self._string_similarity(extracted_norm, reference_norm)
                if similarity >= self.SIMILARITY_THRESHOLD:
                    status = 'match'
                else:
                    status = 'mismatch'
                difference = None

            return FieldComparison(
                field_name=field_name,
                extracted_value=extracted,
                reference_value=reference,
                status=status,
                difference=difference,
                similarity=similarity
            )

        return FieldComparison(
            field_name=field_name,
            extracted_value=extracted,
            reference_value=reference,
            status=status,
            similarity=similarity
        )

    def _normalize(self, value: str) -> str:
        """Normalize a value for comparison"""
        if not value:
            return ""

        # Lowercase
        result = value.lower().strip()

        # Normalize whitespace
        result = re.sub(r'\s+', ' ', result)

        # Normalize decimal separator
        result = result.replace(',', '.')

        return result

    def _numeric_compare(self, val1: str, val2: str) -> Tuple[bool, Optional[float]]:
        """Compare two values as numbers"""
        try:
            # Extract numeric parts
            num1 = float(re.sub(r'[^\d.]', '', val1))
            num2 = float(re.sub(r'[^\d.]', '', val2))

            difference = abs(num1 - num2)
            # Match if within tolerance
            if difference <= self.NUMERIC_TOLERANCE:
                return True, 0.0
            # Match if relative difference is small
            if num2 != 0 and (difference / abs(num2)) <= self.NUMERIC_TOLERANCE:
                return True, difference

            return False, difference
        except (ValueError, ZeroDivisionError):
            return False, None

    def _string_similarity(self, s1: str, s2: str) -> float:
        """Calculate string similarity using simple ratio"""
        if not s1 or not s2:
            return 0.0
        if s1 == s2:
            return 1.0

        # Use simple character-based similarity
        matches = sum(1 for a, b in zip(s1, s2) if a == b)
        return matches / max(len(s1), len(s2))

    def get_aggregate_stats(self) -> Dict[str, Any]:
        """Get aggregate statistics across all comparisons"""
        if not self.results:
            return {}

        total_matches = sum(len(r.matches) for r in self.results)
        total_mismatches = sum(len(r.mismatches) for r in self.results)
        total_new = sum(len(r.new_fields) for r in self.results)
        total_missing = sum(len(r.missing_fields) for r in self.results)

        total_compared = total_matches + total_mismatches
        overall_accuracy = (total_matches / total_compared * 100) if total_compared > 0 else 0

        return {
            'files_compared': len(self.results),
            'overall_accuracy': round(overall_accuracy, 2),
            'total_matches': total_matches,
            'total_mismatches': total_mismatches,
            'total_new_fields': total_new,
            'total_missing_fields': total_missing,
            'per_file': [r.to_dict() for r in self.results]
        }


def _merge_product_data(product_info, product_data, sku_specs):
    """Merge table-extracted product data into ProductInfo"""
    # Merge kit components
    if product_data.kit_components:
        product_info.componenti_kit = product_data.get_componenti_kit()

    # Merge related SKUs
    if product_data.related_skus:
        product_info.sku_correlati = product_data.get_sku_correlati()

    # Extract codici_modelli from pricing tables (primary product codes)
    if product_data.pricing:
        # Get unique product codes from pricing
        codes = [p.code for p in product_data.pricing if p.code]
        if codes:
            product_info.codici_modelli = ';'.join(codes[:5])  # First 5 codes

    # Also add model names from SKU specs as codici_modelli fallback
    if not product_info.codici_modelli and sku_specs:
        model_codes = []
        for spec in sku_specs:
            if spec.sku and spec.sku not in model_codes:
                model_codes.append(spec.sku)
        if model_codes:
            product_info.codici_modelli = ';'.join(model_codes[:5])


def compare_files(idml_path: Path, xlsx_path: Path) -> ComparisonResult:
    """Compare an IDML file with its reference XLSX"""
    # Parse IDML
    document = parse_idml(idml_path)
    product_info = extract_product_info(document)
    sku_specs, product_data = extract_all_from_document(document)

    # Merge product_data into product_info
    _merge_product_data(product_info, product_data, sku_specs)

    extraction = ExtractionResult(
        source_file=str(idml_path.name),
        product_info=product_info,
        sku_specs=sku_specs
    )

    # Load reference
    reference = load_xlsx(xlsx_path)

    # Compare
    comparator = Comparator()
    return comparator.compare(extraction, reference)


def batch_compare(pairs: List[Tuple[Path, Path]]) -> Dict[str, Any]:
    """Compare multiple IDML/XLSX pairs"""
    comparator = Comparator()

    for idml_path, xlsx_path in pairs:
        try:
            document = parse_idml(idml_path)
            product_info = extract_product_info(document)
            sku_specs, product_data = extract_all_from_document(document)

            # Merge product_data into product_info
            _merge_product_data(product_info, product_data, sku_specs)

            extraction = ExtractionResult(
                source_file=str(idml_path.name),
                product_info=product_info,
                sku_specs=sku_specs
            )

            reference = load_xlsx(xlsx_path)
            comparator.compare(extraction, reference)
        except Exception as e:
            logger.error(f"Error comparing {idml_path.name}: {e}")

    return comparator.get_aggregate_stats()
