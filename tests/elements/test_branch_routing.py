from __future__ import annotations

import unittest

from pyptp.elements.enums import SymbolSegment, NodePresentationSymbol
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import BranchPresentation as BranchPresentationLV
from pyptp.elements.lv.presentations import NodePresentation as NodePresentationLV
from pyptp.elements.lv.sheet import SheetLV
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import BranchPresentation as BranchPresentationMV
from pyptp.elements.mv.presentations import NodePresentation as NodePresentationMV
from pyptp.elements.mv.sheet import SheetMV
from pyptp.elements.presentation_helpers import branch_polyline, route_corners


class TestRouteCorners(unittest.TestCase):
    """Splitting a route into the two corner lists."""

    def _presentation(
        self, x: int, y: int, symbol: NodePresentationSymbol, size: int = 1
    ) -> NodePresentationLV:
        return NodePresentationLV(x=x, y=y, symbol=symbol, size=size)

    def _point(self, x: int, y: int) -> NodePresentationLV:
        return self._presentation(x, y, NodePresentationSymbol.CLOSED_CIRCLE)

    def test_straight_run_between_point_symbols(self) -> None:
        first, second = route_corners(self._point(100, 100), self._point(300, 100))

        self.assertEqual(first, [(100, 100)])
        self.assertEqual(second, [(300, 100)])

    def test_default_symbol_segment_is_the_middle_segment(self) -> None:
        first, second = route_corners(
            self._point(100, 100),
            self._point(300, 300),
            via=[(100, 200), (200, 200)],
        )

        self.assertEqual(first, [(100, 100), (100, 200)])
        self.assertEqual(second, [(300, 300), (200, 200)])

    def test_longest_symbol_segment_picks_the_longest_segment(self) -> None:
        first, second = route_corners(
            self._point(100, 100),
            self._point(300, 300),
            via=[(100, 200), (200, 200)],
            symbol_segment=SymbolSegment.LONGEST,
        )

        self.assertEqual(first, [(100, 100), (100, 200), (200, 200)])
        self.assertEqual(second, [(300, 300)])

    def test_segment_index_zero_puts_every_via_point_in_second_corners(self) -> None:
        first, second = route_corners(
            self._point(100, 100),
            self._point(300, 300),
            via=[(100, 200), (200, 200)],
            symbol_segment=0,
        )

        self.assertEqual(first, [(100, 100)])
        self.assertEqual(second, [(300, 300), (200, 200), (100, 200)])

    def test_negative_segment_index_counts_from_node2(self) -> None:
        via = [(100, 200), (200, 200)]
        from_node2 = route_corners(
            self._point(100, 100), self._point(300, 300), via=via, symbol_segment=-1
        )
        from_node1 = route_corners(
            self._point(100, 100), self._point(300, 300), via=via, symbol_segment=2
        )

        self.assertEqual(from_node2, from_node1)

    def test_segment_index_past_the_last_segment_raises(self) -> None:
        with self.assertRaises(ValueError):
            route_corners(
                self._point(100, 100),
                self._point(300, 300),
                via=[(100, 200), (200, 200)],
                symbol_segment=3,
            )

    def test_segment_index_before_the_first_segment_raises(self) -> None:
        with self.assertRaises(ValueError):
            route_corners(
                self._point(100, 100),
                self._point(300, 300),
                via=[(100, 200), (200, 200)],
                symbol_segment=-4,
            )

    def test_symbol_segment_of_another_type_raises(self) -> None:
        for symbol_segment in (True, 1.0, None, "longest"):
            with self.subTest(symbol_segment=symbol_segment):
                with self.assertRaises(TypeError):
                    route_corners(
                        self._point(100, 100),
                        self._point(300, 300),
                        symbol_segment=symbol_segment,  # type: ignore[arg-type]
                    )

    def test_halfway_point_exactly_on_a_corner(self) -> None:
        # Both segments are 200 long, so the first one already reaches halfway.
        first, second = route_corners(
            self._point(0, 0), self._point(200, 200), via=[(0, 200)]
        )

        self.assertEqual(first, [(0, 0)])
        self.assertEqual(second, [(200, 200), (0, 200)])

    def test_ends_are_clamped_onto_a_horizontal_line_symbol(self) -> None:
        # A horizontal line symbol of size 3 reaches 30 px either way.
        first, second = route_corners(
            self._presentation(
                100, 100, NodePresentationSymbol.HORIZONTAL_LINE, size=3
            ),
            self._point(300, 100),
            via=[(120, 200)],
        )

        self.assertEqual(first, [(120, 100), (120, 200)])
        self.assertEqual(second, [(300, 100)])

    def test_clamping_stops_at_the_end_of_the_line(self) -> None:
        first, _ = route_corners(
            self._presentation(
                100, 100, NodePresentationSymbol.HORIZONTAL_LINE, size=1
            ),
            self._point(300, 100),
        )

        self.assertEqual(first, [(110, 100)])

    def test_via_point_equal_to_the_clamped_start_is_dropped(self) -> None:
        first, second = route_corners(
            self._presentation(100, 100, NodePresentationSymbol.VERTICAL_LINE, size=4),
            self._point(300, 300),
            via=[(100, 120)],
        )

        self.assertEqual(first, [(100, 120)])
        self.assertEqual(second, [(300, 300)])

    def test_via_point_equal_to_the_clamped_end_is_dropped(self) -> None:
        first, second = route_corners(
            self._point(100, 100),
            self._presentation(300, 300, NodePresentationSymbol.VERTICAL_LINE, size=4),
            via=[(300, 280)],
        )

        self.assertEqual(first, [(100, 100)])
        self.assertEqual(second, [(300, 280)])


