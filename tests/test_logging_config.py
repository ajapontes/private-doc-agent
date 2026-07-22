"""Unit tests for application-wide logging configuration."""

import logging
import unittest
from unittest.mock import MagicMock, patch

from app import logging_config


class LoggingConfigTests(unittest.TestCase):
    """Validates logging initialization outside the FastAPI entry point."""

    def test_setup_adds_owned_handlers_when_foreign_handler_exists(self):
        """An unrelated runtime handler must not prevent file logging setup."""
        root_logger = logging.getLogger()
        foreign_handler = logging.NullHandler()
        original_handlers = root_logger.handlers[:]

        try:
            root_logger.handlers = [foreign_handler]

            with patch.object(logging_config, "RotatingFileHandler") as handler_class:
                handler_class.return_value = MagicMock(spec=logging.Handler)
                logging_config.setup_logging()

            self.assertEqual(handler_class.call_count, 1)
            self.assertEqual(len(root_logger.handlers), 3)
        finally:
            root_logger.handlers = original_handlers

    def test_setup_is_idempotent_for_application_handlers(self):
        """Repeated initialization must not duplicate application handlers."""
        root_logger = logging.getLogger()
        original_handlers = root_logger.handlers[:]

        try:
            root_logger.handlers = []

            with patch.object(logging_config, "RotatingFileHandler") as handler_class:
                handler_class.return_value = MagicMock(spec=logging.Handler)
                logging_config.setup_logging()
                handler_count = len(root_logger.handlers)
                logging_config.setup_logging()

            self.assertEqual(handler_class.call_count, 1)
            self.assertEqual(len(root_logger.handlers), handler_count)
        finally:
            root_logger.handlers = original_handlers


if __name__ == "__main__":
    unittest.main()
