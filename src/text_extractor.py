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
        return self.product_info

    def _extract_title(self):
        """Extract product title/name"""
        # Look for title-styled text
        for style in self.TITLE_STYLES:
            matches = self.document.find_text_by_style(style)
            if matches:
                # Take the first substantial title
                for tc in matches:
                    if len(tc.text) > 3 and len(tc.text) < 200:
                        self.product_info.name = tc.text.strip()
                        return

        # Fallback: look for largest text or first significant text
        all_texts = []
        for story_texts in self.document.stories.values():
            all_texts.extend(story_texts)

        if all_texts:
            # Sort by position, take first substantial text
            all_texts.sort(key=lambda x: x.position)
            for tc in all_texts:
                text = tc.text.strip()
                if len(text) > 3 and len(text) < 200:
                    self.product_info.name = text
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
        # Category is often in page header or specific styled text
        category_styles = ['category', 'categoria', 'header']

        for style in category_styles:
            matches = self.document.find_text_by_style(style)
            if matches:
                self.product_info.category = matches[0].text.strip()
                return

        # Try to infer from metadata
        if self.document.metadata.get('name'):
            name = self.document.metadata['name']
            # Category might be prefix of filename
            parts = name.split('_')
            if len(parts) > 1:
                self.product_info.category = parts[0]


def extract_product_info(document: IDMLDocument) -> ProductInfo:
    """Convenience function to extract product info from document"""
    extractor = TextExtractor(document)
    return extractor.extract_all()


def extract_product_info_from_idml(idml_path: Path) -> ProductInfo:
    """Extract product info directly from IDML file"""
    from .idml_parser import parse_idml
    document = parse_idml(idml_path)
    return extract_product_info(document)
