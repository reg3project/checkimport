"""
Text Extractor - Extract product information from IDML text content

Extracts:
- Product names and titles
- Descriptions
- SKU codes
- Category information
- Badges and certifications
- Accessory lists
"""

import re
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from pathlib import Path
import logging

from .idml_parser import IDMLDocument, TextContent

logger = logging.getLogger(__name__)


@dataclass
class ProductInfo:
    """Product-level information extracted from IDML"""
    name: str = ""
    category: str = ""
    subcategory: str = ""
    page: str = ""
    description: str = ""
    short_description: str = ""
    features: List[str] = field(default_factory=list)
    badges: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    accessories: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    sku_codes: List[str] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)
    # New fields from table extraction
    componenti_kit: str = ""
    sku_correlati: str = ""
    # Additional product-level fields
    tipo_layout: str = ""
    pagina_catalogo: str = ""
    titolo_prodotto: str = ""
    descrizione_categoria: str = ""
    caratteristica_primaria: str = ""
    valore_primario: str = ""
    caratteristica_secondaria: str = ""
    valore_secondario: str = ""
    intensita_transito: str = ""
    codici_modelli: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'category': self.category,
            'subcategory': self.subcategory,
            'page': self.page,
            'description': self.description,
            'short_description': self.short_description,
            'features': '; '.join(self.features),
            'badges': '; '.join(self.badges),
            'certifications': '; '.join(self.certifications),
            'accessories': '; '.join(self.accessories),
            'images': '; '.join(self.images),
            'sku_codes': '; '.join(self.sku_codes),
            'componenti_kit': self.componenti_kit,
            'sku_correlati': self.sku_correlati,
            'tipo_layout': self.tipo_layout,
            'pagina_catalogo': self.pagina_catalogo,
            'titolo_prodotto': self.titolo_prodotto,
            'descrizione_categoria': self.descrizione_categoria,
            'caratteristica_primaria': self.caratteristica_primaria,
            'valore_primario': self.valore_primario,
            'caratteristica_secondaria': self.caratteristica_secondaria,
            'valore_secondario': self.valore_secondario,
            'intensita_transito': self.intensita_transito,
            'codici_modelli': self.codici_modelli,
        }


