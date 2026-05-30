"""Markdown document parser."""
from pathlib import Path
from typing import Dict, Any, Optional
from .base import DocumentParser


class MarkdownParser(DocumentParser):
    """Parser for Markdown documents."""

    SUPPORTED_EXTENSIONS = {'.md', '.markdown'}

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Markdown parser.

        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)

    def supports(self, file_path: Path) -> bool:
        """Check if parser supports the file type.

        Args:
            file_path: Path to document file

        Returns:
            True if file has .md or .markdown extension
        """
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def parse(self, file_path: Path) -> str:
        """Parse Markdown document and return text content.

        Args:
            file_path: Path to Markdown file

        Returns:
            Extracted text content

        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file format is not supported
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not self.supports(file_path):
            raise ValueError(f"Unsupported file type: {file_path.suffix}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return content