class TestBranchPolyline(unittest.TestCase):
    """The drawn route as one list."""

    def test_second_corners_are_reversed(self) -> None:
        polyline = branch_polyline([(0, 0), (0, 10)], [(50, 0), (50, 10)])

        self.assertEqual(polyline, [(0, 0), (0, 10), (50, 10), (50, 0)])


class TestBranchPresentationBetweenLV(unittest.TestCase):
    """Building an LV branch presentation from its two nodes."""

    def setUp(self) -> None:
        self.sheet = SheetLV(general=SheetLV.General(name="Wijk"))
        self.sheet_guid = self.sheet.general.guid
        self.node1 = NodeLV(
            general=NodeLV.General(name="K1"),
            presentations=[NodePresentationLV(sheet=self.sheet_guid, x=100, y=100)],
        )
        self.node2 = NodeLV(
            general=NodeLV.General(name="K2"),
            presentations=[NodePresentationLV(sheet=self.sheet_guid, x=300, y=100)],
        )

    def test_between_reads_both_node_positions(self) -> None:
        presentation = BranchPresentationLV.between(
            self.node1, self.node2, self.sheet_guid
        )

        self.assertEqual(presentation.sheet, self.sheet_guid)
        self.assertEqual(presentation.first_corners, [(100, 100)])
        self.assertEqual(presentation.second_corners, [(300, 100)])

    def test_polyline_runs_from_node1_to_node2_for_every_symbol_segment(self) -> None:
        expected = [(100, 100), (100, 200), (300, 200), (300, 100)]
        for symbol_segment in (
            SymbolSegment.MIDDLE,
            SymbolSegment.LONGEST,
            0,
            1,
            2,
            -1,
        ):
            with self.subTest(symbol_segment=symbol_segment):
                presentation = BranchPresentationLV.between(
                    self.node1,
                    self.node2,
                    self.sheet_guid,
                    via=[(100, 200), (300, 200)],
                    symbol_segment=symbol_segment,
                )

                self.assertEqual(presentation.polyline(), expected)

    def test_symbol_segment_moves_the_split_without_moving_the_route(self) -> None:
        presentation = BranchPresentationLV.between(
            self.node1,
            self.node2,
            self.sheet_guid,
            via=[(100, 200), (300, 200)],
            symbol_segment=0,
        )

        self.assertEqual(presentation.first_corners, [(100, 100)])
        self.assertEqual(
            presentation.second_corners, [(300, 100), (300, 200), (100, 200)]
        )

    def test_node_not_on_sheet_raises(self) -> None:
        other = NodeLV(general=NodeLV.General(name="K3"), presentations=[])

        with self.assertRaises(ValueError) as ctx:
            BranchPresentationLV.between(self.node1, other, self.sheet_guid)
        self.assertIn("K3", str(ctx.exception))

    def test_segment_index_outside_the_route_raises(self) -> None:
        with self.assertRaises(ValueError):
            BranchPresentationLV.between(
                self.node1, self.node2, self.sheet_guid, symbol_segment=2
            )


class TestBranchPresentationBetweenMV(unittest.TestCase):
    """Building an MV branch presentation from its two nodes."""

    def setUp(self) -> None:
        self.sheet = SheetMV(general=SheetMV.General(name="Blad"))
        self.sheet_guid = self.sheet.general.guid
        self.node1 = NodeMV(
            general=NodeMV.General(name="K1"),
            presentations=[NodePresentationMV(sheet=self.sheet_guid, x=0, y=0)],
        )
        self.node2 = NodeMV(
            general=NodeMV.General(name="K2"),
            presentations=[NodePresentationMV(sheet=self.sheet_guid, x=200, y=200)],
        )

    def test_between_reads_both_node_positions(self) -> None:
        presentation = BranchPresentationMV.between(
            self.node1, self.node2, self.sheet_guid
        )

        self.assertEqual(presentation.sheet, self.sheet_guid)
        self.assertEqual(presentation.first_corners, [(0, 0)])
        self.assertEqual(presentation.second_corners, [(200, 200)])


if __name__ == "__main__":
    unittest.main()
