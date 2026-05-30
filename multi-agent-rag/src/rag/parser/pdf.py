"""PDF document parser."""
from pathlib import Path
from typing import Dict, Any, Optional
from .base import DocumentParser


class PDFParser(DocumentParser):
    """Parser for PDF documents."""

    SUPPORTED_EXTENSIONS = {'.pdf'}

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize PDF parser.

        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)

    def supports(self, file_path: Path) -> bool:
        """Check if parser supports the file type.

        Args:
            file_path: Path to document file

        Returns:
            True if file has .pdf extension
        """
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def parse(self, file_path: Path) -> str:
        """Parse PDF document and return text content.

        Args:
            file_path: Path to PDF file

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

        try:
            import pypdf
        except ImportError:
            raise ImportError(
                "pypdf is required for PDF parsing. "
                "Install it with: pip install pypdf"
            )

        text_content = []
        with open(file_path, 'rb') as f:
            pdf_reader = pypdf.PdfReader(f)
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)

        return '\n\n'.join(text_content)
