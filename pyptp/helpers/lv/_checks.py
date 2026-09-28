"""Checks shared by the LV helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyptp.elements.lv.cable import CableLV
    from pyptp.network_lv import NetworkLV


def check_cable(network: NetworkLV, cable: CableLV) -> None:
    """Raise if ``cable`` is not in the network or has connections on the cable itself."""
    if network.cables.get(cable.general.guid) is not cable:
        msg = f"Cable {cable.general.name!r} is not registered in this network"
        raise ValueError(msg)
    if cable.cable_connections or cable.cable_connection:
        msg = f"Cable {cable.general.name!r} has connections on the cable itself and cannot be split"
        raise ValueError(msg)
