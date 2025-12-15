"""
Multi-Product Extractor - Extract multiple products from a single IDML file

Handles IDML files that contain multiple distinct products, such as:
- Main product (e.g., B614 barrier)
- Accessory products (e.g., Aste Tonde, Aste Rettangolari)

Each product section typically has:
- A section header (e.g., "Aste tonde S - Ø 75mm")
- Pricing tables with unique SKU codes
- Technical specifications
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import logging

from .idml_parser import IDMLDocument, Table, parse_idml
from .text_extractor import ProductInfo, TextExtractor
from .table_extractor import (
    TableExtractor, SKUSpecs, ProductTableData, PricingInfo
)
from .xlsx_writer import ExtractionResult

logger = logging.getLogger(__name__)


# Section markers that indicate a new product within an IDML file
PRODUCT_SECTION_MARKERS = [
    # Arms/poles sections
    ('aste tonde', 'Asta'),
    ('aste rettangolari', 'Asta'),
    ('aste rotonde', 'Asta'),
    # Accessory sections
    ('accessori specifici', 'Accessori'),
    # Kit sections
    ('kit modello', 'Kit'),
]

# Main product section markers (these indicate the primary product)
MAIN_PRODUCT_MARKERS = [
    'modelli famiglia',
    'modello famiglia',
    'dimensioni e caratteristiche',
    'caratteristiche tecniche',
]


@dataclass
class ProductSection:
    """Represents a product section within an IDML file"""
    name: str
    tipo_layout: str
    page_range: str
    text_content: List[str] = field(default_factory=list)
    tables: List[Table] = field(default_factory=list)
    pricing: List[PricingInfo] = field(default_factory=list)
    sku_codes: List[str] = field(default_factory=list)
    is_main_product: bool = False


@dataclass
class MultiProductResult:
    """Result of multi-product extraction"""
    source_file: str
    products: List[ExtractionResult] = field(default_factory=list)

    @property
    def product_count(self) -> int:
        return len(self.products)


class MultiProductExtractor:
    """Extract multiple products from a single IDML file"""

    def __init__(self, document: IDMLDocument):
        self.document = document
        self.all_text_content = []
        self.sections: List[ProductSection] = []

    def extract_all(self) -> MultiProductResult:
        """Extract all products from document"""
        result = MultiProductResult(
            source_file=str(self.document.path.name)
        )

        # Collect all text content with positions
        self._collect_text_content()

        # Identify product sections
        self._identify_sections()

        # If no sections found, treat as single product
        if not self.sections:
            product = self._extract_single_product()
            result.products.append(product)
            return result

        # Extract each product section
        for section in self.sections:
            product = self._extract_from_section(section)
            result.products.append(product)

        return result

    def _collect_text_content(self):
        """Collect all text content from document"""
        for story_id, texts in self.document.stories.items():
            for tc in texts:
                self.all_text_content.append({
                    'text': tc.text,
                    'position': tc.position,
                    'style': tc.style,
                    'story': story_id
                })

        # Sort by position
        self.all_text_content.sort(key=lambda x: x['position'])

    def _identify_sections(self):
        """Identify distinct product sections in the document"""
        # Get all text as one string for pattern matching
        full_text = ' '.join(tc['text'] for tc in self.all_text_content)
        full_text_lower = full_text.lower()

        # Check if this is a multi-product file
        has_aste_tonde = 'aste tonde' in full_text_lower
        has_aste_rettangolari = 'aste rettangolari' in full_text_lower

        # If we have both types of arms, this is likely a multi-product file
        if has_aste_tonde and has_aste_rettangolari:
            # Create sections for B614-style multi-product layout
            self._create_b614_style_sections(full_text_lower)
            return

        # Check for other multi-product patterns
        section_count = sum(1 for marker, _ in PRODUCT_SECTION_MARKERS
                          if marker in full_text_lower)

        if section_count > 0:
            self._create_generic_sections(full_text_lower)

    def _create_b614_style_sections(self, full_text_lower: str):
        """Create sections for B614-style layout (barrier + arms)"""
        # Get page info from filename
        filename = self.document.metadata.get('name', '')
        page_match = re.match(r'^(\d{2,3})-(\d{2,3})', filename)

        if page_match:
            start_page = int(page_match.group(1))
            end_page = int(page_match.group(2))

            # Calculate page ranges based on B614 layout:
            # Pages 1-2: Main barrier
            # Page 3: One type of arms (usually Tonde)
            # Page 4: Other type of arms (usually Rettangolari)

            main_pages = f"{start_page}-{start_page + 1}"
            tonde_page = str(start_page + 2)
            rett_page = str(start_page + 3)
        else:
            main_pages = ""
            tonde_page = ""
            rett_page = ""

        # Main product section (barrier)
        main_section = ProductSection(
            name=self._extract_main_product_name(),
            tipo_layout="Automazione",
            page_range=main_pages,
            is_main_product=True
        )

        # Aste Tonde section
        tonde_section = ProductSection(
            name=self._extract_main_product_name(),  # Same product family
            tipo_layout="Asta",
            page_range=tonde_page
        )

        # Aste Rettangolari section
        rett_section = ProductSection(
            name=self._extract_main_product_name(),  # Same product family
            tipo_layout="Asta",
            page_range=rett_page
        )

        # Assign tables and pricing to sections
        self._assign_tables_to_b614_sections(main_section, tonde_section, rett_section)

        self.sections = [main_section, tonde_section, rett_section]

    def _assign_tables_to_b614_sections(
        self,
        main_section: ProductSection,
        tonde_section: ProductSection,
        rett_section: ProductSection
    ):
        """Assign tables to B614-style sections based on content"""
        # Extract table data
        extractor = TableExtractor(self.document)
        extractor.extract_all()
        product_data = extractor.get_product_data()

        # Group pricing by SKU patterns
        # Main B614 SKUs: 104xxx, 1046xxx
        # Aste Tonde SKUs: 428046, 428045, 428042, 428043, 428002, 428615
        # Aste Rett SKUs: 428088, 428089, 428090, 428091

        tonde_codes = ['428046', '428045', '428042', '428043', '428002', '428615']
        rett_codes = ['428088', '428089', '428090', '428091']

        for pricing in product_data.pricing:
            code = pricing.code
            if code in tonde_codes:
                tonde_section.pricing.append(pricing)
                tonde_section.sku_codes.append(code)
            elif code in rett_codes:
                rett_section.pricing.append(pricing)
                rett_section.sku_codes.append(code)
            elif code.startswith('104'):
                main_section.pricing.append(pricing)
                main_section.sku_codes.append(code)
            else:
                # Assign other codes based on context or to main section
                main_section.pricing.append(pricing)
                if code not in main_section.sku_codes:
                    main_section.sku_codes.append(code)

        # Also check related_skus
        for sku in product_data.related_skus:
            if sku in tonde_codes:
                if sku not in tonde_section.sku_codes:
                    tonde_section.sku_codes.append(sku)
            elif sku in rett_codes:
                if sku not in rett_section.sku_codes:
                    rett_section.sku_codes.append(sku)

    def _create_generic_sections(self, full_text_lower: str):
        """Create sections for generic multi-product layouts"""
        # For now, create single product
        # This can be expanded for other multi-product patterns
        pass

    def _extract_main_product_name(self) -> str:
        """Extract main product name from document"""
        # Try filename first
        filename = self.document.metadata.get('name', '')
        # Pattern: "160-163_B614" -> "B614"
        match = re.search(r'_([A-Z]\d{3,4}[A-Z]?)(?:_|$)', filename)
        if match:
            return match.group(1)

        # Try text content
        for tc in self.all_text_content:
            text = tc['text'].strip()
            if re.match(r'^[A-Z]\d{3,4}[A-Z]?$', text):
                return text

        return "Unknown"

    def _extract_single_product(self) -> ExtractionResult:
        """Extract as a single product (fallback)"""
        text_extractor = TextExtractor(self.document)
        product_info = text_extractor.extract_all()

        table_extractor = TableExtractor(self.document)
        sku_specs = table_extractor.extract_all()
        product_data = table_extractor.get_product_data()

        # Merge product data
        self._merge_product_data(product_info, product_data, sku_specs)

        return ExtractionResult(
            source_file=str(self.document.path.name),
            product_info=product_info,
            sku_specs=sku_specs
        )

    def _extract_from_section(self, section: ProductSection) -> ExtractionResult:
        """Extract product info from a specific section"""
        product_info = ProductInfo()

        # Set basic info
        product_info.name = section.name
        product_info.tipo_layout = section.tipo_layout
        product_info.pagina_catalogo = section.page_range

        # Set SKU codes
        if section.sku_codes:
            product_info.codici_modelli = ';'.join(section.sku_codes)

        # Set category based on tipo_layout
        if section.tipo_layout == "Automazione":
            product_info.category = "Barriere automatiche"
        elif section.tipo_layout == "Asta":
            product_info.category = "Barriere automatiche"  # Same family

        # Extract additional info from text extractor for main product
        if section.is_main_product:
            text_extractor = TextExtractor(self.document)
            full_info = text_extractor.extract_all()

            # Copy relevant fields
            product_info.description = full_info.description
            product_info.short_description = full_info.short_description
            product_info.features = full_info.features
            product_info.badges = full_info.badges
            product_info.certifications = full_info.certifications
            product_info.intensita_transito = full_info.intensita_transito

        # Create SKU specs for this section's codes
        sku_specs = []

        # Get all technical specs from document
        table_extractor = TableExtractor(self.document)
        all_specs = table_extractor.extract_all()

        # Only include specs relevant to this section's SKUs
        for spec in all_specs:
            if section.is_main_product:
                # For main product, include all non-arm specs
                if 'asta' not in spec.sku.lower():
                    sku_specs.append(spec)

        return ExtractionResult(
            source_file=str(self.document.path.name),
            product_info=product_info,
            sku_specs=sku_specs
        )

    def _merge_product_data(
        self,
        product_info: ProductInfo,
        product_data: ProductTableData,
        sku_specs: List[SKUSpecs]
    ):
        """Merge table-extracted data into ProductInfo"""
        if product_data.kit_components:
            product_info.componenti_kit = product_data.get_componenti_kit()

        if product_data.related_skus:
            product_info.sku_correlati = product_data.get_sku_correlati()

        if product_data.pricing:
            codes = [p.code for p in product_data.pricing if p.code]
            if codes:
                product_info.codici_modelli = ';'.join(codes[:10])

        if not product_info.codici_modelli and sku_specs:
            model_codes = []
            for spec in sku_specs:
                if spec.sku and spec.sku not in model_codes:
                    model_codes.append(spec.sku)
            if model_codes:
                product_info.codici_modelli = ';'.join(model_codes[:10])


def extract_multi_product(idml_path: Path) -> MultiProductResult:
    """Extract multiple products from an IDML file"""
    document = parse_idml(idml_path)
    extractor = MultiProductExtractor(document)
    return extractor.extract_all()


def is_multi_product_file(idml_path: Path) -> bool:
    """Check if an IDML file contains multiple products"""
    document = parse_idml(idml_path)
    full_text = document.all_text.lower()

    # Check for known multi-product patterns
    has_aste_tonde = 'aste tonde' in full_text
    has_aste_rettangolari = 'aste rettangolari' in full_text

    return has_aste_tonde and has_aste_rettangolari
