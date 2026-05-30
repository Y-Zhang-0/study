"""Tests for document parsers."""
import pytest
from pathlib import Path
from src.rag.parser.markdown import MarkdownParser
from src.rag.parser.pdf import PDFParser


class TestMarkdownParser:
    """Test cases for MarkdownParser."""

    @pytest.fixture
    def parser(self):
        """Create MarkdownParser instance."""
        return MarkdownParser()

    @pytest.fixture
    def sample_md_file(self, tmp_path):
        """Create a sample markdown file."""
        md_file = tmp_path / "test.md"
        content = """# Test Document

This is a **test** document with *markdown* formatting.

## Section 1
- Item 1
- Item 2

## Section 2
Some text here.
"""
        md_file.write_text(content, encoding='utf-8')
        return md_file

    def test_supports_markdown_files(self, parser):
        """Test that parser supports .md files."""
        assert parser.supports(Path("test.md"))
        assert parser.supports(Path("test.markdown"))
        assert not parser.supports(Path("test.txt"))
        assert not parser.supports(Path("test.pdf"))

    def test_parse_markdown_file(self, parser, sample_md_file):
        """Test parsing markdown file."""
        content = parser.parse(sample_md_file)
        assert "Test Document" in content
        assert "Section 1" in content
        assert "Item 1" in content

    def test_parse_nonexistent_file(self, parser):
        """Test parsing nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            parser.parse(Path("nonexistent.md"))

    def test_parse_with_metadata(self, parser, sample_md_file):
        """Test parsing with metadata."""
        result = parser.parse_with_metadata(sample_md_file)
        assert "content" in result
        assert "metadata" in result
        assert result["metadata"]["filename"] == "test.md"
        assert result["metadata"]["extension"] == ".md"


class TestPDFParser:
    """Test cases for PDFParser."""

    @pytest.fixture
    def parser(self):
        """Create PDFParser instance."""
        return PDFParser()

    def test_supports_pdf_files(self, parser):
        """Test that parser supports .pdf files."""
        assert parser.supports(Path("test.pdf"))
        assert not parser.supports(Path("test.txt"))
        assert not parser.supports(Path("test.md"))

    def test_parse_nonexistent_file(self, parser):
        """Test parsing nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            parser.parse(Path("nonexistent.pdf"))
