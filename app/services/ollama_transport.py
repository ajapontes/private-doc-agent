"""Reliable local HTTP transport shared by Ollama-facing services.

Only transient connection errors and HTTP 5xx responses are retried. Client
errors such as a missing model or invalid endpoint are returned immediately.
"""

import logging
import time

import requests

from app.config import OLLAMA_MAX_RETRIES, OLLAMA_REQUEST_TIMEOUT_SECONDS


logger = logging.getLogger(__name__)


class OllamaTransportError(Exception):
    """Raised when an Ollama request cannot complete after safe retries."""


def post_json(endpoint: str, payload: dict, requester=requests.post) -> dict:
    """Posts JSON to Ollama and returns a decoded object with bounded retries."""
    attempts = OLLAMA_MAX_RETRIES + 1
    last_error = None

    for attempt in range(1, attempts + 1):
        try:
            response = requester(
                endpoint,
                json=payload,
                timeout=OLLAMA_REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.RequestException, ValueError) as error:
            last_error = error
            status_code = getattr(getattr(error, "response", None), "status_code", None)
            retryable = status_code is None or status_code >= 500
            if not retryable or attempt == attempts:
                break
            logger.warning(
                "Transient Ollama request failure. endpoint=%s attempt=%s max_attempts=%s",
                endpoint,
                attempt,
                attempts,
            )
            time.sleep(min(0.25 * attempt, 1.0))

    raise OllamaTransportError(str(last_error)) from last_error
