"""Unit tests for invalid-document quarantine behavior."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.services.document_loader import move_document_to_invalid


class DocumentQuarantineTests(unittest.TestCase):
    """Validates safe movement and collision handling for invalid files."""

    def test_document_is_moved_without_overwriting_existing_file(self):
        """A numeric suffix preserves an existing quarantined document."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            input_dir = root / "data" / "input"
            invalid_dir = root / "data" / "invalid"
            input_dir.mkdir(parents=True)
            invalid_dir.mkdir(parents=True)
            (input_dir / "broken.pdf").write_bytes(b"new")
            (invalid_dir / "broken.pdf").write_bytes(b"old")

            with patch("app.services.document_loader.INPUT_DIR", input_dir), patch(
                "app.services.document_loader.INVALID_DIR", invalid_dir
            ):
                result = move_document_to_invalid("broken.pdf")

            self.assertFalse((input_dir / "broken.pdf").exists())
            self.assertEqual((invalid_dir / "broken.pdf").read_bytes(), b"old")
            self.assertEqual((invalid_dir / "broken_1.pdf").read_bytes(), b"new")
            self.assertEqual(Path(result["invalid_path"]),Path("data/invalid/broken_1.pdf"),)


if __name__ == "__main__":
    unittest.main()
