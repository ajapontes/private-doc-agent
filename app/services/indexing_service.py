"""
Document indexing orchestration service.

This module connects document loading, chunking, local embedding generation,
and ChromaDB persistence into one indexing workflow. It supports indexing one
document or every supported document from ``data/input``.

Embeddings are generated in configurable batches to keep memory and Ollama
request sizes bounded when representative, longer documents are introduced.
Existing records are deleted only after all new embeddings are ready, so an
embedding failure does not remove the last successful index for a document.

Logging strategy:
- Logs filenames, batch counts, chunk counts, and vector dimensions.
- Does not log document content or full embedding vectors.
"""

import logging

from app.config import EMBEDDING_BATCH_SIZE, OLLAMA_EMBEDDING_MODEL
from app.services.document_chunker import chunk_document
from app.services.document_loader import (
    list_documents,
    list_unsupported_documents,
    move_document_to_invalid,
)
from app.services.embedding_service import EmbeddingServiceError, embed_documents
from app.services.vector_store import (
    VectorStoreError,
    delete_document_chunks,
    upsert_chunks,
)


logger = logging.getLogger(__name__)


class IndexingServiceError(Exception):
    """Raised when a document cannot complete the local indexing workflow."""

    pass


class InvalidDocumentError(IndexingServiceError):
    """Raised when a document itself has no content that can be indexed."""

    pass


def _embed_chunks_in_batches(chunks: list[dict]) -> list[list[float]]:
    """
    Generates embeddings for document chunks in bounded local batches.

    Args:
        chunks: Chunk dictionaries produced by the document chunker.

    Returns:
        Embeddings in the same order as the supplied chunks.

    Raises:
        IndexingServiceError: If the configured batch size is invalid.
        EmbeddingServiceError: If Ollama cannot generate the embeddings.
    """
    if EMBEDDING_BATCH_SIZE <= 0:
        raise IndexingServiceError("Embedding batch size must be greater than zero.")

    embeddings = []

    for batch_start in range(0, len(chunks), EMBEDDING_BATCH_SIZE):
        batch = chunks[batch_start : batch_start + EMBEDDING_BATCH_SIZE]
        batch_number = (batch_start // EMBEDDING_BATCH_SIZE) + 1

        logger.info(
            "Generating embedding batch. batch_number=%s batch_size=%s",
            batch_number,
            len(batch),
        )

        batch_embeddings = embed_documents(
            [chunk["content"] for chunk in batch]
        )
        embeddings.extend(batch_embeddings)

    return embeddings


def index_document(filename: str) -> dict:
    """
    Indexes one supported local document.

    Args:
        filename: Name of the document located in ``data/input``.

    Returns:
        Indexing metadata including filename, chunk count, vector dimension,
        and embedding model.

    Raises:
        FileNotFoundError: If the requested document does not exist.
        ValueError: If the requested file extension is unsupported.
        IndexingServiceError: If the document is empty or an embedding/vector
            storage operation fails.
    """
    logger.info("Document indexing started. filename=%s", filename)

    try:
        chunks = chunk_document(filename)

        if not chunks:
            raise InvalidDocumentError(
                f"Document does not contain indexable text: {filename}"
            )

        embeddings = _embed_chunks_in_batches(chunks)

        delete_document_chunks(filename)
        chunks_indexed = upsert_chunks(chunks, embeddings)

    except (FileNotFoundError, ValueError):
        raise
    except IndexingServiceError:
        raise
    except (EmbeddingServiceError, VectorStoreError) as error:
        logger.error(
            "Document indexing failed. filename=%s error=%s",
            filename,
            error,
        )
        raise IndexingServiceError(
            f"Unable to index document '{filename}': {error}"
        ) from error

    result = {
        "filename": filename,
        "chunks_indexed": chunks_indexed,
        "vector_dimension": len(embeddings[0]),
        "embedding_model": OLLAMA_EMBEDDING_MODEL,
    }

    logger.info(
        "Document indexing completed. filename=%s chunks_indexed=%s vector_dimension=%s",
        filename,
        chunks_indexed,
        result["vector_dimension"],
    )

    return result


def index_all_documents() -> dict:
    """
    Indexes every supported local document from the input directory.

    Returns:
        Aggregate counts and the individual result for every document.

    Raises:
        IndexingServiceError: If no supported documents are available or an
            infrastructure failure prevents indexing from continuing.
    """
    documents = list_documents()
    unsupported_documents = list_unsupported_documents()

    if not documents and not unsupported_documents:
        raise IndexingServiceError("No supported documents are available to index.")

    results = []
    invalid_documents = []

    for document in unsupported_documents:
        filename = document["filename"]
        extension = document["extension"] or "<none>"
        error = f"Unsupported file extension: {extension}"
        logger.warning(
            "Unsupported document detected during bulk indexing. "
            "filename=%s extension=%s",
            filename,
            extension,
        )
        try:
            moved = move_document_to_invalid(filename)
            moved["error"] = error
            invalid_documents.append(moved)
        except OSError as move_error:
            logger.error(
                "Unsupported document could not be moved. filename=%s "
                "error_type=%s",
                filename,
                type(move_error).__name__,
            )
            invalid_documents.append(
                {
                    "filename": filename,
                    "error": error,
                    "move_error": str(move_error),
                }
            )

    for document in documents:
        filename = document["filename"]
        try:
            results.append(index_document(filename))
        except (ValueError, InvalidDocumentError) as error:
            logger.warning(
                "Invalid document detected during bulk indexing. "
                "filename=%s error_type=%s",
                filename,
                type(error).__name__,
            )
            try:
                moved = move_document_to_invalid(filename)
                moved["error"] = str(error)
                invalid_documents.append(moved)
            except OSError as move_error:
                logger.error(
                    "Invalid document could not be moved. filename=%s "
                    "error_type=%s",
                    filename,
                    type(move_error).__name__,
                )
                invalid_documents.append(
                    {
                        "filename": filename,
                        "error": str(error),
                        "move_error": str(move_error),
                    }
                )

    aggregate = {
        "documents_indexed": len(results),
        "chunks_indexed": sum(result["chunks_indexed"] for result in results),
        "documents": results,
        "documents_invalid": len(invalid_documents),
        "invalid_documents": invalid_documents,
    }

    logger.info(
        "All documents processed. documents_indexed=%s documents_invalid=%s "
        "chunks_indexed=%s",
        aggregate["documents_indexed"],
        aggregate["documents_invalid"],
        aggregate["chunks_indexed"],
    )

    return aggregate
