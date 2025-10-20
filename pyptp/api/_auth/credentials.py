"""Credential loading and management."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from pathlib import Path


def load_env_file(env_path: Path) -> dict[str, str]:
    """Load environment variables from .env file.

    Args:
        env_path: Path to .env file.

    Returns:
        Dictionary of environment variables.

    """
    env_vars = {}

    if not env_path.exists():
        return env_vars

    try:
        with env_path.open() as f:
            for raw_line in f:
                line_content = raw_line.strip()
                if line_content and not line_content.startswith("#") and "=" in line_content:
                    key, value = line_content.split("=", 1)
                    value = value.strip().strip("'\"")
                    env_vars[key] = value
    except OSError as e:
        logger.warning("Error reading .env file: %s", e)

    return env_vars


def load_credentials(
    client_id: str | None = None,
    client_secret: str | None = None,
    environment: str | None = None,
) -> tuple[str | None, str | None, str]:
    """Load credentials from various sources.

    Order of precedence:
    1. Explicit parameters
    2. Environment variables (via PyPtPCredentials)
    3. .env file (via PyPtPCredentials)

    Args:
        client_id: Explicit client ID.
        client_secret: Explicit client secret.
        environment: Explicit environment name.

    Returns:
        Tuple of (client_id, client_secret, environment).

    """
    from pyptp._credentials import PyPtPCredentials

    # If all provided explicitly, return as-is
    if client_id and client_secret and environment:
        return client_id, client_secret, environment

    # Load from env vars / .env file
    creds = PyPtPCredentials()

    # Use explicit params if provided, otherwise use credentials
    final_id = client_id or creds.client_id
    final_secret = client_secret or creds.client_secret
    final_env = environment or creds.environment

    return final_id, final_secret, final_env
