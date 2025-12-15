"""
IDML Parser - Parse Adobe InDesign IDML files

IDML files are ZIP archives containing XML files that define:
- Stories (text content)
- Spreads (page layouts)
- Resources (fonts, colors, styles)
"""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import re
import logging

logger = logging.getLogger(__name__)

# IDML namespaces
IDML_NS = {
    'idPkg': 'http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging',
    'idml': 'http://ns.adobe.com/AdobeInDesign/idml/1.0'
}


@dataclass
class TextContent:
    """Represents extracted text content from IDML"""
    text: str
    style: str = ""
    paragraph_style: str = ""
    character_style: str = ""
    position: int = 0


@dataclass
class TableCell:
    """Represents a table cell"""
    row: int
    col: int
    content: str
    row_span: int = 1
    col_span: int = 1
    style: str = ""


@dataclass
class Table:
    """Represents an extracted table"""
    cells: List[TableCell] = field(default_factory=list)
    rows: int = 0
    cols: int = 0
    header_rows: int = 0

    def get_cell(self, row: int, col: int) -> Optional[TableCell]:
        """Get cell at specific position"""
        for cell in self.cells:
            if cell.row == row and cell.col == col:
                return cell
        return None

    def to_dict_list(self) -> List[Dict[str, str]]:
        """Convert table to list of dicts using first row as headers"""
        if self.rows < 2:
            return []

        # Get headers from first row
        headers = []
        for col in range(self.cols):
            cell = self.get_cell(0, col)
            headers.append(cell.content if cell else f"col_{col}")

        # Build data rows
        result = []
        for row in range(1, self.rows):
            row_dict = {}
            for col, header in enumerate(headers):
                cell = self.get_cell(row, col)
                row_dict[header] = cell.content if cell else ""
            result.append(row_dict)

        return result


@dataclass
class ImageRef:
    """Represents an image reference"""
    link_id: str
    href: str
    name: str


@dataclass
class IDMLDocument:
    """Represents a parsed IDML document"""
    path: Path
    stories: Dict[str, List[TextContent]] = field(default_factory=dict)
    tables: List[Table] = field(default_factory=list)
    images: List[ImageRef] = field(default_factory=list)
    spreads: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def all_text(self) -> str:
        """Get all text content combined"""
        texts = []
        for story_texts in self.stories.values():
            for tc in story_texts:
                texts.append(tc.text)
        return "\n".join(texts)

    def find_text_by_style(self, style_pattern: str) -> List[TextContent]:
        """Find text content matching a style pattern"""
        pattern = re.compile(style_pattern, re.IGNORECASE)
        results = []
        for story_texts in self.stories.values():
            for tc in story_texts:
                if pattern.search(tc.style) or pattern.search(tc.paragraph_style):
                    results.append(tc)
        return results


