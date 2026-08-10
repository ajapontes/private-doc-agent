"""
Integration tests for the local ChromaDB vector store.

Each test uses a temporary persistent database and handcrafted vectors.
This validates real ChromaDB storage and retrieval without using Ollama,
private documents, or the project's local ``data/chroma`` directory.
"""

import gc
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.services.vector_store import (
    VectorStoreError,
    close_vector_store,
    count_stored_chunks,
    delete_document_chunks,
    delete_stale_document_chunks,
    query_chunks,
    reset_vector_store,
    upsert_chunks,
)


class VectorStoreTests(unittest.TestCase):
    """Validates persistent chunk storage and vector similarity retrieval."""

    def setUp(self):
        """Creates an isolated ChromaDB directory for each test."""
        self.temporary_directory = tempfile.TemporaryDirectory(
            ignore_cleanup_errors=True
        )
        self.path_patch = patch(
            "app.services.vector_store.CHROMA_DIR",
            Path(self.temporary_directory.name),
        )
        self.path_patch.start()

    def tearDown(self):
        """Releases the isolated ChromaDB directory after each test."""
        close_vector_store()
        gc.collect()
        self.path_patch.stop()
        self.temporary_directory.cleanup()

    @staticmethod
    def _chunks() -> list[dict]:
        """Returns two representative chunk records for vector tests."""
        return [
            {
                "chunk_id": 0,
                "filename": "demo.txt",
                "content": "A private document assistant.",
                "start_char": 0,
                "end_char": 29,
            },
            {
                "chunk_id": 1,
                "filename": "demo.txt",
                "content": "A public weather report.",
                "start_char": 20,
                "end_char": 44,
            },
        ]

    def test_chunks_are_persisted_with_metadata(self):
        """Chunks, vectors, content, and metadata are stored together."""
        written = upsert_chunks(self._chunks(), [[1.0, 0.0], [0.0, 1.0]])

        self.assertEqual(written, 2)
        self.assertEqual(count_stored_chunks(), 2)

    def test_upsert_updates_existing_records_without_duplicates(self):
        """Stable IDs allow reindexing to update existing chunk records."""
        chunks = self._chunks()
        upsert_chunks(chunks, [[1.0, 0.0], [0.0, 1.0]])
        chunks[0]["content"] = "Updated private assistant content."

        upsert_chunks(chunks, [[1.0, 0.0], [0.0, 1.0]])

        self.assertEqual(count_stored_chunks(), 2)

    def test_query_returns_closest_chunk_first(self):
        """Cosine search ranks the most similar handcrafted vector first."""
        upsert_chunks(self._chunks(), [[1.0, 0.0], [0.0, 1.0]])

        matches = query_chunks([0.9, 0.1], top_k=2)

        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0]["chunk_id"], 0)
        self.assertLess(matches[0]["distance"], matches[1]["distance"])

    def test_query_empty_collection_returns_no_matches(self):
        """Searching before indexing returns an empty result safely."""
        self.assertEqual(query_chunks([1.0, 0.0]), [])

    def test_document_chunks_can_be_deleted_by_filename(self):
        """Reindexing can remove all old chunks for one source document."""
        upsert_chunks(self._chunks(), [[1.0, 0.0], [0.0, 1.0]])

        delete_document_chunks("demo.txt")

        self.assertEqual(count_stored_chunks(), 0)

    def test_reindexing_deletes_only_stale_document_chunks(self):
        """Chunks absent from the replacement are removed after its upsert."""
        chunks = self._chunks()
        upsert_chunks(chunks, [[1.0, 0.0], [0.0, 1.0]])

        deleted = delete_stale_document_chunks("demo.txt", {0})

        self.assertEqual(deleted, 1)
        self.assertEqual(count_stored_chunks(), 1)

    def test_vector_store_can_be_reset_with_explicit_confirmation(self):
        """A confirmed reset removes all records and recreates the collection."""
        upsert_chunks(self._chunks(), [[1.0, 0.0], [0.0, 1.0]])

        deleted_count = reset_vector_store(confirm=True)

        self.assertEqual(deleted_count, 2)
        self.assertEqual(count_stored_chunks(), 0)

    def test_vector_store_reset_requires_explicit_confirmation(self):
        """Resetting indexed data is rejected unless explicitly confirmed."""
        with self.assertRaisesRegex(VectorStoreError, "confirm=True"):
            reset_vector_store()

    def test_mismatched_chunk_and_embedding_counts_are_rejected(self):
        """Every chunk must have exactly one corresponding vector."""
        with self.assertRaisesRegex(VectorStoreError, "does not match"):
            upsert_chunks(self._chunks(), [[1.0, 0.0]])

    def test_empty_query_embedding_is_rejected(self):
        """A vector search requires a non-empty query embedding."""
        with self.assertRaisesRegex(VectorStoreError, "cannot be empty"):
            query_chunks([])

    def test_invalid_result_count_is_rejected(self):
        """A vector search must request at least one result."""
        with self.assertRaisesRegex(VectorStoreError, "greater than zero"):
            query_chunks([1.0, 0.0], top_k=0)


if __name__ == "__main__":
    unittest.main()
