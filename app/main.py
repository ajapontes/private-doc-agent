from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.config import APP_NAME, APP_VERSION
from app.services.document_loader import list_documents, read_document
from app.services.simple_search import search_keyword


app = FastAPI(
    title="Private Doc Agent",
    description="Local-first assistant for private document analysis.",
    version=APP_VERSION,
)


class SearchRequest(BaseModel):
    query: str


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app": APP_NAME,
        "version": APP_VERSION,
    }


@app.get("/documents")
def get_documents():
    return {
        "documents": list_documents(),
        "count": len(list_documents()),
    }


@app.get("/documents/{filename}")
def get_document(filename: str):
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
    results = search_keyword(request.query)

    return {
        "query": request.query,
        "matches": results,
        "count": len(results),
    }