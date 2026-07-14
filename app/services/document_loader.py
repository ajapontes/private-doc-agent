from pathlib import Path
from app.config import INPUT_DIR, SUPPORTED_EXTENSIONS


def list_documents() -> list[dict]:
    """
    Lists supported documents from data/input.
    Currently supports .txt and .md files.
    """
    INPUT_DIR.mkdir(parents=True, exist_ok=True)

    documents = []

    for file_path in INPUT_DIR.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            documents.append(
                {
                    "filename": file_path.name,
                    "extension": file_path.suffix.lower(),
                    "size_bytes": file_path.stat().st_size,
                    "path": str(file_path.relative_to(INPUT_DIR.parent.parent)),
                }
            )

    return documents


def read_document(filename: str) -> str:
    """
    Reads a supported document by filename from data/input.
    """
    file_path = INPUT_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(f"Document not found: {filename}")

    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension: {file_path.suffix}")

    return file_path.read_text(encoding="utf-8")