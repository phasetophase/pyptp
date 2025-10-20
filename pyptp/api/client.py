# SPDX-FileCopyrightText: Contributors to the PyPtP project
# SPDX-License-Identifier: GPL-3.0-or-later

"""High-level client for Phase to Phase API services."""

from __future__ import annotations

from typing import Any

from pyptp._credentials import PyPtPCredentials
from pyptp.api._auth.token_manager import TokenManager
from pyptp.ptp_log import logger


class Client:
    """Phase to Phase API client.

    Provides a clean interface for interacting with Phase to Phase cloud services
    including network calculations, data storage, and analysis tools.

    The client handles authentication, token management, and environment configuration
    automatically. It supports multiple initialization patterns for flexibility.

    Examples:
        >>> # Pattern 1: Environment variables
        >>> client = Client()

        >>> # Pattern 2: Credentials object (recommended)
        >>> from pyptp import Credentials
        >>> creds = Credentials(
        ...     client_id="your_id",
        ...     client_secret="your_secret",
        ...     environment="acceptance"
        ... )
        >>> client = Client(credentials=creds)

        >>> # Pattern 3: Direct parameters
        >>> client = Client(
        ...     client_id="your_id",
        ...     client_secret="your_secret",
        ...     environment="test"
        ... )

        >>> # Pattern 4: Environment-first factory
        >>> client = Client.for_environment(
        ...     "acceptance",
        ...     client_id="your_id",
        ...     client_secret="your_secret"
        ... )

    Attributes:
        environment: Current API environment (test/acceptance/production).
        base_url: Base URL for API requests.

    """

    def __init__(
        self,
        credentials: PyPtPCredentials | None = None,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        environment: str | None = None,
        timeout: int | None = None,
        max_retries: int | None = None,
    ) -> None:
        """Initialize PyPtP API client.

        Args:
            credentials: Credentials instance (preferred pattern).
            client_id: OAuth2 client ID (overrides credentials).
            client_secret: OAuth2 client secret (overrides credentials).
            environment: API environment - "test", "acceptance", or "production".
            timeout: Request timeout in seconds (overrides credentials).
            max_retries: Maximum retry attempts (overrides credentials).

        Raises:
            APIConfigurationError: If credentials are missing or invalid.
            APIEnvironmentError: If environment is not recognized.

        """
        # Load or create credentials
        if credentials is None:
            credentials = PyPtPCredentials()

        # Apply overrides
        final_client_id = client_id or credentials.client_id
        final_client_secret = client_secret or credentials.client_secret
        final_environment = environment or credentials.environment
        self._timeout = timeout or credentials.timeout
        self._max_retries = max_retries or credentials.max_retries

        # Initialize token manager (handles auth)
        self._token_manager = TokenManager(
            client_id=final_client_id,
            client_secret=final_client_secret,
            environment=final_environment,
        )

        # Store environment info
        self.environment = final_environment
        self.base_url = self._token_manager.base_url

        logger.info(
            "Client initialized for %s environment at %s",
            self.environment,
            self.base_url,
        )

        # Future: API endpoint namespaces will be added here

    @classmethod
    def for_environment(
        cls,
        environment: str,
        client_id: str | None = None,
        client_secret: str | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> Client:
        """Create client for specific environment.

        Convenience factory method for environment-first configuration.
        Useful when the environment is your primary concern.

        Args:
            environment: API environment - "test", "acceptance", or "production".
            client_id: OAuth2 client ID.
            client_secret: OAuth2 client secret.
            **kwargs: Additional options (timeout, max_retries).

        Returns:
            Configured Client instance.

        Example:
            >>> client = Client.for_environment(
            ...     "acceptance",
            ...     client_id="...",
            ...     client_secret="..."
            ... )

        """
        return cls(
            client_id=client_id,
            client_secret=client_secret,
            environment=environment,
            **kwargs,
        )

    def _get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers for API requests.

        Returns:
            Dictionary with Authorization header containing valid Bearer token.

        Raises:
            APIAuthenticationError: If token cannot be acquired.

        """
        token = self._token_manager.get_valid_token()
        return {"Authorization": f"Bearer {token}"}

    def _request(self, method: str, endpoint: str, **kwargs: Any) -> Any:  # noqa: ANN401
        """Make an authenticated request to the API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            endpoint: API endpoint path (relative to base_url).
            **kwargs: Additional request parameters (json, params, etc.).

        Returns:
            Response data.

        Raises:
            APIError: If request fails.

        Note:
            This is a placeholder for future implementation.

        """
        msg = "API request functionality not yet implemented"
        raise NotImplementedError(msg)

    def __repr__(self) -> str:
        """Return string representation of client."""
        return f"Client(environment='{self.environment}', base_url='{self.base_url}')"


__all__ = ["Client"]
