"""Base class for document parsers."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path


class DocumentParser(ABC):
    """Abstract base class for document parsers."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize parser with optional configuration.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}

    @abstractmethod
    def parse(self, file_path: Path) -> str:
        """Parse document and return text content.

        Args:
            file_path: Path to document file

        Returns:
            Extracted text content

        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file format is not supported
        """
        pass

    @abstractmethod
    def supports(self, file_path: Path) -> bool:
        """Check if parser supports the file type.

        Args:
            file_path: Path to document file

        Returns:
            True if parser supports this file type
        """
        pass

    def parse_with_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Parse document and return content with metadata.

        Args:
            file_path: Path to document file

        Returns:
            Dictionary containing 'content' and 'metadata'
        """
        content = self.parse(file_path)
        metadata = self._extract_metadata(file_path)

        return {
            "content": content,
            "metadata": metadata
        }

    def _extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from file.

        Args:
            file_path: Path to document file

        Returns:
            Dictionary containing file metadata
        """
        return {
            "source": str(file_path),
            "filename": file_path.name,
            "extension": file_path.suffix
        }
