"""Cut cables into sections."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
from decimal import Decimal
from itertools import pairwise
from typing import TYPE_CHECKING
from uuid import uuid4

from pyptp._network_objects import all_secondaries
from pyptp.elements.element_utils import SIDE_NODE1, SIDE_NODE2, Guid
from pyptp.elements.enums import NodePresentationSymbol
from pyptp.elements.lv.cable import MIN_PART_LENGTH_M, CableLV
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import BranchPresentation, NodePresentation
from pyptp.elements.lv.shared import GeoCablePart
from pyptp.helpers.lv._checks import check_cable
from pyptp.helpers.lv._routes import CableRoutes, Point, cable_routes, without_repeats

if TYPE_CHECKING:
    from collections.abc import Sequence

    from pyptp.network_lv import NetworkLV

_PHASES = ("L1", "L2", "L3")
_AUXILIARY = ("h1", "h2", "h3", "h4")


@dataclass
class CableSections:
    """A cut cable: its sections from node 1 to node 2, and the joints between them."""

    sections: list[CableLV]
    joints: list[NodeLV]


def split_cable(
    network: NetworkLV,
    cable: CableLV,
    at: Sequence[float],
    *,
    symbol: NodePresentationSymbol = NodePresentationSymbol.CLOSED_CIRCLE,
) -> CableSections:
    """Cut ``cable`` at new joints, ``at`` metres from node 1 in ascending order.

    Positions are rounded to centimetres and the sections add up to the cable's length.
    The first section keeps the cable's GUID.
    The others get new GUIDs and the same name. Fuses, switches and measure fields at
    node 2 move to the last section. Sections meet at the new joints with closed switches
    and no protection.

    A joint 30 m along a 120 m cable is drawn a quarter of the way along the route, on the
    map and on every sheet. A cable without a route on the map gets its joints on the
    straight line between its end nodes, when both have a map position.

    Raises:
        ValueError: If the cable is not in the network or has connections on the cable
            itself, if ``at`` is not ascending or not strictly between 0 and the
            cable's length, or if a section would be shorter than 0.5 m.

    """
    check_cable(network, cable)
    if not at:
        return CableSections([cable], [])
    length = cable.cable_part.length
    cuts = [round(metres, 2) for metres in at]
    _check_cuts(cable, cuts)
    lengths = _section_lengths(cuts, length)
    if min(lengths) < MIN_PART_LENGTH_M:
        msg = (
            f"Cable {cable.general.name!r} cut at {cuts} m gives sections of {lengths} m, "
            f"each must be at least {MIN_PART_LENGTH_M} m"
        )
        raise ValueError(msg)
    routes = cable_routes(network, cable)
    node1 = network.nodes[cable.general.node1]
    node2 = network.nodes[cable.general.node2]

    section_routes = routes.cut([cut / length for cut in cuts])
    joints = [_add_joint(network, node1.general.unom, before, symbol) for before in section_routes[:-1]]
    nodes = [node1, *joints, node2]

    original = deepcopy(cable)
    sections = []
    for index, section_route in enumerate(section_routes):
        section = cable if index == 0 else deepcopy(original)
        _lay_section(section, nodes[index], nodes[index + 1], section_route, lengths[index])
        sections.append(section)

    for section in sections[1:]:
        section.general.guid = Guid(uuid4())
        _clear_end(section, SIDE_NODE1)
        network.add(section)
    for section in sections[:-1]:
        _clear_end(section, SIDE_NODE2)
    _move_node2_secondaries(network, cable, sections[-1])
    return CableSections(sections, joints)


def _check_cuts(cable: CableLV, cuts: list[float]) -> None:
    """Raise unless ``cuts`` are ascending, without duplicates, and inside the cable."""
    for previous, cut in pairwise(cuts):
        if cut <= previous:
            msg = f"Cable {cable.general.name!r} cut at {cuts} m: positions must be ascending, without duplicates"
            raise ValueError(msg)
    length = cable.cable_part.length
    for cut in cuts:
        if not 0 < cut < length:
            msg = f"Cable {cable.general.name!r} cut at {cut} m: positions must lie between 0 and {length} m"
            raise ValueError(msg)


def _section_lengths(cuts: list[float], length: float) -> list[float]:
    """Return the length of each section, the last one taking what remains of ``length``."""
    lengths = []
    previous = 0.0
    for cut in cuts:
        lengths.append(round(cut - previous, 2))
        previous = cut
    remainder = Decimal(str(length)) - Decimal(str(previous))
    lengths.append(float(remainder))
    return lengths


def _add_joint(network: NetworkLV, unom: float, before: CableRoutes, symbol: NodePresentationSymbol) -> NodeLV:
    """Add the joint where ``before`` ends, once on every sheet the cable is drawn on."""
    general = NodeLV.General(unom=unom)
    map_route = before.map_route
    if map_route is not None:
        x, y = map_route[-1]
        general.gx = x
        general.gy = y
    presentations = []
    sheets_with_joint: set[Guid] = set()
    for presentation, polyline in before.drawings:
        if presentation.sheet in sheets_with_joint:
            continue
        sheets_with_joint.add(presentation.sheet)
        x, y = polyline[-1]
        presentations.append(
            NodePresentation(sheet=presentation.sheet, x=round(x), y=round(y), symbol=symbol, color=presentation.color)
        )
    return network.add(NodeLV(general, presentations=presentations))


def _lay_section(section: CableLV, node1: NodeLV, node2: NodeLV, routes: CableRoutes, length: float) -> None:
    """Set ``section``'s nodes, length, geography and drawings to ``routes``."""
    section.general.node1 = node1.general.guid
    section.general.node2 = node2.general.guid
    section.cable_part.length = length
    section.cablepart_geography = _geography(routes.cablepart)
    section.geography = _geography(routes.geography)
    section.presentations = [
        _redrawn(presentation, node1, node2, polyline[1:-1]) for presentation, polyline in routes.drawings
    ]


