"""Tests for network element enums."""

from __future__ import annotations

import unittest
from enum import IntEnum

from pyptp.elements.enums import NodePresentationSymbol, SpecialTransformerSort


class TestNodePresentationSymbol(unittest.TestCase):
    """Test NodePresentationSymbol enum values and behavior."""

    def test_all_symbol_values_are_unique(self) -> None:
        """Verify all NodePresentationSymbol values are unique integers."""
        values = [member.value for member in NodePresentationSymbol]
        self.assertEqual(
            len(values), len(set(values)), "Duplicate enum values detected"
        )

    def test_symbol_count(self) -> None:
        """Verify there are exactly 15 symbol types defined."""
        self.assertEqual(len(NodePresentationSymbol), 15)

    def test_line_symbols(self) -> None:
        """Test line symbol values (1-2 range)."""
        self.assertEqual(NodePresentationSymbol.VERTICAL_LINE.value, 1)
        self.assertEqual(NodePresentationSymbol.HORIZONTAL_LINE.value, 2)

    def test_circle_symbols(self) -> None:
        """Test circle symbol values (11-13 range)."""
        self.assertEqual(NodePresentationSymbol.CLOSED_CIRCLE.value, 11)
        self.assertEqual(NodePresentationSymbol.OPEN_CIRCLE.value, 12)
        self.assertEqual(NodePresentationSymbol.HALF_OPEN_CIRCLE.value, 13)

    def test_square_symbols(self) -> None:
        """Test square symbol values (21-23 range)."""
        self.assertEqual(NodePresentationSymbol.CLOSED_SQUARE.value, 21)
        self.assertEqual(NodePresentationSymbol.OPEN_SQUARE.value, 22)
        self.assertEqual(NodePresentationSymbol.HALF_OPEN_SQUARE.value, 23)

    def test_triangle_symbols(self) -> None:
        """Test triangle symbol values (31-32 range)."""
        self.assertEqual(NodePresentationSymbol.CLOSED_TRIANGLE.value, 31)
        self.assertEqual(NodePresentationSymbol.OPEN_TRIANGLE.value, 32)

    def test_diamond_symbols(self) -> None:
        """Test diamond symbol values (41-42 range)."""
        self.assertEqual(NodePresentationSymbol.CLOSED_DIAMOND.value, 41)
        self.assertEqual(NodePresentationSymbol.OPEN_DIAMOND.value, 42)

    def test_rectangle_symbols(self) -> None:
        """Test rectangle symbol values (51-53 range)."""
        self.assertEqual(NodePresentationSymbol.CLOSED_RECTANGLE.value, 51)
        self.assertEqual(NodePresentationSymbol.OPEN_RECTANGLE.value, 52)
        self.assertEqual(NodePresentationSymbol.HALF_OPEN_RECTANGLE.value, 53)

    def test_default_symbol_is_closed_circle(self) -> None:
        """Verify CLOSED_CIRCLE has value 11 for use as default."""
        self.assertEqual(NodePresentationSymbol.CLOSED_CIRCLE.value, 11)

    def test_enum_construction_from_int(self) -> None:
        """Test creating enum members from integer values."""
        self.assertEqual(
            NodePresentationSymbol(11), NodePresentationSymbol.CLOSED_CIRCLE
        )
        self.assertEqual(NodePresentationSymbol(22), NodePresentationSymbol.OPEN_SQUARE)
        self.assertEqual(
            NodePresentationSymbol(53), NodePresentationSymbol.HALF_OPEN_RECTANGLE
        )

    def test_enum_construction_with_invalid_value_raises(self) -> None:
        """Test that invalid integer values raise ValueError."""
        with self.assertRaises(ValueError):
            NodePresentationSymbol(999)
        with self.assertRaises(ValueError):
            NodePresentationSymbol(0)
        with self.assertRaises(ValueError):
            NodePresentationSymbol(15)  # Valid range but not defined

    def test_enum_is_intenum_subclass(self) -> None:
        """Verify NodePresentationSymbol is an IntEnum for file format compatibility."""
        self.assertTrue(issubclass(NodePresentationSymbol, IntEnum))


class TestSpecialTransformerSort(unittest.TestCase):
    """Test SpecialTransformerSort enum for regression coverage."""

    def test_special_transformer_has_expected_values(self) -> None:
        """Verify SpecialTransformerSort hasn't changed."""
        self.assertEqual(SpecialTransformerSort.NONE.value, 0)
        self.assertEqual(SpecialTransformerSort.AUTO_YNA0_ASYM.value, 4)
        self.assertEqual(SpecialTransformerSort.BOOSTER.value, 11)
        self.assertEqual(SpecialTransformerSort.RELO.value, 31)


if __name__ == "__main__":
    unittest.main()
