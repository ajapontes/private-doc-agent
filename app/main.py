"""
FastAPI application entry point.

This module defines the HTTP API for Private Doc Agent.

Current capabilities:
1. Health check endpoint.
2. Local document listing.
3. Local document content retrieval.
4. Simple keyword search across .txt and .md files.
5. Local LLM-powered document summarization.
6. Application logging for traceability and debugging.
"""

import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.config import APP_NAME, APP_VERSION, OLLAMA_MODEL
from app.logging_config import setup_logging, log_execution_separator
from app.services.document_loader import list_documents, read_document
from app.services.simple_search import search_keyword
from app.services.summarizer import summarize_document, SummarizerError


setup_logging()

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Private Doc Agent",
    description="Local-first assistant for private document analysis.",
    version=APP_VERSION,
)

@app.middleware("http")
async def add_log_separator(request, call_next):
    """
    Adds a visual separator line before selected HTTP request executions.

    This middleware skips technical documentation endpoints to avoid
    unnecessary separators when using Swagger UI.
    """
    ignored_paths = {"/docs", "/openapi.json", "/favicon.ico"}

    if request.url.path not in ignored_paths:
        log_execution_separator()

    response = await call_next(request)

    return response

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
    logger.info("Health check requested.")

    return {
        "status": "ok",
        "app": APP_NAME,
        "version": APP_VERSION,
    }


@app.get("/documents")
@app.get("/documents")
def get_documents():
    """
    Lists all supported documents available in the local input folder.
    """
    logger.info("Listing available documents.")

    documents = list_documents()

    logger.info("Documents listed successfully. count=%s", len(documents))

    return {
        "documents": documents,
        "count": len(documents),
    }


@app.get("/documents/{filename}")
def get_document(filename: str):
    """
    Returns the full content of a specific local document.
    """
    logger.info("Document content requested. filename=%s", filename)

    try:
        content = read_document(filename)

        logger.info("Document read successfully. filename=%s", filename)

        return {
            "filename": filename,
            "content": content,
        }

    except FileNotFoundError as error:
        logger.warning("Document not found. filename=%s error=%s", filename, error)
        raise HTTPException(status_code=404, detail=str(error))
    except ValueError as error:
        logger.warning("Unsupported document requested. filename=%s error=%s", filename, error)
        raise HTTPException(status_code=400, detail=str(error))

@app.post("/search")
def search_documents(request: SearchRequest):
    """
    Searches a keyword or phrase across all supported local documents.
    """
    logger.info("Search requested. query=%s", request.query)

    results = search_keyword(request.query)

    logger.info(
        "Search completed. query=%s matches=%s",
        request.query,
        len(results),
    )

    return {
        "query": request.query,
        "matches": results,
        "count": len(results),
    }

@app.post("/summarize")
def summarize_local_document(request: SummarizeRequest):
    """
    Summarizes a supported local document using the configured local LLM.
    """
    logger.info(
        "Summarization requested. filename=%s model=%s",
        request.filename,
        OLLAMA_MODEL,
    )

    try:
        summary = summarize_document(request.filename)

        logger.info(
            "Summarization completed successfully. filename=%s summary_length=%s",
            request.filename,
            len(summary),
        )

        return {
            "filename": request.filename,
            "summary": summary,
            "model": OLLAMA_MODEL,
            "version": APP_VERSION,
        }

    except FileNotFoundError as error:
        logger.warning(
            "Summarization failed. Document not found. filename=%s error=%s",
            request.filename,
            error,
        )
        raise HTTPException(status_code=404, detail=str(error))
    except ValueError as error:
        logger.warning(
            "Summarization failed. Unsupported file. filename=%s error=%s",
            request.filename,
            error,
        )
        raise HTTPException(status_code=400, detail=str(error))
    except SummarizerError as error:
        logger.error(
            "Summarization failed due to internal error. filename=%s error=%s",
            request.filename,
            error,
        )
        raise HTTPException(status_code=500, detail=str(error))