class IDMLParser:
    """Parser for IDML files"""

    def __init__(self, idml_path: Path):
        self.idml_path = Path(idml_path)
        self.document = IDMLDocument(path=self.idml_path)
        self._zip = None

    def parse(self) -> IDMLDocument:
        """Parse the IDML file and return structured document"""
        if not self.idml_path.exists():
            raise FileNotFoundError(f"IDML file not found: {self.idml_path}")

        if not zipfile.is_zipfile(self.idml_path):
            raise ValueError(f"Not a valid IDML/ZIP file: {self.idml_path}")

        with zipfile.ZipFile(self.idml_path, 'r') as zf:
            self._zip = zf
            self._parse_designmap(zf)
            self._parse_stories(zf)
            self._parse_spreads(zf)
            self._parse_resources(zf)

        return self.document

    def _parse_designmap(self, zf: zipfile.ZipFile):
        """Parse designmap.xml for document structure"""
        try:
            with zf.open('designmap.xml') as f:
                tree = ET.parse(f)
                root = tree.getroot()

                # Extract document metadata
                self.document.metadata['name'] = self.idml_path.stem

                # Find story references
                for story_src in root.findall('.//idPkg:Story', IDML_NS):
                    src = story_src.get('src', '')
                    if src:
                        self.document.spreads.append(src)
        except Exception as e:
            logger.warning(f"Could not parse designmap.xml: {e}")

    def _parse_stories(self, zf: zipfile.ZipFile):
        """Parse all story XML files for text content"""
        story_files = [f for f in zf.namelist() if f.startswith('Stories/') and f.endswith('.xml')]

        for story_file in story_files:
            try:
                story_id = Path(story_file).stem
                self.document.stories[story_id] = []

                with zf.open(story_file) as f:
                    tree = ET.parse(f)
                    root = tree.getroot()

                    # Extract text from Content elements
                    position = 0
                    for elem in root.iter():
                        if elem.tag.endswith('Content') and elem.text:
                            text = elem.text.strip()
                            if text:
                                # Get style information from parent elements
                                para_style = self._get_parent_attr(elem, 'AppliedParagraphStyle', root)
                                char_style = self._get_parent_attr(elem, 'AppliedCharacterStyle', root)

                                tc = TextContent(
                                    text=text,
                                    style=para_style or char_style or "",
                                    paragraph_style=para_style or "",
                                    character_style=char_style or "",
                                    position=position
                                )
                                self.document.stories[story_id].append(tc)
                                position += 1

                        # Parse tables within stories
                        if elem.tag.endswith('Table'):
                            table = self._parse_table_element(elem)
                            if table.cells:
                                self.document.tables.append(table)

            except Exception as e:
                logger.warning(f"Could not parse story {story_file}: {e}")

    def _parse_table_element(self, table_elem: ET.Element) -> Table:
        """Parse a Table XML element"""
        table = Table()

        # Get table dimensions
        table.rows = int(table_elem.get('BodyRowCount', 0)) + int(table_elem.get('HeaderRowCount', 0))
        table.cols = int(table_elem.get('ColumnCount', 0))
        table.header_rows = int(table_elem.get('HeaderRowCount', 0))

        # Parse cells
        for cell_elem in table_elem.iter():
            if cell_elem.tag.endswith('Cell'):
                row = int(cell_elem.get('RowIndex', 0))
                col = int(cell_elem.get('ColumnIndex', 0))
                row_span = int(cell_elem.get('RowSpan', 1))
                col_span = int(cell_elem.get('ColumnSpan', 1))

                # Get cell content
                content_parts = []
                for content_elem in cell_elem.iter():
                    if content_elem.tag.endswith('Content') and content_elem.text:
                        content_parts.append(content_elem.text.strip())

                cell = TableCell(
                    row=row,
                    col=col,
                    content=" ".join(content_parts),
                    row_span=row_span,
                    col_span=col_span
                )
                table.cells.append(cell)

        return table

    def _parse_spreads(self, zf: zipfile.ZipFile):
        """Parse spread files for layout information"""
        spread_files = [f for f in zf.namelist() if f.startswith('Spreads/') and f.endswith('.xml')]

        for spread_file in spread_files:
            try:
                with zf.open(spread_file) as f:
                    tree = ET.parse(f)
                    root = tree.getroot()

                    # Extract image references from spreads
                    for elem in root.iter():
                        if elem.tag.endswith('Link'):
                            link_id = elem.get('Self', '')
                            href = elem.get('LinkResourceURI', '')
                            if href:
                                name = Path(href).name if href else ''
                                self.document.images.append(ImageRef(
                                    link_id=link_id,
                                    href=href,
                                    name=name
                                ))
            except Exception as e:
                logger.warning(f"Could not parse spread {spread_file}: {e}")

    def _parse_resources(self, zf: zipfile.ZipFile):
        """Parse resource files (fonts, colors, styles)"""
        # Parse Resources/Graphic.xml for colors/gradients
        # Parse Resources/Fonts.xml for font information
        # These are optional and used for style information
        pass

    def _get_parent_attr(self, elem: ET.Element, attr_name: str, root: ET.Element) -> Optional[str]:
        """Get attribute from element or its parents"""
        # Simple implementation - in real parser would traverse tree
        return elem.get(attr_name, '')

    def list_contents(self) -> List[str]:
        """List all files in the IDML archive"""
        with zipfile.ZipFile(self.idml_path, 'r') as zf:
            return zf.namelist()


def parse_idml(idml_path: Path) -> IDMLDocument:
    """Convenience function to parse an IDML file"""
    parser = IDMLParser(idml_path)
    return parser.parse()


def extract_raw_text(idml_path: Path) -> str:
    """Extract all raw text from an IDML file"""
    doc = parse_idml(idml_path)
    return doc.all_text


def extract_tables(idml_path: Path) -> List[Table]:
    """Extract all tables from an IDML file"""
    doc = parse_idml(idml_path)
    return doc.tables
