"""Tests for TSelectionLS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.element_utils import Guid
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import NodePresentation
from pyptp.elements.lv.selection import SelectionLV
from pyptp.elements.lv.sheet import SheetLV
from pyptp.network_lv import NetworkLV


class TestSelectionRegistration(unittest.TestCase):
    """Test selection registration and functionality."""

    def setUp(self) -> None:
        """Create a fresh network with sheet and nodes for testing."""
        self.network = NetworkLV()

        # Create and register a sheet
        sheet = SheetLV(
            SheetLV.General(
                guid=Guid(UUID("9c038adb-5a44-4f33-8cb4-8f0518f2b4c2")),
                name="TestSheet",
            ),
        )
        sheet.register(self.network)
        self.sheet_guid = sheet.general.guid

        # Create and register some nodes for selection
        self.node1_guid = Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5"))
        node1 = NodeLV(
            NodeLV.General(guid=self.node1_guid, name="TestNode1"),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node1.register(self.network)

        self.node2_guid = Guid(UUID("aec2228f-a78e-4f54-9ed2-0a7dbd48b3f6"))
        node2 = NodeLV(
            NodeLV.General(guid=self.node2_guid, name="TestNode2"),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node2.register(self.network)

    def test_selection_registration_works(self) -> None:
        """Test that selections can register themselves with the network."""
        general = SelectionLV.General(name="TestSelection")

        objects = [
            SelectionLV.Object(guid=self.node1_guid),
            SelectionLV.Object(guid=self.node2_guid),
        ]

        selection = SelectionLV(general, objects)
        selection.register(self.network)

        # Verify selection is in network
        self.assertEqual(len(self.network.selections), 1)
        self.assertIs(self.network.selections[0], selection)
        self.assertEqual(self.network.selections[0].general.name, "TestSelection")

    def test_selection_with_objects_serializes_correctly(self) -> None:
        """Test that selections with objects serialize correctly."""
        general = SelectionLV.General(name="TestSelection")

        objects = [
            SelectionLV.Object(guid=self.node1_guid),
            SelectionLV.Object(guid=self.node2_guid),
        ]

        selection = SelectionLV(general, objects)
        selection.register(self.network)

        serialized = selection.serialize()

        # Verify general properties
        self.assertIn("#General", serialized)
        self.assertIn("Name:'TestSelection'", serialized)

        # Verify objects
        self.assertIn(f"#Object GUID:'{{{str(self.node1_guid).upper()}}}'", serialized)
        self.assertIn(f"#Object GUID:'{{{str(self.node2_guid).upper()}}}'", serialized)

    def test_empty_selection_serializes_correctly(self) -> None:
        """Test that empty selections serialize correctly."""
        general = SelectionLV.General(name="EmptySelection")

        selection = SelectionLV(general, [])
        selection.register(self.network)

        serialized = selection.serialize()

        # Verify general properties
        self.assertIn("#General", serialized)
        self.assertIn("Name:'EmptySelection'", serialized)

        # Should not have any objects
        self.assertNotIn("#Object", serialized)

    def test_duplicate_selection_registration_allows_duplicates(self) -> None:
        """Test that registering a selection with the same name now allows duplicates."""
        general1 = SelectionLV.General(name="TestSelection")
        objects1 = [SelectionLV.Object(guid=self.node1_guid)]
        selection1 = SelectionLV(general1, objects1)
        selection1.register(self.network)

        general2 = SelectionLV.General(name="TestSelection")
        objects2 = [SelectionLV.Object(guid=self.node2_guid)]
        selection2 = SelectionLV(general2, objects2)
        selection2.register(self.network)

        # Should now have two selections with the same name
        self.assertEqual(len(self.network.selections), 2)
        # First selection
        self.assertEqual(len(self.network.selections[0].objects), 1)
        self.assertEqual(self.network.selections[0].objects[0].guid, self.node1_guid)
        # Second selection
        self.assertEqual(len(self.network.selections[1].objects), 1)
        self.assertEqual(self.network.selections[1].objects[0].guid, self.node2_guid)

    def test_selection_deserialization_works(self) -> None:
        """Test that selection deserialization works correctly."""
        data = {
            "general": [{"Name": "TestSelection"}],
            "objects": [
                {"GUID": f"{{{str(self.node1_guid).upper()}}}"},
                {"GUID": f"{{{str(self.node2_guid).upper()}}}"},
            ],
        }

        selection = SelectionLV.deserialize(data)

        # Verify general properties
        self.assertEqual(selection.general.name, "TestSelection")

        # Verify objects
        self.assertEqual(len(selection.objects), 2)
        guids = [obj.guid for obj in selection.objects]
        self.assertIn(self.node1_guid, guids)
        self.assertIn(self.node2_guid, guids)

    def test_selection_deserialization_empty_objects(self) -> None:
        """Test that selection deserialization works with empty objects."""
        data = {"general": [{"Name": "EmptySelection"}], "objects": []}

        selection = SelectionLV.deserialize(data)

        # Verify general properties
        self.assertEqual(selection.general.name, "EmptySelection")

        # Verify no objects
        self.assertEqual(len(selection.objects), 0)

    def test_selection_round_trip_serialization(self) -> None:
        """Test that selection serialization and deserialization are consistent."""
        original_general = SelectionLV.General(name="RoundTripSelection")
        original_objects = [
            SelectionLV.Object(guid=self.node1_guid),
            SelectionLV.Object(guid=self.node2_guid),
        ]
        original_selection = SelectionLV(original_general, original_objects)

        # Serialize and verify it's not empty
        serialized = original_selection.serialize()
        self.assertIsNotNone(serialized)
        self.assertIn("#General", serialized)

        # Manually create deserialization data (simulating what the importer would do)
        data = {
            "general": [{"Name": "RoundTripSelection"}],
            "objects": [
                {"GUID": f"{{{str(self.node1_guid).upper()}}}"},
                {"GUID": f"{{{str(self.node2_guid).upper()}}}"},
            ],
        }

        # Deserialize
        deserialized_selection = SelectionLV.deserialize(data)

        # Verify consistency
        self.assertEqual(
            deserialized_selection.general.name, original_selection.general.name
        )
        self.assertEqual(
            len(deserialized_selection.objects), len(original_selection.objects)
        )

        original_guids = [obj.guid for obj in original_selection.objects]
        deserialized_guids = [obj.guid for obj in deserialized_selection.objects]
        for guid in original_guids:
            self.assertIn(guid, deserialized_guids)


if __name__ == "__main__":
    unittest.main()
