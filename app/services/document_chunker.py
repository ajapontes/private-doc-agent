"""
Document chunking service.

This module divides supported local documents into deterministic,
overlapping character-based chunks. These chunks will become the input
for the embedding and retrieval components introduced later in v0.3.0.

The service does not call an LLM, generate embeddings, or persist data.

Logging strategy:
- Logs chunking configuration and operational metadata.
- Logs the filename, source length, and number of generated chunks.
- Does not log document or chunk content.
"""

import logging

from app.config import CHUNK_OVERLAP, CHUNK_SIZE
from app.services.document_loader import read_document


logger = logging.getLogger(__name__)


def _validate_chunking_parameters(chunk_size: int, chunk_overlap: int) -> None:
    """
    Validates the parameters used to split text into chunks.

    Args:
        chunk_size: Maximum number of characters in each chunk.
        chunk_overlap: Number of characters repeated between adjacent chunks.

    Raises:
        ValueError: If the chunk size is not positive, the overlap is negative,
            or the overlap is greater than or equal to the chunk size.
    """
    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    if chunk_overlap < 0:
        raise ValueError("Chunk overlap cannot be negative.")

    if chunk_overlap >= chunk_size:
        raise ValueError("Chunk overlap must be smaller than chunk size.")


def chunk_text(
    text: str,
    filename: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[dict]:
    """
    Divides text into overlapping character-based chunks.

    Each result contains stable metadata that can later be stored with its
    embedding in the vector database. Character offsets use Python slice
    semantics: ``start_char`` is inclusive and ``end_char`` is exclusive.

    Args:
        text: Plain text to divide.
        filename: Source filename associated with every generated chunk.
        chunk_size: Maximum number of characters in each chunk.
        chunk_overlap: Number of repeated characters between adjacent chunks.

    Returns:
        A list of dictionaries containing chunk content and source metadata.

    Raises:
        ValueError: If the chunking parameters are invalid.
    """
    _validate_chunking_parameters(chunk_size, chunk_overlap)

    if not text or not text.strip():
        logger.info("Chunking skipped because document is empty. filename=%s", filename)
        return []

    logger.info(
        "Document chunking started. filename=%s document_length=%s chunk_size=%s chunk_overlap=%s",
        filename,
        len(text),
        chunk_size,
        chunk_overlap,
    )

    chunks = []
    step = chunk_size - chunk_overlap

    for start_char in range(0, len(text), step):
        end_char = min(start_char + chunk_size, len(text))

        chunks.append(
            {
                "chunk_id": len(chunks),
                "filename": filename,
                "content": text[start_char:end_char],
                "start_char": start_char,
                "end_char": end_char,
            }
        )

        if end_char == len(text):
            break

    logger.info(
        "Document chunking completed. filename=%s chunks_created=%s",
        filename,
        len(chunks),
    )

    return chunks


def chunk_document(
    filename: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[dict]:
    """
    Reads a supported local document and divides it into chunks.

    Args:
        filename: Name of the document in the configured input folder.
        chunk_size: Maximum number of characters in each chunk.
        chunk_overlap: Number of repeated characters between adjacent chunks.

    Returns:
        A list of chunks with source metadata.

    Raises:
        FileNotFoundError: If the requested document does not exist.
        ValueError: If the file type or chunking parameters are invalid.
    """
    content = read_document(filename)

    return chunk_text(
        text=content,
        filename=filename,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
