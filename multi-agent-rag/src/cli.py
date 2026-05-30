"""CLI for Multi-Agent RAG system."""
import asyncio
import click
from pathlib import Path
from src.config import get_settings
from src.infrastructure.embedding import EmbeddingProvider
from src.infrastructure.vector_store import VectorStore
from src.infrastructure.llm_client import LLMClient
from src.infrastructure.message_bus import MessageBus
from src.rag.parser import MarkdownParser, PDFParser
from src.rag.chunker import Chunker
from src.rag.ingest import IngestPipeline
from src.agents.retriever import RetrieverAgent
from src.agents.analyzer import AnalyzerAgent
from src.agents.orchestrator import OrchestratorAgent
from src.infrastructure.message import Message


@click.group()
def cli():
    """Multi-Agent RAG CLI"""
    pass


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--collection', default='documents', help='Collection name')
def ingest(path, collection):
    """Ingest documents from file or directory"""
    asyncio.run(_ingest(path, collection))


async def _ingest(path, collection):
    settings = get_settings()
    path_obj = Path(path)

    embedding = EmbeddingProvider(
        model_name=settings.embedding_model,
        device=settings.embedding_device
    )
    vector_store = VectorStore(
        collection_name=collection,
        persist_directory=str(settings.chroma_persist_dir)
    )

    md_parser = MarkdownParser()
    pdf_parser = PDFParser()
    chunker = Chunker(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap
    )

    if path_obj.is_file():
        parser = pdf_parser if path_obj.suffix == '.pdf' else md_parser
        pipeline = IngestPipeline(parser, chunker, embedding, vector_store)
        await pipeline.ingest_document(path_obj)
        click.echo(f"Ingested: {path_obj}")
    else:
        pipeline = IngestPipeline(md_parser, chunker, embedding, vector_store)
        result = await pipeline.ingest_directory(path_obj)
        click.echo(f"Ingested {result['processed']} documents")


@cli.command()
@click.argument('query')
@click.option('--collection', default='documents', help='Collection name')
def ask(query, collection):
    """Ask a question"""
    asyncio.run(_ask(query, collection))


async def _ask(query, collection):
    settings = get_settings()

    embedding = EmbeddingProvider(
        model_name=settings.embedding_model,
        device=settings.embedding_device
    )
    vector_store = VectorStore(
        collection_name=collection,
        persist_directory=str(settings.chroma_persist_dir)
    )
    llm = LLMClient(
        api_key=settings.anthropic_api_key,
        model=settings.llm_model,
        max_tokens=settings.llm_max_tokens,
        temperature=settings.llm_temperature
    )

    bus = MessageBus()
    retriever = RetrieverAgent("retriever", {
        "embedding": embedding,
        "vector_store": vector_store,
        "top_k": settings.top_k
    })
    analyzer = AnalyzerAgent("analyzer", {"llm": llm})
    orchestrator = OrchestratorAgent("orchestrator", {
        "retriever": retriever,
        "analyzer": analyzer
    })

    bus.register_agent(retriever)
    bus.register_agent(analyzer)
    bus.register_agent(orchestrator)

    msg = Message.create_request(
        from_agent="cli",
        to_agent="orchestrator",
        intent="query",
        payload={"query": query}
    )

    response = await orchestrator.process(msg)
    click.echo(response.payload.get("answer", "No answer"))


@cli.group()
def collections():
    """Manage collections"""
    pass


@collections.command('list')
def list_collections():
    """List all collections"""
    settings = get_settings()
    client = __import__('chromadb').PersistentClient(
        path=str(settings.chroma_persist_dir)
    )
    colls = client.list_collections()
    for c in colls:
        click.echo(f"{c.name}: {c.count()} documents")


@collections.command('delete')
@click.argument('name')
def delete_collection(name):
    """Delete a collection"""
    settings = get_settings()
    client = __import__('chromadb').PersistentClient(
        path=str(settings.chroma_persist_dir)
    )
    client.delete_collection(name)
    click.echo(f"Deleted collection: {name}")


if __name__ == '__main__':
    cli()
