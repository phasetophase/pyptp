"""Tests for routes on the map, in RD metres or in degrees, checked with great-circle geometry."""

from __future__ import annotations

import math
import unittest

from pyptp.helpers.lv._map import offset_on_map
from pyptp.helpers.lv._routes import to_the_millimetre

from ._scene import EARTH_RADIUS_M, metres_between

Point = tuple[float, float]

# A street in Utrecht that runs north-east, bends east, then south-east
_UTRECHT_STREET = [
    (5.12000, 52.09000),
    (5.12150, 52.09100),
    (5.12330, 52.09110),
    (5.12450, 52.09020),
]


def _bearing(start: Point, end: Point) -> float:
    """Initial bearing from ``start`` to ``end``, in radians clockwise from north."""
    start_lon, start_lat = map(math.radians, start)
    end_lon, end_lat = map(math.radians, end)
    east = math.sin(end_lon - start_lon) * math.cos(end_lat)
    north = math.cos(start_lat) * math.sin(end_lat) - math.sin(start_lat) * math.cos(
        end_lat
    ) * math.cos(end_lon - start_lon)
    return math.atan2(east, north)


def _metres_right_of(start: Point, end: Point, point: Point) -> float:
    """How far ``point`` lies right of the great circle from ``start`` to ``end``, negative when left."""
    angle_to_point = metres_between(start, point) / EARTH_RADIUS_M
    turn = _bearing(start, point) - _bearing(start, end)
    return math.asin(math.sin(angle_to_point) * math.sin(turn)) * EARTH_RADIUS_M


def _legs_at(route: list[Point], index: int) -> list[tuple[Point, Point]]:
    """The legs of ``route`` that end or start at its point ``index``."""
    legs = []
    if index > 0:
        legs.append((route[index - 1], route[index]))
    if index < len(route) - 1:
        legs.append((route[index], route[index + 1]))
    return legs


class TestOffsetInDegrees(unittest.TestCase):
    """A route in degrees moves the given metres, measured on the earth."""

    def test_every_corner_is_the_offset_from_the_legs_it_joins(self) -> None:
        for metres in (2.0, -2.0, 0.5):
            with self.subTest(metres=metres):
                moved = to_the_millimetre(offset_on_map(_UTRECHT_STREET, metres))

                self.assertEqual(len(moved), len(_UTRECHT_STREET))
                for index, point in enumerate(moved):
                    for start, end in _legs_at(_UTRECHT_STREET, index):
                        self.assertAlmostEqual(
                            _metres_right_of(start, end, point), metres, delta=0.01
                        )

    def test_same_trench_stays_within_a_millimetre(self) -> None:
        surveyed = [
            (5.123456789012, 52.091234567891),
            (5.124987654321, 52.092109876543),
        ]

        moved = to_the_millimetre(offset_on_map(surveyed, 0.0))

        for old, new in zip(surveyed, moved, strict=True):
            self.assertLess(metres_between(old, new), 0.001)


class TestOffsetInRD(unittest.TestCase):
    """A route in RD metres moves by plain metres."""

    def test_two_metres_right_walking_north(self) -> None:
        route = [(155_000.0, 463_000.0), (155_000.0, 463_120.0)]

        moved = to_the_millimetre(offset_on_map(route, 2.0))

        self.assertEqual(moved, [(155_002.0, 463_000.0), (155_002.0, 463_120.0)])


if __name__ == "__main__":
    unittest.main()
