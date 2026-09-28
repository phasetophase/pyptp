"""Which objects in a network are branches, elements and secondaries."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import chain
from typing import TYPE_CHECKING, Any, Protocol, TypeVar

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pyptp.elements.element_utils import Guid
    from pyptp.network_lv import NetworkLV
    from pyptp.network_mv import NetworkMV


class NetworkObject(Protocol):
    """An object in a network, with its data in ``general``."""

    general: Any


_NetworkT_contra = TypeVar("_NetworkT_contra", contravariant=True)


class Registrable(Protocol[_NetworkT_contra]):
    """An element that can register itself in a network."""

    def register(self, network: _NetworkT_contra) -> None:
        """Add this element to the network's collection of its kind."""
        ...


_BRANCH_SIDE_NODES: dict[int, str] = {1: "node1", 2: "node2", 3: "node3"}


def nodes_by_side(branch: NetworkObject) -> dict[int, Guid]:
    """Return the node at each side of a branch, keyed by side number."""
    nodes: dict[int, Guid] = {}
    for side, node_field in _BRANCH_SIDE_NODES.items():
        node_guid = getattr(branch.general, node_field, None)
        if node_guid is None:
            continue
        nodes[side] = node_guid
    return nodes


def lv_branches(network: NetworkLV) -> Iterable[NetworkObject]:
    """Return the objects that connect two nodes."""
    return chain(
        network.cables.values(),
        network.links.values(),
        network.transformers.values(),
        network.special_transformers.values(),
        network.reactance_coils.values(),
    )


def lv_elements(network: NetworkLV) -> Iterable[NetworkObject]:
    """Return the objects connected to a single node."""
    return chain(
        network.homes.values(),
        network.sources.values(),
        network.syn_generators.values(),
        network.async_generators.values(),
        network.async_motors.values(),
        network.earthing_transformers.values(),
        network.shunt_capacitors.values(),
        network.batteries.values(),
        network.loads.values(),
        network.pvs.values(),
    )


def mv_branches(network: NetworkMV) -> Iterable[NetworkObject]:
    """Return the objects that connect two or three nodes."""
    return chain(
        network.cables.values(),
        network.links.values(),
        network.lines.values(),
        network.transformers.values(),
        network.special_transformers.values(),
        network.reactance_coils.values(),
        network.threewinding_transformers.values(),
    )


def mv_elements(network: NetworkMV) -> Iterable[NetworkObject]:
    """Return the objects connected to a single node."""
    return chain(
        network.loads.values(),
        network.earthing_transformers.values(),
        network.asynchronous_generators.values(),
        network.asynchronous_motors.values(),
        network.synchronous_generators.values(),
        network.synchronous_motors.values(),
        network.generators.values(),
        network.batteries.values(),
        network.pvs.values(),
        network.sources.values(),
        network.windturbines.values(),
        network.shunt_coils.values(),
        network.shunt_capacitors.values(),
        network.transformer_loads.values(),
    )


def all_secondaries(network: NetworkLV | NetworkMV) -> list[NetworkObject]:
    """Return the fuses, load switches, circuit breakers and measure fields."""
    return [
        *network.fuses.values(),
        *network.load_switches.values(),
        *network.circuit_breakers.values(),
        *network.measure_fields.values(),
    ]


@dataclass
class SecondaryParent:
    """An object fuses, switches and measure fields can sit in, with the sides it has."""

    obj: NetworkObject
    sides: list[int]


def secondary_parents(network: NetworkLV | NetworkMV) -> dict[Guid, SecondaryParent]:
    """Return every object a secondary can sit in, by GUID.

    A node has side 0, an element side 1, and a branch a side for each of its nodes.
    """
    from pyptp.network_lv import NetworkLV

    if isinstance(network, NetworkLV):
        branches = lv_branches(network)
        elements = lv_elements(network)
    else:
        branches = mv_branches(network)
        elements = mv_elements(network)

    parents: dict[Guid, SecondaryParent] = {}
    for node in network.nodes.values():
        parents[node.general.guid] = SecondaryParent(node, [0])
    for branch in branches:
        sides = list(nodes_by_side(branch))
        parents[branch.general.guid] = SecondaryParent(branch, sides)
    for element in elements:
        parents[element.general.guid] = SecondaryParent(element, [1])
    return parents
