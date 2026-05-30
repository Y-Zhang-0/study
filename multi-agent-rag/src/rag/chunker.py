"""Document chunking utilities."""
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
import re


@dataclass
class ChunkMetadata:
    """Metadata for a document chunk."""

    chunk_id: str
    source: str
    start_pos: int
    end_pos: int
    chunk_index: int
    additional_metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary.

        Returns:
            Dictionary representation of metadata
        """
        result = asdict(self)
        if self.additional_metadata:
            result.update(self.additional_metadata)
        return result


class Chunker:
    """Document chunker for splitting text into manageable chunks."""

    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        """Initialize chunker.

        Args:
            chunk_size: Maximum size of each chunk in tokens
            overlap: Number of overlapping tokens between chunks

        Raises:
            ValueError: If overlap >= chunk_size
        """
        if overlap >= chunk_size:
            raise ValueError("Overlap must be less than chunk_size")

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_by_tokens(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Split text into chunks by token count.

        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to chunks

        Returns:
            List of text chunks
        """
        if not text:
            return []

        # Simple word-based tokenization (approximation)
        words = text.split()
        chunks = []
        start_idx = 0

        while start_idx < len(words):
            end_idx = min(start_idx + self.chunk_size, len(words))
            chunk = " ".join(words[start_idx:end_idx])
            chunks.append(chunk)

            # Move forward with overlap
            if end_idx >= len(words):
                break
            start_idx = end_idx - self.overlap

        return chunks

    def chunk_by_sentences(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Split text into chunks by sentences.

        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to chunks

        Returns:
            List of text chunks
        """
        if not text:
            return []

        # Split by sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = []
        current_size = 0

        for sentence in sentences:
            sentence_words = sentence.split()
            sentence_size = len(sentence_words)

            if current_size + sentence_size > self.chunk_size and current_chunk:
                # Save current chunk
                chunks.append(" ".join(current_chunk))
                # Keep overlap sentences
                overlap_words = []
                for s in reversed(current_chunk):
                    words = s.split()
                    if len(overlap_words) + len(words) <= self.overlap:
                        overlap_words = words + overlap_words
                    else:
                        break
                current_chunk = [" ".join(overlap_words)] if overlap_words else []
                current_size = len(overlap_words)

            current_chunk.append(sentence)
            current_size += sentence_size

        # Add remaining chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def create_chunk_metadata(
        self,
        chunk_index: int,
        source: str,
        start_pos: int,
        end_pos: int,
        additional: Optional[Dict[str, Any]] = None
    ) -> ChunkMetadata:
        """Create metadata for a chunk.

        Args:
            chunk_index: Index of the chunk
            source: Source document identifier
            start_pos: Start position in original text
            end_pos: End position in original text
            additional: Additional metadata

        Returns:
            ChunkMetadata object
        """
        chunk_id = f"{source}_chunk_{chunk_index}"
        return ChunkMetadata(
            chunk_id=chunk_id,
            source=source,
            start_pos=start_pos,
            end_pos=end_pos,
            chunk_index=chunk_index,
            additional_metadata=additional
        )
