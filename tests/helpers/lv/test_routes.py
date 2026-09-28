"""Tests for finding the nearest point on a route and cutting it, on a map or a sheet alike."""

from __future__ import annotations

import unittest

from pyptp.helpers.lv._routes import cut_route, nearest_fraction


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


if __name__ == "__main__":
    unittest.main()
