"""Tests for IDML parser module"""

import pytest
from pathlib import Path
import zipfile
import tempfile
import os

from src.idml_parser import IDMLParser, parse_idml, IDMLDocument


class TestIDMLParser:
    """Tests for IDMLParser class"""

    def test_parse_nonexistent_file(self):
        """Test parsing a file that doesn't exist"""
        parser = IDMLParser(Path("/nonexistent/file.idml"))
        with pytest.raises(FileNotFoundError):
            parser.parse()

    def test_parse_invalid_zip(self, tmp_path):
        """Test parsing an invalid ZIP file"""
        # Create a non-ZIP file
        invalid_file = tmp_path / "invalid.idml"
        invalid_file.write_text("not a zip file")

        parser = IDMLParser(invalid_file)
        with pytest.raises(ValueError):
            parser.parse()

    def test_parse_empty_idml(self, tmp_path):
        """Test parsing a minimal IDML structure"""
        # Create a minimal IDML file (ZIP with designmap.xml)
        idml_path = tmp_path / "test.idml"

        with zipfile.ZipFile(idml_path, 'w') as zf:
            # Add minimal designmap.xml
            designmap = '''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging">
</Document>'''
            zf.writestr('designmap.xml', designmap)

        parser = IDMLParser(idml_path)
        doc = parser.parse()

        assert isinstance(doc, IDMLDocument)
        assert doc.path == idml_path

    def test_list_contents(self, tmp_path):
        """Test listing IDML archive contents"""
        idml_path = tmp_path / "test.idml"

        with zipfile.ZipFile(idml_path, 'w') as zf:
            zf.writestr('designmap.xml', '<Document/>')
            zf.writestr('Stories/Story_001.xml', '<Story/>')
            zf.writestr('Spreads/Spread_001.xml', '<Spread/>')

        parser = IDMLParser(idml_path)
        contents = parser.list_contents()

        assert 'designmap.xml' in contents
        assert 'Stories/Story_001.xml' in contents
        assert 'Spreads/Spread_001.xml' in contents


class TestIDMLDocument:
    """Tests for IDMLDocument class"""

    def test_all_text_empty(self):
        """Test all_text with no stories"""
        doc = IDMLDocument(path=Path("test.idml"))
        assert doc.all_text == ""

    def test_find_text_by_style_no_match(self):
        """Test finding text with no matching style"""
        doc = IDMLDocument(path=Path("test.idml"))
        results = doc.find_text_by_style("nonexistent")
        assert results == []


class TestConvenienceFunctions:
    """Tests for convenience functions"""

    def test_parse_idml_function(self, tmp_path):
        """Test the parse_idml convenience function"""
        idml_path = tmp_path / "test.idml"

        with zipfile.ZipFile(idml_path, 'w') as zf:
            zf.writestr('designmap.xml', '<Document/>')

        doc = parse_idml(idml_path)
        assert isinstance(doc, IDMLDocument)
