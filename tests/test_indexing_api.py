"""
HTTP API tests for local document indexing endpoints.

These tests use FastAPI's TestClient and replace the indexing service with
controlled results or errors. They validate routes and HTTP status mappings
without reading documents, calling Ollama, or modifying ChromaDB.
"""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.indexing_service import (
    IndexingInfrastructureError,
    IndexingServiceError,
)


class IndexingApiTests(unittest.TestCase):
    """Validates bulk and single-document indexing HTTP behavior."""

    @patch("app.main.close_vector_store")
    def test_application_shutdown_closes_vector_store(self, mock_close_vector_store):
        """FastAPI releases ChromaDB resources when the application stops."""
        with TestClient(app):
            pass

        mock_close_vector_store.assert_called_once_with()

    @patch("app.main.index_all_documents")
    def test_bulk_indexing_endpoint_returns_aggregate_result(self, mock_index_all):
        """POST /documents/index returns document and chunk totals."""
        mock_index_all.return_value = {
            "documents_indexed": 2,
            "chunks_indexed": 5,
            "documents": [],
        }

        with TestClient(app) as client:
            response = client.post("/documents/index")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["documents_indexed"], 2)
        self.assertEqual(response.json()["chunks_indexed"], 5)

    @patch("app.main.index_document")
    def test_single_document_endpoint_returns_index_result(self, mock_index_document):
        """POST /documents/{filename}/index returns indexing metadata."""
        mock_index_document.return_value = {
            "filename": "demo.md",
            "chunks_indexed": 1,
            "vector_dimension": 768,
            "embedding_model": "nomic-embed-text-v2-moe:latest",
        }

        with TestClient(app) as client:
            response = client.post("/documents/demo.md/index")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["filename"], "demo.md")
        self.assertEqual(response.json()["vector_dimension"], 768)
        mock_index_document.assert_called_once_with("demo.md")

    @patch("app.main.index_document")
    def test_missing_document_returns_404(self, mock_index_document):
        """A missing source document maps to HTTP 404."""
        mock_index_document.side_effect = FileNotFoundError("Document not found")

        with TestClient(app) as client:
            response = client.post("/documents/missing.md/index")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Document not found")

    @patch("app.main.index_document")
    def test_unsupported_document_returns_400(self, mock_index_document):
        """An unsupported source extension maps to HTTP 400."""
        mock_index_document.side_effect = ValueError("Unsupported file extension: .pdf")

        with TestClient(app) as client:
            response = client.post("/documents/demo.pdf/index")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Unsupported file extension", response.json()["detail"])

    @patch("app.main.index_document")
    def test_indexing_service_failure_returns_500(self, mock_index_document):
        """Ollama or ChromaDB workflow failures map to HTTP 500."""
        mock_index_document.side_effect = IndexingServiceError("Ollama unavailable")

        with TestClient(app) as client:
            response = client.post("/documents/demo.md/index")

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["detail"], "Ollama unavailable")

    @patch("app.main.index_all_documents")
    def test_bulk_indexing_failure_returns_500(self, mock_index_all):
        """Bulk indexing failures are exposed as HTTP 500 responses."""
        mock_index_all.side_effect = IndexingServiceError("No supported documents")

        with TestClient(app) as client:
            response = client.post("/documents/index")

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["detail"], "No supported documents")

    @patch("app.main.index_document")
    def test_infrastructure_failure_returns_503(self, mock_index_document):
        """Temporary Ollama or ChromaDB failures advertise unavailability."""
        mock_index_document.side_effect = IndexingInfrastructureError(
            "Ollama unavailable"
        )

        with TestClient(app) as client:
            response = client.post("/documents/demo.md/index")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "Ollama unavailable")


if __name__ == "__main__":
    unittest.main()
