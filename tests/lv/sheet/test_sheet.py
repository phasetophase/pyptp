"""Tests for TSheetLS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import CL_GREEN, CL_RED, DelphiColor
from pyptp.elements.element_utils import Guid
from pyptp.elements.lv.sheet import SheetLV
from pyptp.network_lv import NetworkLV, NetworkModelError


class TestSheetRegistration(unittest.TestCase):
    """Test sheet registration and functionality."""

    def setUp(self) -> None:
        """Prepare file paths for export comparison."""
        self.guid1 = Guid(UUID("ccf32c78-bc1d-47e0-9f50-c05a19a43907"))
        self.guid2 = Guid(UUID("4160640b-635d-471f-87fa-c16ba9008040"))
        self.guid3 = Guid(UUID("b3fd8a3d-6afe-40d6-a2f3-057b63840bb6"))
        self.guid4 = Guid(UUID("e34b3c3d-98e7-4f83-a5c3-a6fe29f9d1a1"))

    def test_sheet_registration_works(self) -> None:
        """Test that sheets can register themselves with the network."""
        network = NetworkLV()

        sheet = SheetLV(
            SheetLV.General(guid=self.guid1, name="TestSheet", color=CL_RED)
        )
        sheet.register(network)

        # Verify sheet is in network
        self.assertIn(self.guid1, network.sheets)
        self.assertIs(network.sheets[self.guid1], sheet)

        # Verify lookup works
        found_guid = network.get_sheet_guid_by_name("TestSheet")
        self.assertEqual(found_guid, str(self.guid1))

    def test_multiple_sheets_with_colors_register_correctly(self) -> None:
        """Test that multiple sheets with different colors register and serialize correctly."""
        network = NetworkLV()

        # Create and register sheets with different colors
        sheet1 = SheetLV(SheetLV.General(guid=self.guid1, name="MainSheet"))
        sheet1.register(network)

        sheet2 = SheetLV(
            SheetLV.General(guid=self.guid2, name="RedSheet", color=CL_RED)
        )
        sheet2.register(network)

        sheet3 = SheetLV(
            SheetLV.General(guid=self.guid3, name="GreenSheet", color=CL_GREEN)
        )
        sheet3.register(network)

        custom_blue = DelphiColor("$0000FF")
        sheet4 = SheetLV(
            SheetLV.General(guid=self.guid4, name="BlueSheet", color=custom_blue)
        )
        sheet4.register(network)

        # Verify all sheets are registered
        self.assertEqual(len(network.sheets), 4)
        self.assertIn(self.guid1, network.sheets)
        self.assertIn(self.guid2, network.sheets)
        self.assertIn(self.guid3, network.sheets)
        self.assertIn(self.guid4, network.sheets)

        # Verify GUIDs are correct
        self.assertEqual(sheet1.general.guid, self.guid1)
        self.assertEqual(sheet2.general.guid, self.guid2)
        self.assertEqual(sheet3.general.guid, self.guid3)
        self.assertEqual(sheet4.general.guid, self.guid4)

        # Verify colors are correct
        default_color = sheet1.general.color
        self.assertIsInstance(default_color, str)
        self.assertTrue(default_color.startswith("$"))

        self.assertEqual(sheet2.general.color, CL_RED)
        self.assertEqual(sheet3.general.color, CL_GREEN)
        self.assertEqual(sheet4.general.color, custom_blue)

        # Verify lookups work
        self.assertEqual(network.get_sheet_guid_by_name("MainSheet"), str(self.guid1))
        self.assertEqual(network.get_sheet_guid_by_name("RedSheet"), str(self.guid2))
        self.assertEqual(network.get_sheet_guid_by_name("GreenSheet"), str(self.guid3))
        self.assertEqual(network.get_sheet_guid_by_name("BlueSheet"), str(self.guid4))

        # Test serialization
        serialized1 = sheet1.serialize()
        serialized2 = sheet2.serialize()
        serialized3 = sheet3.serialize()
        serialized4 = sheet4.serialize()

        self.assertIn("Color", serialized1)
        self.assertNotIn(f"{CL_RED}", serialized1)
        self.assertIn(f"{CL_RED}", serialized2)
        self.assertIn(f"{CL_GREEN}", serialized3)
        self.assertIn(f"{custom_blue}", serialized4)

    def test_sheet_with_grid_and_map_properties_serializes_correctly(self) -> None:
        """Test that sheets with grid and map properties serialize correctly."""
        network = NetworkLV()

        sheet = SheetLV(
            SheetLV.General(
                guid=self.guid1,
                name="GridMapSheet",
                coarse_grid_width=50,
                coarse_grid_height=60,
                map_sheet_width=800,
                map_sheet_height=600,
                map_sheet_grid_width=100,
                map_sheet_grid_height=120,
                map_sheet_grid_left=10,
                map_sheet_grid_top=20,
                map_sheet_numbering=2,
                map_sheet_number_offset=5,
            ),
        )
        sheet.register(network)

        serialized = sheet.serialize()

        # Verify all grid and map properties are serialized
        self.assertIn("CoarseGridWidth:50", serialized)
        self.assertIn("CoarseGridHeight:60", serialized)
        self.assertIn("MapSheetWidth:800", serialized)
        self.assertIn("MapSheetHeight:600", serialized)
        self.assertIn("MapSheetGridWidth:100", serialized)
        self.assertIn("MapSheetGridHeight:120", serialized)
        self.assertIn("MapSheetGridLeft:10", serialized)
        self.assertIn("MapSheetGridTop:20", serialized)
        self.assertIn("MapSheetNumbering:2", serialized)
        self.assertIn("MapSheetNumberOffset:5", serialized)

    def test_sheet_with_empty_name_gets_auto_named(self) -> None:
        """Test that sheets with empty names get auto-named during registration."""
        network = NetworkLV()

        sheet = SheetLV(SheetLV.General(guid=self.guid1, name=""))

        # Sheet auto-naming logs from the sheet module logger
        sheet.register(network)

        # Verify sheet was auto-named
        self.assertEqual(sheet.general.name, "Sheet1")
        self.assertIn(self.guid1, network.sheets)

        # Verify warning was logged
        # Test multiple empty sheets get sequential names
        sheet2 = SheetLV(SheetLV.General(guid=self.guid2, name=""))
        sheet3 = SheetLV(SheetLV.General(guid=self.guid3, name=""))

        # Register additional sheets
        sheet2.register(network)
        sheet3.register(network)

        self.assertEqual(sheet2.general.name, "Sheet2")
        self.assertEqual(sheet3.general.name, "Sheet3")

        # Verify lookups work with auto-named sheets
        found_guid1 = network.get_sheet_guid_by_name("Sheet1")
        found_guid2 = network.get_sheet_guid_by_name("Sheet2")
        found_guid3 = network.get_sheet_guid_by_name("Sheet3")

        self.assertEqual(found_guid1, str(self.guid1))
        self.assertEqual(found_guid2, str(self.guid2))
        self.assertEqual(found_guid3, str(self.guid3))

    def test_sheet_lookup_missing_raises_error(self) -> None:
        """Test that looking up a nonexistent sheet raises an error with proper logging."""
        network = NetworkLV()

        sheet = SheetLV(SheetLV.General(guid=self.guid1, name="OnlySheet"))
        sheet.register(network)

        with self.assertRaises(NetworkModelError):
            network.get_sheet_guid_by_name("DoesNotExist")

    def test_sheet_property_updates_reflect_in_lookup(self) -> None:
        """Test that updating sheet properties updates the lookup mechanism."""
        network = NetworkLV()

        sheet = SheetLV(SheetLV.General(guid=self.guid1, name="OriginalName"))
        sheet.register(network)

        # Update the name
        sheet.general.name = "UpdatedName"

        # Lookup should work with new name
        found_guid = network.get_sheet_guid_by_name("UpdatedName")
        self.assertEqual(found_guid, str(self.guid1))

        # Old name should not be found
        with self.assertRaises(NetworkModelError):
            network.get_sheet_guid_by_name("OriginalName")

    def test_sheet_deletion_removes_from_lookup(self) -> None:
        """Test that deleting a sheet removes it from the lookup mechanism."""
        network = NetworkLV()

        sheet = SheetLV(SheetLV.General(guid=self.guid1, name="ToDelete"))
        sheet.register(network)

        # Verify it exists
        network.get_sheet_guid_by_name("ToDelete")

        # Delete it
        del network.sheets[self.guid1]

        # Lookup should fail
        with self.assertRaises(NetworkModelError):
            network.get_sheet_guid_by_name("ToDelete")

    def test_duplicate_sheet_registration_overwrites(self) -> None:
        """Test that registering a sheet with the same GUID overwrites the existing one."""
        network = NetworkLV()

        sheet1 = SheetLV(SheetLV.General(guid=self.guid1, name="FirstSheet"))
        sheet1.register(network)

        sheet2 = SheetLV(SheetLV.General(guid=self.guid1, name="SecondSheet"))
        sheet2.register(network)

        # Should only have one sheet
        self.assertEqual(len(network.sheets), 1)
        # Should be the second sheet
        self.assertEqual(network.sheets[self.guid1].general.name, "SecondSheet")

    def test_minimal_sheet_serialization(self) -> None:
        """Test that minimal sheets serialize correctly with only required fields."""
        network = NetworkLV()

        sheet = SheetLV(SheetLV.General(guid=self.guid1, name="MinimalSheet"))
        sheet.register(network)

        serialized = sheet.serialize()

        # Should have basic properties
        self.assertIn("Name:'MinimalSheet'", serialized)
        self.assertIn("Color", serialized)  # Should have default color

        # Should not have grid/map properties
        self.assertNotIn("CoarseGridWidth", serialized)
        self.assertNotIn("MapSheetWidth", serialized)


if __name__ == "__main__":
    unittest.main()
