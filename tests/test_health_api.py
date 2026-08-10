"""API tests for detailed dependency health reporting."""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


class HealthApiTests(unittest.TestCase):
    """Validates healthy and degraded API status responses."""

    @patch("app.main.check_dependencies")
    def test_health_reports_available_dependencies(self, mock_check):
        mock_check.return_value = {
            "ollama": {"status": "ok"},
            "vector_store": {"status": "ok", "stored_chunks": 12},
        }

        with TestClient(app) as client:
            response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertEqual(
            response.json()["components"]["vector_store"]["stored_chunks"], 12
        )

    @patch("app.main.check_dependencies")
    def test_health_reports_degraded_dependency(self, mock_check):
        mock_check.return_value = {
            "ollama": {"status": "unavailable", "error_type": "ConnectionError"},
            "vector_store": {"status": "ok", "stored_chunks": 0},
        }

        with TestClient(app) as client:
            response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "degraded")


if __name__ == "__main__":
    unittest.main()
