"""
Semantic document retrieval service.

This module coordinates query embedding generation and local vector search.
It validates user questions, applies configurable result limits and relevance
thresholds, and returns source-aware matches for the future RAG layer.

Logging strategy:
- Logs result limits and returned match counts.
- Does not log questions, document content, or embedding vectors.
"""

import logging

from app.config import VECTOR_MIN_RELEVANCE_SCORE, VECTOR_SEARCH_TOP_K
from app.logging_config import setup_logging
from app.services.embedding_service import EmbeddingServiceError, embed_query
from app.services.vector_store import VectorStoreError, query_chunks


logger = logging.getLogger(__name__)


class RetrievalServiceError(Exception):
    """Raised when semantic document retrieval cannot be completed."""

    pass


def retrieve_relevant_chunks(question: str, top_k: int | None = None) -> dict:
    """
    Retrieves the document chunks most closely related to a question.

    Args:
        question: Natural-language question to search for.
        top_k: Optional maximum result count; configuration is used if omitted.

    Returns:
        The normalized question and ranked matches with relevance scores.

    Raises:
        ValueError: If the question or result limit is invalid.
        RetrievalServiceError: If embedding generation or vector search fails.
    """
    setup_logging()

    if not isinstance(question, str) or not question.strip():
        raise ValueError("Question cannot be empty.")

    resolved_top_k = VECTOR_SEARCH_TOP_K if top_k is None else top_k

    if (
        not isinstance(resolved_top_k, int)
        or isinstance(resolved_top_k, bool)
        or resolved_top_k <= 0
    ):
        raise ValueError("top_k must be a positive integer.")

    normalized_question = question.strip()

    try:
        query_embedding = embed_query(normalized_question)
        raw_matches = query_chunks(
            query_embedding=query_embedding,
            top_k=resolved_top_k,
        )
    except (EmbeddingServiceError, VectorStoreError) as error:
        logger.error(
            "Semantic retrieval failed. top_k=%s error=%s",
            resolved_top_k,
            error,
        )
        raise RetrievalServiceError(
            f"Unable to retrieve relevant chunks: {error}"
        ) from error

    matches = [
        {
            "filename": match["filename"],
            "chunk_id": match["chunk_id"],
            "content": match["content"],
            "start_char": match["start_char"],
            "end_char": match["end_char"],
            "distance": match["distance"],
            "relevance_score": match["relevance_score"],
        }
        for match in raw_matches
        if VECTOR_MIN_RELEVANCE_SCORE is None
        or match["relevance_score"] >= VECTOR_MIN_RELEVANCE_SCORE
    ]

    logger.info(
        "Semantic retrieval completed. requested_results=%s returned_results=%s relevance_threshold=%s",
        resolved_top_k,
        len(matches),
        VECTOR_MIN_RELEVANCE_SCORE,
    )

    return {"question": normalized_question, "matches": matches}
