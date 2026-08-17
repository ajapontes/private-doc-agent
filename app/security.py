"""Security helpers for optional HTTP API key authentication.

The application remains open for local backward compatibility when no API key
is configured. When authentication is enabled, supplied secrets are compared
in constant time and are never included in errors or log messages.
"""

import secrets
from enum import Enum


class ApiKeyStatus(str, Enum):
    """Possible outcomes of validating a request API key."""

    DISABLED = "disabled"
    AUTHENTICATED = "authenticated"
    MISSING = "missing"
    INVALID = "invalid"


PUBLIC_PATHS = {"/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico"}


def validate_api_key(configured_key: str | None, supplied_key: str | None) -> ApiKeyStatus:
    """Validates an optional API key without exposing either secret."""
    if configured_key is None:
        return ApiKeyStatus.DISABLED
    if supplied_key is None or not supplied_key:
        return ApiKeyStatus.MISSING
    if secrets.compare_digest(configured_key, supplied_key):
        return ApiKeyStatus.AUTHENTICATED
    return ApiKeyStatus.INVALID


def requires_api_key(path: str, protect_all: bool) -> bool:
    """Returns whether a path belongs to the configured protected surface."""
    if path.startswith("/admin/"):
        return True
    return protect_all and path not in PUBLIC_PATHS
