"""Dependency health checks for the local Ollama and ChromaDB services."""

import requests

from app.config import OLLAMA_BASE_URL, OLLAMA_REQUEST_TIMEOUT_SECONDS
from app.services.vector_store import VectorStoreError, count_stored_chunks


def check_dependencies() -> dict:
    """Returns sanitized availability metadata without exposing private data."""
    components = {}

    try:
        response = requests.get(
            f"{OLLAMA_BASE_URL}/api/tags",
            timeout=min(OLLAMA_REQUEST_TIMEOUT_SECONDS, 5),
        )
        response.raise_for_status()
        components["ollama"] = {"status": "ok"}
    except requests.exceptions.RequestException as error:
        components["ollama"] = {
            "status": "unavailable",
            "error_type": type(error).__name__,
        }

    try:
        components["vector_store"] = {
            "status": "ok",
            "stored_chunks": count_stored_chunks(),
        }
    except VectorStoreError as error:
        components["vector_store"] = {
            "status": "unavailable",
            "error_type": type(error).__name__,
        }

    return components
