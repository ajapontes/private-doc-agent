"""
Unit tests for the local document loader service.

These tests validate document discovery, text extraction dispatching, supported
formats, invalid files, and empty content without accessing the project's real
input directory or calling Ollama and ChromaDB.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.services import document_loader


class DocumentLoaderTests(unittest.TestCase):
    """Validates document discovery and local text extraction behavior."""

    def setUp(self):
        """Creates an isolated input directory for every test."""
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.input_directory = Path(self.temporary_directory.name)

        self.input_dir_patch = patch.object(
            document_loader,
            "INPUT_DIR",
            self.input_directory,
        )
        self.input_dir_patch.start()

    def tearDown(self):
        """Removes the isolated directory and restores patched configuration."""
        self.input_dir_patch.stop()
        self.temporary_directory.cleanup()

    def test_list_documents_returns_only_supported_files(self):
        """Document discovery includes all supported formats and ignores others."""
        (self.input_directory / "notes.txt").write_text("Text", encoding="utf-8")
        (self.input_directory / "guide.md").write_text("Markdown", encoding="utf-8")
        (self.input_directory / "report.pdf").write_bytes(b"pdf")
        (self.input_directory / "contract.docx").write_bytes(b"docx")
        (self.input_directory / "image.png").write_bytes(b"png")

        documents = document_loader.list_documents()

        filenames = {document["filename"] for document in documents}

        self.assertEqual(
            filenames,
            {"notes.txt", "guide.md", "report.pdf", "contract.docx"},
        )

    def test_list_unsupported_documents_returns_invalid_formats(self):
        """Unsupported files are exposed for bulk-index quarantine."""
        (self.input_directory / "notes.txt").write_text("Text", encoding="utf-8")
        (self.input_directory / "workbook.xlsx").write_bytes(b"xlsx")
        (self.input_directory / "README").write_text("no extension", encoding="utf-8")

        documents = document_loader.list_unsupported_documents()

        self.assertEqual(
            {document["filename"] for document in documents},
            {"workbook.xlsx", "README"},
        )
        extensions = {document["filename"]: document["extension"] for document in documents}
        self.assertEqual(extensions["workbook.xlsx"], ".xlsx")
        self.assertEqual(extensions["README"], "")

    def test_text_document_is_read_as_utf8(self):
        """UTF-8 TXT content is returned without modification."""
        file_path = self.input_directory / "notes.txt"
        file_path.write_text("Documento privado con acentos: información.", encoding="utf-8")

        content = document_loader.read_document("notes.txt")

        self.assertEqual(content, "Documento privado con acentos: información.")

    def test_unicode_filename_is_preserved_during_discovery(self):
        """Discovery returns the exact physical name without normalization."""
        filename = "2025 innovación técnica — versión ñ.txt"
        (self.input_directory / filename).write_text("Contenido", encoding="utf-8")

        documents = document_loader.list_documents()

        self.assertEqual(documents[0]["filename"], filename)

    def test_apparently_damaged_filename_is_read_without_renaming(self):
        """Suspicious-looking names remain valid opaque document identifiers."""
        filename = "innovacinnn tecnolnngica.md"
        (self.input_directory / filename).write_text("Contenido", encoding="utf-8")

        content = document_loader.read_document(filename)

        self.assertEqual(content, "Contenido")

    def test_markdown_document_is_read_as_utf8(self):
        """Markdown documents use the same UTF-8 reader as plain text."""
        file_path = self.input_directory / "guide.md"
        file_path.write_text("# Private document", encoding="utf-8")

        content = document_loader.read_document("guide.md")

        self.assertEqual(content, "# Private document")

    def test_invalid_utf8_text_is_rejected(self):
        """Plain-text files with invalid UTF-8 bytes produce a controlled error."""
        file_path = self.input_directory / "invalid.txt"
        file_path.write_bytes(b"\xff\xfe\xfa")

        with self.assertRaisesRegex(ValueError, "not valid UTF-8"):
            document_loader.read_document("invalid.txt")

    @patch("app.services.document_loader.PdfReader")
    def test_pdf_text_is_extracted_by_page(self, mock_pdf_reader):
        """Extractable PDF pages are joined with blank lines."""
        first_page = MagicMock()
        first_page.extract_text.return_value = "First page"

        empty_page = MagicMock()
        empty_page.extract_text.return_value = None

        third_page = MagicMock()
        third_page.extract_text.return_value = "Third page"

        reader = MagicMock()
        reader.is_encrypted = False
        reader.pages = [first_page, empty_page, third_page]
        mock_pdf_reader.return_value = reader

        (self.input_directory / "report.pdf").write_bytes(b"mock pdf")

        content = document_loader.read_document("report.pdf")

        self.assertEqual(content, "First page\n\nThird page")

    @patch("app.services.document_loader.PdfReader")
    def test_encrypted_pdf_is_rejected(self, mock_pdf_reader):
        """Encrypted PDF documents return an explicit unsupported error."""
        reader = MagicMock()
        reader.is_encrypted = True
        mock_pdf_reader.return_value = reader

        (self.input_directory / "encrypted.pdf").write_bytes(b"mock pdf")

        with self.assertRaisesRegex(ValueError, "Encrypted PDF"):
            document_loader.read_document("encrypted.pdf")

    @patch("app.services.document_loader.PdfReader")
    def test_pdf_without_extractable_text_is_rejected(self, mock_pdf_reader):
        """Image-only or blank PDF documents do not produce empty content."""
        page = MagicMock()
        page.extract_text.return_value = "   "

        reader = MagicMock()
        reader.is_encrypted = False
        reader.pages = [page]
        mock_pdf_reader.return_value = reader

        (self.input_directory / "scanned.pdf").write_bytes(b"mock pdf")

        with self.assertRaisesRegex(ValueError, "no extractable text"):
            document_loader.read_document("scanned.pdf")

    @patch(
        "app.services.document_loader.PdfReader",
        side_effect=RuntimeError("Damaged PDF"),
    )
    def test_damaged_pdf_is_rejected(self, _mock_pdf_reader):
        """PDF parser failures are converted into controlled loader errors."""
        (self.input_directory / "damaged.pdf").write_bytes(b"invalid pdf")

        with self.assertRaisesRegex(ValueError, "Unable to read PDF"):
            document_loader.read_document("damaged.pdf")

    @patch("app.services.document_loader.Document")
    def test_docx_paragraphs_are_extracted(self, mock_document):
        """Non-empty DOCX paragraphs are returned separated by blank lines."""
        first_paragraph = MagicMock()
        first_paragraph.text = "First paragraph"

        empty_paragraph = MagicMock()
        empty_paragraph.text = "   "

        third_paragraph = MagicMock()
        third_paragraph.text = "Third paragraph"

        mock_document.return_value.paragraphs = [
            first_paragraph,
            empty_paragraph,
            third_paragraph,
        ]

        (self.input_directory / "contract.docx").write_bytes(b"mock docx")

        content = document_loader.read_document("contract.docx")

        self.assertEqual(content, "First paragraph\n\nThird paragraph")

    @patch("app.services.document_loader.Document")
    def test_empty_docx_is_rejected(self, mock_document):
        """DOCX documents without textual paragraphs are rejected."""
        paragraph = MagicMock()
        paragraph.text = "   "
        mock_document.return_value.paragraphs = [paragraph]

        (self.input_directory / "empty.docx").write_bytes(b"mock docx")

        with self.assertRaisesRegex(ValueError, "no extractable text"):
            document_loader.read_document("empty.docx")

    @patch(
        "app.services.document_loader.Document",
        side_effect=RuntimeError("Damaged DOCX"),
    )
    def test_damaged_docx_is_rejected(self, _mock_document):
        """DOCX parser failures are converted into controlled loader errors."""
        (self.input_directory / "damaged.docx").write_bytes(b"invalid docx")

        with self.assertRaisesRegex(ValueError, "Unable to read DOCX"):
            document_loader.read_document("damaged.docx")

    @patch("app.services.document_loader._read_pdf_document")
    def test_uppercase_extension_uses_expected_reader(self, mock_pdf_reader):
        """Supported extensions are matched without distinguishing case."""
        file_path = self.input_directory / "REPORT.PDF"
        file_path.write_bytes(b"mock pdf")
        mock_pdf_reader.return_value = "Extracted content"

        content = document_loader.read_document("REPORT.PDF")

        mock_pdf_reader.assert_called_once_with(file_path)
        self.assertEqual(content, "Extracted content")

    def test_missing_document_is_rejected(self):
        """A missing document preserves the expected file-not-found error."""
        with self.assertRaisesRegex(FileNotFoundError, "Document not found"):
            document_loader.read_document("missing.txt")

    def test_unsupported_extension_is_rejected(self):
        """Existing files with unsupported extensions are not processed."""
        (self.input_directory / "image.png").write_bytes(b"png")

        with self.assertRaisesRegex(ValueError, "Unsupported file extension"):
            document_loader.read_document("image.png")


if __name__ == "__main__":
    unittest.main()
