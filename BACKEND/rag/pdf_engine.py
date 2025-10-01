"""
PDF RAG Engine (cleaned and refactored from rag_engine.py).
"""

from pathlib import Path
import asyncio
from typing import Dict, Any
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from sentence_transformers import CrossEncoder

from ..config.settings import PDF_RAG_CONFIG

# Globals
vector_store = None
reranker = None


def initialize_pdf_rag_blocking():
    """
    Initializes the PDF RAG pipeline only once.
    Loads persisted ChromaDB if it exists, otherwise builds it.
    """
    global vector_store, reranker

    data_path = Path(PDF_RAG_CONFIG["data_path"])
    persist_dir = Path(PDF_RAG_CONFIG["persist_dir"])
    persist_dir.mkdir(parents=True, exist_ok=True)

    embeddings = HuggingFaceEmbeddings(
        model_name=PDF_RAG_CONFIG["embedding_model"]
    )

    # If DB exists, just load it
    if persist_dir.exists() and any(persist_dir.iterdir()):
        print("✅ Loading existing PDF ChromaDB...")
        vector_store = Chroma(
            persist_directory=str(persist_dir),
            embedding_function=embeddings
        )
    else:
        print("⚡ Creating new PDF ChromaDB (first time only)...")
        loader = DirectoryLoader(data_path, glob="**/*.pdf", loader_cls=PyPDFLoader)
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=PDF_RAG_CONFIG["chunk_size"],
            chunk_overlap=PDF_RAG_CONFIG["chunk_overlap"],
            add_start_index=True
        )
        texts = text_splitter.split_documents(documents)

        vector_store = Chroma.from_documents(
            documents=texts,
            embedding=embeddings,
            persist_directory=str(persist_dir)
        )

    # Simple reranker (cross-encoder, small model for speed)
    reranker = CrossEncoder(PDF_RAG_CONFIG["reranker_model"])
    print("✅ PDF RAG engine initialized!")


async def initialize_pdf_rag():
    """Async wrapper to initialize PDF RAG engine in a non-blocking way."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, initialize_pdf_rag_blocking)


async def get_pdf_rag_answer_async(query: str, k: int = 5, top_n: int = 2) -> Dict[str, Any]:
    """
    Retrieve documents for a query, rerank them, and return context + sources.
    """
    global vector_store, reranker
    if not vector_store:
        raise RuntimeError("PDF RAG engine not initialized. Call initialize_pdf_rag() first.")

    def _retrieve():
        retriever = vector_store.as_retriever(search_kwargs={"k": k})
        return retriever.get_relevant_documents(query)

    docs = await asyncio.to_thread(_retrieve)

    if not docs:
        return {"context": "", "sources": []}

    # Rerank docs (blocking)
    if reranker:
        pairs = [(query, d.page_content) for d in docs]

        # reranker.predict is synchronous and can be expensive; run in thread
        scores = await asyncio.to_thread(reranker.predict, pairs)
        reranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
        top_docs = reranked[:top_n]
        final_context = "\n\n".join(d.page_content for d, _ in top_docs)
        sources = [d.metadata.get("source", "unknown") for d, _ in top_docs]
    else:
        final_context = "\n\n".join(d.page_content for d in docs[:top_n])
        sources = [d.metadata.get("source", "unknown") for d in docs[:top_n]]

    return {"context": final_context, "sources": sources}