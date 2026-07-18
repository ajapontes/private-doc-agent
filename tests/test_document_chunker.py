"""
Unit tests for the document chunking service.

These tests validate deterministic chunk boundaries, overlap behavior,
metadata, empty input handling, and invalid configuration without calling
the local LLM or requiring a vector database.
"""

import unittest

from app.services.document_chunker import chunk_text


class DocumentChunkerTests(unittest.TestCase):
    """Validates the behavior of the character-based chunking service."""

    def test_short_text_creates_one_chunk(self):
        """Text shorter than the configured size remains in one chunk."""
        chunks = chunk_text("Private document", "demo.txt", chunk_size=50, chunk_overlap=10)

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["chunk_id"], 0)
        self.assertEqual(chunks[0]["filename"], "demo.txt")
        self.assertEqual(chunks[0]["content"], "Private document")
        self.assertEqual(chunks[0]["start_char"], 0)
        self.assertEqual(chunks[0]["end_char"], 16)

    def test_long_text_creates_overlapping_chunks(self):
        """Adjacent chunks repeat the configured number of characters."""
        chunks = chunk_text("abcdefghijkl", "demo.txt", chunk_size=5, chunk_overlap=2)

        self.assertEqual([chunk["content"] for chunk in chunks], ["abcde", "defgh", "ghijk", "jkl"])
        self.assertEqual(chunks[0]["content"][-2:], chunks[1]["content"][:2])
        self.assertEqual(chunks[1]["content"][-2:], chunks[2]["content"][:2])

    def test_empty_or_whitespace_text_creates_no_chunks(self):
        """Empty documents do not create meaningless chunks."""
        self.assertEqual(chunk_text("", "empty.txt", chunk_size=10, chunk_overlap=2), [])
        self.assertEqual(chunk_text("   \n", "empty.txt", chunk_size=10, chunk_overlap=2), [])

    def test_invalid_chunk_size_is_rejected(self):
        """A chunk size must always be positive."""
        with self.assertRaisesRegex(ValueError, "greater than zero"):
            chunk_text("content", "demo.txt", chunk_size=0, chunk_overlap=0)

    def test_negative_overlap_is_rejected(self):
        """Overlap cannot use a negative number of characters."""
        with self.assertRaisesRegex(ValueError, "cannot be negative"):
            chunk_text("content", "demo.txt", chunk_size=10, chunk_overlap=-1)

    def test_overlap_must_be_smaller_than_chunk_size(self):
        """Overlap cannot consume the complete chunk window."""
        with self.assertRaisesRegex(ValueError, "smaller than chunk size"):
            chunk_text("content", "demo.txt", chunk_size=10, chunk_overlap=10)


if __name__ == "__main__":
    unittest.main()
