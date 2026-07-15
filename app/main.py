"""
FastAPI application entry point.

This module defines the HTTP API for Private Doc Agent.

Current capabilities:
1. Health check endpoint.
2. Local document listing.
3. Local document content retrieval.
4. Simple keyword search across .txt and .md files.
5. Local LLM-powered document summarization.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.config import APP_NAME, APP_VERSION, OLLAMA_MODEL
from app.services.document_loader import list_documents, read_document
from app.services.simple_search import search_keyword
from app.services.summarizer import summarize_document, SummarizerError


app = FastAPI(
    title="Private Doc Agent",
    description="Local-first assistant for private document analysis.",
    version=APP_VERSION,
)


class SearchRequest(BaseModel):
    """
    Request model for keyword search.

    Attributes:
        query: Keyword or phrase to search across supported documents.
    """

    query: str


class SummarizeRequest(BaseModel):
    """
    Request model for document summarization.

    Attributes:
        filename: Name of the local document to summarize.
    """

    filename: str


@app.get("/health")
def health_check():
    """
    Returns the current health status of the API.

    This endpoint is useful to verify that the FastAPI application
    is running correctly.
    """
    return {
        "status": "ok",
        "app": APP_NAME,
        "version": APP_VERSION,
    }


@app.get("/documents")
def get_documents():
    """
    Lists all supported documents available in the local input folder.

    Supported file extensions are defined in app/config.py.
    """
    documents = list_documents()

    return {
        "documents": documents,
        "count": len(documents),
    }


@app.get("/documents/{filename}")
def get_document(filename: str):
    """
    Returns the full content of a specific local document.

    Args:
        filename: Name of the document located in the data/input folder.
    """
    try:
        content = read_document(filename)
        return {
            "filename": filename,
            "content": content,
        }
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/search")
def search_documents(request: SearchRequest):
    """
    Searches a keyword or phrase across all supported local documents.

    Args:
        request: SearchRequest containing the query to search.
    """
    results = search_keyword(request.query)

    return {
        "query": request.query,
        "matches": results,
        "count": len(results),
    }


@app.post("/summarize")
def summarize_local_document(request: SummarizeRequest):
    """
    Summarizes a supported local document using the configured local LLM.

    Args:
        request: SummarizeRequest containing the filename to summarize.

    Returns:
        A JSON response containing the filename, generated summary,
        local model name, and application version.

    Raises:
        HTTPException: Returns a specific HTTP error when the document
        does not exist, the extension is unsupported, or the local LLM
        summarization process fails.
    """
    try:
        summary = summarize_document(request.filename)

        return {
            "filename": request.filename,
            "summary": summary,
            "model": OLLAMA_MODEL,
            "version": APP_VERSION,
        }

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except SummarizerError as error:
        raise HTTPException(status_code=500, detail=str(error))