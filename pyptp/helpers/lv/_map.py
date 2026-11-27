"""Routes on the map, in RD metres or in degrees of longitude and latitude."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyptp.helpers.lv._routes import in_degrees, offset_route, to_degrees, to_metres

if TYPE_CHECKING:
    from collections.abc import Sequence

    from pyptp.helpers.lv._routes import Point


def offset_on_map(route: Sequence[Point], metres: float) -> list[Point]:
    """Return ``route`` moved ``metres`` to its right, seen walking along it with north up."""
    # y runs up on the map and down on a sheet
    if not in_degrees(route):
        return offset_route(route, -metres)

    origin = route[0]
    moved = offset_route(to_metres(route, origin), -metres)
    return to_degrees(moved, origin)
