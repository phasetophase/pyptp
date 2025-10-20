# SPDX-FileCopyrightText: Contributors to the PyPtP project
# SPDX-License-Identifier: GPL-3.0-or-later

"""PyPtP API integration module for Phase-to-Phase cloud services.

This module provides programmatic access to Phase-to-Phase cloud APIs including:
- Network calculations
- VCS (Vision Cloud Solution)
- Network data management

Examples:
    >>> from pyptp.api import Client
    >>> client = Client()
    >>> # Future: client.calculations.loadflow(network)

"""

from __future__ import annotations

__all__ = [
    "APIAuthenticationError",
    "APIConfigurationError",
    "APIEnvironmentError",
    "APIError",
    "Client",
    "TokenManager",
]

# High-level client (primary interface)
# Low-level components (advanced usage)
from pyptp.api._auth import TokenManager
from pyptp.api._core.exceptions import (
    APIAuthenticationError,
    APIConfigurationError,
    APIEnvironmentError,
    APIError,
)
from pyptp.api.client import Client
