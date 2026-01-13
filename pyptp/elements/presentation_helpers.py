"""Helper functions for network presentation coordinate transformations.

Provides reusable functions for calculating bounds, scaling, and transforming
presentation coordinates across both LV and MV network types.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from pyptp.elements.enums import NodePresentationSymbol

if TYPE_CHECKING:
    from collections.abc import Sequence

    from pyptp.elements.element_utils import Guid


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
