"""Helper functions for network presentation coordinate transformations.

Provides reusable functions for calculating bounds, scaling, and transforming
presentation coordinates across both LV and MV network types.
"""

from __future__ import annotations

import math
from itertools import pairwise
from typing import TYPE_CHECKING, Protocol

from pyptp.elements.element_utils import name_or_guid
from pyptp.elements.enums import NodePresentationSymbol, SymbolSegment

if TYPE_CHECKING:
    from collections.abc import Sequence

    from pyptp.elements.element_utils import Guid, IntCoords
    from pyptp.elements.lv.node import NodeLV
    from pyptp.elements.lv.presentations import NodePresentation as NodePresentationLV
    from pyptp.elements.mv.node import NodeMV
    from pyptp.elements.mv.presentations import NodePresentation as NodePresentationMV


COORDINATE_GRID_SIZE: int = 20
"""Grid size used for coordinate snapping in Gaia/Vision file formats."""


def round_to_grid(value: int, grid_size: int = COORDINATE_GRID_SIZE) -> int:
    """Round a coordinate value to the nearest grid point.

    Args:
        value: Coordinate value to round.
        grid_size: Grid alignment size (default: COORDINATE_GRID_SIZE).

    Returns:
        Value rounded to nearest multiple of grid_size.

    """
    return grid_size * round(value / grid_size)


def points_match_on_grid(
    point1: tuple[int, int],
    point2: tuple[int, int],
    grid_size: int = COORDINATE_GRID_SIZE,
) -> bool:
    """Check if two points will match after grid rounding.

    Useful for validating whether coordinates that differ slightly will
    resolve to the same position when saved to file format.

    Args:
        point1: First (x, y) coordinate tuple.
        point2: Second (x, y) coordinate tuple.
        grid_size: Grid alignment size (default: COORDINATE_GRID_SIZE).

    Returns:
        True if both points round to the same grid position.

    """
    return round_to_grid(point1[0], grid_size) == round_to_grid(point2[0], grid_size) and round_to_grid(
        point1[1], grid_size
    ) == round_to_grid(point2[1], grid_size)


NODE_SIZE_PIXEL_MULTIPLIER: int = 10
"""Base pixel size per size unit in Gaia/Vision rendering.

Used to calculate the visual extent of line-type node symbols (VERTICAL_LINE,
HORIZONTAL_LINE) where the connection area extends beyond a single point.
The actual extent is calculated as: size * NODE_SIZE_PIXEL_MULTIPLIER pixels.
"""


def point_in_node_bounds(
    point: tuple[int, int],
    node_x: int,
    node_y: int,
    symbol: NodePresentationSymbol,
    size: int,
) -> bool:
    """Check if a coordinate point falls within a node's visual bounds.

    Handles special node symbols where the valid connection area extends
    beyond a single point:

    - VERTICAL_LINE: Line extends along Y-axis by size * NODE_SIZE_PIXEL_MULTIPLIER
      pixels in each direction. Point must have matching X and Y within the range.
    - HORIZONTAL_LINE: Line extends along X-axis by size * NODE_SIZE_PIXEL_MULTIPLIER
      pixels in each direction. Point must have matching Y and X within the range.
    - Other symbols (circles, squares, etc.): Point must match (node_x, node_y) exactly.

    Args:
        point: (x, y) coordinate tuple to check.
        node_x: X coordinate of the node presentation.
        node_y: Y coordinate of the node presentation.
        symbol: The node's presentation symbol type.
        size: The node's presentation size.

    Returns:
        True if the point falls within the node's visual bounds.

    """
    point_x, point_y = point

    if symbol == NodePresentationSymbol.VERTICAL_LINE:
        extent = size * NODE_SIZE_PIXEL_MULTIPLIER
        return point_x == node_x and (node_y - extent) <= point_y <= (node_y + extent)

    if symbol == NodePresentationSymbol.HORIZONTAL_LINE:
        extent = size * NODE_SIZE_PIXEL_MULTIPLIER
        return point_y == node_y and (node_x - extent) <= point_x <= (node_x + extent)

    return point_x == node_x and point_y == node_y


