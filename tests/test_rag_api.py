"""
HTTP API tests for retrieval-augmented question answering.

These tests replace the RAG service with controlled results or errors. They
validate request forwarding, HTTP error mapping, default values, and logging
privacy without calling Ollama or querying ChromaDB.
"""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.rag_service import RAGServiceError


class RagApiTests(unittest.TestCase):
    """Validates retrieval-augmented question-answering endpoint behavior."""

    @staticmethod
    def _service_result():
        """Returns a representative grounded answer for endpoint tests."""
        return {
            "question": "What does the assistant do?",
            "answer": "It answers questions about private documents.",
            "sources": [
                {
                    "filename": "demo.txt",
                    "chunk_id": 0,
                    "distance": 0.19,
                    "relevance_score": 0.81,
                }
            ],
        }

    @patch("app.main.answer_question")
    def test_ask_endpoint_returns_answer_and_sources(self, mock_answer):
        """POST /ask returns the grounded answer and source metadata."""
        mock_answer.return_value = self._service_result()

        with TestClient(app) as client:
            response = client.post(
                "/ask",
                json={"question": "What does the assistant do?", "top_k": 2},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["answer"], self._service_result()["answer"])
        self.assertEqual(response.json()["sources"][0]["filename"], "demo.txt")

    @patch("app.main.answer_question")
    def test_ask_endpoint_forwards_question_and_top_k(self, mock_answer):
        """The endpoint forwards explicit request values to the RAG service."""
        mock_answer.return_value = self._service_result()

        with TestClient(app) as client:
            client.post(
                "/ask",
                json={"question": "What does the assistant do?", "top_k": 2},
            )

        mock_answer.assert_called_once_with(
            question="What does the assistant do?",
            top_k=2,
        )

    @patch("app.main.answer_question")
    def test_ask_endpoint_uses_default_top_k(self, mock_answer):
        """The endpoint requests configured number of sources when top_k is omitted."""
        mock_answer.return_value = self._service_result()

        with TestClient(app) as client:
            response = client.post(
                "/ask",
                json={"question": "What does the assistant do?"},
            )

        self.assertEqual(response.status_code, 200)
        mock_answer.assert_called_once_with(
            question="What does the assistant do?",
            top_k=5,
        )

    @patch("app.main.answer_question")
    def test_empty_question_returns_400(self, mock_answer):
        """An empty question rejected by the service maps to HTTP 400."""
        mock_answer.side_effect = ValueError("Question cannot be empty.")

        with TestClient(app) as client:
            response = client.post(
                "/ask",
                json={"question": "   ", "top_k": 2},
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Question cannot be empty.")

    @patch("app.main.answer_question")
    def test_invalid_top_k_returns_400(self, mock_answer):
        """An invalid result limit rejected by the service maps to HTTP 400."""
        mock_answer.side_effect = ValueError("top_k must be greater than zero.")

        with TestClient(app) as client:
            response = client.post(
                "/ask",
                json={"question": "Question", "top_k": 0},
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["detail"],
            "top_k must be greater than zero.",
        )

    @patch("app.main.answer_question")
    def test_rag_service_failure_returns_500(self, mock_answer):
        """Retrieval or generation failures map to HTTP 500."""
        mock_answer.side_effect = RAGServiceError("Ollama unavailable")

        with TestClient(app) as client:
            response = client.post(
                "/ask",
                json={"question": "What does the assistant do?"},
            )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["detail"], "Ollama unavailable")

    @patch("app.main.answer_question")
    def test_ask_operational_logs_do_not_expose_private_text(self, mock_answer):
        """Operational logs contain metrics but not questions or answers."""
        private_question = "CONFIDENTIAL question content"
        private_answer = "CONFIDENTIAL answer content"
        result = self._service_result()
        result["question"] = private_question
        result["answer"] = private_answer
        mock_answer.return_value = result

        with self.assertLogs("app.main", level="INFO") as captured_logs:
            with TestClient(app) as client:
                response = client.post(
                    "/ask",
                    json={"question": private_question, "top_k": 2},
                )

        log_output = "\n".join(captured_logs.output)
        self.assertEqual(response.status_code, 200)
        self.assertIn("sources=1", log_output)
        self.assertIn(f"answer_length={len(private_answer)}", log_output)
        self.assertNotIn(private_question, log_output)
        self.assertNotIn(private_answer, log_output)


if __name__ == "__main__":
    unittest.main()
