"""Unit tests for semantic document retrieval orchestration."""

import unittest
from unittest.mock import patch

from app.services.embedding_service import EmbeddingServiceError
from app.services.retrieval_service import (
    RetrievalServiceError,
    retrieve_relevant_chunks,
)
from app.services.vector_store import VectorStoreError


class RetrievalServiceTests(unittest.TestCase):
    """Validates retrieval inputs, coordination, output, and failures."""

    @patch("app.services.retrieval_service.query_chunks")
    @patch("app.services.retrieval_service.embed_query")
    def test_retrieval_returns_ranked_matches_with_relevance(
        self, mock_embed_query, mock_query_chunks
    ):
        """Distances are converted into source-aware similarity results."""
        mock_embed_query.return_value = [0.8, 0.2]
        mock_query_chunks.return_value = [
            {
                "filename": "demo.md",
                "chunk_id": 0,
                "content": "Private local document assistant.",
                "start_char": 0,
                "end_char": 33,
                "distance": 0.12,
                "relevance_score": 0.88,
            }
        ]

        result = retrieve_relevant_chunks("  How is privacy protected?  ", top_k=2)

        self.assertEqual(result["question"], "How is privacy protected?")
        self.assertEqual(result["matches"][0]["relevance_score"], 0.88)
        self.assertEqual(result["matches"][0]["distance"], 0.12)
        mock_embed_query.assert_called_once_with("How is privacy protected?")
        mock_query_chunks.assert_called_once_with(
            query_embedding=[0.8, 0.2], top_k=2
        )

    @patch("app.services.retrieval_service.query_chunks", return_value=[])
    @patch("app.services.retrieval_service.embed_query", return_value=[1.0, 0.0])
    def test_empty_collection_returns_no_matches(self, _mock_embed, _mock_query):
        """An empty vector collection produces a successful empty result."""
        result = retrieve_relevant_chunks("What is documented?")

        self.assertEqual(result["matches"], [])

    def test_empty_question_is_rejected(self):
        """Blank questions are rejected before generating embeddings."""
        with self.assertRaisesRegex(ValueError, "cannot be empty"):
            retrieve_relevant_chunks("   ")

    def test_invalid_top_k_is_rejected(self):
        """The requested result limit must be a positive integer."""
        for invalid_value in (0, -1, 1.5, True):
            with self.subTest(top_k=invalid_value):
                with self.assertRaisesRegex(ValueError, "positive integer"):
                    retrieve_relevant_chunks("Valid question", top_k=invalid_value)

    @patch("app.services.retrieval_service.embed_query")
    def test_embedding_failure_is_wrapped(self, mock_embed_query):
        """Ollama failures become retrieval-layer errors."""
        mock_embed_query.side_effect = EmbeddingServiceError("Ollama unavailable")

        with self.assertRaisesRegex(RetrievalServiceError, "Ollama unavailable"):
            retrieve_relevant_chunks("What is documented?")

    @patch("app.services.retrieval_service.query_chunks")
    @patch("app.services.retrieval_service.embed_query", return_value=[1.0, 0.0])
    def test_vector_store_failure_is_wrapped(self, _mock_embed, mock_query_chunks):
        """ChromaDB failures become retrieval-layer errors."""
        mock_query_chunks.side_effect = VectorStoreError("Database unavailable")

        with self.assertRaisesRegex(RetrievalServiceError, "Database unavailable"):
            retrieve_relevant_chunks("What is documented?")


if __name__ == "__main__":
    unittest.main()
