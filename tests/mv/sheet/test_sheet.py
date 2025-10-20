"""Tests for TSheetMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import CL_CREAM, DelphiColor
from pyptp.elements.element_utils import Guid
from pyptp.elements.mv.shared import Comment
from pyptp.elements.mv.sheet import SheetMV
from pyptp.network_mv import NetworkMV


class TestSheetRegistration(unittest.TestCase):
    """Test sheet registration and functionality."""

    def setUp(self) -> None:
        """Create a fresh network for testing."""
        self.network = NetworkMV()
        self.sheet_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_sheet_registration_works(self) -> None:
        """Test that sheets can register themselves with the network."""
        general = SheetMV.General(guid=self.sheet_guid, name="TestSheet")

        sheet = SheetMV(general)
        sheet.register(self.network)

        # Verify sheet is in network
        self.assertIn(self.sheet_guid, self.network.sheets)
        self.assertIs(self.network.sheets[self.sheet_guid], sheet)

    def test_sheet_with_full_properties_serializes_correctly(self) -> None:
        """Test that sheets with all properties serialize correctly."""
        general = SheetMV.General(
            guid=self.sheet_guid,
            name="FullSheet",
            color=DelphiColor("$FF0000"),
            coarse_grid_width=10,
            coarse_grid_height=20,
            map_sheet_width=100,
            map_sheet_height=200,
            map_sheet_grid_width=5,
            map_sheet_grid_height=10,
            map_sheet_grid_left=15,
            map_sheet_grid_top=25,
            map_sheet_numbering=1,
            map_sheet_number_offset=2,
        )

        comment = Comment(text="Test comment")
        sheet = SheetMV(general, comment)
        sheet.register(self.network)

        # Test serialization
        serialized = sheet.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertEqual(serialized.count("#Comment"), 1)

        # Verify general properties
        self.assertIn("Name:'FullSheet'", serialized)
        self.assertIn("Color:$FF0000", serialized)
        self.assertIn("CoarseGridWidth:10", serialized)
        self.assertIn("CoarseGridHeight:20", serialized)
        self.assertIn("MapSheetWidth:100", serialized)
        self.assertIn("MapSheetHeight:200", serialized)
        self.assertIn("MapSheetGridWidth:5", serialized)
        self.assertIn("MapSheetGridHeight:10", serialized)
        self.assertIn("MapSheetGridLeft:15", serialized)
        self.assertIn("MapSheetGridTop:25", serialized)
        self.assertIn("MapSheetNumbering:1", serialized)
        self.assertIn("MapSheetNumberOffset:2", serialized)
        self.assertIn(f"GUID:'{{{str(self.sheet_guid).upper()}}}'", serialized)

        # Verify comment
        self.assertIn("Text:Test comment", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a sheet with the same GUID overwrites the existing one."""
        general1 = SheetMV.General(guid=self.sheet_guid, name="FirstSheet")
        sheet1 = SheetMV(general1)
        sheet1.register(self.network)

        general2 = SheetMV.General(guid=self.sheet_guid, name="SecondSheet")
        sheet2 = SheetMV(general2)
        sheet2.register(self.network)

        # Should only have one sheet
        self.assertEqual(len(self.network.sheets), 1)
        # Should be the second sheet
        self.assertEqual(
            self.network.sheets[self.sheet_guid].general.name, "SecondSheet"
        )

    def test_minimal_sheet_serialization(self) -> None:
        """Test that minimal sheets serialize correctly with only required fields."""
        general = SheetMV.General(guid=self.sheet_guid, name="MinimalSheet")
        sheet = SheetMV(general)
        sheet.register(self.network)

        serialized = sheet.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertEqual(serialized.count("#Comment"), 0)

        # Should have basic properties
        self.assertIn("Name:'MinimalSheet'", serialized)
        self.assertIn(f"GUID:'{{{str(self.sheet_guid).upper()}}}'", serialized)

        # Default values should be skipped properly

    def test_sheet_with_comment_serializes_correctly(self) -> None:
        """Test that sheets with comment serialize correctly."""
        general = SheetMV.General(guid=self.sheet_guid, name="CommentSheet")
        comment = Comment(text="Test comment")
        sheet = SheetMV(general, comment)
        sheet.register(self.network)

        serialized = sheet.serialize()
        self.assertIn("#Comment", serialized)
        self.assertIn("Text:Test comment", serialized)

    def test_sheet_with_color_serializes_correctly(self) -> None:
        """Test that sheets with color serialize correctly."""
        general = SheetMV.General(
            guid=self.sheet_guid,
            name="ColorSheet",
            color=DelphiColor("$00FF00"),
        )
        sheet = SheetMV(general)
        sheet.register(self.network)

        serialized = sheet.serialize()
        self.assertIn("Color:$00FF00", serialized)

    def test_sheet_with_grid_properties_serializes_correctly(self) -> None:
        """Test that sheets with grid properties serialize correctly."""
        general = SheetMV.General(
            guid=self.sheet_guid,
            name="GridSheet",
            coarse_grid_width=15,
            coarse_grid_height=25,
        )
        sheet = SheetMV(general)
        sheet.register(self.network)

        serialized = sheet.serialize()
        self.assertIn("CoarseGridWidth:15", serialized)
        self.assertIn("CoarseGridHeight:25", serialized)

    def test_sheet_with_mapsheet_properties_serializes_correctly(self) -> None:
        """Test that sheets with map sheet properties serialize correctly."""
        general = SheetMV.General(
            guid=self.sheet_guid,
            name="MapSheet",
            map_sheet_width=300,
            map_sheet_height=400,
            map_sheet_grid_width=10,
            map_sheet_grid_height=15,
            map_sheet_grid_left=20,
            map_sheet_grid_top=30,
            map_sheet_numbering=2,
            map_sheet_number_offset=5,
        )
        sheet = SheetMV(general)
        sheet.register(self.network)

        serialized = sheet.serialize()
        self.assertIn("MapSheetWidth:300", serialized)
        self.assertIn("MapSheetHeight:400", serialized)
        self.assertIn("MapSheetGridWidth:10", serialized)
        self.assertIn("MapSheetGridHeight:15", serialized)
        self.assertIn("MapSheetGridLeft:20", serialized)
        self.assertIn("MapSheetGridTop:30", serialized)
        self.assertIn("MapSheetNumbering:2", serialized)
        self.assertIn("MapSheetNumberOffset:5", serialized)

    def test_sheet_with_empty_name_serializes_correctly(self) -> None:
        """Test that sheets with empty name serialize correctly."""
        general = SheetMV.General(guid=self.sheet_guid, name="")
        sheet = SheetMV(general)
        sheet.register(self.network)

        serialized = sheet.serialize()
        self.assertIn("Name:''", serialized)

    def test_sheet_deserialization_works(self) -> None:
        """Test that sheets can be deserialized correctly."""
        data = {
            "general": [
                {
                    "GUID": str(self.sheet_guid),
                    "Name": "TestSheet",
                    "Color": "$FF0000",
                    "CoarseGridWidth": 10,
                    "CoarseGridHeight": 20,
                    "MapSheetWidth": 100,
                    "MapSheetHeight": 200,
                    "MapSheetGridWidth": 5,
                    "MapSheetGridHeight": 10,
                    "MapSheetGridLeft": 15,
                    "MapSheetGridTop": 25,
                    "MapSheetNumbering": 1,
                    "MapSheetNumberOffset": 2,
                }
            ],
            "comment": [
                {
                    "Text": "Test comment",
                }
            ],
        }

        sheet = SheetMV.deserialize(data)

        self.assertEqual(sheet.general.guid, self.sheet_guid)
        self.assertEqual(sheet.general.name, "TestSheet")
        self.assertEqual(sheet.general.color, DelphiColor("$FF0000"))
        self.assertEqual(sheet.general.coarse_grid_width, 10)
        self.assertEqual(sheet.general.coarse_grid_height, 20)
        self.assertEqual(sheet.general.map_sheet_width, 100)
        self.assertEqual(sheet.general.map_sheet_height, 200)
        self.assertEqual(sheet.general.map_sheet_grid_width, 5)
        self.assertEqual(sheet.general.map_sheet_grid_height, 10)
        self.assertEqual(sheet.general.map_sheet_grid_left, 15)
        self.assertEqual(sheet.general.map_sheet_grid_top, 25)
        self.assertEqual(sheet.general.map_sheet_numbering, 1)
        self.assertEqual(sheet.general.map_sheet_number_offset, 2)
        self.assertIsNotNone(sheet.comment)
        if sheet.comment:
            self.assertEqual(sheet.comment.text, "Test comment")

    def test_sheet_deserialization_with_missing_data_works(self) -> None:
        """Test that sheet deserialization works with missing data."""
        data = {}

        sheet = SheetMV.deserialize(data)

        self.assertEqual(sheet.general.name, "")
        self.assertEqual(sheet.general.color, CL_CREAM)
        self.assertEqual(sheet.general.coarse_grid_width, 0)
        self.assertEqual(sheet.general.coarse_grid_height, 0)
        self.assertEqual(sheet.general.map_sheet_width, 0)
        self.assertEqual(sheet.general.map_sheet_height, 0)
        self.assertEqual(sheet.general.map_sheet_grid_width, 0)
        self.assertEqual(sheet.general.map_sheet_grid_height, 0)
        self.assertEqual(sheet.general.map_sheet_grid_left, 0)
        self.assertEqual(sheet.general.map_sheet_grid_top, 0)
        self.assertEqual(sheet.general.map_sheet_numbering, 0)
        self.assertEqual(sheet.general.map_sheet_number_offset, 0)
        self.assertIsNone(sheet.comment)

    def test_sheet_deserialization_with_no_comment_works(self) -> None:
        """Test that sheet deserialization works without comment."""
        data = {
            "general": [
                {
                    "GUID": str(self.sheet_guid),
                    "Name": "TestSheet",
                }
            ],
        }

        sheet = SheetMV.deserialize(data)

        self.assertEqual(sheet.general.guid, self.sheet_guid)
        self.assertEqual(sheet.general.name, "TestSheet")
        self.assertIsNone(sheet.comment)

    def test_sheet_general_serialization_works(self) -> None:
        """Test that sheet general serialization works correctly."""
        general = SheetMV.General(
            guid=self.sheet_guid,
            name="TestSheet",
            color=DelphiColor("$FF0000"),
            coarse_grid_width=10,
            coarse_grid_height=20,
            map_sheet_width=100,
            map_sheet_height=200,
            map_sheet_grid_width=5,
            map_sheet_grid_height=10,
            map_sheet_grid_left=15,
            map_sheet_grid_top=25,
            map_sheet_numbering=1,
            map_sheet_number_offset=2,
        )
        serialized = general.serialize()

        self.assertIn("Name:'TestSheet'", serialized)
        self.assertIn("Color:$FF0000", serialized)
        self.assertIn("CoarseGridWidth:10", serialized)
        self.assertIn("CoarseGridHeight:20", serialized)
        self.assertIn("MapSheetWidth:100", serialized)
        self.assertIn("MapSheetHeight:200", serialized)
        self.assertIn("MapSheetGridWidth:5", serialized)
        self.assertIn("MapSheetGridHeight:10", serialized)
        self.assertIn("MapSheetGridLeft:15", serialized)
        self.assertIn("MapSheetGridTop:25", serialized)
        self.assertIn("MapSheetNumbering:1", serialized)
        self.assertIn("MapSheetNumberOffset:2", serialized)
        self.assertIn(f"GUID:'{{{str(self.sheet_guid).upper()}}}'", serialized)

    def test_sheet_with_default_color_serializes_correctly(self) -> None:
        """Test that sheets with default color serialize correctly."""
        general = SheetMV.General(guid=self.sheet_guid, name="DefaultColorSheet")
        sheet = SheetMV(general)
        sheet.register(self.network)

        serialized = sheet.serialize()
        # Default color should be skipped
        self.assertIsNotNone(serialized)
        self.assertNotIn("SheetColor", serialized)  # Default color should not appear


if __name__ == "__main__":
    unittest.main()
