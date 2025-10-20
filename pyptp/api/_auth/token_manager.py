"""OAuth2 token management for API authentication."""

from __future__ import annotations

import threading
from datetime import UTC, datetime, timedelta
from urllib.parse import quote

import requests

from pyptp._credentials import PyPtPCredentials
from pyptp.api._core.exceptions import (
    APIAuthenticationError,
    APIConfigurationError,
    APIEnvironmentError,
)
from pyptp.ptp_log import logger

from .environments import get_environment_config


class TokenManager:
    """Manages OAuth2 tokens for API authentication.

    Handles token acquisition, refresh, and caching with thread safety.
    Automatically URL-encodes credentials for proper authentication.

    Attributes:
        client_id: OAuth2 client ID.
        client_secret: OAuth2 client secret.
        environment: API environment (test, acceptance, production).
        base_url: Base URL for API requests.
        token_url: URL for token endpoint.

    """

    def __init__(
        self,
        credentials: PyPtPCredentials | None = None,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        environment: str | None = None,
    ) -> None:
        """Initialize TokenManager with credentials.

        Args:
            credentials: PyPtPCredentials instance (preferred). If not provided,
                loads from environment variables.
            client_id: OAuth2 client ID (overrides credentials if provided).
            client_secret: OAuth2 client secret (overrides credentials if provided).
            environment: API environment (overrides credentials if provided).

        Raises:
            APIConfigurationError: If credentials are missing.
            APIEnvironmentError: If environment is invalid.

        Examples:
            >>> # Load from environment variables
            >>> tm = TokenManager()

            >>> # Explicit credentials (preferred)
            >>> creds = PyPtPCredentials(client_id="...", client_secret="...")
            >>> tm = TokenManager(credentials=creds)

            >>> # Mixed approach
            >>> tm = TokenManager(client_id="...", client_secret="...")

        """
        # Load credentials from env vars if not provided
        if credentials is None:
            credentials = PyPtPCredentials()

        # Allow explicit parameter overrides
        self.client_id = client_id or credentials.client_id
        self.client_secret = client_secret or credentials.client_secret
        env_name = environment or credentials.environment

        # Validate credentials
        if not self.client_id or not self.client_secret:
            msg = (
                "No credentials found! Please provide credentials via:\n"
                "1. PyPtPCredentials instance: TokenManager(credentials=PyPtPCredentials(...))\n"
                "2. Constructor parameters: TokenManager(client_id='...', client_secret='...')\n"
                "3. Environment variables: PYPTP_CLIENT_ID, PYPTP_CLIENT_SECRET\n"
                "4. .env file with PYPTP_CLIENT_ID and PYPTP_CLIENT_SECRET"
            )
            raise APIConfigurationError(msg)

        # Get environment configuration
        try:
            env_config = get_environment_config(env_name)
        except ValueError as e:
            raise APIEnvironmentError(str(e)) from e

        self.environment = env_name
        self.base_url = env_config["base_url"]
        self.token_url = env_config["token_url"]

        # Token cache
        self._token: str | None = None
        self._token_expires_at: datetime | None = None
        self._lock = threading.Lock()

        mask_length = 10
        masked_id = f"{self.client_id[:mask_length]}..." if len(self.client_id) > mask_length else "***"
        logger.debug(
            "TokenManager initialized for %s environment with client_id: %s",
            self.environment,
            masked_id,
        )

    def _refresh_token(self) -> None:
        """Acquire a new token from the OAuth2 endpoint.

        Raises:
            APIAuthenticationError: If token acquisition fails.

        """
        # URL-encode credentials for proper authentication
        # These are guaranteed non-None by __init__ validation
        encoded_client_id = quote(self.client_id or "", safe="")
        encoded_client_secret = quote(self.client_secret or "", safe="")

        try:
            response = requests.post(
                self.token_url,
                data={
                    "grant_type": "client_credentials",
                    "scope": "openid",
                },
                auth=(encoded_client_id, encoded_client_secret),
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()
            self._token = data["access_token"]

            token_expiry_buffer = 10
            expires_in = data.get("expires_in", 300)  # Default 5 minutes
            self._token_expires_at = datetime.now(UTC) + timedelta(seconds=expires_in - token_expiry_buffer)

            logger.debug("Token refreshed successfully, expires at %s", self._token_expires_at)

        except requests.exceptions.RequestException as e:
            msg = f"Failed to acquire token from {self.environment} environment: {e}"
            raise APIAuthenticationError(msg) from e
        except (KeyError, ValueError) as e:
            msg = f"Invalid token response: {e}"
            raise APIAuthenticationError(msg) from e

    def get_valid_token(self) -> str:
        """Get a valid access token, refreshing if necessary.

        Returns:
            Valid OAuth2 access token.

        Raises:
            APIAuthenticationError: If token cannot be acquired.

        """
        with self._lock:
            # Check if we need a new token
            if self._token is None or self._token_expires_at is None or datetime.now(UTC) >= self._token_expires_at:
                self._refresh_token()

            if self._token is None:
                msg = "Failed to acquire access token"
                raise APIAuthenticationError(msg)

            return self._token

    def invalidate_token(self) -> None:
        """Invalidate the cached token, forcing refresh on next request."""
        with self._lock:
            self._token = None
            self._token_expires_at = None
            logger.debug("Token invalidated")

    @property
    def token_expires_at(self) -> datetime | None:
        """Get token expiration time.

        Returns:
            Token expiration datetime or None if no token.

        """
        return self._token_expires_at
