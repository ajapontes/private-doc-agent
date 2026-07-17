"""
Local document loader service.

This module contains utility functions to list and read supported local
documents from the configured input folder.

Supported extensions are defined in app/config.py.

Logging strategy:
- Logs operational events such as directory scanning and document reading.
- Logs metadata such as filename, extension, file size and character count.
- Does not log document content to avoid exposing private information.
"""

import logging

from app.config import INPUT_DIR, SUPPORTED_EXTENSIONS


logger = logging.getLogger(__name__)


def list_documents() -> list[dict]:
    """
    Lists supported documents from the local input folder.

    The function scans the configured input directory and returns metadata
    for all files with supported extensions.

    Returns:
        A list of dictionaries containing document metadata:
        filename, extension, size in bytes and relative path.
    """
    logger.info(
        "Scanning input directory for supported documents. input_dir=%s supported_extensions=%s",
        INPUT_DIR,
        sorted(SUPPORTED_EXTENSIONS),
    )

    INPUT_DIR.mkdir(parents=True, exist_ok=True)

    documents = []

    for file_path in INPUT_DIR.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            document_metadata = {
                "filename": file_path.name,
                "extension": file_path.suffix.lower(),
                "size_bytes": file_path.stat().st_size,
                "path": str(file_path.relative_to(INPUT_DIR.parent.parent)),
            }

            documents.append(document_metadata)

            logger.info(
                "Supported document found. filename=%s extension=%s size_bytes=%s",
                document_metadata["filename"],
                document_metadata["extension"],
                document_metadata["size_bytes"],
            )

    logger.info("Document scan completed. count=%s", len(documents))

    return documents


def read_document(filename: str) -> str:
    """
    Reads a supported local document by filename.

    Args:
        filename: Name of the document located in the configured input folder.

    Returns:
        The document content as plain text.

    Raises:
        FileNotFoundError: If the document does not exist.
        ValueError: If the document extension is not supported.
    """
    logger.info("Reading document requested. filename=%s", filename)

    file_path = INPUT_DIR / filename

    if not file_path.exists():
        logger.warning("Document not found. filename=%s path=%s", filename, file_path)
        raise FileNotFoundError(f"Document not found: {filename}")

    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        logger.warning(
            "Unsupported document extension. filename=%s extension=%s",
            filename,
            file_path.suffix.lower(),
        )
        raise ValueError(f"Unsupported file extension: {file_path.suffix}")

    content = file_path.read_text(encoding="utf-8")

    logger.info(
        "Document read completed. filename=%s size_chars=%s",
        filename,
        len(content),
    )

    return content