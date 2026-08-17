"""
Unit tests for centralized application configuration.

The tests load a separate copy of the configuration module for each case so
environment overrides can be validated without changing configuration already
imported by other tests.
"""

import importlib.util
import os
import unittest
from pathlib import Path
from unittest.mock import patch


CONFIG_PATH = Path(__file__).resolve().parent.parent / "app" / "config.py"


def load_config():
    """Loads an isolated configuration module without reading the local .env."""
    spec = importlib.util.spec_from_file_location(
        "test_runtime_config",
        CONFIG_PATH,
    )
    module = importlib.util.module_from_spec(spec)

    with patch("dotenv.load_dotenv"):
        spec.loader.exec_module(module)

    return module


class ConfigurationTests(unittest.TestCase):
    """Validates defaults, conversions, and early configuration failures."""

    def test_new_configuration_defaults_are_safe(self):
        """New retrieval and sensitive-log settings use safe defaults."""
        with patch.dict(os.environ, {}, clear=True):
            config = load_config()

        self.assertEqual(config.APP_VERSION, "0.10.0")
        self.assertEqual(config.OLLAMA_REQUEST_TIMEOUT_SECONDS, 120)
        self.assertEqual(config.OLLAMA_MAX_RETRIES, 2)
        self.assertEqual(config.VECTOR_DISTANCE_METRIC, "cosine")
        self.assertEqual(config.VECTOR_SEARCH_TOP_K, 5)
        self.assertIsNone(config.VECTOR_MIN_RELEVANCE_SCORE)
        self.assertFalse(config.LOG_SENSITIVE_CONTENT)
        self.assertFalse(config.DETAILED_TRACE_ENABLED)
        self.assertIsNone(config.API_KEY)
        self.assertFalse(config.API_KEY_PROTECT_ALL)

    def test_api_key_is_trimmed_and_loaded(self):
        """A configured API key is loaded without surrounding whitespace."""
        with patch.dict(os.environ, {"API_KEY": "  local-secret  "}, clear=True):
            config = load_config()

        self.assertEqual(config.API_KEY, "local-secret")

    def test_api_key_protect_all_requires_boolean_value(self):
        """Full API protection accepts only explicit boolean configuration."""
        with patch.dict(os.environ, {"API_KEY_PROTECT_ALL": "yes"}, clear=True):
            with self.assertRaisesRegex(ValueError, "true or false"):
                load_config()

    def test_detailed_trace_requires_boolean_value(self):
        """Detailed tracing accepts only an explicit true or false value."""
        with patch.dict(
            os.environ, {"DETAILED_TRACE_ENABLED": "yes"}, clear=True
        ):
            with self.assertRaisesRegex(ValueError, "true or false"):
                load_config()

    def test_supported_vector_metric_is_normalized(self):
        """A supported metric is accepted regardless of case or whitespace."""
        with patch.dict(
            os.environ, {"VECTOR_DISTANCE_METRIC": " L2 "}, clear=True
        ):
            config = load_config()

        self.assertEqual(config.VECTOR_DISTANCE_METRIC, "l2")

    def test_invalid_vector_metric_is_rejected(self):
        """Unsupported distance metrics fail while configuration is loaded."""
        with patch.dict(
            os.environ, {"VECTOR_DISTANCE_METRIC": "manhattan"}, clear=True
        ):
            with self.assertRaisesRegex(ValueError, "VECTOR_DISTANCE_METRIC"):
                load_config()

    def test_chunk_overlap_must_be_smaller_than_chunk_size(self):
        """Invalid chunk boundaries are rejected before chunking starts."""
        with patch.dict(
            os.environ,
            {"CHUNK_SIZE": "100", "CHUNK_OVERLAP": "100"},
            clear=True,
        ):
            with self.assertRaisesRegex(ValueError, "must be smaller"):
                load_config()

    def test_positive_numeric_configuration_is_validated(self):
        """Batch size and retrieval result count must be positive integers."""
        for variable_name in ("EMBEDDING_BATCH_SIZE", "VECTOR_SEARCH_TOP_K"):
            with self.subTest(variable_name=variable_name):
                with patch.dict(
                    os.environ, {variable_name: "0"}, clear=True
                ):
                    with self.assertRaisesRegex(ValueError, variable_name):
                        load_config()

    def test_sensitive_content_logging_requires_boolean_value(self):
        """Sensitive logging cannot be enabled by an ambiguous value."""
        with patch.dict(
            os.environ, {"LOG_SENSITIVE_CONTENT": "yes"}, clear=True
        ):
            with self.assertRaisesRegex(ValueError, "true or false"):
                load_config()

    def test_optional_relevance_score_accepts_blank_or_number(self):
        """The relevance filter supports a disabled or numeric value."""
        with patch.dict(
            os.environ, {"VECTOR_MIN_RELEVANCE_SCORE": "0.75"}, clear=True
        ):
            config = load_config()

        self.assertEqual(config.VECTOR_MIN_RELEVANCE_SCORE, 0.75)


if __name__ == "__main__":
    unittest.main()
