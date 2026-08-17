"""Unit tests for API key validation and protected-path selection."""

import unittest
from unittest.mock import patch

from app.security import ApiKeyStatus, requires_api_key, validate_api_key


class ApiKeySecurityTests(unittest.TestCase):
    """Validates secure, backward-compatible API key behavior."""

    def test_authentication_is_disabled_without_configured_key(self):
        self.assertEqual(validate_api_key(None, None), ApiKeyStatus.DISABLED)

    def test_missing_key_is_rejected_when_authentication_is_enabled(self):
        self.assertEqual(validate_api_key("secret", None), ApiKeyStatus.MISSING)

    def test_invalid_key_is_rejected(self):
        self.assertEqual(validate_api_key("secret", "wrong"), ApiKeyStatus.INVALID)

    @patch("app.security.secrets.compare_digest", return_value=True)
    def test_valid_key_uses_constant_time_comparison(self, compare_digest):
        self.assertEqual(
            validate_api_key("secret", "secret"), ApiKeyStatus.AUTHENTICATED
        )
        compare_digest.assert_called_once_with("secret", "secret")

    def test_admin_paths_are_always_sensitive(self):
        self.assertTrue(requires_api_key("/admin/vector-store/reset", False))

    def test_full_protection_keeps_health_and_docs_public(self):
        self.assertFalse(requires_api_key("/health", True))
        self.assertFalse(requires_api_key("/docs", True))
        self.assertTrue(requires_api_key("/documents", True))
