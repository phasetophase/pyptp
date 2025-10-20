"""Tests for LV Legend parsing and serialization."""

from __future__ import annotations

import unittest

from pyptp.IO.importers._gnf_handlers.legend_handler import LegendHandler
from pyptp.network_lv import NetworkLV


class TestLegendParsing(unittest.TestCase):
    """Test legend parsing with multiple text lines per cell."""

    def test_legend_with_multiple_text_lines_per_cell(self) -> None:
        """Test parsing a legend where cells have multiple text lines."""
        raw_section = """#General GUID:'{DDBFBE42-D69B-4819-B322-3FC1E53125F5}' CreationTime:0 MutationDate:45625 Rows:5 Columns:5
#Merge C1:E2
#Merge B4:D4
#Merge B5:D5
#Cell Row:1 Column:3 TextSize:20
#Text https://www.phasetophase.nl/help/PtP logo M.bmp
#Cell Row:1 Column:1 TextSize:20
#Text Netwerk:
#Cell Row:2 Column:1 TextSize:20
#Text Versie:
#Cell Row:5 Column:2 TextSize:20
#Text Phase to Phase B.V.
#Text Blabla
#Text BloeBla
#Presentation Sheet:'{ACBCA773-8D71-4131-9962-F2AAD50F3DC0}' X1:15320 Y1:15680 X2:16180 Y2:15860 Color:$00808040 Width:2 TextSize:20
#END"""

        network = NetworkLV()
        handler = LegendHandler()
        handler.handle(network, raw_section)

        # Verify legend was registered
        self.assertEqual(len(network.legends), 1)

        legend = list(network.legends.values())[0]

        # Verify general properties
        self.assertEqual(legend.general.rows, 5)
        self.assertEqual(legend.general.columns, 5)

        # Verify merges
        self.assertEqual(len(legend.merges), 3)
        self.assertIn("C1:E2", legend.merges)
        self.assertIn("B4:D4", legend.merges)
        self.assertIn("B5:D5", legend.merges)

        # Verify cells
        self.assertEqual(len(legend.cells), 4)

        # Find the cell with multiple text lines (Row:5 Column:2)
        cell_with_multiple_texts = None
        for cell in legend.cells:
            if cell.row == 5 and cell.column == 2:
                cell_with_multiple_texts = cell
                break

        self.assertIsNotNone(
            cell_with_multiple_texts, "Cell at Row:5 Column:2 should exist"
        )
        self.assertEqual(len(cell_with_multiple_texts.text_lines), 3)
        self.assertEqual(cell_with_multiple_texts.text_lines[0], "Phase to Phase B.V.")
        self.assertEqual(cell_with_multiple_texts.text_lines[1], "Blabla")
        self.assertEqual(cell_with_multiple_texts.text_lines[2], "BloeBla")

        # Verify other cells have single text lines
        cell_1_1 = next((c for c in legend.cells if c.row == 1 and c.column == 1), None)
        self.assertIsNotNone(cell_1_1)
        self.assertEqual(len(cell_1_1.text_lines), 1)
        self.assertEqual(cell_1_1.text_lines[0], "Netwerk:")

        # Verify presentations
        self.assertEqual(len(legend.presentations), 1)

    def test_legend_roundtrip_with_multiple_text_lines(self) -> None:
        """Test that legends with multiple text lines serialize correctly."""
        raw_section = """#General GUID:'{DDBFBE42-D69B-4819-B322-3FC1E53125F5}' CreationTime:0 MutationDate:45625 Rows:5 Columns:5
#Cell Row:5 Column:2 TextSize:20
#Text Phase to Phase B.V.
#Text Blabla
#Text BloeBla
#END"""

        network = NetworkLV()
        handler = LegendHandler()
        handler.handle(network, raw_section)

        legend = list(network.legends.values())[0]
        serialized = legend.serialize()

        # Verify all three text lines appear in serialized output
        self.assertIn("Phase to Phase B.V.", serialized)
        self.assertIn("Blabla", serialized)
        self.assertIn("BloeBla", serialized)

        # Verify they appear in the correct order
        lines = serialized.split("\n")
        text_lines = [line for line in lines if line.startswith("#Text ")]
        self.assertEqual(len(text_lines), 3)
        self.assertIn("Phase to Phase B.V.", text_lines[0])
        self.assertIn("Blabla", text_lines[1])
        self.assertIn("BloeBla", text_lines[2])

    def test_legend_without_variant_field(self) -> None:
        """Test that LV legends don't have Variant field (unlike MV)."""
        raw_section = """#General GUID:'{DDBFBE42-D69B-4819-B322-3FC1E53125F5}' CreationTime:0 Rows:1 Columns:1
#END"""

        network = NetworkLV()
        handler = LegendHandler()
        handler.handle(network, raw_section)

        legend = list(network.legends.values())[0]

        # Verify LV General doesn't have 'variant' attribute
        self.assertFalse(hasattr(legend.general, "variant"))

        # Verify serialized output doesn't contain Variant
        serialized = legend.serialize()
        self.assertNotIn("Variant", serialized)


if __name__ == "__main__":
    unittest.main()
