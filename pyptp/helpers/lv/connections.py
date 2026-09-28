"""Move connections onto another cable, for example a new cable laid alongside an overloaded one."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_DOWN, Decimal
from typing import TYPE_CHECKING

from pyptp.elements.enums import NodePresentationSymbol
from pyptp.elements.lv.cable import MIN_PART_LENGTH_M
from pyptp.helpers.lv._checks import check_cable
from pyptp.helpers.lv._routes import cable_routes, nearest_fraction, nearest_fraction_on_map
from pyptp.helpers.lv.cables import CableSections, split_cable

if TYPE_CHECKING:
    from collections.abc import Sequence

    from pyptp.elements.lv.cable import CableLV
    from pyptp.elements.lv.connection import ConnectionLV
    from pyptp.elements.lv.node import NodeLV
    from pyptp.helpers.lv._routes import CableRoutes
    from pyptp.network_lv import NetworkLV


def move_connections_to_cable(
    network: NetworkLV,
    cable: CableLV,
    connections: Sequence[ConnectionLV],
    *,
    symbol: NodePresentationSymbol = NodePresentationSymbol.CLOSED_TRIANGLE,
) -> CableSections:
    """Move ``connections`` onto ``cable``, each at a new joint where the cable passes nearest.

    The cable is cut at the joints as by ``split_cable``, and N and PE are joined at each
    new joint. Joints stay at least 0.5 m from the cable ends and from each other, so
    connections close together share a joint.
    Each connection keeps its drawing and length. Its cable route on the map is redrawn
    straight from the joint, or dropped when the joint or the connection has no map position.

    Raises:
        ValueError: If the cable is not in the network, has connections on the cable
            itself or is shorter than 1 m, if a connection is not in the network, or
            if a connection is drawn on a sheet without the cable or shares neither
            the map nor a sheet with it.

    """
    check_cable(network, cable)
    length = cable.cable_part.length
    shortest_cable = 2 * MIN_PART_LENGTH_M
    if length < shortest_cable:
        msg = f"Cable {cable.general.name!r} is {length} m, it must be at least {shortest_cable} m to take a joint"
        raise ValueError(msg)
    _check_connections(network, connections)
    if not connections:
        return CableSections([cable], [])

    routes = cable_routes(network, cable)
    placed = [(_metres_along(routes, cable, connection), connection) for connection in connections]
    groups = _group(placed)
    at = [group.metres for group in groups]
    result = split_cable(network, cable, at, symbol=symbol)
    for joint, group in zip(result.joints, groups, strict=True):
        joint.general.s_N_PE = True
        for connection in group.connections:
            connection.general.node = joint.general.guid
            _redraw_connection_geography(connection, joint)
    return result


@dataclass
class _JointGroup:
    """Connections that share one joint, ``metres`` from node 1."""

    metres: float
    connections: list[ConnectionLV]


def _check_connections(network: NetworkLV, connections: Sequence[ConnectionLV]) -> None:
    """Raise if any of ``connections`` is not in the network."""
    for connection in connections:
        if network.homes.get(connection.general.guid) is not connection:
            msg = f"Connection {connection.general.name!r} is not registered in this network"
            raise ValueError(msg)


def _metres_along(routes: CableRoutes, cable: CableLV, connection: ConnectionLV) -> float:
    """Where the connection's joint goes, in metres from node 1, at least 0.5 m from either end."""
    connection_sheets = {presentation.sheet for presentation in connection.presentations}
    cable_sheets = {presentation.sheet for presentation, _ in routes.drawings}
    if not connection_sheets <= cable_sheets:
        msg = f"Connection {connection.general.name!r} is drawn on a sheet without cable {cable.general.name!r}"
        raise ValueError(msg)
    fraction = _nearest_fraction(routes, cable, connection)
    length = cable.cable_part.length
    metres = round(fraction * length, 2)
    latest = Decimal(str(length)) - Decimal(str(MIN_PART_LENGTH_M))
    latest_centimetre = float(latest.quantize(Decimal("0.01"), rounding=ROUND_DOWN))
    return min(max(metres, MIN_PART_LENGTH_M), latest_centimetre)


def _nearest_fraction(routes: CableRoutes, cable: CableLV, connection: ConnectionLV) -> float:
    """Where the cable passes nearest: on its map route, a shared sheet, or the line between its end nodes."""
    location = (connection.general.geo_x_coord, connection.general.geo_y_coord)
    has_location = location != (0, 0)
    if has_location and routes.geography_route is not None:
        return nearest_fraction_on_map(routes.geography_route, location)
    for presentation, polyline in routes.drawings:
        drawn = connection.get_presentation_on_sheet(presentation.sheet)
        if drawn is not None:
            return nearest_fraction(polyline, (drawn.x, drawn.y))
    if has_location and routes.straight_line is not None:
        return nearest_fraction_on_map(routes.straight_line, location)

    if has_location:
        msg = (
            f"Connection {connection.general.name!r} is not drawn on any sheet "
            f"and cable {cable.general.name!r} has no map position"
        )
    else:
        msg = (
            f"Connection {connection.general.name!r} has no map position and is not drawn on any sheet, "
            f"so it cannot be placed on cable {cable.general.name!r}"
        )
    raise ValueError(msg)


def _group(placed: list[tuple[float, ConnectionLV]]) -> list[_JointGroup]:
    """Group connections less than 0.5 m past the first in the group, sorted by position."""
    placed = sorted(placed, key=lambda pair: pair[0])
    groups: list[_JointGroup] = []
    for metres, connection in placed:
        if groups and metres - groups[-1].metres < MIN_PART_LENGTH_M:
            groups[-1].connections.append(connection)
        else:
            groups.append(_JointGroup(metres, [connection]))
    return groups


def _redraw_connection_geography(connection: ConnectionLV, joint: NodeLV) -> None:
    """Redraw the connection's geography straight from ``joint``, or drop it."""
    route = connection.connection_geography
    if route is None:
        return
    joint_position = (joint.general.gx, joint.general.gy)
    location = (connection.general.geo_x_coord, connection.general.geo_y_coord)
    if joint_position == (0, 0) or location == (0, 0):
        connection.connection_geography = None
        return
    route.coordinates = [joint_position, location]
