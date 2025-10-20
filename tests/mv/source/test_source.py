"""Tests for TSourceMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid
from pyptp.elements.mixins import Extra, Note
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import ElementPresentation, NodePresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.elements.mv.source import SourceMV
from pyptp.network_mv import NetworkMV


class TestSourceRegistration(unittest.TestCase):
    """Test source registration and functionality."""

    def setUp(self) -> None:
        """Create a fresh network with sheet and node for testing."""
        self.network = NetworkMV()

        # Create and register a sheet
        sheet = SheetMV(
            SheetMV.General(
                guid=Guid(UUID("9c038adb-5a44-4f33-8cb4-8f0518f2b4c2")),
                name="TestSheet",
            ),
        )
        sheet.register(self.network)
        self.sheet_guid = sheet.general.guid

        # Create and register a node for the source
        node = NodeMV(
            NodeMV.General(
                guid=Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5")), name="TestNode"
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node.register(self.network)
        self.node_guid = node.general.guid

        self.source_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_source_registration_works(self) -> None:
        """Test that sources can register themselves with the network."""
        general = SourceMV.General(
            guid=self.source_guid, name="TestSource", node=self.node_guid
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        source = SourceMV(general, [presentation])
        source.register(self.network)

        # Verify source is in network
        self.assertIn(self.source_guid, self.network.sources)
        self.assertIs(self.network.sources[self.source_guid], source)

    def test_source_with_full_properties_serializes_correctly(self) -> None:
        """Test that sources with all properties serialize correctly."""
        general = SourceMV.General(
            guid=self.source_guid,
            node=self.node_guid,
            creation_time=123.45,
            mutation_date=10,
            revision_date=20,
            variant=True,
            name="FullSource",
            switch_state=True,
            field_name="TestField",
            failure_frequency=0.01,
            maintenance_frequency=0.1,
            maintenance_duration=4.0,
            maintenance_cancel_duration=1.0,
            not_preferred=True,
            uref=20.0,
            angle=30.0,
            sk2nom=1000.0,
            sk2min=800.0,
            sk2max=1200.0,
            r_x=0.1,
            z0_z1=3.0,
            smin=50.0,
            smax=100.0,
            pmin=40.0,
            pmax=80.0,
        )

        presentation = ElementPresentation(
            sheet=self.sheet_guid,
            x=100,
            y=200,
            color=DelphiColor("$FF0000"),
            size=2,
            width=3,
            text_color=DelphiColor("$00FF00"),
            text_size=12,
            font="Arial",
            text_style=1,
            no_text=True,
            upside_down_text=True,
            strings1_x=10,
            strings1_y=20,
            symbol_strings_x=30,
            symbol_strings_y=40,
            note_x=50,
            note_y=60,
            flag_flipped=True,
        )

        source = SourceMV(general, [presentation])
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
        self.assertIn("FieldName:'TestField'", serialized)
        self.assertIn("Variant:True", serialized)
        self.assertIn("SwitchState:1", serialized)
        self.assertIn("NotPreferred:True", serialized)
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("MaintenanceFrequency:0.1", serialized)
        self.assertIn("MaintenanceDuration:4.0", serialized)
        self.assertIn("MaintenanceCancelDuration:1.0", serialized)
        self.assertIn("Uref:20", serialized)
        self.assertIn("Angle:30", serialized)
        self.assertIn("Sk2nom:1000", serialized)
        self.assertIn("Sk2min:800", serialized)
        self.assertIn("Sk2max:1200", serialized)
        self.assertIn("R/X:0.1", serialized)
        self.assertIn("Z0/Z1:3", serialized)
        self.assertIn("Smin:50", serialized)
        self.assertIn("Smax:100", serialized)
        self.assertIn("Pmin:40", serialized)
        self.assertIn("Pmax:80", serialized)

        # Verify node reference
        self.assertIn(f"Node:'{{{str(self.node_guid).upper()}}}'", serialized)

        # Verify presentation properties
        self.assertIn(f"Sheet:'{{{str(self.sheet_guid).upper()}}}'", serialized)
        self.assertIn("X:100", serialized)
        self.assertIn("Y:200", serialized)
        self.assertIn("Color:$FF0000", serialized)
        self.assertIn("Size:2", serialized)
        self.assertIn("Width:3", serialized)
        self.assertIn("TextColor:$00FF00", serialized)
        self.assertIn("TextSize:12", serialized)
        self.assertIn("NoText:True", serialized)
        self.assertIn("UpsideDownText:True", serialized)
        self.assertIn("Strings1X:10", serialized)
        self.assertIn("Strings1Y:20", serialized)
        self.assertIn("SymbolStringsX:30", serialized)
        self.assertIn("SymbolStringsY:40", serialized)
        self.assertIn("NoteX:50", serialized)
        self.assertIn("NoteY:60", serialized)
        self.assertIn("FlagFlipped:True", serialized)

        # Verify extras and notes
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a source with the same GUID overwrites the existing one."""
        general1 = SourceMV.General(
            guid=self.source_guid, name="FirstSource", node=self.node_guid
        )
        source1 = SourceMV(general1, [ElementPresentation(sheet=self.sheet_guid)])
        source1.register(self.network)

        general2 = SourceMV.General(
            guid=self.source_guid, name="SecondSource", node=self.node_guid
        )
        source2 = SourceMV(general2, [ElementPresentation(sheet=self.sheet_guid)])
        source2.register(self.network)

        # Should only have one source
        self.assertEqual(len(self.network.sources), 1)
        # Should be the second source
        self.assertEqual(
            self.network.sources[self.source_guid].general.name, "SecondSource"
        )

    def test_minimal_source_serialization(self) -> None:
        """Test that minimal sources serialize correctly with only required fields."""
        general = SourceMV.General(
            guid=self.source_guid, name="MinimalSource", node=self.node_guid
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        source = SourceMV(general, [presentation])
        source.register(self.network)

        serialized = source.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalSource'", serialized)
        # Default values like Variant:False, SwitchState:False, NotPreferred:False, etc. are skipped in serialization

        # Should not have optional sections
        self.assertNotIn("#Extra", serialized)
        self.assertNotIn("#Note", serialized)

    def test_multiple_presentations_serialize_correctly(self) -> None:
        """Test that sources with multiple presentations serialize correctly."""
        general = SourceMV.General(
            guid=self.source_guid, name="MultiPresSource", node=self.node_guid
        )

        pres1 = ElementPresentation(
            sheet=self.sheet_guid,
            x=100,
            y=200,
            color=DelphiColor("$FF0000"),
        )
        pres2 = ElementPresentation(
            sheet=self.sheet_guid,
            x=300,
            y=400,
            color=DelphiColor("$00FF00"),
        )

        source = SourceMV(general, [pres1, pres2])
        source.register(self.network)

        serialized = source.serialize()

        # Should have two presentations
        self.assertEqual(serialized.count("#Presentation"), 2)
        self.assertIn("Color:$FF0000", serialized)
        self.assertIn("Color:$00FF00", serialized)

    def test_source_with_power_limits_serializes_correctly(self) -> None:
        """Test that sources with power limits serialize correctly."""
        general = SourceMV.General(
            guid=self.source_guid,
            name="PowerLimitSource",
            node=self.node_guid,
            smin=50.0,
            smax=100.0,
            pmin=40.0,
            pmax=80.0,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        source = SourceMV(general, [presentation])
        source.register(self.network)

        serialized = source.serialize()
        self.assertIn("Smin:50", serialized)
        self.assertIn("Smax:100", serialized)
        self.assertIn("Pmin:40", serialized)
        self.assertIn("Pmax:80", serialized)

    def test_source_with_short_circuit_properties_serializes_correctly(self) -> None:
        """Test that sources with short circuit properties serialize correctly."""
        general = SourceMV.General(
            guid=self.source_guid,
            name="ShortCircuitSource",
            node=self.node_guid,
            sk2nom=1000.0,
            sk2min=800.0,
            sk2max=1200.0,
            r_x=0.1,
            z0_z1=3.0,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        source = SourceMV(general, [presentation])
        source.register(self.network)

        serialized = source.serialize()
        self.assertIn("Sk2nom:1000", serialized)
        self.assertIn("Sk2min:800", serialized)
        self.assertIn("Sk2max:1200", serialized)
        self.assertIn("R/X:0.1", serialized)
        self.assertIn("Z0/Z1:3", serialized)

    def test_source_with_maintenance_properties_serializes_correctly(self) -> None:
        """Test that sources with maintenance properties serialize correctly."""
        general = SourceMV.General(
            guid=self.source_guid,
            name="MaintenanceSource",
            node=self.node_guid,
            failure_frequency=0.01,
            maintenance_frequency=0.1,
            maintenance_duration=4.0,
            maintenance_cancel_duration=1.0,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        source = SourceMV(general, [presentation])
        source.register(self.network)

        serialized = source.serialize()
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("MaintenanceFrequency:0.1", serialized)
        self.assertIn("MaintenanceDuration:4.0", serialized)
        self.assertIn("MaintenanceCancelDuration:1.0", serialized)

    def test_source_with_switch_state_serializes_correctly(self) -> None:
        """Test that sources with switch state serialize correctly."""
        general = SourceMV.General(
            guid=self.source_guid,
            name="SwitchStateSource",
            node=self.node_guid,
            switch_state=True,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        source = SourceMV(general, [presentation])
        source.register(self.network)

        serialized = source.serialize()
        self.assertIn("SwitchState:1", serialized)

    def test_source_with_reference_voltage_serializes_correctly(self) -> None:
        """Test that sources with reference voltage serialize correctly."""
        general = SourceMV.General(
            guid=self.source_guid,
            name="RefVoltageSource",
            node=self.node_guid,
            uref=20.0,
            angle=30.0,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        source = SourceMV(general, [presentation])
        source.register(self.network)

        serialized = source.serialize()
        self.assertIn("Uref:20", serialized)
        self.assertIn("Angle:30", serialized)


if __name__ == "__main__":
    unittest.main()
