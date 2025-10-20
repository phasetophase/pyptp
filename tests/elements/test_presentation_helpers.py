"""Tests for presentation helper functions."""

from __future__ import annotations

import unittest
from dataclasses import dataclass
from uuid import UUID

from pyptp.elements.element_utils import Guid
from pyptp.elements.presentation_helpers import (
    calculate_auto_scale,
    compute_presentation_bounds,
    transform_corners,
    transform_point,
)


@dataclass
class MockPresentation:
    """Mock presentation object for testing."""

    sheet: Guid
    x: float
    y: float


class TestComputePresentationBounds(unittest.TestCase):
    """Test compute_presentation_bounds function."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.sheet1 = Guid(UUID("11111111-1111-1111-1111-111111111111"))
        self.sheet2 = Guid(UUID("22222222-2222-2222-2222-222222222222"))

    def test_single_presentation_returns_point_bounds(self) -> None:
        """Test bounds calculation with single presentation."""
        pres = MockPresentation(sheet=self.sheet1, x=100.0, y=200.0)
        min_x, min_y, max_x, max_y = compute_presentation_bounds([pres], self.sheet1)

        self.assertEqual(min_x, 100.0)
        self.assertEqual(min_y, 200.0)
        self.assertEqual(max_x, 100.0)
        self.assertEqual(max_y, 200.0)

    def test_multiple_presentations_returns_bounding_box(self) -> None:
        """Test bounds calculation with multiple presentations."""
        presentations = [
            MockPresentation(sheet=self.sheet1, x=100.0, y=200.0),
            MockPresentation(sheet=self.sheet1, x=300.0, y=50.0),
            MockPresentation(sheet=self.sheet1, x=150.0, y=400.0),
        ]
        min_x, min_y, max_x, max_y = compute_presentation_bounds(
            presentations, self.sheet1
        )

        self.assertEqual(min_x, 100.0)
        self.assertEqual(min_y, 50.0)
        self.assertEqual(max_x, 300.0)
        self.assertEqual(max_y, 400.0)

    def test_filters_by_sheet_guid(self) -> None:
        """Test that only presentations on target sheet are included."""
        presentations = [
            MockPresentation(sheet=self.sheet1, x=100.0, y=200.0),
            MockPresentation(sheet=self.sheet2, x=999.0, y=999.0),  # Different sheet
            MockPresentation(sheet=self.sheet1, x=300.0, y=50.0),
        ]
        min_x, min_y, max_x, max_y = compute_presentation_bounds(
            presentations, self.sheet1
        )

        self.assertEqual(min_x, 100.0)
        self.assertEqual(min_y, 50.0)
        self.assertEqual(max_x, 300.0)
        self.assertEqual(max_y, 200.0)

    def test_empty_list_returns_infinity_bounds(self) -> None:
        """Test bounds calculation with empty presentation list."""
        min_x, min_y, max_x, max_y = compute_presentation_bounds([], self.sheet1)

        self.assertEqual(min_x, float("inf"))
        self.assertEqual(min_y, float("inf"))
        self.assertEqual(max_x, float("-inf"))
        self.assertEqual(max_y, float("-inf"))

    def test_no_matching_sheets_returns_infinity_bounds(self) -> None:
        """Test bounds when no presentations match target sheet."""
        presentations = [
            MockPresentation(sheet=self.sheet2, x=100.0, y=200.0),
            MockPresentation(sheet=self.sheet2, x=300.0, y=50.0),
        ]
        min_x, min_y, max_x, max_y = compute_presentation_bounds(
            presentations, self.sheet1
        )

        self.assertEqual(min_x, float("inf"))
        self.assertEqual(min_y, float("inf"))
        self.assertEqual(max_x, float("-inf"))
        self.assertEqual(max_y, float("-inf"))


class TestCalculateAutoScale(unittest.TestCase):
    """Test calculate_auto_scale function."""

    def test_zero_delta_returns_minimum_scale(self) -> None:
        """Test scale calculation when all points are identical."""
        scale = calculate_auto_scale(100.0, 200.0, 100.0, 200.0)
        self.assertEqual(scale, 120.0)

    def test_small_delta_returns_large_scale(self) -> None:
        """Test scale increases for smaller content bounds."""
        scale = calculate_auto_scale(0.0, 0.0, 10.0, 10.0)
        self.assertAlmostEqual(scale, 200.0, delta=1.0)  # (800.0/10.0) + 120.0 = 200.0

    def test_large_delta_returns_small_scale(self) -> None:
        """Test scale decreases for larger content bounds."""
        scale = calculate_auto_scale(0.0, 0.0, 800.0, 800.0)
        self.assertAlmostEqual(scale, 121.0, delta=1.0)  # (800.0/800.0) + 120.0 = 121.0

    def test_asymmetric_bounds_uses_max_delta(self) -> None:
        """Test that scale is based on maximum dimension."""
        scale_wide = calculate_auto_scale(0.0, 0.0, 400.0, 100.0)
        scale_tall = calculate_auto_scale(0.0, 0.0, 100.0, 400.0)
        self.assertAlmostEqual(scale_wide, scale_tall)

    def test_negative_coordinates_handled_correctly(self) -> None:
        """Test scale calculation with negative coordinates."""
        scale = calculate_auto_scale(-100.0, -200.0, 100.0, 200.0)
        # delta_x = 200, delta_y = 400, max = 400
        self.assertAlmostEqual(scale, 122.0, delta=1.0)  # (800.0/400.0) + 120.0 = 122.0


class TestTransformPoint(unittest.TestCase):
    """Test transform_point function."""

    def test_basic_transform_without_grid_snapping(self) -> None:
        """Test basic coordinate transformation without grid."""
        x, y = transform_point(10.0, 20.0, min_x=0.0, min_y=0.0, scale=2.0, grid_size=0)
        self.assertEqual(x, 20)
        self.assertEqual(y, -40)  # Y-axis inverted

    def test_transform_with_offset(self) -> None:
        """Test transformation with offset normalization."""
        x, y = transform_point(
            110.0, 220.0, min_x=100.0, min_y=200.0, scale=2.0, grid_size=0
        )
        self.assertEqual(x, 20)
        self.assertEqual(y, -40)  # (220-200)*2 = 40, inverted = -40

    def test_transform_with_grid_snapping(self) -> None:
        """Test transformation with grid alignment."""
        x, y = transform_point(
            10.5, 20.3, min_x=0.0, min_y=0.0, scale=2.0, grid_size=20
        )
        # 10.5*2 = 21, round(21/20)*20 = 20
        # 20.3*2 = 40.6, round(40.6/20)*20 = 40
        self.assertEqual(x, 20)
        self.assertEqual(y, -40)

    def test_transform_without_y_inversion(self) -> None:
        """Test transformation with Y-axis inversion disabled."""
        x, y = transform_point(
            10.0, 20.0, min_x=0.0, min_y=0.0, scale=2.0, grid_size=0, invert_y=False
        )
        self.assertEqual(x, 20)
        self.assertEqual(y, 40)  # Not inverted

    def test_transform_returns_integers(self) -> None:
        """Test that transform returns integer coordinates."""
        x, y = transform_point(10.7, 20.3, min_x=0.0, min_y=0.0, scale=1.0, grid_size=0)
        self.assertIsInstance(x, int)
        self.assertIsInstance(y, int)

    def test_transform_with_negative_coordinates(self) -> None:
        """Test transformation with negative input coordinates."""
        x, y = transform_point(
            -10.0, -20.0, min_x=-50.0, min_y=-50.0, scale=2.0, grid_size=0
        )
        # (-10 - (-50)) * 2 = 40 * 2 = 80
        # (-20 - (-50)) * 2 = 30 * 2 = 60
        self.assertEqual(x, 80)
        self.assertEqual(y, -60)


class TestTransformCorners(unittest.TestCase):
    """Test transform_corners function."""

    def test_empty_corners_list_returns_empty(self) -> None:
        """Test transformation of empty corner list."""
        corners = transform_corners([], min_x=0.0, min_y=0.0, scale=1.0, grid_size=0)
        self.assertEqual(corners, [])

    def test_single_corner_transforms_correctly(self) -> None:
        """Test transformation of single corner point."""
        corners = transform_corners(
            [(10.0, 20.0)], min_x=0.0, min_y=0.0, scale=2.0, grid_size=0
        )
        self.assertEqual(corners, [(20, -40)])

    def test_multiple_corners_all_transformed(self) -> None:
        """Test transformation of multiple corner points."""
        input_corners = [(10.0, 20.0), (30.0, 40.0), (50.0, 60.0)]
        corners = transform_corners(
            input_corners, min_x=0.0, min_y=0.0, scale=2.0, grid_size=0
        )
        expected = [(20, -40), (60, -80), (100, -120)]
        self.assertEqual(corners, expected)

    def test_corners_with_grid_snapping(self) -> None:
        """Test transformation with grid alignment for corners."""
        input_corners = [(10.5, 20.3), (31.7, 42.1)]
        corners = transform_corners(
            input_corners, min_x=0.0, min_y=0.0, scale=2.0, grid_size=20
        )
        # Same logic as test_transform_with_grid_snapping but for multiple points
        self.assertEqual(len(corners), 2)
        self.assertIsInstance(corners[0][0], int)
        self.assertIsInstance(corners[0][1], int)

    def test_corners_preserve_order(self) -> None:
        """Test that corner transformation preserves input order."""
        input_corners = [(50.0, 60.0), (10.0, 20.0), (30.0, 40.0)]
        corners = transform_corners(
            input_corners, min_x=0.0, min_y=0.0, scale=2.0, grid_size=0
        )
        expected = [(100, -120), (20, -40), (60, -80)]
        self.assertEqual(corners, expected)


if __name__ == "__main__":
    unittest.main()
