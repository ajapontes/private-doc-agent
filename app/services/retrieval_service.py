"""
Semantic document retrieval service.

This module coordinates query embedding generation and local vector search.
It validates user questions, converts ChromaDB cosine distances into readable
similarity scores, and returns source-aware matches for the future RAG layer.

Logging strategy:
- Logs result limits and returned match counts.
- Does not log questions, document content, or embedding vectors.
"""

import logging

from app.services.embedding_service import EmbeddingServiceError, embed_query
from app.services.vector_store import VectorStoreError, query_chunks


logger = logging.getLogger(__name__)


class RetrievalServiceError(Exception):
    """Raised when semantic document retrieval cannot be completed."""

    pass


def retrieve_relevant_chunks(question: str, top_k: int = 3) -> dict:
    """
    Retrieves the document chunks most closely related to a question.

    Args:
        question: Natural-language question to search for.
        top_k: Maximum number of matching chunks to return.

    Returns:
        The normalized question and ranked matches with cosine similarity.

    Raises:
        ValueError: If the question or result limit is invalid.
        RetrievalServiceError: If embedding generation or vector search fails.
    """
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Question cannot be empty.")

    if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k <= 0:
        raise ValueError("top_k must be a positive integer.")

    normalized_question = question.strip()

    try:
        query_embedding = embed_query(normalized_question)
        raw_matches = query_chunks(query_embedding=query_embedding, top_k=top_k)
    except (EmbeddingServiceError, VectorStoreError) as error:
        logger.error("Semantic retrieval failed. top_k=%s error=%s", top_k, error)
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
            "similarity": round(1 - match["distance"], 6),
        }
        for match in raw_matches
    ]

    logger.info(
        "Semantic retrieval completed. requested_results=%s returned_results=%s",
        top_k,
        len(matches),
    )

    return {"question": normalized_question, "matches": matches}
