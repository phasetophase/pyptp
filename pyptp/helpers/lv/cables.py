"""Cut cables into sections, or lay a new cable beside them."""

from __future__ import annotations

import math
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
from pyptp.helpers.lv._checks import check_cable, check_registered
from pyptp.helpers.lv._map import offset_on_map
from pyptp.helpers.lv._routes import (
    CableRoutes,
    Drawing,
    Point,
    cable_routes,
    join_routes,
    map_position,
    offset_route,
    route_length,
    to_the_millimetre,
    without_repeats,
)

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


def lay_parallel_cable(
    network: NetworkLV,
    cables: Sequence[CableLV],
    *,
    offset_px: int,
    offset_m: float = 0.0,
    name: str | None = None,
    node1: NodeLV | None = None,
    node2: NodeLV | None = None,
    length: float | None = None,
) -> CableLV:
    """Lay a new cable beside ``cables``, from the start of the first to the end of the last.

    ``cables`` is the old cable, or its sections in order, each stored either way round.
    The new cable is as long as the sections together and has the first section's type,
    name and drawing style. Its ends are closed, without protection or fuses.

    On every sheet all sections and both its nodes are drawn on, it runs ``offset_px``
    pixels beside the old route, and on the map ``offset_m`` metres beside it. Positive
    is to the right, walking from the first cable to the last. Both ends stay on the nodes.
    When a section has no route on the map, the new cable has none either.

    ``node1`` and ``node2`` connect the new cable to other nodes than the start and end
    of ``cables``. The route then runs straight from the old route's ends to these nodes.
    When ``node1`` is the end of ``cables`` or ``node2`` its start, the new cable runs
    from the last cable to the first, on the same side. Give ``length`` when the new
    cable is not as long as the sections together.

    Raises:
        ValueError: If an offset is not a finite number, if ``length`` is below 0.5 m,
            if ``cables`` is not one chain of this network's cables that passes each node
            once, if ``node1`` or ``node2`` is not in this network, if both are the same
            node, if the sections and both nodes share no sheet, or if a route turns back
            on itself while its offset is not 0.

    """
    if not math.isfinite(offset_px) or not math.isfinite(offset_m):
        msg = f"Offsets must be finite numbers, got offset_px={offset_px!r} and offset_m={offset_m!r}"
        raise ValueError(msg)
    if length is not None and not MIN_PART_LENGTH_M <= length < math.inf:
        msg = f"Length must be at least {MIN_PART_LENGTH_M} m, got {length!r}"
        raise ValueError(msg)
    if not cables:
        msg = "No cables given to lay a new cable beside"
        raise ValueError(msg)
    for cable in cables:
        check_registered(network, cable)
    for node in (node1, node2):
        if node is not None and network.nodes.get(node.general.guid) is not node:
            msg = f"Node {node.general.name!r} is not registered in this network"
            raise ValueError(msg)
    first = cables[0]
    start = _chain_start(cables)
    routes, end = _chain_routes(network, cables, start)
    if node1 is None:
        node1 = network.nodes[start]
    if node2 is None:
        node2 = network.nodes[end]
    if node1 is node2:
        msg = f"A new cable needs two different nodes, got {node1.general.name!r} twice"
        raise ValueError(msg)
    backwards = node1.general.guid == end or node2.general.guid == start
    at_start = node1
    at_end = node2
    if backwards:
        at_start = node2
        at_end = node1

    drawings_by_sheet = _shared_drawings(routes, node1, node2)
    if not drawings_by_sheet:
        msg = (
            f"Cable {first.general.name!r} and the cables after it are not all drawn on one sheet"
            f" with {node1.general.name!r} and {node2.general.name!r}, or only on a point"
        )
        raise ValueError(msg)

    try:
        presentations = [
            _drawing_beside(at_start, at_end, drawings, offset_px) for drawings in drawings_by_sheet.values()
        ]
        cablepart_geography = _map_route_beside(at_start, at_end, routes, offset_m)
    except ValueError as error:
        msg = f"Cannot lay a cable beside {first.general.name!r}: {error}"
        raise ValueError(msg) from error
    if backwards:
        presentations = [_turned_round(presentation) for presentation in presentations]
        if cablepart_geography is not None:
            cablepart_geography = GeoCablePart(cablepart_geography.coordinates[::-1])

    if length is None:
        length = round(sum(cable.cable_part.length for cable in cables), 2)
    new_name = first.general.name if name is None else name
    new_cable = CableLV(
        CableLV.General(node1=node1.general.guid, node2=node2.general.guid, name=new_name),
        presentations=presentations,
        cable_part=CableLV.CablePart(length=length, type=first.cable_part.type),
        cable_type=deepcopy(first.cable_type),
        cablepart_geography=cablepart_geography,
    )
    return network.add(new_cable)


