"""Tests for TNodeLS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid, encode_guid
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import NodePresentation
from pyptp.elements.lv.shared import Fields
from pyptp.elements.lv.sheet import SheetLV
from pyptp.elements.mixins import Extra, Note
from pyptp.network_lv import NetworkLV, NetworkModelError


class TestNodeRegistration(unittest.TestCase):
    """Test node registration and basic functionality."""

    def setUp(self) -> None:
        """Create a fresh network with one sheet for testing."""
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

        self.node_guid = Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5"))

    def test_node_registration_works(self) -> None:
        """Test that nodes can register themselves with the network."""
        general = NodeLV.General(
            guid=self.node_guid, name="TestNode", unom=0.4, function="Load"
        )
        presentation = NodePresentation(sheet=self.sheet_guid, x=100, y=200)

        node = NodeLV(general, [presentation])
        node.register(self.network)

        # Verify node is in network
        self.assertIn(self.node_guid, self.network.nodes)
        self.assertIs(self.network.nodes[self.node_guid], node)

        # Verify lookup works
        found_guid = self.network.get_node_guid_by_name("TestNode")
        self.assertEqual(found_guid, str(self.node_guid))

    def test_node_with_full_properties_serializes_correctly(self) -> None:
        """Test that nodes with all properties serialize correctly."""
        general = NodeLV.General(
            guid=self.node_guid,
            creation_time=123.45,
            mutation_date=10,
            revision_date=20.5,
            name="FullNode",
            short_name="FN",
            id="ID123",
            unom=0.6,
            function="Transformer",
            earthing_configuration="TN-C-S",
            s_N_PE=True,
            s_PE_e=True,
            Re=5.0,
            k_h1=1,
            k_h2=2,
            k_h3=3,
            k_h4=4,
            s_h1=True,
            s_h2=False,
            s_h3=True,
            s_h4=False,
            gx=10.0,
            gy=20.0,
            failure_frequency=0.01,
            risk=True,
        )

        presentation = NodePresentation(
            sheet=self.sheet_guid,
            x=100,
            y=200,
            symbol=7,
            color=DelphiColor("$00FF00"),
            size=2,
            width=3,
            text_color=DelphiColor("$FF0000"),
            text_size=12,
            font="Arial",
            text_style=1,
            no_text=True,
            upside_down_text=True,
            text_rotation=45,
            upstrings_x=5,
            upstrings_y=6,
            fault_strings_x=7,
            fault_strings_y=8,
            note_x=9,
            note_y=10,
        )

        node = NodeLV(general, [presentation])
        node.fields = Fields(values=["A", "B", "C"])
        node.extras.append(Extra(text="foo=bar"))
        node.notes.append(Note(text="Test note"))
        node.register(self.network)

        # Test serialization
        serialized = node.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#Fields", serialized)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify key properties are serialized
        self.assertIn("Name:'FullNode'", serialized)
        self.assertIn("ShortName:'FN'", serialized)
        self.assertIn("ID:'ID123'", serialized)
        self.assertIn("Unom:0.6", serialized)
        self.assertIn("Function:'Transformer'", serialized)
        self.assertIn("EarthingConfiguration:'TN-C-S'", serialized)
        self.assertIn("s_N_PE:True", serialized)
        self.assertIn("s_PE_e:True", serialized)
        self.assertIn("Re:5.0", serialized)
        self.assertIn("GX:10.0", serialized)
        self.assertIn("GY:20.0", serialized)
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("Risk:True", serialized)

        # Verify presentation properties
        self.assertIn(f"Sheet:{encode_guid(self.sheet_guid)}", serialized)
        self.assertIn("X:100", serialized)
        self.assertIn("Y:200", serialized)
        self.assertIn("Symbol:7", serialized)
        self.assertIn("Color:$00FF00", serialized)
        self.assertIn("TextColor:$FF0000", serialized)

        # Verify fields, extras, and notes
        self.assertIn("#Fields Name0:'A' Name1:'B' Name2:'C'", serialized)
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a node with the same GUID overwrites the existing one."""
        general1 = NodeLV.General(guid=self.node_guid, name="FirstNode")
        node1 = NodeLV(general1, [NodePresentation(sheet=self.sheet_guid)])
        node1.register(self.network)

        general2 = NodeLV.General(guid=self.node_guid, name="SecondNode")
        node2 = NodeLV(general2, [NodePresentation(sheet=self.sheet_guid)])
        node2.register(self.network)

        # Should only have one node
        self.assertEqual(len(self.network.nodes), 1)
        # Should be the second node
        self.assertEqual(self.network.nodes[self.node_guid].general.name, "SecondNode")

    def test_node_lookup_by_name_works(self) -> None:
        """Test that nodes can be looked up by name."""
        general = NodeLV.General(guid=self.node_guid, name="LookupNode")
        node = NodeLV(general, [NodePresentation(sheet=self.sheet_guid)])
        node.register(self.network)

        found_guid = self.network.get_node_guid_by_name("LookupNode")
        self.assertEqual(found_guid, str(self.node_guid))

    def test_node_lookup_missing_raises_error(self) -> None:
        """Test that looking up a nonexistent node raises an error."""
        with self.assertRaises(NetworkModelError):
            self.network.get_node_guid_by_name("NoSuchNode")

    def test_node_property_updates_reflect_in_lookup(self) -> None:
        """Test that updating node properties updates the lookup mechanism."""
        general = NodeLV.General(guid=self.node_guid, name="OriginalName")
        node = NodeLV(general, [NodePresentation(sheet=self.sheet_guid)])
        node.register(self.network)

        # Update the name
        node.general.name = "UpdatedName"

        # Lookup should work with new name
        found_guid = self.network.get_node_guid_by_name("UpdatedName")
        self.assertEqual(found_guid, str(self.node_guid))

        # Old name should not be found
        with self.assertRaises(NetworkModelError):
            self.network.get_node_guid_by_name("OriginalName")

    def test_node_deletion_removes_from_lookup(self) -> None:
        """Test that deleting a node removes it from the lookup mechanism."""
        general = NodeLV.General(guid=self.node_guid, name="ToDelete")
        node = NodeLV(general, [NodePresentation(sheet=self.sheet_guid)])
        node.register(self.network)

        # Verify it exists
        self.network.get_node_guid_by_name("ToDelete")

        # Delete it
        del self.network.nodes[self.node_guid]

        # Lookup should fail
        with self.assertRaises(NetworkModelError):
            self.network.get_node_guid_by_name("ToDelete")

    def test_minimal_node_serialization(self) -> None:
        """Test that minimal nodes serialize correctly with only required fields."""
        general = NodeLV.General(name="MinimalNode")
        node = NodeLV(general, [NodePresentation(sheet=self.sheet_guid)])
        node.register(self.network)

        serialized = node.serialize()

        # Should have General and Presentation, but no Fields
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#Presentation", serialized)
        self.assertNotIn("#Fields", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalNode'", serialized)
        self.assertIn("Unom:0.4", serialized)  # Default value

    def test_multiple_presentations_serialize_correctly(self) -> None:
        """Test that nodes with multiple presentations serialize correctly."""
        general = NodeLV.General(guid=self.node_guid, name="MultiPresNode")

        pres1 = NodePresentation(
            sheet=self.sheet_guid, x=100, y=100, color=DelphiColor("$FF0000")
        )
        pres2 = NodePresentation(
            sheet=self.sheet_guid, x=200, y=200, color=DelphiColor("$00FF00")
        )

        node = NodeLV(general, [pres1, pres2])
        node.register(self.network)

        serialized = node.serialize()

        # Should have two presentations
        self.assertEqual(serialized.count("#Presentation"), 2)
        self.assertIn("Color:$FF0000", serialized)
        self.assertIn("Color:$00FF00", serialized)
        self.assertIn("X:100", serialized)
        self.assertIn("X:200", serialized)


if __name__ == "__main__":
    unittest.main()
