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
7. Local document indexing with chunking, embeddings, and ChromaDB.
8. Semantic retrieval of relevant document chunks.
9. Retrieval-augmented question answering with traceable sources.
10. Single-step local agent execution through allowlisted tools.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.config import (
    APP_NAME,
    APP_VERSION,
    CHROMA_COLLECTION_NAME,
    OLLAMA_MODEL,
    VECTOR_DISTANCE_METRIC,
    VECTOR_SEARCH_TOP_K,
)
from app.logging_config import setup_logging, log_execution_separator
from app.services.agent_service import (
    AgentExecutionError,
    AgentPlanningError,
    run_agent,
)
from app.services.document_loader import list_documents, read_document
from app.services.indexing_service import (
    IndexingServiceError,
    index_all_documents,
    index_document,
)
from app.services.rag_service import RAGServiceError, answer_question
from app.services.retrieval_service import (
    RetrievalServiceError,
    retrieve_relevant_chunks,
)
from app.services.simple_search import search_keyword
from app.services.summarizer import summarize_document, SummarizerError
from app.services.vector_store import (
    VectorStoreError,
    close_vector_store,
    reset_vector_store,
)


setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Manages resources used during the FastAPI application lifetime.

    ChromaDB is opened lazily on the first vector operation and closed when
    the application stops, releasing SQLite and vector-index file handles.
    """
    yield
    close_vector_store()


app = FastAPI(
    title="Private Doc Agent",
    description="Local-first assistant for private document analysis.",
    version=APP_VERSION,
    lifespan=lifespan,
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


class RetrievalRequest(BaseModel):
    """
    Request model for semantic document retrieval.

    Attributes:
        question: Natural-language question used for vector search.
        top_k: Maximum number of relevant chunks to return.
    """

    question: str
    top_k: int = VECTOR_SEARCH_TOP_K


class AskRequest(BaseModel):
    """
    Request model for retrieval-augmented question answering.

    Attributes:
        question: Natural-language question to answer from indexed documents.
        top_k: Maximum number of relevant chunks to use as evidence.
    """

    question: str
    top_k: int = VECTOR_SEARCH_TOP_K


class AgentRequest(BaseModel):
    """
    Request model for single-step local agent execution.

    Attributes:
        request: Natural-language instruction to plan and execute.
    """

    request: str


class VectorStoreResetRequest(BaseModel):
    """Request model for the destructive vector-store reset operation.

    Attributes:
        confirm: Explicit authorization to delete all indexed chunks from the
            configured vector collection.
    """

    confirm: bool = False


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


@app.post("/documents/index")
def index_available_documents():
    """
    Indexes every supported document available in the local input folder.
    """
    logger.info("Bulk document indexing requested.")

    try:
        result = index_all_documents()
    except IndexingServiceError as error:
        logger.error("Bulk document indexing failed. error=%s", error)
        raise HTTPException(status_code=500, detail=str(error))

    logger.info(
        "Bulk document indexing completed. documents_indexed=%s "
        "documents_invalid=%s chunks_indexed=%s",
        result["documents_indexed"],
        result.get("documents_invalid", 0),
        result["chunks_indexed"],
    )

    return result


@app.post("/documents/{filename}/index")
def index_available_document(filename: str):
    """Indexes one supported local document by filename."""
    logger.info("Single document indexing requested. filename=%s", filename)

    try:
        result = index_document(filename)
    except FileNotFoundError as error:
        logger.warning("Document indexing failed. filename=%s error=%s", filename, error)
        raise HTTPException(status_code=404, detail=str(error))
    except ValueError as error:
        logger.warning("Document indexing failed. filename=%s error=%s", filename, error)
        raise HTTPException(status_code=400, detail=str(error))
    except IndexingServiceError as error:
        logger.error("Document indexing failed. filename=%s error=%s", filename, error)
        raise HTTPException(status_code=500, detail=str(error))

    logger.info(
        "Single document indexing completed. filename=%s chunks_indexed=%s",
        filename,
        result["chunks_indexed"],
    )

    return result


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


@app.post("/retrieve")
def retrieve_document_chunks(request: RetrievalRequest):
    """Retrieves document chunks semantically related to a question."""
    logger.info("Semantic retrieval requested. top_k=%s", request.top_k)

    try:
        result = retrieve_relevant_chunks(
            question=request.question,
            top_k=request.top_k,
        )
    except ValueError as error:
        logger.warning("Semantic retrieval request rejected. error=%s", error)
        raise HTTPException(status_code=400, detail=str(error))
    except RetrievalServiceError as error:
        logger.error("Semantic retrieval request failed. error=%s", error)
        raise HTTPException(status_code=500, detail=str(error))

    logger.info(
        "Semantic retrieval request completed. matches=%s",
        len(result["matches"]),
    )

    return result


@app.post("/admin/vector-store/reset")
def reset_configured_vector_store(request: VectorStoreResetRequest):
    """Resets the configured vector collection after explicit confirmation."""
    logger.warning(
        "Vector store reset API request received. collection=%s metric=%s "
        "confirmed=%s",
        CHROMA_COLLECTION_NAME,
        VECTOR_DISTANCE_METRIC,
        request.confirm,
    )

    if request.confirm is not True:
        logger.warning(
            "Vector store reset API request rejected. collection=%s",
            CHROMA_COLLECTION_NAME,
        )
        raise HTTPException(
            status_code=400,
            detail="Vector store reset requires confirm=true.",
        )

    try:
        deleted_records = reset_vector_store(confirm=True)
    except VectorStoreError as error:
        logger.error(
            "Vector store reset API request failed. collection=%s metric=%s "
            "error_type=%s",
            CHROMA_COLLECTION_NAME,
            VECTOR_DISTANCE_METRIC,
            type(error).__name__,
        )
        raise HTTPException(status_code=500, detail=str(error))

    logger.warning(
        "Vector store reset API request completed. collection=%s metric=%s "
        "deleted_records=%s",
        CHROMA_COLLECTION_NAME,
        VECTOR_DISTANCE_METRIC,
        deleted_records,
    )

    return {
        "status": "reset",
        "collection": CHROMA_COLLECTION_NAME,
        "metric": VECTOR_DISTANCE_METRIC,
        "deleted_records": deleted_records,
    }


@app.post("/ask")
def ask_document_question(request: AskRequest):
    """Answers a question using only evidence from indexed documents."""
    logger.info("RAG API request received. top_k=%s", request.top_k)

    try:
        result = answer_question(
            question=request.question,
            top_k=request.top_k,
        )
    except (ValueError, TypeError) as error:
        logger.warning("RAG API request rejected. error=%s", error)
        raise HTTPException(status_code=400, detail=str(error))
    except RAGServiceError as error:
        logger.error("RAG API request failed. error=%s", error)
        raise HTTPException(status_code=500, detail=str(error))

    logger.info(
        "RAG API request completed. sources=%s answer_length=%s",
        len(result["sources"]),
        len(result["answer"]),
    )

    return result


@app.post("/agent")
def execute_local_agent(request: AgentRequest):
    """Plans and executes one allowlisted local tool."""
    logger.info(
        "Local agent API request received. request_length=%s",
        len(request.request.strip()),
    )

    try:
        result = run_agent(request.request)
    except (ValueError, TypeError) as error:
        logger.warning("Local agent API request rejected. error=%s", error)
        raise HTTPException(status_code=400, detail=str(error))
    except AgentPlanningError as error:
        logger.warning(
            "Local agent API planning failed. error_type=%s",
            type(error).__name__,
        )
        raise HTTPException(status_code=422, detail=str(error))
    except AgentExecutionError as error:
        logger.error(
            "Local agent API execution failed. error_type=%s",
            type(error).__name__,
        )
        raise HTTPException(status_code=500, detail=str(error))

    response = result.to_dict()
    logger.info(
        "Local agent API request completed. tools_used=%s",
        len(response["tools_used"]),
    )
    return response


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