def _chain_start(cables: Sequence[CableLV]) -> Guid:
    """Return the first cable's node away from the second cable."""
    first = cables[0]
    if len(cables) == 1:
        return first.general.node1

    second = cables[1]
    if first.general.node1 in (second.general.node1, second.general.node2):
        return first.general.node2
    return first.general.node1


def _chain_routes(network: NetworkLV, cables: Sequence[CableLV], start: Guid) -> tuple[list[CableRoutes], Guid]:
    """Return each cable's routes running away from ``start``, and the node the chain ends at."""
    chain_routes = []
    passed = {start}
    node = start
    for cable in cables:
        next_node = _other_node(cable, node)
        if next_node in passed:
            msg = f"Cable {cable.general.name!r} comes back to a node the chain has already passed"
            raise ValueError(msg)
        try:
            routes = cable_routes(network, cable)
        except ValueError as error:
            msg = f"Cannot lay a cable beside {cable.general.name!r}: {error}"
            raise ValueError(msg) from error
        if cable.general.node1 != node:
            routes = routes.reversed()
        chain_routes.append(routes)
        passed.add(next_node)
        node = next_node
    return chain_routes, node


def _other_node(cable: CableLV, node: Guid) -> Guid:
    if cable.general.node1 == node:
        return cable.general.node2
    if cable.general.node2 == node:
        return cable.general.node1
    msg = f"Cable {cable.general.name!r} does not join the previous cable"
    raise ValueError(msg)


def _shared_drawings(routes: Sequence[CableRoutes], node1: NodeLV, node2: NodeLV) -> dict[Guid, list[Drawing]]:
    """Return each section's first drawing, per sheet every section and both nodes are drawn on."""
    drawings_by_sheet = {}
    for presentation, _polyline in routes[0].drawings:
        sheet = presentation.sheet
        if not _drawn_on(node1, sheet) or not _drawn_on(node2, sheet):
            continue
        drawings = _drawings_on(routes, sheet)
        if drawings is not None and route_length(_joined_polylines(drawings)) > 0:
            drawings_by_sheet[sheet] = drawings
    return drawings_by_sheet


def _drawn_on(node: NodeLV, sheet: Guid) -> bool:
    return any(presentation.sheet == sheet for presentation in node.presentations)


def _drawings_on(routes: Sequence[CableRoutes], sheet: Guid) -> list[Drawing] | None:
    """Return each section's first drawing on ``sheet``, or None when a section is not drawn there."""
    drawings = []
    for section_routes in routes:
        drawing = _first_drawing_on(section_routes, sheet)
        if drawing is None:
            return None
        drawings.append(drawing)
    return drawings


def _first_drawing_on(section_routes: CableRoutes, sheet: Guid) -> Drawing | None:
    for drawing in section_routes.drawings:
        presentation, _polyline = drawing
        if presentation.sheet == sheet:
            return drawing
    return None


def _joined_polylines(drawings: list[Drawing]) -> list[Point]:
    polylines = [polyline for _presentation, polyline in drawings]
    return join_routes(polylines)


def _drawing_beside(node1: NodeLV, node2: NodeLV, drawings: list[Drawing], offset_px: int) -> BranchPresentation:
    """Return one drawing ``offset_px`` beside the sections' drawings, in the first one's style."""
    first_presentation, _first_polyline = drawings[0]
    style = BranchPresentation(
        sheet=first_presentation.sheet,
        color=first_presentation.color,
        size=first_presentation.size,
        width=first_presentation.width,
        text_color=first_presentation.text_color,
        text_size=first_presentation.text_size,
        font=first_presentation.font,
        text_style=first_presentation.text_style,
        no_text=first_presentation.no_text,
        upside_down_text=first_presentation.upside_down_text,
    )
    old_route = _joined_polylines(drawings)
    new_route = offset_route(old_route, offset_px)
    return _redrawn(style, node1, node2, new_route)


def _map_route_beside(
    node1: NodeLV, node2: NodeLV, routes: Sequence[CableRoutes], offset_m: float
) -> GeoCablePart | None:
    """Return the map route ``offset_m`` beside the sections, or None when one has no map route."""
    map_routes = []
    for section_routes in routes:
        map_route = section_routes.map_route
        if map_route is None:
            return None
        map_routes.append(map_route)

    old_route = join_routes(map_routes)
    new_route = offset_on_map(old_route, offset_m)
    start = map_position(node1.general)
    end = map_position(node2.general)
    if start is not None:
        new_route.insert(0, start)
    if end is not None:
        new_route.append(end)
    return GeoCablePart(without_repeats(to_the_millimetre(new_route)))


def _turned_round(presentation: BranchPresentation) -> BranchPresentation:
    """Return ``presentation`` with its nodes swapped, drawn along the same route."""
    return replace(presentation, first_corners=presentation.second_corners, second_corners=presentation.first_corners)


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
