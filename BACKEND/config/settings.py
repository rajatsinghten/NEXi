"""
Configuration settings for Nexi assistant.
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent  # BACKEND directory
DATA_DIR = BASE_DIR / "PDF"  # PDF folder inside BACKEND
JSON_DATA_DIR = BASE_DIR / "JSON"  # JSON folder inside BACKEND
STORAGE_DIR = BASE_DIR / "storage"  # storage inside BACKEND
SESSION_DIR = BASE_DIR / "session_data"  # session_data inside BACKEND

# RAG Configuration
PDF_RAG_CONFIG = {
    "data_path": str(DATA_DIR),
    "persist_dir": str(STORAGE_DIR / "chroma_langchain"),
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "chunk_size": 1000,
    "chunk_overlap": 100,
    "reranker_model": "cross-encoder/ms-marco-MiniLM-L-6-v2",
}

JSON_RAG_CONFIG = {
    "data_path": str(JSON_DATA_DIR),
    "persist_dir": str(STORAGE_DIR / "chroma_json"),
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
}

# LiveKit Configuration
LIVEKIT_CONFIG = {
    "deepgram_model": "nova-2",
    "deepgram_language": "en-US",
    "gemini_model": "gemini-2.5-flash",
    "cartesia_model": "sonic-english",
    "cartesia_voice": "a0e99841-438c-4a64-b679-ae501e7d6091",
}

# Session Management
SESSION_CONFIG = {
    "timeout_seconds": 30,
    "cleanup_interval": 10,
    "max_context_messages": 3,
}

# API Keys (from environment)
API_KEYS = {
    "google": os.getenv("GOOGLE_API_KEY"),
    "cartesia": os.getenv("CARTESIA_API_KEY"),
}

# Ensure directories exist
for directory in [STORAGE_DIR, SESSION_DIR]:
    directory.mkdir(parents=True, exist_ok=True)