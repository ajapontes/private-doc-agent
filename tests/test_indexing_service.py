"""
Unit tests for the document indexing orchestration service.

These tests simulate chunking, Ollama embeddings, and vector persistence to
validate orchestration order, batching, results, and error handling without
reading local documents or modifying ChromaDB.
"""

import unittest
from unittest.mock import call, patch

from app.services.embedding_service import EmbeddingServiceError
from app.services.indexing_service import (
    IndexingServiceError,
    index_all_documents,
    index_document,
)


def _chunk(chunk_id: int, content: str) -> dict:
    """Builds representative chunk metadata for indexing tests."""
    return {
        "chunk_id": chunk_id,
        "filename": "demo.md",
        "content": content,
        "start_char": chunk_id * 10,
        "end_char": (chunk_id * 10) + len(content),
    }


class IndexingServiceTests(unittest.TestCase):
    """Validates the complete indexing orchestration without external calls."""

    @patch("app.services.indexing_service.upsert_chunks")
    @patch("app.services.indexing_service.delete_document_chunks")
    @patch("app.services.indexing_service.embed_documents")
    @patch("app.services.indexing_service.chunk_document")
    def test_document_is_chunked_embedded_and_persisted(
        self,
        mock_chunk_document,
        mock_embed_documents,
        mock_delete_document_chunks,
        mock_upsert_chunks,
    ):
        """One document flows through every indexing stage successfully."""
        chunks = [_chunk(0, "first"), _chunk(1, "second")]
        embeddings = [[1.0, 0.0], [0.0, 1.0]]
        mock_chunk_document.return_value = chunks
        mock_embed_documents.return_value = embeddings
        mock_upsert_chunks.return_value = 2

        result = index_document("demo.md")

        mock_chunk_document.assert_called_once_with("demo.md")
        mock_embed_documents.assert_called_once_with(["first", "second"])
        mock_delete_document_chunks.assert_called_once_with("demo.md")
        mock_upsert_chunks.assert_called_once_with(chunks, embeddings)
        self.assertEqual(result["filename"], "demo.md")
        self.assertEqual(result["chunks_indexed"], 2)
        self.assertEqual(result["vector_dimension"], 2)

    @patch("app.services.indexing_service.upsert_chunks", return_value=3)
    @patch("app.services.indexing_service.delete_document_chunks")
    @patch("app.services.indexing_service.embed_documents")
    @patch("app.services.indexing_service.chunk_document")
    @patch("app.services.indexing_service.EMBEDDING_BATCH_SIZE", 2)
    def test_embeddings_are_generated_in_configured_batches(
        self,
        mock_chunk_document,
        mock_embed_documents,
        _mock_delete,
        _mock_upsert,
    ):
        """Longer documents are sent to Ollama in bounded batches."""
        chunks = [
            _chunk(0, "first"),
            _chunk(1, "second"),
            _chunk(2, "third"),
        ]
        mock_chunk_document.return_value = chunks
        mock_embed_documents.side_effect = [
            [[1.0, 0.0], [0.0, 1.0]],
            [[0.5, 0.5]],
        ]

        result = index_document("demo.md")

        self.assertEqual(
            mock_embed_documents.call_args_list,
            [call(["first", "second"]), call(["third"])],
        )
        self.assertEqual(result["chunks_indexed"], 3)

    @patch("app.services.indexing_service.delete_document_chunks")
    @patch("app.services.indexing_service.embed_documents")
    @patch("app.services.indexing_service.chunk_document")
    def test_embedding_failure_preserves_previous_index(
        self,
        mock_chunk_document,
        mock_embed_documents,
        mock_delete_document_chunks,
    ):
        """Old records are not deleted when new embeddings cannot be created."""
        mock_chunk_document.return_value = [_chunk(0, "content")]
        mock_embed_documents.side_effect = EmbeddingServiceError("Ollama unavailable")

        with self.assertRaisesRegex(IndexingServiceError, "Ollama unavailable"):
            index_document("demo.md")

        mock_delete_document_chunks.assert_not_called()

    @patch("app.services.indexing_service.chunk_document", return_value=[])
    def test_empty_document_is_rejected(self, _mock_chunk_document):
        """Documents without indexable text are not sent to Ollama."""
        with self.assertRaisesRegex(IndexingServiceError, "does not contain indexable text"):
            index_document("empty.md")

    @patch("app.services.indexing_service.chunk_document")
    def test_missing_document_error_is_preserved(self, mock_chunk_document):
        """Missing-file errors remain available for a future HTTP 404 response."""
        mock_chunk_document.side_effect = FileNotFoundError("Document not found")

        with self.assertRaises(FileNotFoundError):
            index_document("missing.md")

    @patch("app.services.indexing_service.index_document")
    @patch("app.services.indexing_service.list_documents")
    def test_all_documents_are_indexed_and_aggregated(
        self,
        mock_list_documents,
        mock_index_document,
    ):
        """Bulk indexing returns document and chunk totals."""
        mock_list_documents.return_value = [
            {"filename": "first.md"},
            {"filename": "second.txt"},
        ]
        mock_index_document.side_effect = [
            {"filename": "first.md", "chunks_indexed": 2},
            {"filename": "second.txt", "chunks_indexed": 3},
        ]

        result = index_all_documents()

        self.assertEqual(result["documents_indexed"], 2)
        self.assertEqual(result["chunks_indexed"], 5)
        self.assertEqual(result["documents_invalid"], 0)
        self.assertEqual(mock_index_document.call_args_list, [call("first.md"), call("second.txt")])

    @patch("app.services.indexing_service.move_document_to_invalid")
    @patch("app.services.indexing_service.index_document")
    @patch("app.services.indexing_service.list_documents")
    def test_invalid_document_is_moved_and_remaining_documents_continue(
        self,
        mock_list_documents,
        mock_index_document,
        mock_move_document,
    ):
        """A bad document is quarantined without cancelling bulk indexing."""
        mock_list_documents.return_value = [
            {"filename": "broken.pdf"},
            {"filename": "valid.md"},
        ]
        mock_index_document.side_effect = [
            ValueError("Unable to read PDF document: broken.pdf"),
            {"filename": "valid.md", "chunks_indexed": 2},
        ]
        mock_move_document.return_value = {
            "filename": "broken.pdf",
            "invalid_path": "data/invalid/broken.pdf",
        }

        result = index_all_documents()

        self.assertEqual(result["documents_indexed"], 1)
        self.assertEqual(result["documents_invalid"], 1)
        self.assertEqual(result["chunks_indexed"], 2)
        mock_move_document.assert_called_once_with("broken.pdf")
        self.assertIn("Unable to read PDF", result["invalid_documents"][0]["error"])

    @patch("app.services.indexing_service.move_document_to_invalid")
    @patch("app.services.indexing_service.index_document")
    @patch("app.services.indexing_service.list_documents")
    def test_infrastructure_failure_stops_without_moving_document(
        self,
        mock_list_documents,
        mock_index_document,
        mock_move_document,
    ):
        """Ollama or vector failures must not quarantine a valid document."""
        mock_list_documents.return_value = [{"filename": "valid.md"}]
        mock_index_document.side_effect = IndexingServiceError(
            "Unable to index document: Ollama unavailable"
        )

        with self.assertRaisesRegex(IndexingServiceError, "Ollama unavailable"):
            index_all_documents()

        mock_move_document.assert_not_called()

    @patch("app.services.indexing_service.list_documents", return_value=[])
    def test_bulk_indexing_requires_documents(self, _mock_list_documents):
        """Bulk indexing reports when the input directory has no documents."""
        with self.assertRaisesRegex(IndexingServiceError, "No supported documents"):
            index_all_documents()


if __name__ == "__main__":
    unittest.main()
