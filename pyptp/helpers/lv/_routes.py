"""Routes a cable follows on the map and on its sheets, from node 1 to node 2."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from itertools import pairwise
from typing import TYPE_CHECKING, TypeVar

from pyptp.elements.lv.presentations import BranchPresentation
from pyptp.elements.presentation_helpers import node_presentations_on_sheet

if TYPE_CHECKING:
    from pyptp.elements.lv.cable import CableLV
    from pyptp.elements.lv.node import NodeLV
    from pyptp.elements.lv.shared import GeoCablePart
    from pyptp.network_lv import NetworkLV

Point = tuple[float, float]
Drawing = tuple[BranchPresentation, Sequence[Point]]
PointOrPixel = TypeVar("PointOrPixel", bound=Point)

_MIN_ROUTE_POINTS = 2
_METRES_PER_DEGREE_LATITUDE = 111_195.0
_MAX_LONGITUDE = 180.0
_MAX_LATITUDE = 90.0


@dataclass
class CableRoutes:
    """A cable's geography and drawings, or those of one section."""

    cablepart: list[Point] | None
    geography: list[Point] | None
    straight_line: list[Point] | None
    """The line between the end nodes on the map, when both have a map position."""
    drawings: list[Drawing]

    @property
    def geography_route(self) -> list[Point] | None:
        """Return the cable's own route on the map, or None without one."""
        if self.cablepart is not None:
            return self.cablepart
        return self.geography

    @property
    def map_route(self) -> list[Point] | None:
        """Return the route on the map that joints are placed on."""
        if self.geography_route is not None:
            return self.geography_route
        return self.straight_line

    def cut(self, fractions: Sequence[float]) -> list[CableRoutes]:
        """Cut every route at the ascending ``fractions`` of its length, into one ``CableRoutes`` per section."""
        section_count = len(fractions) + 1
        cablepart_by_section = _cut_if_present(self.cablepart, fractions, section_count)
        geography_by_section = _cut_if_present(self.geography, fractions, section_count)
        straight_line_by_section = _cut_if_present(self.straight_line, fractions, section_count)

        sections = []
        for cablepart, geography, straight_line in zip(
            cablepart_by_section, geography_by_section, straight_line_by_section, strict=True
        ):
            sections.append(CableRoutes(cablepart, geography, straight_line, drawings=[]))

        for presentation, polyline in self.drawings:
            polyline_by_section = cut_route(polyline, fractions)
            for section, section_polyline in zip(sections, polyline_by_section, strict=True):
                section.drawings.append((presentation, section_polyline))
        return sections


def cable_routes(network: NetworkLV, cable: CableLV) -> CableRoutes:
    """Return the cable's routes from node 1 to node 2.

    Raises:
        ValueError: If a drawing's end node is missing from its sheet, or the
            geography cannot be oriented.

    """
    node1 = network.nodes[cable.general.node1]
    node2 = network.nodes[cable.general.node2]

    drawings: list[Drawing] = []
    for presentation in cable.presentations:
        node_presentations_on_sheet(node1, node2, presentation.sheet)
        drawings.append((presentation, presentation.polyline()))

    cablepart = _oriented_geography(node1.general, node2.general, cable.cablepart_geography)
    geography = _oriented_geography(node1.general, node2.general, cable.geography)
    straight_line = _straight_line(node1.general, node2.general)
    return CableRoutes(cablepart, geography, straight_line, drawings)


def route_length(route: Sequence[Point]) -> float:
    """Return the length of ``route``."""
    return sum(math.dist(start, end) for start, end in pairwise(route))


def nearest_fraction(route: Sequence[Point], point: Point) -> float:
    """Return where ``route`` passes nearest to ``point``, as a fraction of its length."""
    total_length = route_length(route)
    if total_length == 0:
        return 0.0

    nearest_distance = math.inf
    nearest_along_route = 0.0
    walked = 0.0
    for start, end in pairwise(route):
        along_segment = _distance_along_segment(start, end, point)
        on_segment = _point_along_segment(start, end, along_segment)

        distance = math.dist(point, on_segment)
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_along_route = walked + along_segment

        walked += math.dist(start, end)

    return nearest_along_route / total_length


def cut_route(route: Sequence[Point], fractions: Sequence[float]) -> list[list[Point]]:
    """Cut ``route`` at the ascending ``fractions`` of its length, into one route per section."""
    total_length = route_length(route)
    cut_distances = [fraction * total_length for fraction in fractions]

    section_routes = []
    section_route = [route[0]]
    walked = 0.0
    for start, end in pairwise(route):
        segment_length = math.dist(start, end)
        while cut_distances and cut_distances[0] <= walked + segment_length:
            cut_distance = cut_distances.pop(0)
            cut_point = _point_along_segment(start, end, cut_distance - walked)
            section_route.append(cut_point)
            section_routes.append(section_route)
            section_route = [cut_point]

        if section_route[-1] != end:
            section_route.append(end)
        walked += segment_length

    section_routes.append(section_route)
    return section_routes


def nearest_fraction_on_map(route: Sequence[Point], point: Point) -> float:
    """Return ``nearest_fraction`` for a route on the map, measuring a route in degrees in metres."""
    if not in_degrees(route):
        return nearest_fraction(route, point)

    origin = route[0]
    location = to_metres([point], origin)[0]
    return nearest_fraction(to_metres(route, origin), location)