class TextExtractor:
    """Extract product information from IDML text"""

    # Style patterns for different content types
    TITLE_STYLES = ['title', 'heading', 'nome', 'product', 'h1', 'h2']
    DESCRIPTION_STYLES = ['description', 'body', 'text', 'paragraph']
    BADGE_STYLES = ['badge', 'tag', 'label', 'icon']

    # Known badge/certification patterns
    CERTIFICATION_PATTERNS = [
        r'\bCE\b',
        r'\bIP\d{2}\b',
        r'\bUL\b',
        r'\bISO\s*\d+',
        r'\bEN\s*\d+',
        r'\bIEC\s*\d+',
    ]

    # SKU patterns
    SKU_PATTERNS = [
        r'\b(\d{6,})\b',
        r'\b([A-Z]{1,3}\d{5,}[A-Z]?)\b',
        r'\b(FAAC\d+)\b',
    ]

    def __init__(self, document: IDMLDocument):
        self.document = document
        self.product_info = ProductInfo()

    def extract_all(self) -> ProductInfo:
        """Extract all product information"""
        self._extract_title()
        self._extract_description()
        self._extract_skus()
        self._extract_certifications()
        self._extract_badges()
        self._extract_accessories()
        self._extract_images()
        self._extract_category()
        self._extract_page_info()
        self._extract_layout_type()
        self._extract_subtitle()
        self._extract_characteristics()
        self._extract_traffic_intensity()
        return self.product_info

    def _extract_title(self):
        """Extract product title/name"""
        # FAAC product name patterns - alphanumeric codes like "740 C", "770N 230V", "S2500I", etc.
        product_name_patterns = [
            r'\b(\d{3,4}\s*[A-Z]?\s*(?:230V|24V)?)\b',  # 740 C, 770N 230V
            r'\b([A-Z]\d{4}[A-Z]?)\b',  # S2500I
            r'\b([A-Z]+\s+\d+[A-Z]?(?:\s*kit)?)\b',  # LEADER kit, MASTER kit
            r'\b(B\d{3})\b',  # B614
            r'\b(XTO)\b',  # XTO
        ]

        # Collect all text sorted by position
        all_texts = []
        for story_texts in self.document.stories.values():
            all_texts.extend(story_texts)
        all_texts.sort(key=lambda x: x.position)

        # Try to extract from filename first
        if self.document.metadata.get('name'):
            filename = self.document.metadata['name']
            # Pattern: "116-117_740_C" -> extract "740 C" or "030_MASTER_kit" -> "MASTER kit"
            for pattern in product_name_patterns:
                match = re.search(pattern, filename.replace('_', ' '), re.IGNORECASE)
                if match:
                    self.product_info.name = match.group(1).strip()
                    return

        # Look for product name patterns in text
        for tc in all_texts:
            text = tc.text.strip()
            if 3 < len(text) < 50:
                for pattern in product_name_patterns:
                    if re.match(pattern, text, re.IGNORECASE):
                        self.product_info.name = text
                        return

        # Look for title-styled text
        for style in self.TITLE_STYLES:
            matches = self.document.find_text_by_style(style)
            if matches:
                for tc in matches:
                    if len(tc.text) > 3 and len(tc.text) < 200:
                        self.product_info.name = tc.text.strip()
                        return

        # Fallback: look for text after category keywords
        category_keywords = ['automazioni', 'barriere', 'motoriduttore', 'kit', 'sistema']
        found_category = False
        for tc in all_texts:
            text = tc.text.strip().lower()
            if any(kw in text for kw in category_keywords):
                found_category = True
                continue
            if found_category and 3 < len(tc.text.strip()) < 50:
                # This might be the product name following the category
                self.product_info.name = tc.text.strip()
                return

    def _extract_description(self):
        """Extract product description"""
        descriptions = []

        for style in self.DESCRIPTION_STYLES:
            matches = self.document.find_text_by_style(style)
            for tc in matches:
                text = tc.text.strip()
                if len(text) > 20:  # Substantial text
                    descriptions.append(text)

        if descriptions:
            # Combine descriptions
            self.product_info.description = ' '.join(descriptions)

            # Create short description from first sentence
            first_desc = descriptions[0]
            sentences = re.split(r'[.!?]', first_desc)
            if sentences:
                self.product_info.short_description = sentences[0].strip()

        # Also look for feature bullet points
        self._extract_features()

    def _extract_features(self):
        """Extract feature bullet points"""
        all_text = self.document.all_text

        # Look for bullet points or numbered lists
        bullet_patterns = [
            r'[•●○▪]\s*(.+)',
            r'^\s*[-–—]\s*(.+)',
            r'^\s*\d+[.)]\s*(.+)',
        ]

        features = set()
        for pattern in bullet_patterns:
            matches = re.findall(pattern, all_text, re.MULTILINE)
            for match in matches:
                feature = match.strip()
                if 5 < len(feature) < 200:
                    features.add(feature)

        self.product_info.features = list(features)

    def _extract_skus(self):
        """Extract SKU codes from text"""
        all_text = self.document.all_text
        skus = set()

        for pattern in self.SKU_PATTERNS:
            matches = re.findall(pattern, all_text)
            for match in matches:
                if self._is_valid_sku(match):
                    skus.add(match)

        self.product_info.sku_codes = sorted(list(skus))

    def _is_valid_sku(self, code: str) -> bool:
        """Validate if string looks like a valid SKU"""
        if not code:
            return False

        # Too short or too long
        if len(code) < 5 or len(code) > 20:
            return False

        # Should have digits
        if not any(c.isdigit() for c in code):
            return False

        # Exclude common false positives
        false_positives = ['2024', '2023', '2022', '12345']
        if code in false_positives:
            return False

        return True

    def _extract_certifications(self):
        """Extract certifications (CE, IP rating, etc.)"""
        all_text = self.document.all_text
        certs = set()

        for pattern in self.CERTIFICATION_PATTERNS:
            matches = re.findall(pattern, all_text)
            for match in matches:
                certs.add(match.upper())

        self.product_info.certifications = sorted(list(certs))

    def _extract_badges(self):
        """Extract product badges/tags"""
        badges = set()

        # Look for badge-styled text
        for style in self.BADGE_STYLES:
            matches = self.document.find_text_by_style(style)
            for tc in matches:
                text = tc.text.strip()
                if 2 < len(text) < 50:
                    badges.add(text)

        # Common badge keywords
        badge_keywords = [
            'new', 'nuovo', 'best', 'top', 'eco', 'smart',
            'wireless', 'solar', 'premium', 'pro', 'plus'
        ]

        all_text = self.document.all_text.lower()
        for keyword in badge_keywords:
            if keyword in all_text:
                badges.add(keyword.capitalize())

        self.product_info.badges = sorted(list(badges))

    def _extract_accessories(self):
        """Extract accessory list"""
        all_text = self.document.all_text.lower()

        # Look for accessory section
        accessory_markers = ['accessori', 'accessories', 'optional', 'opzionali']

        for marker in accessory_markers:
            idx = all_text.find(marker)
            if idx >= 0:
                # Extract text after marker
                section = self.document.all_text[idx:idx+500]
                lines = section.split('\n')

                for line in lines[1:]:  # Skip header line
                    line = line.strip()
                    if line and len(line) > 3 and len(line) < 100:
                        # Stop if we hit another section
                        if any(m in line.lower() for m in ['caratteristiche', 'features', 'specifiche']):
                            break
                        self.product_info.accessories.append(line)

                if self.product_info.accessories:
                    break

    def _extract_images(self):
        """Extract image references"""
        for img in self.document.images:
            if img.name:
                self.product_info.images.append(img.name)

    def _extract_category(self):
        """Extract product category"""
        # Known FAAC category patterns
        category_keywords = [
            'automazioni per cancelli',
            'automazioni per ante',
            'barriere stradali',
            'barriere automatiche',
            'motoriduttore',
            'kit special',
            'perfect kit',
            'schema installazione',
            'sistema'
        ]

        # Collect all text sorted by position
        all_texts = []
        for story_texts in self.document.stories.values():
            all_texts.extend(story_texts)
        all_texts.sort(key=lambda x: x.position)

        # Look for category keywords in text
        for tc in all_texts:
            text = tc.text.strip()
            text_lower = text.lower()
            for keyword in category_keywords:
                if keyword in text_lower and len(text) < 100:
                    self.product_info.category = text
                    return

        # Look for category-styled text
        category_styles = ['category', 'categoria', 'header']
        for style in category_styles:
            matches = self.document.find_text_by_style(style)
            if matches:
                self.product_info.category = matches[0].text.strip()
                return

        # Try to infer from metadata (filename)
        if self.document.metadata.get('name'):
            name = self.document.metadata['name']
            # For kit files like "030_MASTER_kit_24V_PERFECT_60"
            if 'PERFECT' in name.upper():
                self.product_info.category = "PERFECT KIT"
                return
            if 'kit' in name.lower():
                self.product_info.category = "Kit"
                return
            # For schema files like "268_400_SI"
            if '_SI' in name:
                self.product_info.category = "Schema Installazione"
                return

    def _extract_page_info(self):
        """Extract page catalog number from filename"""
        if self.document.metadata.get('name'):
            filename = self.document.metadata['name']
            # Pattern: "116-117_740_C" -> extract "116-117"
            # Pattern: "028_LEADER_kit" -> extract "28"
            match = re.match(r'^(\d{2,3}(?:-\d{2,3})?)', filename)
            if match:
                page = match.group(1)
                # Remove leading zeros for single page numbers
                if '-' not in page:
                    page = page.lstrip('0') or '0'
                self.product_info.pagina_catalogo = page

    def _extract_layout_type(self):
        """Extract layout type based on content patterns"""
        filename = self.document.metadata.get('name', '').lower()
        category = self.product_info.category.lower() if self.product_info.category else ""

        # Determine layout type from patterns
        if 'kit' in filename or 'kit' in category:
            self.product_info.tipo_layout = "Kit special"
        elif '_si' in filename or 'schema' in category:
            self.product_info.tipo_layout = "Schema Installazione"
        elif 'barriere' in category or 'barriera' in category:
            self.product_info.tipo_layout = "Barriera"
        elif 'automazioni' in category or 'motoriduttore' in category:
            self.product_info.tipo_layout = "Automazione"
        elif 'sistema' in category or 'xto' in filename.lower():
            self.product_info.tipo_layout = "Sistema"

    def _extract_subtitle(self):
        """Extract product subtitle/title"""
        # Collect all text sorted by position
        all_texts = []
        for story_texts in self.document.stories.values():
            all_texts.extend(story_texts)
        all_texts.sort(key=lambda x: x.position)

        # Look for subtitle patterns (usually after product name)
        subtitle_keywords = [
            'motoriduttore',
            'automazione',
            'sistema',
            'operatore',
            'attuatore',
            'barriera',
            'ricevitore',
            'trasmittente'
        ]

        for tc in all_texts:
            text = tc.text.strip()
            text_lower = text.lower()
            # Look for subtitle that's not the main product name
            if 10 < len(text) < 80:
                for keyword in subtitle_keywords:
                    if keyword in text_lower and text != self.product_info.name:
                        self.product_info.titolo_prodotto = text
                        return

    def _extract_characteristics(self):
        """Extract primary and secondary characteristics"""
        # Collect all text
        all_texts = []
        for story_texts in self.document.stories.values():
            all_texts.extend(story_texts)
        all_texts.sort(key=lambda x: x.position)

        # Known characteristic patterns
        char_patterns = [
            (r'peso\s*(?:max|massimo)?\s*(?:anta|cancello)?[:\s]*(\d+[\s,.]?\d*\s*(?:kg|Kg|KG)?)', 'Peso max anta'),
            (r'larghezza\s*(?:max|massima)?\s*(?:anta|cancello)?[:\s]*(\d+[\s,.]?\d*\s*(?:m|cm)?)', 'Larghezza max anta'),
            (r'velocit[àa]\s*(?:max|massima)?[:\s]*(\d+[\s,.]?\d*\s*(?:m/min|rpm)?)', 'Velocità max'),
            (r'lunghezza\s*(?:max|massima)?[:\s]*(\d+[\s,.]?\d*\s*(?:m|cm)?)', 'Lunghezza max'),
        ]

        all_text = ' '.join(tc.text for tc in all_texts)

        for pattern, char_name in char_patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if not self.product_info.caratteristica_primaria:
                    self.product_info.caratteristica_primaria = char_name
                    self.product_info.valore_primario = value
                elif not self.product_info.caratteristica_secondaria:
                    self.product_info.caratteristica_secondaria = char_name
                    self.product_info.valore_secondario = value
                    break

    def _extract_traffic_intensity(self):
        """Extract traffic intensity (Basso/Medio/Alto)"""
        # Collect all text
        all_texts = []
        for story_texts in self.document.stories.values():
            all_texts.extend(story_texts)

        all_text = ' '.join(tc.text.lower() for tc in all_texts)

        # Look for traffic intensity indicators
        if 'alto' in all_text and 'transito' in all_text:
            self.product_info.intensita_transito = "Alto"
        elif 'medio' in all_text and 'transito' in all_text:
            self.product_info.intensita_transito = "Medio"
        elif 'basso' in all_text and 'transito' in all_text:
            self.product_info.intensita_transito = "Basso"
        # Also check for intensity without "transito"
        elif 'intensivo' in all_text or 'intenso' in all_text:
            self.product_info.intensita_transito = "Alto"
        elif 'residenziale' in all_text:
            self.product_info.intensita_transito = "Basso"


def extract_product_info(document: IDMLDocument) -> ProductInfo:
    """Convenience function to extract product info from document"""
    extractor = TextExtractor(document)
    return extractor.extract_all()


def extract_product_info_from_idml(idml_path: Path) -> ProductInfo:
    """Extract product info directly from IDML file"""
    from .idml_parser import parse_idml
    document = parse_idml(idml_path)
    return extract_product_info(document)
