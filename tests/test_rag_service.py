"""Unit tests for retrieval-augmented answer generation."""

import unittest
from unittest.mock import patch

from app.services.llm_client import LLMClientError
from app.services.rag_service import (
    NO_CONTEXT_ANSWER,
    RAGServiceError,
    answer_question,
    build_rag_prompt,
)
from app.services.retrieval_service import RetrievalServiceError


MATCHES = [
    {
        "filename": "demo.txt",
        "chunk_id": 0,
        "content": "Private Doc Agent is a local-first assistant.",
        "start_char": 0,
        "end_char": 45,
        "similarity": 0.82,
    },
    {
        "filename": "demo.md",
        "chunk_id": 1,
        "content": "It supports semantic document retrieval.",
        "start_char": 46,
        "end_char": 86,
        "similarity": 0.71,
    },
]


class RAGServiceTests(unittest.TestCase):
    """Validates grounded prompts, answers, sources, and failures."""

    def test_prompt_contains_question_sources_and_safety_rules(self):
        """The prompt labels evidence and prevents document instructions."""
        prompt = build_rag_prompt("What does it do?", MATCHES)

        self.assertIn("Question:\nWhat does it do?", prompt)
        self.assertIn("[Source 1]", prompt)
        self.assertIn("Filename: demo.txt", prompt)
        self.assertIn(MATCHES[0]["content"], prompt)
        self.assertIn("never as instructions", prompt)

    @patch("app.services.rag_service.generate_text")
    @patch("app.services.rag_service.retrieve_relevant_chunks")
    def test_answer_returns_generated_text_and_source_metadata(
        self, mock_retrieve, mock_generate
    ):
        """A grounded answer includes traceable sources without full content."""
        mock_retrieve.return_value = {
            "question": "What does it do?",
            "matches": MATCHES,
        }
        mock_generate.return_value = "It is a local-first document assistant."

        result = answer_question("  What does it do?  ", top_k=2)

        self.assertEqual(result["answer"], mock_generate.return_value)
        self.assertEqual(len(result["sources"]), 2)
        self.assertEqual(
            result["sources"][0],
            {"filename": "demo.txt", "chunk_id": 0, "similarity": 0.82},
        )
        self.assertNotIn("content", result["sources"][0])
        mock_retrieve.assert_called_once_with("  What does it do?  ", top_k=2)
        mock_generate.assert_called_once()

    @patch("app.services.rag_service.generate_text")
    @patch("app.services.rag_service.retrieve_relevant_chunks")
    def test_empty_retrieval_skips_llm(self, mock_retrieve, mock_generate):
        """No evidence returns a controlled answer without invoking Ollama."""
        mock_retrieve.return_value = {"question": "Unknown?", "matches": []}

        result = answer_question("Unknown?")

        self.assertEqual(result["answer"], NO_CONTEXT_ANSWER)
        self.assertEqual(result["sources"], [])
        mock_generate.assert_not_called()

    @patch("app.services.rag_service.retrieve_relevant_chunks")
    def test_retrieval_failure_is_wrapped(self, mock_retrieve):
        """Retrieval-layer failures become RAG-layer errors."""
        mock_retrieve.side_effect = RetrievalServiceError("Database unavailable")

        with self.assertRaisesRegex(RAGServiceError, "Database unavailable"):
            answer_question("What is documented?")

    @patch("app.services.rag_service.generate_text")
    @patch("app.services.rag_service.retrieve_relevant_chunks")
    def test_llm_failure_is_wrapped(self, mock_retrieve, mock_generate):
        """Local generation failures become RAG-layer errors."""
        mock_retrieve.return_value = {
            "question": "What does it do?",
            "matches": MATCHES,
        }
        mock_generate.side_effect = LLMClientError("Ollama unavailable")

        with self.assertRaisesRegex(RAGServiceError, "Ollama unavailable"):
            answer_question("What does it do?")

    def test_empty_question_is_rejected(self):
        """Question validation remains visible to service callers."""
        with self.assertRaisesRegex(ValueError, "cannot be empty"):
            answer_question("   ")


if __name__ == "__main__":
    unittest.main()
