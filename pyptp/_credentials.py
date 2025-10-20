# SPDX-FileCopyrightText: Contributors to the PyPtP project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Credential management for PyPtP API access."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class PyPtPCredentials(BaseSettings):
    """API credentials - can be set via env vars or passed explicitly.

    Environment variables (optional):
        PYPTP_CLIENT_ID: API client ID
        PYPTP_CLIENT_SECRET: API client secret
        PYPTP_ENVIRONMENT: API environment (production/acceptance/test)
        PYPTP_TIMEOUT: Request timeout in seconds
        PYPTP_MAX_RETRIES: Maximum retry attempts
        PYPTP_VERIFY_SSL: Whether to verify SSL certificates

    Examples:
        >>> # From env vars
        >>> creds = PyPtPCredentials()

        >>> # Explicit
        >>> creds = PyPtPCredentials(
        ...     client_id="your_id",
        ...     client_secret="your_secret"
        ... )

    """

    model_config = SettingsConfigDict(
        env_prefix="PYPTP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    client_id: str | None = None
    client_secret: str | None = None
    environment: str = "production"
    timeout: int = 120
    max_retries: int = 3
    verify_ssl: bool = True


__all__ = ["PyPtPCredentials"]