def _geography(route: list[Point] | None) -> GeoCablePart | None:
    """Return ``route`` as a cable geography, or None without a route."""
    if route is None:
        return None
    return GeoCablePart(route)


def _move_node2_secondaries(network: NetworkLV, cable: CableLV, last: CableLV) -> None:
    """Move fuses, circuit breakers, load switches and measure fields at node 2 onto ``last``."""
    for secondary in all_secondaries(network):
        if secondary.general.in_object == cable.general.guid and secondary.general.side == SIDE_NODE2:
            secondary.general.in_object = last.general.guid


def _clear_end(section: CableLV, side: int) -> None:
    """Reset one end of a section to that of a new cable: closed, no protection."""
    names = [f"field_name{side}", f"switch_state{side}_N", f"switch_state{side}_PE"]
    for conductor in _PHASES:
        names.append(f"switch_state{side}_{conductor}")
        names.append(f"k{side}_{conductor}")
    for conductor in _AUXILIARY:
        names.append(f"switch_state{side}_{conductor}")
        names.append(f"k{side}_{conductor}")
        names.append(f"protection_type{side}_{conductor}")

    blank = CableLV.General()
    for name in names:
        setattr(section.general, name, getattr(blank, name))
    for conductor in _AUXILIARY:
        setattr(section, f"fuse{side}_{conductor}", None)
        setattr(section, f"current{side}_{conductor}", None)


def _redrawn(
    presentation: BranchPresentation, node1: NodeLV, node2: NodeLV, via: Sequence[Point]
) -> BranchPresentation:
    """Return ``presentation`` redrawn between ``node1`` and ``node2`` through the points ``via``."""
    rounded_via = [(round(x), round(y)) for x, y in via]
    drawn = BranchPresentation.between(node1, node2, presentation.sheet, via=without_repeats(rounded_via))
    return replace(presentation, first_corners=drawn.first_corners, second_corners=drawn.second_corners)
