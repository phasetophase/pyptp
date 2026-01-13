"""Tests for branch corner coordinate validator."""

from __future__ import annotations

import unittest

from pyptp.elements.enums import NodePresentationSymbol
from pyptp.elements.lv.link import LinkLV
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import BranchPresentation as BranchPresentationLV
from pyptp.elements.lv.presentations import NodePresentation as NodePresentationLV
from pyptp.elements.lv.sheet import SheetLV
from pyptp.elements.mv.link import LinkMV
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import BranchPresentation as BranchPresentationMV
from pyptp.elements.mv.presentations import NodePresentation as NodePresentationMV
from pyptp.elements.mv.sheet import SheetMV
from pyptp.network_lv import NetworkLV
from pyptp.network_mv import NetworkMV
from pyptp.validator.shared.branch_corner_coordinates import (
    BranchCornerCoordinatesValidator,
)
from pyptp.validator.test_helpers import assert_issue_count, assert_no_validation_issues


class TestBranchCornerCoordinatesLV(unittest.TestCase):
    """LV-specific tests for the branch corner coordinates validator."""

    def setUp(self) -> None:
        """Set up test network with a sheet."""
        self.network = NetworkLV()
        self.sheet = SheetLV(general=SheetLV.General(name="TestSheet"))
        self.sheet.register(self.network)
        self.sheet_guid = self.sheet.general.guid
        self.validator = BranchCornerCoordinatesValidator()

    def create_node(
        self,
        name: str,
        x: int,
        y: int,
        symbol: NodePresentationSymbol = NodePresentationSymbol.CLOSED_CIRCLE,
        size: int = 1,
    ) -> NodeLV:
        """Create a node with presentation at specified coordinates."""
        node = NodeLV(
            general=NodeLV.General(name=name),
            presentations=[
                NodePresentationLV(
                    sheet=self.sheet_guid,
                    x=x,
                    y=y,
                    symbol=symbol,
                    size=size,
                )
            ],
        )
        node.register(self.network)
        return node

    def create_link(
        self,
        name: str,
        node1: NodeLV,
        node2: NodeLV,
        first_corners: list[tuple[int, int]],
        second_corners: list[tuple[int, int]],
    ) -> LinkLV:
        """Create a link with specified corner coordinates."""
        link = LinkLV(
            general=LinkLV.General(
                name=name,
                node1=node1.general.guid,
                node2=node2.general.guid,
            ),
            presentations=[
                BranchPresentationLV(
                    sheet=self.sheet_guid,
                    first_corners=first_corners,
                    second_corners=second_corners,
                )
            ],
        )
        link.register(self.network)
        return link

    def test_valid_coordinates_no_issues(self) -> None:
        """Test that correct coordinates produce no issues."""
        node1 = self.create_node("Node1", x=100, y=100)
        node2 = self.create_node("Node2", x=300, y=100)
        self.create_link(
            "Link1",
            node1,
            node2,
            first_corners=[(100, 100), (200, 100)],
            second_corners=[(300, 100)],
        )

        assert_no_validation_issues(self, self.validator, self.network)

    def test_mismatched_first_corners_reports_issue(self) -> None:
        """Test that mismatched first_corners produces a warning."""
        node1 = self.create_node("Node1", x=100, y=100)
        node2 = self.create_node("Node2", x=300, y=100)
        self.create_link(
            "Link1",
            node1,
            node2,
            first_corners=[(150, 100), (200, 100)],  # Wrong: should start at (100, 100)
            second_corners=[(300, 100)],
        )

        issues = self.validator.validate(self.network)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "corner_coordinate_mismatch")
        self.assertIsNotNone(issues[0].details)
        assert issues[0].details is not None  # For type checker
        self.assertEqual(issues[0].details["corner_type"], "first_corners")

    def test_mismatched_second_corners_reports_issue(self) -> None:
        """Test that mismatched second_corners produces a warning."""
        node1 = self.create_node("Node1", x=100, y=100)
        node2 = self.create_node("Node2", x=300, y=100)
        self.create_link(
            "Link1",
            node1,
            node2,
            first_corners=[(100, 100), (200, 100)],
            second_corners=[(250, 100)],  # Wrong: should start at (300, 100)
        )

        issues = self.validator.validate(self.network)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "corner_coordinate_mismatch")
        self.assertIsNotNone(issues[0].details)
        assert issues[0].details is not None  # For type checker
        self.assertEqual(issues[0].details["corner_type"], "second_corners")

    def test_empty_first_corners_reports_warning(self) -> None:
        """Test that empty first_corners produces a warning."""
        node1 = self.create_node("Node1", x=100, y=100)
        node2 = self.create_node("Node2", x=300, y=100)
        self.create_link(
            "Link1",
            node1,
            node2,
            first_corners=[],
            second_corners=[(300, 100)],
        )

        issues = self.validator.validate(self.network)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "empty_corner_array")
        self.assertIsNotNone(issues[0].details)
        assert issues[0].details is not None  # For type checker
        self.assertEqual(issues[0].details["corner_type"], "first_corners")

    def test_empty_second_corners_reports_warning(self) -> None:
        """Test that empty second_corners produces a warning."""
        node1 = self.create_node("Node1", x=100, y=100)
        node2 = self.create_node("Node2", x=300, y=100)
        self.create_link(
            "Link1",
            node1,
            node2,
            first_corners=[(100, 100)],
            second_corners=[],
        )

        issues = self.validator.validate(self.network)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "empty_corner_array")
        self.assertIsNotNone(issues[0].details)
        assert issues[0].details is not None  # For type checker
        self.assertEqual(issues[0].details["corner_type"], "second_corners")

    def test_both_corners_empty_reports_two_warnings(self) -> None:
        """Test that both empty corner arrays produce two warnings."""
        node1 = self.create_node("Node1", x=100, y=100)
        node2 = self.create_node("Node2", x=300, y=100)
        self.create_link(
            "Link1",
            node1,
            node2,
            first_corners=[],
            second_corners=[],
        )

        assert_issue_count(self, self.validator, self.network, 2)

    def test_vertical_line_node_within_range(self) -> None:
        """Test that VERTICAL_LINE node accepts points within Y range."""
        # Node at (100, 100) with size=5 means Y range is [50, 150]
        node1 = self.create_node(
            "Node1",
            x=100,
            y=100,
            symbol=NodePresentationSymbol.VERTICAL_LINE,
            size=5,
        )
        node2 = self.create_node("Node2", x=300, y=100)
        # first_corners starts at (100, 50) - within vertical range
        self.create_link(
            "Link1",
            node1,
            node2,
            first_corners=[(100, 50), (200, 50)],
            second_corners=[(300, 100)],
        )

        assert_no_validation_issues(self, self.validator, self.network)

    def test_vertical_line_node_outside_range(self) -> None:
        """Test that VERTICAL_LINE node rejects points outside Y range."""
        # Node at (100, 100) with size=5 means Y range is [50, 150]
        node1 = self.create_node(
            "Node1",
            x=100,
            y=100,
            symbol=NodePresentationSymbol.VERTICAL_LINE,
            size=5,
        )
        node2 = self.create_node("Node2", x=300, y=100)
        # first_corners starts at (100, 200) - outside vertical range
        self.create_link(
            "Link1",
            node1,
            node2,
            first_corners=[(100, 200), (200, 200)],
            second_corners=[(300, 100)],
        )

        issues = self.validator.validate(self.network)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "corner_coordinate_mismatch")

    def test_vertical_line_node_wrong_x(self) -> None:
        """Test that VERTICAL_LINE node rejects points with wrong X coordinate."""
        node1 = self.create_node(
            "Node1",
            x=100,
            y=100,
            symbol=NodePresentationSymbol.VERTICAL_LINE,
            size=5,
        )
        node2 = self.create_node("Node2", x=300, y=100)
        # first_corners starts at (110, 100) - X doesn't match
        self.create_link(
            "Link1",
            node1,
            node2,
            first_corners=[(110, 100), (200, 100)],
            second_corners=[(300, 100)],
        )

        issues = self.validator.validate(self.network)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "corner_coordinate_mismatch")

    def test_horizontal_line_node_within_range(self) -> None:
        """Test that HORIZONTAL_LINE node accepts points within X range."""
        # Node at (100, 100) with size=5 means X range is [50, 150]
        node1 = self.create_node(
            "Node1",
            x=100,
            y=100,
            symbol=NodePresentationSymbol.HORIZONTAL_LINE,
            size=5,
        )
        node2 = self.create_node("Node2", x=300, y=100)
        # first_corners starts at (50, 100) - within horizontal range
        self.create_link(
            "Link1",
            node1,
            node2,
            first_corners=[(50, 100), (200, 100)],
            second_corners=[(300, 100)],
        )

        assert_no_validation_issues(self, self.validator, self.network)

    def test_horizontal_line_node_outside_range(self) -> None:
        """Test that HORIZONTAL_LINE node rejects points outside X range."""
        # Node at (100, 100) with size=5 means X range is [50, 150]
        node1 = self.create_node(
            "Node1",
            x=100,
            y=100,
            symbol=NodePresentationSymbol.HORIZONTAL_LINE,
            size=5,
        )
        node2 = self.create_node("Node2", x=300, y=100)
        # first_corners starts at (200, 100) - outside horizontal range
        self.create_link(
            "Link1",
            node1,
            node2,
            first_corners=[(200, 100), (250, 100)],
            second_corners=[(300, 100)],
        )

        issues = self.validator.validate(self.network)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "corner_coordinate_mismatch")

    def test_horizontal_line_node_wrong_y(self) -> None:
        """Test that HORIZONTAL_LINE node rejects points with wrong Y coordinate."""
        node1 = self.create_node(
            "Node1",
            x=100,
            y=100,
            symbol=NodePresentationSymbol.HORIZONTAL_LINE,
            size=5,
        )
        node2 = self.create_node("Node2", x=300, y=100)
        # first_corners starts at (100, 110) - Y doesn't match
        self.create_link(
            "Link1",
            node1,
            node2,
            first_corners=[(100, 110), (200, 110)],
            second_corners=[(300, 100)],
        )

        issues = self.validator.validate(self.network)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "corner_coordinate_mismatch")

    def test_grid_tolerance_same_cell_passes(self) -> None:
        """Test that small offset within same grid cell passes validation.

        Corner (108, 195) and node (100, 200) both round to (100, 200) on 20-pixel grid.
        """
        node1 = self.create_node("Node1", x=100, y=200)
        node2 = self.create_node("Node2", x=300, y=200)
        self.create_link(
            "Link1",
            node1,
            node2,
            first_corners=[(108, 195)],  # Rounds to (100, 200)
            second_corners=[(300, 200)],
        )

        assert_no_validation_issues(self, self.validator, self.network)

    def test_grid_tolerance_boundary_crossing_fails(self) -> None:
        """Test that small offset crossing grid boundary fails validation.

        Corner (111, 400) rounds to (120, 400), node (109, 400) rounds to (100, 400).
        Only 2 pixels apart raw, but 20 pixels apart on grid.
        """
        node1 = self.create_node("Node1", x=109, y=400)
        node2 = self.create_node("Node2", x=300, y=400)
        self.create_link(
            "Link1",
            node1,
            node2,
            first_corners=[(111, 400)],  # Rounds to (120, 400) - mismatch!
            second_corners=[(300, 400)],
        )

        issues = self.validator.validate(self.network)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "corner_coordinate_mismatch")

    def test_grid_tolerance_y_boundary_crossing_fails(self) -> None:
        """Test grid boundary crossing on Y coordinate.

        Corner (100, 490) rounds to (100, 480), node (100, 509) rounds to (100, 500).
        19 pixels apart raw, 20 pixels apart on grid.
        """
        node1 = self.create_node("Node1", x=100, y=509)
        node2 = self.create_node("Node2", x=300, y=500)
        self.create_link(
            "Link1",
            node1,
            node2,
            first_corners=[(100, 490)],  # Rounds to (100, 480) - mismatch!
            second_corners=[(300, 500)],
        )

        issues = self.validator.validate(self.network)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "corner_coordinate_mismatch")

    def test_vertical_line_grid_tolerance_x_within_cell(self) -> None:
        """Test VERTICAL_LINE with X offset within same grid cell passes."""
        node1 = self.create_node(
            "Node1",
            x=100,
            y=100,
            symbol=NodePresentationSymbol.VERTICAL_LINE,
            size=5,
        )
        node2 = self.create_node("Node2", x=300, y=100)
        # X=108 rounds to 100 (same as node), Y=75 is within vertical range [50, 150]
        self.create_link(
            "Link1",
            node1,
            node2,
            first_corners=[(108, 75)],
            second_corners=[(300, 100)],
        )

        assert_no_validation_issues(self, self.validator, self.network)

    def test_vertical_line_grid_tolerance_x_boundary_crossing_fails(self) -> None:
        """Test VERTICAL_LINE with X crossing grid boundary fails."""
        node1 = self.create_node(
            "Node1",
            x=109,
            y=100,
            symbol=NodePresentationSymbol.VERTICAL_LINE,
            size=5,
        )
        node2 = self.create_node("Node2", x=300, y=100)
        # X=111 rounds to 120, node X=109 rounds to 100 - mismatch!
        self.create_link(
            "Link1",
            node1,
            node2,
            first_corners=[(111, 100)],
            second_corners=[(300, 100)],
        )

        issues = self.validator.validate(self.network)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "corner_coordinate_mismatch")


