"""Unit tests for configurable vector metrics and relevance filtering."""

import unittest
from unittest.mock import MagicMock, patch

from app.services.retrieval_service import retrieve_relevant_chunks
from app.services.vector_store import distance_to_relevance, get_collection


class VectorMetricTests(unittest.TestCase):
    """Validates metric configuration and distance normalization."""

    def test_cosine_distance_is_converted_to_relevance(self):
        """Cosine distance is inverted into a bounded relevance score."""
        self.assertEqual(distance_to_relevance(0.0, "cosine"), 1.0)
        self.assertEqual(distance_to_relevance(0.25, "cosine"), 0.75)
        self.assertEqual(distance_to_relevance(1.0, "cosine"), 0.0)

    def test_l2_distance_is_converted_to_relevance(self):
        """Squared Euclidean distance is normalized after taking its root."""
        self.assertEqual(distance_to_relevance(0.0, "l2"), 1.0)
        self.assertEqual(distance_to_relevance(1.0, "l2"), 0.5)
        self.assertEqual(distance_to_relevance(4.0, "l2"), 0.333333)

    def test_inner_product_distance_is_converted_to_relevance(self):
        """Inner-product distance follows ChromaDB's distance convention."""
        self.assertEqual(distance_to_relevance(0.0, "ip"), 1.0)
        self.assertEqual(distance_to_relevance(0.4, "ip"), 0.6)
        self.assertEqual(distance_to_relevance(1.0, "ip"), 0.0)

    def test_relevance_is_bounded_between_zero_and_one(self):
        """Unusual distance values cannot escape the public score range."""
        self.assertEqual(distance_to_relevance(-0.5, "cosine"), 1.0)
        self.assertEqual(distance_to_relevance(2.0, "cosine"), 0.0)

    @patch("app.services.vector_store.get_client")
    def test_collection_uses_configured_metric(self, mock_get_client):
        """The configured metric is passed to ChromaDB collection creation."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        with (
            patch("app.services.vector_store.VECTOR_DISTANCE_METRIC", "l2"),
            patch("app.services.vector_store.CHROMA_COLLECTION_NAME", "test_docs"),
        ):
            get_collection()

        mock_client.get_or_create_collection.assert_called_once_with(
            name="test_docs",
            embedding_function=None,
            configuration={"hnsw": {"space": "l2"}},
        )


class ConfigurableRetrievalTests(unittest.TestCase):
    """Validates configurable result limits and relevance thresholds."""

    @patch("app.services.retrieval_service.query_chunks")
    @patch("app.services.retrieval_service.embed_query", return_value=[1.0, 0.0])
    def test_configured_top_k_is_used_when_omitted(
        self, _mock_embed_query, mock_query_chunks
    ):
        """Retrieval uses VECTOR_SEARCH_TOP_K when the caller omits top_k."""
        mock_query_chunks.return_value = []

        with patch("app.services.retrieval_service.VECTOR_SEARCH_TOP_K", 7):
            retrieve_relevant_chunks("What is documented?")

        mock_query_chunks.assert_called_once_with(
            query_embedding=[1.0, 0.0],
            top_k=7,
        )

    @patch("app.services.retrieval_service.query_chunks")
    @patch("app.services.retrieval_service.embed_query", return_value=[1.0, 0.0])
    def test_matches_below_configured_threshold_are_removed(
        self, _mock_embed_query, mock_query_chunks
    ):
        """Only matches meeting the minimum relevance score are returned."""
        mock_query_chunks.return_value = [
            {
                "filename": "demo.md",
                "chunk_id": 0,
                "content": "Relevant content.",
                "start_char": 0,
                "end_char": 17,
                "distance": 0.1,
                "relevance_score": 0.9,
            },
            {
                "filename": "demo.md",
                "chunk_id": 1,
                "content": "Weak content.",
                "start_char": 18,
                "end_char": 31,
                "distance": 0.6,
                "relevance_score": 0.4,
            },
        ]

        with patch(
            "app.services.retrieval_service.VECTOR_MIN_RELEVANCE_SCORE",
            0.5,
        ):
            result = retrieve_relevant_chunks("What is documented?", top_k=2)

        self.assertEqual(len(result["matches"]), 1)
        self.assertEqual(result["matches"][0]["chunk_id"], 0)
        self.assertEqual(result["matches"][0]["distance"], 0.1)
        self.assertEqual(result["matches"][0]["relevance_score"], 0.9)


if __name__ == "__main__":
    unittest.main()
