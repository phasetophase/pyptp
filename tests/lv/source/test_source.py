"""Tests for TSourceLS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid, encode_guid
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import ElementPresentation, NodePresentation
from pyptp.elements.lv.sheet import SheetLV
from pyptp.elements.lv.source import SourceLV
from pyptp.elements.mixins import Extra, Note
from pyptp.network_lv import NetworkLV


class TestSourceRegistration(unittest.TestCase):
    """Test source registration and functionality."""

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

        self.source_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_source_registration_works(self) -> None:
        """Test that sources can register themselves with the network."""
        general = SourceLV.General(
            guid=self.source_guid, name="TestSource", node=self.node_guid
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        source = SourceLV(general, [presentation])
        source.register(self.network)

        # Verify source is in network
        self.assertIn(self.source_guid, self.network.sources)
        self.assertIs(self.network.sources[self.source_guid], source)

    def test_source_with_full_properties_serializes_correctly(self) -> None:
        """Test that sources with all properties serialize correctly."""
        general = SourceLV.General(
            guid=self.source_guid,
            creation_time=123.45,
            mutation_date=10,
            revision_date=20.5,
            node=self.node_guid,
            name="FullSource",
            s_L1=True,
            s_L2=False,
            s_L3=True,
            s_N=False,
            field_name="SourceField",
            umin=0.38,
            umax=0.42,
            uref=0.4,
            sk2nom=50.0,
            is_sk2_used_for_loadflow=True,
            failure_frequency=0.005,
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

        source = SourceLV(general, [presentation])
        source.extras.append(Extra(text="foo=bar"))
        source.notes.append(Note(text="Test note"))
        source.register(self.network)

        # Test serialization
        serialized = source.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify key properties are serialized
        self.assertIn("Name:'FullSource'", serialized)
        self.assertIn("FieldName:'SourceField'", serialized)
        self.assertIn("s_L1:True", serialized)
        self.assertIn("s_L2:False", serialized)
        self.assertIn("s_L3:True", serialized)
        self.assertIn("s_N:False", serialized)
        self.assertIn("Umin:0.38", serialized)
        self.assertIn("Umax:0.42", serialized)
        self.assertIn("Uref:0.4", serialized)
        self.assertIn("Sk2nom:50.0", serialized)
        self.assertIn("Sk2TakeWith:True", serialized)
        self.assertIn("FailureFrequency:0.005", serialized)

        # Verify presentation properties
        self.assertIn(f"Sheet:{encode_guid(self.sheet_guid)}", serialized)
        self.assertIn("X:100", serialized)
        self.assertIn("Y:200", serialized)
        self.assertIn("Color:$00FF00", serialized)
        self.assertIn("TextColor:$FF0000", serialized)

        # Verify extras and notes
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a source with the same GUID overwrites the existing one."""
        general1 = SourceLV.General(
            guid=self.source_guid, name="FirstSource", node=self.node_guid
        )
        source1 = SourceLV(general1, [ElementPresentation(sheet=self.sheet_guid)])
        source1.register(self.network)

        general2 = SourceLV.General(
            guid=self.source_guid, name="SecondSource", node=self.node_guid
        )
        source2 = SourceLV(general2, [ElementPresentation(sheet=self.sheet_guid)])
        source2.register(self.network)

        # Should only have one source
        self.assertEqual(len(self.network.sources), 1)
        # Should be the second source
        self.assertEqual(
            self.network.sources[self.source_guid].general.name, "SecondSource"
        )

    def test_source_with_voltage_limits_serializes_correctly(self) -> None:
        """Test that sources with different voltage limits serialize correctly."""
        general = SourceLV.General(
            guid=self.source_guid,
            name="VoltageSource",
            node=self.node_guid,
            umin=0.35,
            umax=0.45,
            uref=0.4,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        source = SourceLV(general, [presentation])
        source.register(self.network)

        serialized = source.serialize()

        # Verify voltage properties are serialized
        self.assertIn("Umin:0.35", serialized)
        self.assertIn("Umax:0.45", serialized)
        self.assertIn("Uref:0.4", serialized)

    def test_source_with_short_circuit_data_serializes_correctly(self) -> None:
        """Test that sources with short circuit data serialize correctly."""
        general = SourceLV.General(
            guid=self.source_guid,
            name="ShortCircuitSource",
            node=self.node_guid,
            sk2nom=100.0,
            is_sk2_used_for_loadflow=False,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        source = SourceLV(general, [presentation])
        source.register(self.network)

        serialized = source.serialize()

        # Verify short circuit properties are serialized
        self.assertIn("Sk2nom:100.0", serialized)
        self.assertIn("Sk2TakeWith:False", serialized)

    def test_minimal_source_serialization(self) -> None:
        """Test that minimal sources serialize correctly with only required fields."""
        general = SourceLV.General(
            guid=self.source_guid, name="MinimalSource", node=self.node_guid
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        source = SourceLV(general, [presentation])
        source.register(self.network)

        serialized = source.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalSource'", serialized)
        self.assertIn("s_L1:True", serialized)  # Default values
        self.assertIn("s_L2:True", serialized)
        self.assertIn("s_L3:True", serialized)
        self.assertIn("s_N:True", serialized)
        self.assertIn("Umin:0.4", serialized)  # Default values
        self.assertIn("Umax:0.4", serialized)
        self.assertIn("Uref:0.4", serialized)
        self.assertIn("Sk2nom:40", serialized)  # Default value
        self.assertIn("Sk2TakeWith:False", serialized)  # Default value

        # Should not have optional sections
        self.assertNotIn("#Extra", serialized)
        self.assertNotIn("#Note", serialized)

    def test_multiple_presentations_serialize_correctly(self) -> None:
        """Test that sources with multiple presentations serialize correctly."""
        general = SourceLV.General(
            guid=self.source_guid, name="MultiPresSource", node=self.node_guid
        )

        pres1 = ElementPresentation(
            sheet=self.sheet_guid, x=100, y=100, color=DelphiColor("$FF0000")
        )
        pres2 = ElementPresentation(
            sheet=self.sheet_guid, x=200, y=200, color=DelphiColor("$00FF00")
        )

        source = SourceLV(general, [pres1, pres2])
        source.register(self.network)

        serialized = source.serialize()

        # Should have two presentations
        self.assertEqual(serialized.count("#Presentation"), 2)
        self.assertIn("Color:$FF0000", serialized)
        self.assertIn("Color:$00FF00", serialized)
        self.assertIn("X:100", serialized)
        self.assertIn("X:200", serialized)

    def test_source_with_failure_frequency_serializes_correctly(self) -> None:
        """Test that sources with failure frequency serialize correctly."""
        general = SourceLV.General(
            guid=self.source_guid,
            name="FailureSource",
            node=self.node_guid,
            failure_frequency=0.01,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        source = SourceLV(general, [presentation])
        source.register(self.network)

        serialized = source.serialize()

        # Verify failure frequency is serialized
        self.assertIn("FailureFrequency:0.01", serialized)


if __name__ == "__main__":
    unittest.main()
