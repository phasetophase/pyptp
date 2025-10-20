"""Helper functions for network presentation coordinate transformations.

Provides reusable functions for calculating bounds, scaling, and transforming
presentation coordinates across both LV and MV network types.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Sequence

    from pyptp.elements.element_utils import Guid


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
