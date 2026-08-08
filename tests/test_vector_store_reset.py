"""Unit tests for safe local vector-store reset behavior.

These tests use mocks to verify confirmation, metric configuration, record
counts, and privacy-safe logs without deleting a real ChromaDB collection.
"""

import unittest
from unittest.mock import MagicMock, patch

from app.services.vector_store import VectorStoreError, reset_vector_store


class VectorStoreResetTests(unittest.TestCase):
    """Validates the guarded vector collection reset workflow."""

    @patch("app.services.vector_store.get_client")
    def test_confirmed_reset_deletes_and_recreates_existing_collection(
        self,
        mock_get_client,
    ):
        """Existing records are counted before the configured collection resets."""
        client = MagicMock()
        collection = MagicMock()
        collection.name = "private_documents"
        existing_collection = MagicMock()
        existing_collection.count.return_value = 17
        client.list_collections.return_value = [collection]
        client.get_collection.return_value = existing_collection
        mock_get_client.return_value = client

        with patch(
            "app.services.vector_store.VECTOR_DISTANCE_METRIC",
            "l2",
        ):
            deleted_count = reset_vector_store(confirm=True)

        self.assertEqual(deleted_count, 17)
        client.delete_collection.assert_called_once_with(name="private_documents")
        client.get_or_create_collection.assert_called_once_with(
            name="private_documents",
            embedding_function=None,
            configuration={"hnsw": {"space": "l2"}},
        )

    @patch("app.services.vector_store.get_client")
    def test_reset_creates_collection_when_it_does_not_exist(self, mock_get_client):
        """A missing collection is created without attempting a deletion."""
        client = MagicMock()
        client.list_collections.return_value = []
        mock_get_client.return_value = client

        deleted_count = reset_vector_store(confirm=True)

        self.assertEqual(deleted_count, 0)
        client.get_collection.assert_not_called()
        client.delete_collection.assert_not_called()
        client.get_or_create_collection.assert_called_once()

    @patch("app.services.vector_store.get_client")
    def test_reset_without_confirmation_does_not_open_database(self, mock_get_client):
        """Missing confirmation stops the operation before accessing ChromaDB."""
        with self.assertRaisesRegex(VectorStoreError, "confirm=True"):
            reset_vector_store()

        mock_get_client.assert_not_called()

    @patch("app.services.vector_store.get_client")
    def test_reset_failure_is_wrapped_as_vector_store_error(self, mock_get_client):
        """Storage failures expose a consistent service-level exception."""
        client = MagicMock()
        client.list_collections.side_effect = RuntimeError("database locked")
        mock_get_client.return_value = client

        with self.assertRaisesRegex(VectorStoreError, "database locked"):
            reset_vector_store(confirm=True)

    @patch("app.services.vector_store.get_client")
    def test_reset_logs_metadata_without_document_content(self, mock_get_client):
        """Reset logs operational metadata but never indexed document content."""
        client = MagicMock()
        client.list_collections.return_value = []
        mock_get_client.return_value = client

        with self.assertLogs("app.services.vector_store", level="WARNING") as logs:
            reset_vector_store(confirm=True)

        combined_logs = " ".join(logs.output)
        self.assertIn("Vector store reset started", combined_logs)
        self.assertIn("Vector store reset completed", combined_logs)
        self.assertIn("deleted_records=0", combined_logs)
        self.assertNotIn("document_content", combined_logs)


if __name__ == "__main__":
    unittest.main()
