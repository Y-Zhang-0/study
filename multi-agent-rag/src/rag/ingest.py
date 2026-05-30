"""Document ingestion pipeline."""
from pathlib import Path
from typing import Dict, Any, List


class IngestPipeline:
    """Pipeline for ingesting documents into vector store."""

    def __init__(self, parser, chunker, embedding, vector_store):
        self.parser = parser
        self.chunker = chunker
        self.embedding = embedding
        self.vector_store = vector_store

    async def ingest_document(self, file_path: Path) -> None:
        """Ingest a single document."""
        content = self.parser.parse(file_path)
        chunks = self.chunker.chunk(content)

        texts = [chunk["content"] for chunk in chunks]
        embeddings = await self.embedding.embed_batch(texts)

        documents = []
        for chunk, emb in zip(chunks, embeddings):
            documents.append({
                "content": chunk["content"],
                "embedding": emb,
                "metadata": {**chunk["metadata"], "source": str(file_path)}
            })

        await self.vector_store.add_documents(documents)

    async def ingest_directory(self, dir_path: Path) -> Dict[str, Any]:
        """Ingest all documents in directory."""
        files = list(dir_path.glob("*.md")) + list(dir_path.glob("*.pdf"))

        for file in files:
            await self.ingest_document(file)

        return {"processed": len(files)}
