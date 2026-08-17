"""
Application configuration module.

This module centralizes and validates the configuration values used by the
Private Doc Agent application. Environment-dependent values are loaded from
the .env file so they can be changed without modifying source code.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


SUPPORTED_VECTOR_DISTANCE_METRICS = {"cosine", "l2", "ip"}


def _get_positive_int(variable_name: str, default: int) -> int:
    """Loads a strictly positive integer from the environment."""
    raw_value = os.getenv(variable_name, str(default))
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{variable_name} must be an integer") from exc
    if value <= 0:
        raise ValueError(f"{variable_name} must be greater than zero")
    return value


def _get_non_negative_int(variable_name: str, default: int) -> int:
    """Loads a non-negative integer from the environment."""
    raw_value = os.getenv(variable_name, str(default))
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{variable_name} must be an integer") from exc
    if value < 0:
        raise ValueError(f"{variable_name} cannot be negative")
    return value


def _get_optional_float(variable_name: str) -> float | None:
    """Loads an optional floating-point value; blank means disabled."""
    raw_value = os.getenv(variable_name, "").strip()
    if not raw_value:
        return None
    try:
        return float(raw_value)
    except ValueError as exc:
        raise ValueError(f"{variable_name} must be a number or blank") from exc


def _get_bool(variable_name: str, default: bool = False) -> bool:
    """Loads a boolean written as true or false from the environment."""
    raw_value = os.getenv(variable_name, str(default)).strip().lower()
    if raw_value not in {"true", "false"}:
        raise ValueError(f"{variable_name} must be true or false")
    return raw_value == "true"


def _get_required_text(variable_name: str, default: str) -> str:
    """Loads a non-blank text value from the environment."""
    value = os.getenv(variable_name, default).strip()
    if not value:
        raise ValueError(f"{variable_name} cannot be blank")
    return value


# Application metadata
APP_NAME = "private-doc-agent"
APP_VERSION = "0.10.0"
API_KEY = os.getenv("API_KEY", "").strip() or None
API_KEY_PROTECT_ALL = _get_bool("API_KEY_PROTECT_ALL", False)


# Base project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
INVALID_DIR = DATA_DIR / "invalid"
CHROMA_DIR = DATA_DIR / "chroma"


# Supported document types for this version
SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}


# Local LLM configuration
OLLAMA_BASE_URL = _get_required_text(
    "OLLAMA_BASE_URL", "http://localhost:11434"
)
OLLAMA_MODEL = _get_required_text("OLLAMA_MODEL", "qwen3.5:4b")
OLLAMA_EMBEDDING_MODEL = _get_required_text(
    "OLLAMA_EMBEDDING_MODEL", "nomic-embed-text-v2-moe:latest"
)
EMBEDDING_BATCH_SIZE = _get_positive_int("EMBEDDING_BATCH_SIZE", 32)
OLLAMA_REQUEST_TIMEOUT_SECONDS = _get_positive_int(
    "OLLAMA_REQUEST_TIMEOUT_SECONDS", 120
)
OLLAMA_MAX_RETRIES = _get_non_negative_int("OLLAMA_MAX_RETRIES", 2)


# Document chunking configuration for the RAG pipeline
CHUNK_SIZE = _get_positive_int("CHUNK_SIZE", 1000)
CHUNK_OVERLAP = _get_non_negative_int("CHUNK_OVERLAP", 200)
if CHUNK_OVERLAP >= CHUNK_SIZE:
    raise ValueError("CHUNK_OVERLAP must be smaller than CHUNK_SIZE")


# Local vector store and retrieval configuration
CHROMA_COLLECTION_NAME = _get_required_text(
    "CHROMA_COLLECTION_NAME", "private_documents"
)
VECTOR_DISTANCE_METRIC = os.getenv(
    "VECTOR_DISTANCE_METRIC", "cosine"
).strip().lower()
if VECTOR_DISTANCE_METRIC not in SUPPORTED_VECTOR_DISTANCE_METRICS:
    supported_metrics = ", ".join(sorted(SUPPORTED_VECTOR_DISTANCE_METRICS))
    raise ValueError(
        f"VECTOR_DISTANCE_METRIC must be one of: {supported_metrics}"
    )
VECTOR_SEARCH_TOP_K = _get_positive_int("VECTOR_SEARCH_TOP_K", 5)
VECTOR_MIN_RELEVANCE_SCORE = _get_optional_float(
    "VECTOR_MIN_RELEVANCE_SCORE"
)


# Logging and controlled diagnostics configuration
LOG_SENSITIVE_CONTENT = _get_bool("LOG_SENSITIVE_CONTENT", False)
DETAILED_TRACE_ENABLED = _get_bool("DETAILED_TRACE_ENABLED", False)
