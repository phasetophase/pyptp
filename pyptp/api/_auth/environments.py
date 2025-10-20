"""Environment configurations for API endpoints."""

from __future__ import annotations

from typing import TypedDict


class EnvironmentConfig(TypedDict):
    """Configuration for an API environment."""

    base_url: str
    token_url: str


# Environment configurations
ENVIRONMENTS: dict[str, EnvironmentConfig] = {
    "test": {
        "base_url": "https://api.testvcs.phasetophase.nl",
        "token_url": "https://testvcs.phasetophase.nl/auth/realms/vcs/protocol/openid-connect/token",
    },
    "acceptance": {
        "base_url": "https://api.accvcs.phasetophase.nl",
        "token_url": "https://accvcs.phasetophase.nl/auth/realms/vcs/protocol/openid-connect/token",
    },
    "production": {
        "base_url": "https://api.prodvcs.phasetophase.nl",
        "token_url": "https://prodvcs.phasetophase.nl/auth/realms/vcs/protocol/openid-connect/token",
    },
}


def get_environment_config(environment: str) -> EnvironmentConfig:
    """Get configuration for the specified environment.

    Args:
        environment: Environment name (test, acceptance, production).

    Returns:
        Environment configuration.

    Raises:
        ValueError: If environment is not recognized.

    """
    if environment not in ENVIRONMENTS:
        msg = f"Invalid environment: {environment}. Must be one of: {', '.join(ENVIRONMENTS.keys())}"
        raise ValueError(msg)

    return ENVIRONMENTS[environment]
