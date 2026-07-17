"""
Simple keyword search service.

This module provides deterministic keyword search across all supported
local documents.

It does not use AI, embeddings, vector search, or semantic search.
It only performs case-insensitive keyword or phrase matching over the
document lines.

Logging strategy:
- Logs when a keyword search starts and finishes.
- Logs the number of documents scanned.
- Logs the number of matches found.
- Does not log full document content.
"""

import logging

from app.services.document_loader import list_documents, read_document


logger = logging.getLogger(__name__)


def search_keyword(query: str) -> list[dict]:
    """
    Searches a keyword or phrase across all supported local documents.

    The search is case-insensitive and returns the matching line number
    and line content for each match.

    Args:
        query: Keyword or phrase to search across supported documents.

    Returns:
        A list of dictionaries with search results, including filename,
        line number and matching line.
    """
    logger.info("Keyword search requested. query=%s", query)

    if not query or not query.strip():
        logger.warning("Keyword search skipped because query is empty.")
        return []

    query_normalized = query.strip().lower()
    results = []

    documents = list_documents()

    logger.info(
        "Keyword search started. query=%s documents_to_scan=%s",
        query,
        len(documents),
    )

    for document in documents:
        filename = document["filename"]

        logger.info("Scanning document for keyword. filename=%s", filename)

        content = read_document(filename)

        for line_number, line in enumerate(content.splitlines(), start=1):
            if query_normalized in line.lower():
                results.append(
                    {
                        "filename": filename,
                        "line_number": line_number,
                        "line": line.strip(),
                    }
                )

    logger.info(
        "Keyword search completed. query=%s matches=%s",
        query,
        len(results),
    )

    return results