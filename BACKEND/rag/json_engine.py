"""
JSON RAG Engine (cleaned and refactored from rag_json_engine.py).
"""

import os
import json
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Any
from pathlib import Path

from langchain_community.docstore.document import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from ..config.settings import JSON_RAG_CONFIG

# Global vector store
json_vector_store: Chroma = None


def flatten_json(data, parent_key="") -> List[str]:
    """Recursively flatten JSON into readable strings for embeddings."""
    docs = []

    if isinstance(data, dict):
        # Special handling: faculty / staff profiles
        if "name" in data and ("title" in data or "department" in data or "phd" in data):
            name = data.get("name", "")
            title = data.get("title", "")
            dept = data.get("department", "")
            phd = data.get("phd", "")
            email = data.get("email", "")
            text = f"{name} is a {title} in the {dept} department. {name} holds {phd}. Email: {email}."
            docs.append(text)

        # Special handling: holidays/events
        elif ("event" in data or "name" in data) and ("date" in data or "from_date" in data):
            name = data.get("event") or data.get("name")
            date = data.get("date") or f"{data.get('from_date')} to {data.get('to_date')}"
            text = f"{name} is on {date}."
            docs.append(text)

        else:
            # generic recursion
            for k, v in data.items():
                docs.extend(flatten_json(v, parent_key + "." + k if parent_key else k))

    elif isinstance(data, list):
        for item in data:
            docs.extend(flatten_json(item, parent_key))

    else:
        docs.append(str(data))

    return docs


def load_json_documents(json_dir: str) -> List[Document]:
    """Load and flatten JSON files into Documents for embeddings."""
    docs: List[Document] = []
    
    for fname in os.listdir(json_dir):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(json_dir, fname)
        
        with open(fpath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f"[WARN] Skipping {fname}: {e}")
                continue

        flattened = flatten_json(data)
        for i, text in enumerate(flattened):
            docs.append(Document(
                page_content=text, 
                metadata={"source": fname, "item_index": i}
            ))

    return docs


async def initialize_json_rag():
    """Initialize embeddings + Chroma vector store with JSON documents."""
    global json_vector_store
    
    json_dir = JSON_RAG_CONFIG["data_path"]
    persist_dir = JSON_RAG_CONFIG["persist_dir"]
    embedding_model = JSON_RAG_CONFIG["embedding_model"]
    
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)

    # Create persist directory
    Path(persist_dir).mkdir(parents=True, exist_ok=True)
    
    docs = load_json_documents(json_dir)
    if not docs:
        raise RuntimeError(f"No JSON docs found in {json_dir}")

    # Create Chroma store
    json_vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=persist_dir,
    )
    print(f"[INFO] Loaded {len(docs)} JSON docs into vector store at {persist_dir}")


async def get_json_rag_answer_async(
    query: str,
    k: int = 10,
    top_n: int = 5,
    include_embeddings: bool = False,
) -> Dict[str, Any]:
    """Query the JSON vector store and return structured JSON output."""
    global json_vector_store
    if json_vector_store is None:
        raise RuntimeError("JSON RAG engine not initialized. Call initialize_json_rag() first.")

    # Retrieve top-k
    def _retrieve():
        retriever = json_vector_store.as_retriever(search_kwargs={"k": k})
        return retriever.get_relevant_documents(query)

    docs = await asyncio.to_thread(_retrieve)

    results: List[Dict[str, Any]] = []
    for doc in docs[:top_n]:
        result_item = {
            "source": doc.metadata.get("source", "json"),
            "page_content": doc.page_content,
            "metadata": doc.metadata,
        }
        
        # Add embeddings if requested
        if include_embeddings and hasattr(doc, 'embeddings'):
            result_item["embeddings"] = doc.embeddings
            
        results.append(result_item)

    combined_context = "\n\n".join(r["page_content"] for r in results)

    return {
        "query": query,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "results": results,
        "combined_context": combined_context,
        "sources": [r["source"] for r in results],
    }