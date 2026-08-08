"""
Application configuration module.

This module centralizes the main configuration values used by the
Private Doc Agent application, including application metadata,
local document paths, supported file extensions, and local LLM settings.

The values related to Ollama, embeddings, and document chunking are loaded
from environment variables defined in the .env file.
"""

from pathlib import Path
from dotenv import load_dotenv
import os


# Load environment variables from .env file
load_dotenv()


# Application metadata
APP_NAME = "private-doc-agent"
APP_VERSION = "0.5.0"


# Base project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
CHROMA_DIR = DATA_DIR / "chroma"


# Supported document types for this version
SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}

# Local LLM configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:4b")
OLLAMA_EMBEDDING_MODEL = os.getenv(
    "OLLAMA_EMBEDDING_MODEL",
    "nomic-embed-text-v2-moe:latest",
)
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))


# Document chunking configuration for the RAG pipeline
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))


# Local vector store configuration
CHROMA_COLLECTION_NAME = os.getenv(
    "CHROMA_COLLECTION_NAME",
    "private_documents",
)
