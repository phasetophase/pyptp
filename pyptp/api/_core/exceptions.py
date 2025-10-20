"""API-specific exceptions for PyPtP cloud services."""

from __future__ import annotations


class APIError(Exception):
    """Base exception for all API-related errors."""


class APIConfigurationError(APIError):
    """Raised when API configuration is missing or invalid."""


class APIAuthenticationError(APIError):
    """Raised when authentication fails."""


class APIEnvironmentError(APIError):
    """Raised when an invalid environment is specified."""
