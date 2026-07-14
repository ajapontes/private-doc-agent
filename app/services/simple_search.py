from app.services.document_loader import list_documents, read_document


def search_keyword(query: str) -> list[dict]:
    """
    Searches a keyword or phrase across all supported documents.
    Returns matching lines with line numbers.
    """
    if not query or not query.strip():
        return []

    query_normalized = query.strip().lower()
    results = []

    for document in list_documents():
        filename = document["filename"]
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

    return results