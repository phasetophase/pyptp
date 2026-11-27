"""Tests for route geometry, on a map or a sheet alike."""

from __future__ import annotations

import math
import unittest

from pyptp.elements.element_utils import Guid
from pyptp.elements.lv.presentations import BranchPresentation
from pyptp.helpers.lv._routes import (
    CableRoutes,
    cut_route,
    join_routes,
    nearest_fraction,
    offset_route,
)


class TestRouteGeometry(unittest.TestCase):
    """Finding the nearest point on a route and cutting it, on a map or a sheet alike."""

    def test_nearest_point_on_a_segment(self) -> None:
        """A point beside a straight route lands opposite it."""
        self.assertAlmostEqual(
            nearest_fraction([(0.0, 0.0), (100.0, 0.0)], (50.0, 10.0)), 0.5
        )

    def test_nearest_point_past_the_ends(self) -> None:
        """A point beyond either end of the route lands on that end."""
        route = [(0.0, 0.0), (100.0, 0.0)]
        self.assertEqual(nearest_fraction(route, (-20.0, 0.0)), 0.0)
        self.assertEqual(nearest_fraction(route, (120.0, 0.0)), 1.0)

    def test_nearest_point_after_a_corner(self) -> None:
        """The nearest point can lie on the segment after a corner."""
        self.assertAlmostEqual(
            nearest_fraction([(0.0, 0.0), (50.0, 0.0), (50.0, 50.0)], (55.0, 25.0)),
            0.75,
        )

    def test_cut_exactly_on_a_corner(self) -> None:
        """A cut on a corner does not repeat the corner point."""
        section_routes = cut_route([(0.0, 0.0), (50.0, 0.0), (50.0, 50.0)], [0.5])
        self.assertEqual(
            section_routes, [[(0.0, 0.0), (50.0, 0.0)], [(50.0, 0.0), (50.0, 50.0)]]
        )

    def test_two_cuts_in_one_segment(self) -> None:
        """Two cuts within one segment give three section routes that meet."""
        section_routes = cut_route([(0.0, 0.0), (100.0, 0.0)], [0.2, 0.4])
        self.assertEqual(
            section_routes,
            [
                [(0.0, 0.0), (20.0, 0.0)],
                [(20.0, 0.0), (40.0, 0.0)],
                [(40.0, 0.0), (100.0, 0.0)],
            ],
        )


def _to_pixels(route: list[tuple[float, float]]) -> list[tuple[int, int]]:
    return [(round(x), round(y)) for x, y in route]


class TestOffsetRoute(unittest.TestCase):
    """Moving a route sideways, as a parallel cable follows the old one."""

    def test_straight_route_moves_to_the_right(self) -> None:
        self.assertEqual(
            offset_route([(0.0, 0.0), (100.0, 0.0)], 20), [(0.0, 20.0), (100.0, 20.0)]
        )

    def test_right_angle_bend_is_mitred_on_both_sides(self) -> None:
        route = [(0.0, 0.0), (50.0, 0.0), (50.0, 50.0), (100.0, 50.0)]

        self.assertEqual(
            _to_pixels(offset_route(route, 20)),
            [(0, 20), (30, 20), (30, 70), (100, 70)],
        )
        self.assertEqual(
            _to_pixels(offset_route(route, -20)),
            [(0, -20), (70, -20), (70, 30), (100, 30)],
        )

    def test_sharp_bend_keeps_its_corner_close(self) -> None:
        moved = offset_route([(0.0, 0.0), (100.0, 0.0), (0.0, 10.0)], 20)

        corner = moved[1]
        self.assertLessEqual(math.dist(corner, (100.0, 0.0)), 40.0 + 1e-9)
        self.assertLess(corner[0], 100.0)

    def test_repeated_points_are_dropped(self) -> None:
        moved = offset_route([(0.0, 0.0), (0.0, 0.0), (100.0, 0.0), (100.0, 0.0)], 20)

        self.assertEqual(moved, [(0.0, 20.0), (100.0, 20.0)])

    def test_points_where_the_route_goes_straight_on_are_dropped(self) -> None:
        moved = offset_route([(0.0, 0.0), (50.0, 0.0), (100.0, 0.0)], 20)

        self.assertEqual(moved, [(0.0, 20.0), (100.0, 20.0)])

    def test_route_that_turns_back_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "turns back"):
            offset_route([(0.0, 0.0), (100.0, 0.0), (40.0, 0.0)], 20)

    def test_route_that_turns_back_stays_as_it_is_without_offset(self) -> None:
        route = [(0.0, 0.0), (100.0, 0.0), (40.0, 0.0)]

        self.assertEqual(offset_route(route, 0), route)

    def test_route_of_one_distinct_point_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "two distinct points"):
            offset_route([(10.0, 10.0), (10.0, 10.0)], 20)


class TestJoinAndReverse(unittest.TestCase):
    """Joining section routes into one, and turning a section's routes round."""

    def test_join_keeps_the_shared_point_once(self) -> None:
        joined = join_routes([[(0.0, 0.0), (50.0, 0.0)], [(50.0, 0.0), (50.0, 30.0)]])

        self.assertEqual(joined, [(0.0, 0.0), (50.0, 0.0), (50.0, 30.0)])

    def test_join_keeps_both_points_when_routes_do_not_meet(self) -> None:
        joined = join_routes([[(0.0, 0.0), (50.0, 0.0)], [(50.0, 10.0), (100.0, 10.0)]])

        self.assertEqual(joined, [(0.0, 0.0), (50.0, 0.0), (50.0, 10.0), (100.0, 10.0)])

    def test_reversed_turns_every_route_round(self) -> None:
        presentation = BranchPresentation(sheet=Guid.random())
        routes = CableRoutes(
            cablepart=[(0.0, 0.0), (5.0, 1.0), (10.0, 0.0)],
            geography=[(0.0, 0.0), (10.0, 2.0)],
            straight_line=[(0.0, 0.0), (10.0, 0.0)],
            drawings=[(presentation, [(0, 500), (200, 500), (200, 800)])],
        )

        self.assertEqual(
            routes.reversed(),
            CableRoutes(
                cablepart=[(10.0, 0.0), (5.0, 1.0), (0.0, 0.0)],
                geography=[(10.0, 2.0), (0.0, 0.0)],
                straight_line=[(10.0, 0.0), (0.0, 0.0)],
                drawings=[(presentation, [(200, 800), (200, 500), (0, 500)])],
            ),
        )


if __name__ == "__main__":
    unittest.main()