def cut_on_map(route: Sequence[Point], fractions: Sequence[float]) -> list[list[Point]]:
    """Cut a route on the map like ``cut_route``, measuring a route in degrees in metres."""
    if not in_degrees(route):
        return cut_route(route, fractions)

    origin = route[0]
    section_routes = []
    for section_in_metres in cut_route(to_metres(route, origin), fractions):
        section_in_degrees = to_the_millimetre(to_degrees(section_in_metres, origin))
        section_routes.append(without_repeats(section_in_degrees))
    return section_routes


def in_degrees(route: Sequence[Point]) -> bool:
    """Return whether a route on the map is in degrees of longitude and latitude, rather than metres.

    Every point must be a longitude and latitude within range, neither of them zero.
    """
    for longitude, latitude in route:
        if longitude == 0 or latitude == 0:
            return False
        if abs(longitude) > _MAX_LONGITUDE or abs(latitude) > _MAX_LATITUDE:
            return False
    return True


def to_metres(route: Sequence[Point], origin: Point) -> list[Point]:
    """Return a route in degrees as metres east and north of ``origin``."""
    origin_longitude, origin_latitude = origin
    metres_per_degree_longitude = _metres_per_degree_longitude(origin_latitude)
    in_metres = []
    for longitude, latitude in route:
        east = (longitude - origin_longitude) * metres_per_degree_longitude
        north = (latitude - origin_latitude) * _METRES_PER_DEGREE_LATITUDE
        in_metres.append((east, north))
    return in_metres


def to_degrees(route: Sequence[Point], origin: Point) -> list[Point]:
    """Return a route in metres east and north of ``origin`` as degrees."""
    origin_longitude, origin_latitude = origin
    metres_per_degree_longitude = _metres_per_degree_longitude(origin_latitude)
    points = []
    for east, north in route:
        longitude = origin_longitude + east / metres_per_degree_longitude
        latitude = origin_latitude + north / _METRES_PER_DEGREE_LATITUDE
        points.append((longitude, latitude))
    return points


def to_the_millimetre(route: Sequence[Point]) -> list[Point]:
    """Return a route on the map rounded to the millimetre."""
    decimals = 8 if in_degrees(route) else 3
    return [(round(x, decimals), round(y, decimals)) for x, y in route]


def map_position(node: NodeLV.General) -> Point | None:
    """Return the node's position on the map, or None when it has none."""
    # A node at (0, 0) has no coordinates
    position = (node.gx, node.gy)
    if position == (0, 0):
        return None
    return position


def without_repeats(route: Sequence[PointOrPixel]) -> list[PointOrPixel]:
    """Return ``route`` without points that repeat the point before them."""
    distinct: list[PointOrPixel] = []
    for point in route:
        if not distinct or point != distinct[-1]:
            distinct.append(point)
    return distinct


def _metres_per_degree_longitude(latitude: float) -> float:
    return _METRES_PER_DEGREE_LATITUDE * math.cos(math.radians(latitude))


def _cut_if_present(route: list[Point] | None, fractions: Sequence[float], count: int) -> list[list[Point] | None]:
    """Cut ``route`` like ``cut_on_map``, or give ``count`` Nones when there is no route."""
    if route is None:
        return [None] * count
    section_routes: list[list[Point] | None] = [*cut_on_map(route, fractions)]
    return section_routes


def _distance_along_segment(start: Point, end: Point, point: Point) -> float:
    """Return how far from ``start`` the segment passes nearest to ``point``."""
    segment_length = math.dist(start, end)
    if segment_length == 0:
        return 0.0

    start_x, start_y = start
    end_x, end_y = end
    point_x, point_y = point
    projection = ((point_x - start_x) * (end_x - start_x) + (point_y - start_y) * (end_y - start_y)) / segment_length
    return max(0.0, min(projection, segment_length))


def _point_along_segment(start: Point, end: Point, distance: float) -> Point:
    """Return the point ``distance`` from ``start`` towards ``end``."""
    segment_length = math.dist(start, end)
    if segment_length == 0:
        return start

    share = distance / segment_length
    start_x, start_y = start
    end_x, end_y = end
    return (start_x + share * (end_x - start_x), start_y + share * (end_y - start_y))


def _straight_line(node1: NodeLV.General, node2: NodeLV.General) -> list[Point] | None:
    """Return the line from node 1 to node 2 on the map, or None if either has no map position."""
    node1_position = map_position(node1)
    node2_position = map_position(node2)
    if node1_position is None or node2_position is None:
        return None
    return [node1_position, node2_position]


def _oriented_geography(
    node1: NodeLV.General,
    node2: NodeLV.General,
    part: GeoCablePart | None,
) -> list[Point] | None:
    """Return the cable's geography running from node 1 to node 2, or None without geography."""
    if part is None or len(part.coordinates) < _MIN_ROUTE_POINTS:
        return None

    points = list(part.coordinates)
    first_point = points[0]
    last_point = points[-1]

    node1_position = map_position(node1)
    node2_position = map_position(node2)
    if node1_position is None and node2_position is None:
        msg = "Cable geography cannot be oriented: neither end node has coordinates"
        raise ValueError(msg)

    stored_order = 0.0
    reversed_order = 0.0
    if node1_position is not None:
        stored_order += math.dist(first_point, node1_position)
        reversed_order += math.dist(last_point, node1_position)
    if node2_position is not None:
        stored_order += math.dist(last_point, node2_position)
        reversed_order += math.dist(first_point, node2_position)

    if reversed_order < stored_order:
        points.reverse()
    return points
