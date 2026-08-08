"""HTTP API tests for the guarded vector-store reset endpoint.

These tests replace the storage reset service with controlled outcomes. They
verify explicit confirmation, structured responses, HTTP error mappings, and
privacy-safe logging without deleting a real ChromaDB collection.
"""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.vector_store import VectorStoreError


class VectorStoreResetApiTests(unittest.TestCase):
    """Validates the administrative vector collection reset endpoint."""

    @patch("app.main.reset_vector_store")
    def test_confirmed_reset_returns_structured_result(self, mock_reset):
        """A confirmed request returns the active configuration and count."""
        mock_reset.return_value = 23

        with TestClient(app) as client:
            response = client.post(
                "/admin/vector-store/reset",
                json={"confirm": True},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "reset",
                "collection": "private_documents",
                "metric": "cosine",
                "deleted_records": 23,
            },
        )
        mock_reset.assert_called_once_with(confirm=True)

    @patch("app.main.reset_vector_store")
    def test_false_confirmation_returns_400_without_resetting(self, mock_reset):
        """An explicitly false confirmation never reaches the storage layer."""
        with TestClient(app) as client:
            response = client.post(
                "/admin/vector-store/reset",
                json={"confirm": False},
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["detail"],
            "Vector store reset requires confirm=true.",
        )
        mock_reset.assert_not_called()

    @patch("app.main.reset_vector_store")
    def test_missing_confirmation_returns_400_without_resetting(self, mock_reset):
        """The safe default rejects a request that omits confirmation."""
        with TestClient(app) as client:
            response = client.post("/admin/vector-store/reset", json={})

        self.assertEqual(response.status_code, 400)
        mock_reset.assert_not_called()

    @patch("app.main.reset_vector_store")
    def test_vector_store_failure_returns_500(self, mock_reset):
        """Controlled storage failures map to an internal-server response."""
        mock_reset.side_effect = VectorStoreError("database locked")

        with TestClient(app) as client:
            response = client.post(
                "/admin/vector-store/reset",
                json={"confirm": True},
            )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["detail"], "database locked")

    @patch("app.main.reset_vector_store")
    def test_reset_api_logs_do_not_expose_indexed_content(self, mock_reset):
        """API logs contain operational metadata but no document content."""
        private_content = "CONFIDENTIAL indexed document content"
        mock_reset.return_value = 4

        with self.assertLogs("app.main", level="WARNING") as captured_logs:
            with TestClient(app) as client:
                response = client.post(
                    "/admin/vector-store/reset",
                    json={"confirm": True},
                )

        log_output = "\n".join(captured_logs.output)
        self.assertEqual(response.status_code, 200)
        self.assertIn("deleted_records=4", log_output)
        self.assertIn("collection=private_documents", log_output)
        self.assertNotIn(private_content, log_output)


if __name__ == "__main__":
    unittest.main()
