"""
Local embedding service.

This module converts document chunks and user queries into numeric vectors
through Ollama's local ``/api/embed`` endpoint. The vectors will later be
stored and compared by the RAG retrieval layer.

The configured Nomic model requires task prefixes:
- ``search_document:`` for document content.
- ``search_query:`` for questions or search requests.

Logging strategy:
- Logs the model, endpoint, task type, input count, and vector dimensions.
- Does not log source texts or generated vectors because they may represent
  private document content.
"""

import logging
from typing import Literal

import requests

from app.config import OLLAMA_BASE_URL, OLLAMA_EMBEDDING_MODEL
from app.services.ollama_transport import OllamaTransportError, post_json


logger = logging.getLogger(__name__)

DOCUMENT_PREFIX = "search_document: "
QUERY_PREFIX = "search_query: "


class EmbeddingServiceError(Exception):
    """Raised when local embedding generation cannot be completed safely."""

    pass


def _validate_texts(texts: list[str]) -> None:
    """
    Validates the texts before sending them to the embedding model.

    Args:
        texts: Text values that will be converted into embeddings.

    Raises:
        EmbeddingServiceError: If the list is empty or contains blank text.
    """
    if not texts:
        raise EmbeddingServiceError("At least one text is required.")

    if any(not isinstance(text, str) or not text.strip() for text in texts):
        raise EmbeddingServiceError("Embedding texts cannot be empty.")


def generate_embeddings(
    texts: list[str],
    task: Literal["document", "query"],
) -> list[list[float]]:
    """
    Generates local embeddings for one or more texts.

    Args:
        texts: Text values to convert into numeric vectors.
        task: ``document`` for source content or ``query`` for a question.

    Returns:
        One numeric vector for every input text, preserving input order.

    Raises:
        EmbeddingServiceError: If inputs are invalid, Ollama is unavailable,
            or Ollama returns an invalid response.
    """
    _validate_texts(texts)

    if task == "document":
        prefix = DOCUMENT_PREFIX
    elif task == "query":
        prefix = QUERY_PREFIX
    else:
        raise EmbeddingServiceError(f"Unsupported embedding task: {task}")

    endpoint = f"{OLLAMA_BASE_URL}/api/embed"
    prepared_texts = [f"{prefix}{text.strip()}" for text in texts]

    payload = {
        "model": OLLAMA_EMBEDDING_MODEL,
        "input": prepared_texts,
    }

    logger.info(
        "Sending local embedding request. model=%s endpoint=%s task=%s input_count=%s",
        OLLAMA_EMBEDDING_MODEL,
        endpoint,
        task,
        len(prepared_texts),
    )

    try:
        data = post_json(endpoint, payload, requester=requests.post)
    except OllamaTransportError as error:
        logger.error(
            "Error communicating with local embedding model. model=%s endpoint=%s error=%s",
            OLLAMA_EMBEDDING_MODEL,
            endpoint,
            error,
        )
        raise EmbeddingServiceError(
            f"Error communicating with local embedding model: {error}"
        ) from error

    embeddings = data.get("embeddings")

    if not isinstance(embeddings, list):
        raise EmbeddingServiceError(
            "Invalid response from local embedding model. Missing 'embeddings' field."
        )

    if len(embeddings) != len(texts):
        raise EmbeddingServiceError(
            "Invalid response from local embedding model. "
            "Embedding count does not match input count."
        )

    if any(not isinstance(vector, list) or not vector for vector in embeddings):
        raise EmbeddingServiceError(
            "Invalid response from local embedding model. Empty embedding vector."
        )

    vector_dimension = len(embeddings[0])

    if any(len(vector) != vector_dimension for vector in embeddings):
        raise EmbeddingServiceError(
            "Invalid response from local embedding model. Inconsistent vector dimensions."
        )

    logger.info(
        "Local embeddings generated. model=%s task=%s embedding_count=%s vector_dimension=%s",
        OLLAMA_EMBEDDING_MODEL,
        task,
        len(embeddings),
        vector_dimension,
    )

    return embeddings


def embed_documents(texts: list[str]) -> list[list[float]]:
    """Generates embeddings for document chunks using the document prefix."""
    return generate_embeddings(texts=texts, task="document")


def embed_query(query: str) -> list[float]:
    """Generates one embedding for a user question using the query prefix."""
    return generate_embeddings(texts=[query], task="query")[0]
