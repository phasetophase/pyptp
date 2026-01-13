# SPDX-FileCopyrightText: Contributors to the PyPtP project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Branch corner coordinate validator for network presentation integrity.

Ensures that branch presentation corners start at the correct node positions,
supporting proper visual representation of electrical connections in network
diagrams. Handles special node symbols (vertical/horizontal lines) that have
extended hit areas based on their size property.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from pyptp.elements.enums import NodePresentationSymbol
from pyptp.elements.presentation_helpers import (
    COORDINATE_GRID_SIZE,
    NODE_SIZE_PIXEL_MULTIPLIER,
    round_to_grid,
)
from pyptp.validator import Issue, Severity, Validator, ValidatorCategory

if TYPE_CHECKING:
    from collections.abc import Mapping

    from pyptp.elements.element_utils import Guid
    from pyptp.network_lv import NetworkLV
    from pyptp.network_mv import NetworkMV


class _BranchGeneral(Protocol):
    """Protocol for branch general attributes needed by validator."""

    @property
    def guid(self) -> Guid: ...
    @property
    def name(self) -> str: ...
    @property
    def node1(self) -> Guid: ...
    @property
    def node2(self) -> Guid: ...


class _BranchPresentation(Protocol):
    """Protocol for branch presentation attributes needed by validator."""

    @property
    def sheet(self) -> Guid: ...
    @property
    def first_corners(self) -> list[tuple[int, int]]: ...
    @property
    def second_corners(self) -> list[tuple[int, int]]: ...


class _Branch(Protocol):
    """Protocol for branch elements that can be validated."""

    @property
    def general(self) -> _BranchGeneral: ...
    @property
    def presentations(self) -> list[_BranchPresentation]: ...


class _NodePresentation(Protocol):
    """Protocol for node presentation with point containment check."""

    @property
    def x(self) -> int: ...
    @property
    def y(self) -> int: ...
    @property
    def symbol(self) -> NodePresentationSymbol: ...
    @property
    def size(self) -> int: ...
    def contains_point(self, point: tuple[int, int]) -> bool: ...


def _point_matches_node_on_grid(
    point: tuple[int, int],
    node_pres: _NodePresentation,
    grid_size: int = COORDINATE_GRID_SIZE,
) -> bool:
    """Check if a point will match a node position after grid rounding.

    For line-type symbols (VERTICAL_LINE, HORIZONTAL_LINE), checks if the
    rounded point falls within the line's extent.

    For other symbols, checks if both coordinates round to the same grid point.

    Args:
        point: (x, y) coordinate tuple to check.
        node_pres: Node presentation with position, symbol and size.
        grid_size: Grid alignment size for rounding.

    Returns:
        True if the point will align with the node after grid rounding.

    """
    point_x, point_y = point
    node_x, node_y = node_pres.x, node_pres.y
    symbol = node_pres.symbol
    size = node_pres.size

    if symbol == NodePresentationSymbol.VERTICAL_LINE:
        extent = size * NODE_SIZE_PIXEL_MULTIPLIER
        return round_to_grid(point_x, grid_size) == round_to_grid(node_x, grid_size) and (
            node_y - extent
        ) <= point_y <= (node_y + extent)

    if symbol == NodePresentationSymbol.HORIZONTAL_LINE:
        extent = size * NODE_SIZE_PIXEL_MULTIPLIER
        return round_to_grid(point_y, grid_size) == round_to_grid(node_y, grid_size) and (
            node_x - extent
        ) <= point_x <= (node_x + extent)

    return round_to_grid(point_x, grid_size) == round_to_grid(node_x, grid_size) and round_to_grid(
        point_y, grid_size
    ) == round_to_grid(node_y, grid_size)


class _Node(Protocol):
    """Protocol for nodes that can be looked up by the validator.

    The return type uses Any to match HasPresentationsMixin's return type,
    since the mixin can't know the specific presentation type at definition.
    """

    def get_presentation_on_sheet(self, sheet_guid: Guid) -> _NodePresentation | None:
        """Get the node's presentation on a specific sheet."""
        ...


def _get_branch_collections(network: NetworkLV | NetworkMV) -> list[tuple[str, dict]]:
    """Get all branch element collections from the network.

    Returns a list of (element_type_name, collection_dict) tuples for all
    branch types present in the network.

    Args:
        network: Network model (LV or MV).

    Returns:
        List of tuples: (human-readable type name, collection dictionary).

    """
    collections: list[tuple[str, dict]] = []

    # Common to both LV and MV
    collections.append(("Link", network.links))
    collections.append(("Cable", network.cables))
    collections.append(("Transformer", network.transformers))
    collections.append(("SpecialTransformer", network.special_transformers))
    collections.append(("ReactanceCoil", network.reactance_coils))

    # MV only - use getattr to avoid type error for NetworkLV
    lines = getattr(network, "lines", None)
    if lines is not None:
        collections.append(("Line", lines))

    return collections