class TestBranchCornerCoordinatesMV(unittest.TestCase):
    """MV-specific tests for the branch corner coordinates validator."""

    def setUp(self) -> None:
        """Set up test network with a sheet."""
        self.network = NetworkMV()
        self.sheet = SheetMV(general=SheetMV.General(name="TestSheet"))
        self.sheet.register(self.network)
        self.sheet_guid = self.sheet.general.guid
        self.validator = BranchCornerCoordinatesValidator()

    def create_node(
        self,
        name: str,
        x: int,
        y: int,
        symbol: NodePresentationSymbol = NodePresentationSymbol.CLOSED_CIRCLE,
        size: int = 1,
    ) -> NodeMV:
        """Create a node with presentation at specified coordinates."""
        node = NodeMV(
            general=NodeMV.General(name=name),
            presentations=[
                NodePresentationMV(
                    sheet=self.sheet_guid,
                    x=x,
                    y=y,
                    symbol=symbol,
                    size=size,
                )
            ],
        )
        node.register(self.network)
        return node

    def create_link(
        self,
        name: str,
        node1: NodeMV,
        node2: NodeMV,
        first_corners: list[tuple[int, int]],
        second_corners: list[tuple[int, int]],
    ) -> LinkMV:
        """Create a link with specified corner coordinates."""
        link = LinkMV(
            general=LinkMV.General(
                name=name,
                node1=node1.general.guid,
                node2=node2.general.guid,
            ),
            presentations=[
                BranchPresentationMV(
                    sheet=self.sheet_guid,
                    first_corners=first_corners,
                    second_corners=second_corners,
                )
            ],
        )
        link.register(self.network)
        return link

    def test_valid_coordinates_no_issues(self) -> None:
        """Test that correct coordinates produce no issues (MV)."""
        node1 = self.create_node("Node1", x=100, y=100)
        node2 = self.create_node("Node2", x=300, y=100)
        self.create_link(
            "Link1",
            node1,
            node2,
            first_corners=[(100, 100), (200, 100)],
            second_corners=[(300, 100)],
        )

        assert_no_validation_issues(self, self.validator, self.network)

    def test_mismatched_coordinates_reports_issue(self) -> None:
        """Test that mismatched coordinates produce a warning (MV)."""
        node1 = self.create_node("Node1", x=100, y=100)
        node2 = self.create_node("Node2", x=300, y=100)
        self.create_link(
            "Link1",
            node1,
            node2,
            first_corners=[(150, 100)],  # Wrong: should be (100, 100)
            second_corners=[(300, 100)],
        )

        issues = self.validator.validate(self.network)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "corner_coordinate_mismatch")

    def test_empty_corners_reports_warning(self) -> None:
        """Test that empty corner arrays produce warnings (MV)."""
        node1 = self.create_node("Node1", x=100, y=100)
        node2 = self.create_node("Node2", x=300, y=100)
        self.create_link(
            "Link1",
            node1,
            node2,
            first_corners=[],
            second_corners=[],
        )

        assert_issue_count(self, self.validator, self.network, 2)

    def test_vertical_line_node_mv(self) -> None:
        """Test VERTICAL_LINE handling works for MV networks."""
        node1 = self.create_node(
            "Node1",
            x=100,
            y=100,
            symbol=NodePresentationSymbol.VERTICAL_LINE,
            size=10,
        )
        node2 = self.create_node("Node2", x=300, y=100)
        # first_corners at (100, 0) is within range [100-100, 100+100]
        self.create_link(
            "Link1",
            node1,
            node2,
            first_corners=[(100, 0)],
            second_corners=[(300, 100)],
        )

        assert_no_validation_issues(self, self.validator, self.network)


if __name__ == "__main__":
    unittest.main()
