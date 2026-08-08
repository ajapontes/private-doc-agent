"""
HTTP API tests for semantic document retrieval.

These tests replace the retrieval service with controlled results or errors.
They validate request forwarding and HTTP responses without calling Ollama or
querying ChromaDB.
"""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.retrieval_service import RetrievalServiceError


class RetrievalApiTests(unittest.TestCase):
    """Validates semantic retrieval endpoint behavior."""

    @patch("app.main.retrieve_relevant_chunks")
    def test_retrieval_endpoint_returns_ranked_matches(self, mock_retrieve):
        """POST /retrieve returns the service result and forwards inputs."""
        mock_retrieve.return_value = {
            "question": "What does the assistant do?",
            "matches": [
                {
                    "filename": "demo.txt",
                    "chunk_id": 0,
                    "content": "Private Doc Agent is a local-first assistant.",
                    "start_char": 0,
                    "end_char": 45,
                    "similarity": 0.81,
                }
            ],
        }

        with TestClient(app) as client:
            response = client.post(
                "/retrieve",
                json={"question": "What does the assistant do?", "top_k": 2},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["matches"][0]["filename"], "demo.txt")
        self.assertEqual(response.json()["matches"][0]["similarity"], 0.81)
        mock_retrieve.assert_called_once_with(
            question="What does the assistant do?",
            top_k=2,
        )

    @patch("app.main.retrieve_relevant_chunks")
    def test_retrieval_endpoint_uses_default_top_k(self, mock_retrieve):
        """The endpoint requests configured number of matches when top_k is omitted."""
        mock_retrieve.return_value = {"question": "Question", "matches": []}

        with TestClient(app) as client:
            response = client.post("/retrieve", json={"question": "Question"})

        self.assertEqual(response.status_code, 200)
        mock_retrieve.assert_called_once_with(question="Question", top_k=5)

    @patch("app.main.retrieve_relevant_chunks")
    def test_invalid_retrieval_request_returns_400(self, mock_retrieve):
        """Service input validation errors map to HTTP 400."""
        mock_retrieve.side_effect = ValueError("Question cannot be empty.")

        with TestClient(app) as client:
            response = client.post(
                "/retrieve",
                json={"question": "   ", "top_k": 2},
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Question cannot be empty.")

    @patch("app.main.retrieve_relevant_chunks")
    def test_retrieval_service_failure_returns_500(self, mock_retrieve):
        """Ollama or ChromaDB failures map to HTTP 500."""
        mock_retrieve.side_effect = RetrievalServiceError("Ollama unavailable")

        with TestClient(app) as client:
            response = client.post(
                "/retrieve",
                json={"question": "What does the assistant do?"},
            )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["detail"], "Ollama unavailable")


if __name__ == "__main__":
    unittest.main()
