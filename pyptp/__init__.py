# SPDX-FileCopyrightText: Contributors to the PyPtP project
# SPDX-License-Identifier: GPL-3.0-or-later

"""PyPtP: Python SDK for Phase to Phase electrical network data.

PyPtP enables Distribution System Operators (DSOs) to work with electrical
network data in native Gaia (LV) and Vision (MV) formats, with programmatic
access to Phase to Phase cloud services.

Core Classes:
    NetworkLV: Low-voltage network modeling (Gaia/GNF format)
    NetworkMV: Medium-voltage network modeling (Vision/VNF format)
    Client: API client for Phase to Phase cloud services
    Credentials: Type-safe credential management

Examples:
    >>> # Work with local network files
    >>> from pyptp import NetworkLV, NetworkMV
    >>> lv_network = NetworkLV.load("network.gnf")
    >>> mv_network = NetworkMV.load("network.vnf")

    >>> # Connect to cloud services
    >>> from pyptp import Client, Credentials
    >>> client = Client.for_environment("acceptance")
    >>> # Future: result = client.calculations.loadflow(network)

    >>> # Configure logging (silent by default)
    >>> from pyptp import configure_logging
    >>> configure_logging(level="DEBUG")

"""

from pyptp._credentials import PyPtPCredentials as Credentials
from pyptp.api import Client
from pyptp.graph.networkx_converter import NetworkxConverter
from pyptp.network_lv import NetworkLV
from pyptp.network_mv import NetworkMV
from pyptp.ptp_log import configure_logging

__all__ = [
    "Client",
    "Credentials",
    "NetworkLV",
    "NetworkMV",
    "NetworkxConverter",
    "configure_logging",
]