def clamp_point_to_node(
    point: tuple[int, int],
    node_x: int,
    node_y: int,
    symbol: NodePresentationSymbol,
    size: int,
) -> tuple[int, int]:
    """Clamp a point to the nearest valid connection position on a node.

    For line-type symbols, finds the closest point on the line segment.
    For other symbols, returns the node's center coordinates.

    This function requires the node presentation to be fully defined with
    valid coordinates, symbol, and size before calling.

    Args:
        point: (x, y) coordinate tuple to clamp.
        node_x: X coordinate of the node presentation.
        node_y: Y coordinate of the node presentation.
        symbol: The node's presentation symbol type.
        size: The node's presentation size.

    Returns:
        The clamped (x, y) coordinate on the node's visual bounds.

    """
    point_x, point_y = point

    if symbol == NodePresentationSymbol.VERTICAL_LINE:
        extent = size * NODE_SIZE_PIXEL_MULTIPLIER
        clamped_y = max(node_y - extent, min(point_y, node_y + extent))
        return (node_x, clamped_y)

    if symbol == NodePresentationSymbol.HORIZONTAL_LINE:
        extent = size * NODE_SIZE_PIXEL_MULTIPLIER
        clamped_x = max(node_x - extent, min(point_x, node_x + extent))
        return (clamped_x, node_y)

    return (node_x, node_y)


def node_presentations_on_sheet(
    node1: NodeLV | NodeMV,
    node2: NodeLV | NodeMV,
    sheet_guid: Guid,
) -> tuple[NodePresentationLV | NodePresentationMV, NodePresentationLV | NodePresentationMV]:
    """Return the presentation of each node on one sheet.

    Raises:
        ValueError: If either node has no presentation on that sheet.

    """
    presentation1 = _node_presentation_on_sheet(node1, 1, sheet_guid)
    presentation2 = _node_presentation_on_sheet(node2, 2, sheet_guid)
    return presentation1, presentation2


def _node_presentation_on_sheet(
    node: NodeLV | NodeMV,
    number: int,
    sheet_guid: Guid,
) -> NodePresentationLV | NodePresentationMV:
    presentation = node.get_presentation_on_sheet(sheet_guid)
    if presentation is None:
        msg = f"Node {number} ({name_or_guid(node.general)}) has no presentation on sheet {sheet_guid}"
        raise ValueError(msg)
    return presentation


def _segment_lengths(route: IntCoords) -> list[float]:
    return [math.hypot(x2 - x1, y2 - y1) for (x1, y1), (x2, y2) in pairwise(route)]


def _symbol_segment_index(route: IntCoords, symbol_segment: SymbolSegment | int) -> int:
    """Return the index of the segment that gets the branch symbol.

    Raises:
        TypeError: If ``symbol_segment`` is neither a :class:`SymbolSegment` nor an int.
        ValueError: If ``symbol_segment`` is an index outside the route.

    """
    lengths = _segment_lengths(route)
    if isinstance(symbol_segment, SymbolSegment):
        return _named_segment_index(lengths, symbol_segment)
    if isinstance(symbol_segment, bool) or not isinstance(symbol_segment, int):
        msg = f"symbol_segment must be a SymbolSegment or a segment index, got {symbol_segment!r}"
        raise TypeError(msg)
    return _counted_segment_index(lengths, symbol_segment)


def _named_segment_index(lengths: list[float], symbol_segment: SymbolSegment) -> int:
    if symbol_segment is SymbolSegment.LONGEST:
        return lengths.index(max(lengths))
    return _middle_segment_index(lengths)


def _middle_segment_index(lengths: list[float]) -> int:
    total = sum(lengths)
    if total == 0.0:
        return 0
    covered = 0.0
    for index, length in enumerate(lengths):
        covered += length
        if covered >= total / 2:
            return index
    return len(lengths) - 1


def _counted_segment_index(lengths: list[float], symbol_segment: int) -> int:
    count = len(lengths)
    if not -count <= symbol_segment < count:
        msg = f"symbol_segment {symbol_segment} is out of range for a route of {count} segments"
        raise ValueError(msg)
    return symbol_segment % count


def route_corners(
    presentation1: NodePresentationLV | NodePresentationMV,
    presentation2: NodePresentationLV | NodePresentationMV,
    via: Sequence[tuple[int, int]] = (),
    symbol_segment: SymbolSegment | int = SymbolSegment.MIDDLE,
) -> tuple[IntCoords, IntCoords]:
    """Return ``first_corners`` and ``second_corners`` for a route between two node presentations.

    ``via`` gives the corners from node 1 to node 2. ``symbol_segment`` is a
    :class:`SymbolSegment` or the index of a segment counted from node 1. A
    negative index counts from node 2.

    Raises:
        TypeError: If ``symbol_segment`` is neither a :class:`SymbolSegment` nor an int.
        ValueError: If ``symbol_segment`` is an index outside the route.

    """
    points: IntCoords = [(int(x), int(y)) for x, y in via]
    if points:
        toward_start = points[0]
        toward_end = points[-1]
    else:
        toward_start = (presentation2.x, presentation2.y)
        toward_end = (presentation1.x, presentation1.y)
    start = presentation1.clamp_point(toward_start)
    end = presentation2.clamp_point(toward_end)

    if points and points[0] == start:
        points = points[1:]
    if points and points[-1] == end:
        points = points[:-1]

    index = _symbol_segment_index([start, *points, end], symbol_segment)
    return [start, *points[:index]], [end, *reversed(points[index:])]


