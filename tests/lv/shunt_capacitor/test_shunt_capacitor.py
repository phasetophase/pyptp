"""Tests for TShuntCapacitorLS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid, encode_guid
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import ElementPresentation, NodePresentation
from pyptp.elements.lv.sheet import SheetLV
from pyptp.elements.lv.shunt_capacitor import ShuntCapacitorLV
from pyptp.elements.mixins import Extra, Note
from pyptp.network_lv import NetworkLV


class TestShuntCapacitorRegistration(unittest.TestCase):
    """Test shunt capacitor registration and functionality."""

    def setUp(self) -> None:
        """Create a fresh network with sheet and node for testing."""
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

        # Create and register a node
        node = NodeLV(
            NodeLV.General(
                guid=Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5")), name="TestNode"
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node.register(self.network)
        self.node_guid = node.general.guid

        self.cap_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_shunt_capacitor_registration_works(self) -> None:
        """Test that shunt capacitors can register themselves with the network."""
        general = ShuntCapacitorLV.General(
            guid=self.cap_guid,
            name="TestShuntCapacitor",
            node=self.node_guid,
            field_name="CapField",
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        cap = ShuntCapacitorLV(general, [presentation])
        cap.register(self.network)

        # Verify shunt capacitor is in network
        self.assertIn(self.cap_guid, self.network.shunt_capacitors)
        self.assertIs(self.network.shunt_capacitors[self.cap_guid], cap)

    def test_shunt_capacitor_with_full_properties_serializes_correctly(self) -> None:
        """Test that shunt capacitors with all properties serialize correctly."""
        cap = self._create_full_capacitor()
        cap.register(self.network)

        # Test serialization
        serialized = cap.serialize()

        # Verify all sections are present
        self._verify_sections_present(serialized)

        # Verify key general properties are serialized
        self._verify_general_properties(serialized)

        # Verify presentation properties
        self._verify_presentation_properties(serialized)

        # Verify extras and notes
        self._verify_extras_and_notes(serialized)

    def _create_full_capacitor(self) -> ShuntCapacitorLV:
        """Create a shunt capacitor with all properties set."""
        general = ShuntCapacitorLV.General(
            guid=self.cap_guid,
            node=self.node_guid,
            name="FullShuntCapacitor",
            s_L1=True,
            s_L2=False,
            s_L3=True,
            s_N=False,
            field_name="CapField",
            Q=50.0,
            passive_filter_frequency=60.0,
            passive_filter_quality_factor=0.95,
            creation_time=1234567890,
            mutation_date=123456789,
            revision_date=1234567890.0,
        )

        presentation = ElementPresentation(
            sheet=self.sheet_guid,
            x=100,
            y=200,
            color=DelphiColor("$00FF00"),
            size=2,
            width=3,
            text_color=DelphiColor("$FF0000"),
            text_size=12,
            font="Arial",
            text_style=1,
            no_text=True,
            upside_down_text=True,
        )

        cap = ShuntCapacitorLV(general, [presentation])
        cap.extras.append(Extra(text="foo=bar"))
        cap.notes.append(Note(text="Test note"))
        return cap

    def _verify_sections_present(self, serialized: str) -> None:
        """Verify all required sections are present in serialized output."""
        self.assertEqual(serialized.count("#General"), 1)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

    def _verify_general_properties(self, serialized: str) -> None:
        """Verify general properties are serialized correctly."""
        self.assertIn("Name:'FullShuntCapacitor'", serialized)
        self.assertIn("FieldName:'CapField'", serialized)
        self.assertNotIn("s_L2:", serialized)  # False values are skipped
        self.assertNotIn("s_N:", serialized)  # False values are skipped
        self.assertIn("Q:50.0", serialized)
        self.assertIn("PassiveFilterFrequency:60.0", serialized)
        self.assertIn("PassiveFilterQualityFactor:0.95", serialized)
        self.assertIn("CreationTime:1234567890", serialized)
        self.assertIn("MutationDate:123456789", serialized)
        self.assertIn("RevisionDate:1234567890.0", serialized)

    def _verify_presentation_properties(self, serialized: str) -> None:
        """Verify presentation properties are serialized correctly."""
        self.assertIn(f"Sheet:{encode_guid(self.sheet_guid)}", serialized)
        self.assertIn("X:100", serialized)
        self.assertIn("Y:200", serialized)
        self.assertIn("Color:$00FF00", serialized)
        self.assertIn("TextColor:$FF0000", serialized)

    def _verify_extras_and_notes(self, serialized: str) -> None:
        """Verify extras and notes are serialized correctly."""
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a shunt capacitor with the same GUID overwrites the existing one."""
        general1 = ShuntCapacitorLV.General(
            guid=self.cap_guid,
            name="FirstCap",
            node=self.node_guid,
            field_name="Field1",
        )
        cap1 = ShuntCapacitorLV(general1, [ElementPresentation(sheet=self.sheet_guid)])
        cap1.register(self.network)

        general2 = ShuntCapacitorLV.General(
            guid=self.cap_guid,
            name="SecondCap",
            node=self.node_guid,
            field_name="Field2",
        )
        cap2 = ShuntCapacitorLV(general2, [ElementPresentation(sheet=self.sheet_guid)])
        cap2.register(self.network)

        # Should only have one shunt capacitor
        self.assertEqual(len(self.network.shunt_capacitors), 1)
        # Should be the second shunt capacitor
        self.assertEqual(
            self.network.shunt_capacitors[self.cap_guid].general.name, "SecondCap"
        )

    def test_minimal_shunt_capacitor_serialization(self) -> None:
        """Test that minimal shunt capacitors serialize correctly with only required fields."""
        general = ShuntCapacitorLV.General(
            guid=self.cap_guid,
            name="MinimalCap",
            node=self.node_guid,
            field_name="MinimalField",
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        cap = ShuntCapacitorLV(general, [presentation])
        cap.register(self.network)

        serialized = cap.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalCap'", serialized)
        self.assertIn("FieldName:'MinimalField'", serialized)

        # Should not have optional sections
        self.assertNotIn("#Extra", serialized)
        self.assertNotIn("#Note", serialized)

    def test_multiple_presentations_serialize_correctly(self) -> None:
        """Test that shunt capacitors with multiple presentations serialize correctly."""
        general = ShuntCapacitorLV.General(
            guid=self.cap_guid,
            name="MultiPresCap",
            node=self.node_guid,
            field_name="MultiField",
        )

        pres1 = ElementPresentation(
            sheet=self.sheet_guid, x=100, y=100, color=DelphiColor("$FF0000")
        )
        pres2 = ElementPresentation(
            sheet=self.sheet_guid, x=200, y=200, color=DelphiColor("$00FF00")
        )

        cap = ShuntCapacitorLV(general, [pres1, pres2])
        cap.register(self.network)

        serialized = cap.serialize()

        # Should have two presentations
        self.assertEqual(serialized.count("#Presentation"), 2)
        self.assertIn("Color:$FF0000", serialized)
        self.assertIn("Color:$00FF00", serialized)
        self.assertIn("X:100", serialized)
        self.assertIn("X:200", serialized)


if __name__ == "__main__":
    unittest.main()