class BranchCornerCoordinatesValidator(Validator):
    """Verifies branch presentation corners align with node positions.

    For each branch element, validates that:
    1. first_corners[0] matches node1's position on the same sheet
    2. second_corners[0] matches node2's position on the same sheet
    3. Corner arrays are not empty (warns if missing routing information)

    Handles special node symbols (VERTICAL_LINE, HORIZONTAL_LINE) where the
    valid connection area extends based on the node's size property.
    """

    name = "branch_corner_coordinates"
    description = "Verifies branch presentation corners align with node positions"
    applies_to = ("LV", "MV")
    categories = ValidatorCategory.CORE

    def validate(self, network: NetworkLV | NetworkMV) -> list[Issue]:
        """Validate all branch corner coordinates match node positions.

        Args:
            network: Network model to validate (LV or MV).

        Returns:
            List of validation issues found. Empty if all coordinates are valid.

        """
        issues: list[Issue] = []

        for element_type, collection in _get_branch_collections(network):
            for branch in collection.values():
                issues.extend(
                    self._validate_branch(
                        branch,
                        element_type,
                        network.nodes,  # type: ignore[arg-type]  # Mixin method not visible to type checker
                    )
                )

        return issues

    def _validate_branch(
        self,
        branch: _Branch,
        element_type: str,
        nodes: Mapping[Guid, _Node],
    ) -> list[Issue]:
        """Validate a single branch element's presentations.

        Args:
            branch: Branch element with general and presentations attributes.
            element_type: Human-readable type name for error messages.
            nodes: Dictionary of nodes indexed by GUID.

        Returns:
            List of issues found for this branch.

        """
        issues: list[Issue] = []
        general = branch.general
        branch_guid = general.guid
        branch_name = general.name or str(branch_guid)

        node1_guid = general.node1
        node2_guid = general.node2

        # Skip if nodes don't exist (separate validator handles this)
        node1 = nodes.get(node1_guid)
        node2 = nodes.get(node2_guid)
        if node1 is None or node2 is None:
            return issues

        for pres_idx, pres in enumerate(branch.presentations):
            sheet_guid = pres.sheet
            first_corners = pres.first_corners
            second_corners = pres.second_corners

            # Check for empty corner arrays
            if not first_corners:
                issues.append(
                    self._create_empty_corners_issue(
                        branch_guid,
                        branch_name,
                        element_type,
                        "first_corners",
                        pres_idx,
                    )
                )
            if not second_corners:
                issues.append(
                    self._create_empty_corners_issue(
                        branch_guid,
                        branch_name,
                        element_type,
                        "second_corners",
                        pres_idx,
                    )
                )

            # Validate first_corners[0] against node1 (using grid-normalized comparison)
            if first_corners:
                node1_pres = node1.get_presentation_on_sheet(sheet_guid)
                if node1_pres is not None and not _point_matches_node_on_grid(first_corners[0], node1_pres):
                    issues.append(
                        self._create_mismatch_issue(
                            branch_guid,
                            branch_name,
                            element_type,
                            "first_corners",
                            first_corners[0],
                            (node1_pres.x, node1_pres.y),
                            node1_guid,
                            pres_idx,
                        )
                    )

            # Validate second_corners[0] against node2 (using grid-normalized comparison)
            if second_corners:
                node2_pres = node2.get_presentation_on_sheet(sheet_guid)
                if node2_pres is not None and not _point_matches_node_on_grid(second_corners[0], node2_pres):
                    issues.append(
                        self._create_mismatch_issue(
                            branch_guid,
                            branch_name,
                            element_type,
                            "second_corners",
                            second_corners[0],
                            (node2_pres.x, node2_pres.y),
                            node2_guid,
                            pres_idx,
                        )
                    )

        return issues

    def _create_empty_corners_issue(
        self,
        branch_guid: Guid,
        branch_name: str,
        element_type: str,
        corner_type: str,
        presentation_index: int,
    ) -> Issue:
        """Create an issue for empty corner arrays.

        Args:
            branch_guid: GUID of the branch element.
            branch_name: Name of the branch element.
            element_type: Type of branch element.
            corner_type: Which corners are empty ('first_corners' or 'second_corners').
            presentation_index: Index of the presentation within the branch.

        Returns:
            Issue describing the empty corners.

        """
        return Issue(
            code="empty_corner_array",
            message=(f"{element_type} '{branch_name}' has empty {corner_type} in presentation {presentation_index}"),
            severity=Severity.WARNING,
            object_type=element_type,
            object_id=branch_guid,
            validator=self.name,
            details={
                "corner_type": corner_type,
                "presentation_index": presentation_index,
            },
        )

    def _create_mismatch_issue(
        self,
        branch_guid: Guid,
        branch_name: str,
        element_type: str,
        corner_type: str,
        actual_coord: tuple[int, int],
        expected_coord: tuple[int, int],
        node_guid: Guid,
        presentation_index: int,
    ) -> Issue:
        """Create an issue for coordinate mismatches.

        Args:
            branch_guid: GUID of the branch element.
            branch_name: Name of the branch element.
            element_type: Type of branch element.
            corner_type: Which corners have mismatch ('first_corners' or 'second_corners').
            actual_coord: The actual coordinate found in the corners.
            expected_coord: The expected coordinate based on node position.
            node_guid: GUID of the node that should be matched.
            presentation_index: Index of the presentation within the branch.

        Returns:
            Issue describing the coordinate mismatch.

        """
        return Issue(
            code="corner_coordinate_mismatch",
            message=(
                f"{element_type} '{branch_name}' {corner_type}[0] at {actual_coord} "
                f"does not match node position {expected_coord}"
            ),
            severity=Severity.WARNING,
            object_type=element_type,
            object_id=branch_guid,
            validator=self.name,
            details={
                "corner_type": corner_type,
                "actual_coordinate": actual_coord,
                "expected_coordinate": expected_coord,
                "node_guid": node_guid,
                "presentation_index": presentation_index,
            },
        )