def branch_polyline(first_corners: IntCoords, second_corners: IntCoords) -> IntCoords:
    """Return the drawn route of a branch as one list, from node 1 to node 2."""
    return [*first_corners, *reversed(second_corners)]


class HasPresentation(Protocol):
    """Protocol for objects with presentation data."""

    @property
    def sheet(self) -> Guid:
        """Sheet GUID where presentation is displayed."""
        ...

    @property
    def x(self) -> int | float:
        """X coordinate on sheet."""
        ...

    @property
    def y(self) -> int | float:
        """Y coordinate on sheet."""
        ...


def compute_presentation_bounds(
    presentations: Sequence[HasPresentation],
    sheet_guid: Guid,
) -> tuple[float, float, float, float]:
    """Calculate bounding box for all presentations on specified sheet.

    Args:
        presentations: List of presentation objects to compute bounds for.
        sheet_guid: Target sheet for bounds calculation.

    Returns:
        Tuple of (min_x, min_y, max_x, max_y) coordinate bounds.
        Returns infinities if no valid presentations found.

    """
    min_x: float = float("inf")
    min_y: float = float("inf")
    max_x: float = float("-inf")
    max_y: float = float("-inf")

    for pres in presentations:
        if pres.sheet == sheet_guid:
            min_x = min(min_x, pres.x)
            min_y = min(min_y, pres.y)
            max_x = max(max_x, pres.x)
            max_y = max(max_y, pres.y)

    return min_x, min_y, max_x, max_y


def calculate_auto_scale(
    min_x: float,
    min_y: float,
    max_x: float,
    max_y: float,
) -> float:
    """Calculate automatic scale factor based on content bounds.

    Used primarily for LV networks to auto-size presentation to fit viewport.

    Args:
        min_x: Minimum X coordinate from bounds calculation.
        min_y: Minimum Y coordinate from bounds calculation.
        max_x: Maximum X coordinate from bounds calculation.
        max_y: Maximum Y coordinate from bounds calculation.

    Returns:
        Scale factor for coordinate transformation (minimum 120.0).

    """
    delta_x: float = abs(max_x - min_x)
    delta_y: float = abs(max_y - min_y)
    scale: float = 120.0
    max_delta: float = max(delta_x, delta_y)
    if max_delta > 0.0:
        scale = (800.0 / max_delta) + 120.0
    return scale


def transform_point(
    x: float,
    y: float,
    min_x: float,
    min_y: float,
    scale: float,
    grid_size: int = 0,
    *,
    invert_y: bool = True,
) -> tuple[int, int]:
    """Transform and optionally grid-snap a coordinate point.

    Applies offset normalization, scaling, optional grid snapping, and Y-axis inversion.

    Args:
        x: X coordinate to transform.
        y: Y coordinate to transform.
        min_x: X offset for normalization.
        min_y: Y offset for normalization.
        scale: Scale factor for transformation.
        grid_size: Grid alignment size (0 = no snapping).
        invert_y: Whether to invert Y-axis (default True for both LV and MV).

    Returns:
        Tuple of (transformed_x, transformed_y) as integers.

    """
    # Apply offset and scale
    new_x = (x - min_x) * scale
    new_y = (y - min_y) * scale

    # Grid snapping if requested
    if grid_size > 0:
        new_x = grid_size * round(new_x / grid_size)
        new_y = grid_size * round(new_y / grid_size)
    else:
        new_x = round(new_x)
        new_y = round(new_y)

    # Y-axis inversion
    if invert_y:
        new_y = new_y * -1

    return int(new_x), int(new_y)


def transform_corners(
    corners: Sequence[tuple[float, float]],
    min_x: float,
    min_y: float,
    scale: float,
    grid_size: int = 0,
    *,
    invert_y: bool = True,
) -> list[tuple[int, int]]:
    """Transform list of corner coordinates for cable/branch presentations.

    Args:
        corners: Sequence of (x, y) coordinate tuples (accepts float coordinates).
        min_x: X offset for normalization.
        min_y: Y offset for normalization.
        scale: Scale factor for transformation.
        grid_size: Grid alignment size (0 = no snapping).
        invert_y: Whether to invert Y-axis (default True).

    Returns:
        List of transformed (x, y) coordinate tuples as integers.

    """
    return [transform_point(x, y, min_x, min_y, scale, grid_size, invert_y=invert_y) for x, y in corners]
