"""Tests for bounded retries used by local Ollama requests."""

import unittest
from unittest.mock import Mock, patch

import requests

from app.services.ollama_transport import OllamaTransportError, post_json


class OllamaTransportTests(unittest.TestCase):
    """Validates retry and fail-fast behavior without network access."""

    @patch("app.services.ollama_transport.time.sleep")
    @patch("app.services.ollama_transport.OLLAMA_MAX_RETRIES", 2)
    def test_transient_failure_is_retried(self, mock_sleep):
        requester = Mock()
        success = Mock()
        success.json.return_value = {"response": "ok"}
        requester.side_effect = [
            requests.exceptions.ConnectionError("temporary"),
            success,
        ]

        result = post_json("http://ollama/api", {}, requester=requester)

        self.assertEqual(result, {"response": "ok"})
        self.assertEqual(requester.call_count, 2)
        mock_sleep.assert_called_once()

    @patch("app.services.ollama_transport.time.sleep")
    @patch("app.services.ollama_transport.OLLAMA_MAX_RETRIES", 2)
    def test_client_error_is_not_retried(self, mock_sleep):
        response = Mock(status_code=404)
        error = requests.exceptions.HTTPError("not found", response=response)
        response.raise_for_status.side_effect = error
        requester = Mock(return_value=response)

        with self.assertRaisesRegex(OllamaTransportError, "not found"):
            post_json("http://ollama/api", {}, requester=requester)

        requester.assert_called_once()
        mock_sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()
