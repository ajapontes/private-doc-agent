"""
Unit tests for the local embedding service.

The tests replace the HTTP call to Ollama with controlled mock responses.
They validate payload construction, task prefixes, response handling, and
error behavior without requiring Ollama or downloading a model.
"""

import unittest
from unittest.mock import Mock, patch

import requests

from app.config import OLLAMA_EMBEDDING_MODEL
from app.services.embedding_service import (
    EmbeddingServiceError,
    embed_documents,
    embed_query,
    generate_embeddings,
)


class EmbeddingServiceTests(unittest.TestCase):
    """Validates local embedding request and response behavior."""

    @patch("app.services.embedding_service.requests.post")
    def test_document_embeddings_use_document_prefix(self, mock_post):
        """Document chunks are sent in order with the required task prefix."""
        mock_response = Mock()
        mock_response.json.return_value = {"embeddings": [[0.1, 0.2], [0.3, 0.4]]}
        mock_post.return_value = mock_response

        embeddings = embed_documents(["First chunk", "Second chunk"])

        self.assertEqual(embeddings, [[0.1, 0.2], [0.3, 0.4]])
        mock_post.assert_called_once()
        _, call_kwargs = mock_post.call_args
        self.assertEqual(call_kwargs["json"]["model"], OLLAMA_EMBEDDING_MODEL)
        self.assertEqual(
            call_kwargs["json"]["input"],
            ["search_document: First chunk", "search_document: Second chunk"],
        )
        self.assertEqual(call_kwargs["timeout"], 120)

    @patch("app.services.embedding_service.requests.post")
    def test_query_embedding_uses_query_prefix(self, mock_post):
        """A user question is sent with the required query task prefix."""
        mock_response = Mock()
        mock_response.json.return_value = {"embeddings": [[0.5, 0.6]]}
        mock_post.return_value = mock_response

        embedding = embed_query("Where is the private document?")

        self.assertEqual(embedding, [0.5, 0.6])
        _, call_kwargs = mock_post.call_args
        self.assertEqual(
            call_kwargs["json"]["input"],
            ["search_query: Where is the private document?"],
        )

    def test_empty_text_list_is_rejected(self):
        """At least one text is required for an embedding request."""
        with self.assertRaisesRegex(EmbeddingServiceError, "At least one text"):
            embed_documents([])

    def test_blank_text_is_rejected(self):
        """Blank values are rejected before contacting Ollama."""
        with self.assertRaisesRegex(EmbeddingServiceError, "cannot be empty"):
            embed_query("   ")

    def test_unsupported_task_is_rejected(self):
        """Only document and query task types are accepted."""
        with self.assertRaisesRegex(EmbeddingServiceError, "Unsupported embedding task"):
            generate_embeddings(["content"], task="invalid")

    @patch("app.services.embedding_service.requests.post")
    def test_ollama_connection_error_is_wrapped(self, mock_post):
        """Connection failures are exposed through the service exception."""
        mock_post.side_effect = requests.exceptions.ConnectionError("Ollama unavailable")

        with self.assertRaisesRegex(EmbeddingServiceError, "Ollama unavailable"):
            embed_query("question")

    @patch("app.services.embedding_service.requests.post")
    def test_missing_embeddings_field_is_rejected(self, mock_post):
        """A response without embeddings is considered invalid."""
        mock_response = Mock()
        mock_response.json.return_value = {"model": OLLAMA_EMBEDDING_MODEL}
        mock_post.return_value = mock_response

        with self.assertRaisesRegex(EmbeddingServiceError, "Missing 'embeddings'"):
            embed_query("question")

    @patch("app.services.embedding_service.requests.post")
    def test_embedding_count_must_match_input_count(self, mock_post):
        """Every source text must receive exactly one vector."""
        mock_response = Mock()
        mock_response.json.return_value = {"embeddings": [[0.1, 0.2]]}
        mock_post.return_value = mock_response

        with self.assertRaisesRegex(EmbeddingServiceError, "does not match"):
            embed_documents(["first", "second"])

    @patch("app.services.embedding_service.requests.post")
    def test_vector_dimensions_must_be_consistent(self, mock_post):
        """All vectors in one response must use the same dimension."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "embeddings": [[0.1, 0.2], [0.3]],
        }
        mock_post.return_value = mock_response

        with self.assertRaisesRegex(EmbeddingServiceError, "Inconsistent vector dimensions"):
            embed_documents(["first", "second"])


if __name__ == "__main__":
    unittest.main()
