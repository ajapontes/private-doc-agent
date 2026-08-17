"""HTTP integration tests for optional API key authentication."""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


class ApiKeyAuthenticationApiTests(unittest.TestCase):
    """Validates HTTP status mappings and protected endpoint behavior."""

    @patch("app.main.API_KEY", "configured-secret")
    def test_missing_key_returns_401_for_admin_endpoint(self):
        with TestClient(app) as client:
            response = client.post("/admin/vector-store/reset", json={"confirm": True})

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "API key is required.")
        self.assertEqual(response.headers["www-authenticate"], "ApiKey")

    @patch("app.main.API_KEY", "configured-secret")
    def test_invalid_key_returns_403_for_admin_endpoint(self):
        with TestClient(app) as client:
            response = client.post(
                "/admin/vector-store/reset",
                json={"confirm": True},
                headers={"X-API-Key": "wrong-secret"},
            )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"], "Invalid API key.")

    @patch("app.main.API_KEY", "configured-secret")
    @patch("app.main.reset_vector_store", return_value=2)
    def test_valid_key_allows_admin_endpoint(self, _mock_reset):
        with TestClient(app) as client:
            response = client.post(
                "/admin/vector-store/reset",
                json={"confirm": True},
                headers={"X-API-Key": "configured-secret"},
            )

        self.assertEqual(response.status_code, 200)

    @patch("app.main.API_KEY", "configured-secret")
    @patch("app.main.API_KEY_PROTECT_ALL", True)
    def test_full_protection_rejects_operational_endpoint_without_key(self):
        with TestClient(app) as client:
            response = client.get("/documents")

        self.assertEqual(response.status_code, 401)

    @patch("app.main.API_KEY", "configured-secret")
    @patch("app.main.API_KEY_PROTECT_ALL", True)
    @patch("app.main.list_documents", return_value=[])
    def test_full_protection_accepts_operational_endpoint_with_key(self, _mock_list):
        with TestClient(app) as client:
            response = client.get(
                "/documents", headers={"X-API-Key": "configured-secret"}
            )

        self.assertEqual(response.status_code, 200)

    @patch("app.main.API_KEY", "configured-secret")
    @patch("app.main.API_KEY_PROTECT_ALL", True)
    @patch("app.main.check_dependencies", return_value={})
    def test_health_remains_public(self, _mock_health):
        with TestClient(app) as client:
            response = client.get("/health")

        self.assertEqual(response.status_code, 200)

    @patch("app.main.API_KEY", "configured-secret")
    def test_rejection_logs_do_not_expose_supplied_key(self):
        supplied_key = "never-log-this-secret"
        with self.assertLogs("app.main", level="WARNING") as captured_logs:
            with TestClient(app) as client:
                response = client.post(
                    "/admin/vector-store/reset",
                    json={"confirm": True},
                    headers={"X-API-Key": supplied_key},
                )

        self.assertEqual(response.status_code, 403)
        self.assertNotIn(supplied_key, "\n".join(captured_logs.output))
