"""Network to NetworkX graph converter.

Every electrical object (nodes, branches, elements and secondaries) becomes a graph
node keyed by ``str(guid)``, with a ``type`` attribute holding the element class
name. Sheets, texts and other drawing objects are not in the graph. Edges follow
the electrical connection path:

- A branch side runs ``node -- secondary -- ... -- branch``. The graph lines up the
  secondaries on a side between the node and the branch: fuses first, then load
  switches, circuit breakers and measure fields, each in the order they were added.
- An element runs ``node -- secondary -- ... -- element`` in the same way.
- Secondaries always keep their edge towards the branch or element they belong to.
- The edge towards the node exists only while the side is closed. An open side
  leaves the branch or element and its secondaries as a separate fragment. Pass
  ``respect_switch_states=False`` to connect every side regardless of its switch
  states.
- A secondary in a node stays in the graph without edges.
- Objects that point to a missing node or object keep no edge towards it, and a
  warning is logged.

A side counts as closed when at least one of its phase or auxiliary conductor switches
is closed.
"""

from __future__ import annotations

from itertools import pairwise
from typing import TYPE_CHECKING

from networkx import Graph

from pyptp._network_objects import (
    NetworkObject,
    all_secondaries,
    lv_branches,
    lv_elements,
    mv_branches,
    mv_elements,
    nodes_by_side,
)
from pyptp.elements.element_utils import BRANCH_SIDE_SWITCHES, NIL_GUID, Guid, name_or_guid
from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pyptp.network_lv import NetworkLV
    from pyptp.network_mv import NetworkMV


# Switch-state fields of a node-connected element. ``s_Hh`` is the auxiliary
# core switch of a connection.
_ELEMENT_SWITCHES: tuple[str, ...] = ("switch_state", "s_L1", "s_L2", "s_L3", "s_Hh")


def _side_closed(general: object, switches: tuple[str, ...]) -> bool:
    """Return whether a side conducts: any present switch closed, or no switches at all."""
    states = [getattr(general, name) for name in switches if hasattr(general, name)]
    return not states or any(states)


class NetworkxConverter:
    """Convert a network into an undirected NetworkX graph of its topology.

    See the module docstring for the node and edge rules.
    """

    @classmethod
    def graph_lv(cls, network: NetworkLV, *, respect_switch_states: bool = True) -> Graph:
        """Export an unbalanced network to a NetworkX graph.

        Args:
            network: The network to convert.
            respect_switch_states: When True, an open side has no edge towards its
                node. When False, every side is connected regardless of switch states.

        """
        return cls._build(
            network.nodes.values(),
            lv_branches(network),
            lv_elements(network),
            all_secondaries(network),
            respect_switch_states=respect_switch_states,
        )

    @classmethod
    def graph_mv(cls, network: NetworkMV, *, respect_switch_states: bool = True) -> Graph:
        """Export a balanced network to a NetworkX graph.

        Args:
            network: The network to convert.
            respect_switch_states: When True, an open side has no edge towards its
                node. When False, every side is connected regardless of switch states.

        """
        return cls._build(
            network.nodes.values(),
            mv_branches(network),
            mv_elements(network),
            all_secondaries(network),
            respect_switch_states=respect_switch_states,
        )

    @classmethod
    def _build(
        cls,
        nodes: Iterable[NetworkObject],
        branches: Iterable[NetworkObject],
        elements: Iterable[NetworkObject],
        secondaries: list[NetworkObject],
        *,
        respect_switch_states: bool,
    ) -> Graph:
        graph = Graph()
        by_parent = _group_by_parent(secondaries)
        for node in nodes:
            cls._add_node(graph, node)
            by_parent.pop(node.general.guid, None)
        for secondary in secondaries:
            cls._add_node(graph, secondary)

        for branch in branches:
            cls._add_node(graph, branch)
            in_branch = by_parent.pop(branch.general.guid, [])
            cls._connect_branch(graph, branch, in_branch, respect_switch_states=respect_switch_states)

        for element in elements:
            cls._add_node(graph, element)
            in_element = by_parent.pop(element.general.guid, [])
            in_series = sorted(in_element, key=lambda secondary: secondary.general.side)
            closed = not respect_switch_states or _side_closed(element.general, _ELEMENT_SWITCHES)
            cls._connect_side(graph, element.general.node, in_series, element, closed=closed)

        _warn_unplaced(by_parent)
        return graph

    @staticmethod
    def _add_node(graph: Graph, obj: NetworkObject) -> None:
        graph.add_node(str(obj.general.guid), type=type(obj).__name__)

    @classmethod
    def _connect_branch(
        cls,
        graph: Graph,
        branch: NetworkObject,
        secondaries: list[NetworkObject],
        *,
        respect_switch_states: bool,
    ) -> None:
        nodes = nodes_by_side(branch)
        for side, node_guid in nodes.items():
            on_side = [secondary for secondary in secondaries if secondary.general.side == side]
            closed = not respect_switch_states or _side_closed(branch.general, BRANCH_SIDE_SWITCHES[side])
            cls._connect_side(graph, node_guid, on_side, branch, closed=closed)

    @staticmethod
    def _connect_side(
        graph: Graph,
        node_guid: Guid,
        secondaries: list[NetworkObject],
        parent: NetworkObject,
        *,
        closed: bool,
    ) -> None:
        """Add the edges ``node -- secondary -- ... -- parent`` for one side.

        The edge at the node end is left out when the side is open, has no node, or
        its node is not in the network.
        """
        node_in_graph = _node_in_graph(graph, node_guid, parent)
        path = [*(str(secondary.general.guid) for secondary in secondaries), str(parent.general.guid)]
        if closed and node_in_graph:
            path.insert(0, str(node_guid))
        graph.add_edges_from(pairwise(path))


def _group_by_parent(secondaries: list[NetworkObject]) -> dict[Guid, list[NetworkObject]]:
    by_parent: dict[Guid, list[NetworkObject]] = {}
    for secondary in secondaries:
        in_object: Guid = secondary.general.in_object
        if in_object == NIL_GUID:
            continue
        if in_object not in by_parent:
            by_parent[in_object] = []
        by_parent[in_object].append(secondary)
    return by_parent


def _node_in_graph(graph: Graph, node_guid: Guid, parent: NetworkObject) -> bool:
    """Return whether the side's node is in the graph, with a warning when the network lacks it."""
    if node_guid == NIL_GUID:
        return False
    if str(node_guid) in graph:
        return True
    logger.warning(
        "%s %s has no edge to node %s, which is not in the network",
        type(parent).__name__,
        name_or_guid(parent.general),
        node_guid,
    )
    return False


def _warn_unplaced(by_parent: dict[Guid, list[NetworkObject]]) -> None:
    for in_object, unplaced in by_parent.items():
        for secondary in unplaced:
            logger.warning(
                "%s %s has no edges, because it belongs to %s, which is not in the network",
                type(secondary).__name__,
                name_or_guid(secondary.general),
                in_object,
            )
