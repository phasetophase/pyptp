"""Tests for TReactanceCoilMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid
from pyptp.elements.mixins import Extra, Note
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import ElementPresentation, NodePresentation
from pyptp.elements.mv.reactance_coil import ReactanceCoilMV
from pyptp.elements.mv.sheet import SheetMV
from pyptp.network_mv import NetworkMV


class TestReactanceCoilRegistration(unittest.TestCase):
    """Test reactance coil registration and functionality."""

    def setUp(self) -> None:
        """Create a fresh network with sheet and nodes for testing."""
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

        # Create and register nodes for the reactance coil
        node1 = NodeMV(
            NodeMV.General(
                guid=Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5")),
                name="TestNode1",
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node1.register(self.network)
        self.node1_guid = node1.general.guid

        node2 = NodeMV(
            NodeMV.General(
                guid=Guid(UUID("8b7d4c3e-2f1a-4e5d-9c8b-7a6f5e4d3c2b")),
                name="TestNode2",
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node2.register(self.network)
        self.node2_guid = node2.general.guid

        self.reactance_coil_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_reactance_coil_registration_works(self) -> None:
        """Test that reactance coils can register themselves with the network."""
        general = ReactanceCoilMV.General(
            guid=self.reactance_coil_guid,
            name="TestReactanceCoil",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        reactance_coil_type = ReactanceCoilMV.ReactanceCoilType(short_name="TestType")
        presentation = ElementPresentation(sheet=self.sheet_guid)

        reactance_coil = ReactanceCoilMV(general, [presentation], reactance_coil_type)
        reactance_coil.register(self.network)

        # Verify reactance coil is in network
        self.assertIn(self.reactance_coil_guid, self.network.reactance_coils)
        self.assertIs(
            self.network.reactance_coils[self.reactance_coil_guid], reactance_coil
        )

    def test_reactance_coil_with_full_properties_serializes_correctly(self) -> None:
        """Test that reactance coils with all properties serialize correctly."""
        general = ReactanceCoilMV.General(
            guid=self.reactance_coil_guid,
            creation_time=123.45,
            mutation_date=10,
            revision_date=20,
            variant=True,
            node1=self.node1_guid,
            node2=self.node2_guid,
            name="FullReactanceCoil",
            switch_state1=True,
            switch_state2=True,
            field_name1="Field1",
            field_name2="Field2",
            subnet_border=True,
            source1="Source1",
            source2="Source2",
            failure_frequency=0.01,
            repair_duration=2.5,
            maintenance_frequency=0.1,
            maintenance_duration=4.0,
            maintenance_cancel_duration=1.0,
            type="GenType",
        )

        reactance_coil_type = ReactanceCoilMV.ReactanceCoilType(
            short_name="FullType",
            unom=20.0,
            inom=100.0,
            R=0.1,
            X=0.2,
            R0=0.05,
            X0=0.15,
            R2=0.08,
            X2=0.18,
            Ik2s=150.0,
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

        reactance_coil = ReactanceCoilMV(general, [presentation], reactance_coil_type)
        reactance_coil.extras.append(Extra(text="foo=bar"))
        reactance_coil.notes.append(Note(text="Test note"))
        reactance_coil.register(self.network)

        # Test serialization
        serialized = reactance_coil.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertEqual(serialized.count("#ReactanceCoilType"), 1)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify general properties
        self.assertIn("Name:'FullReactanceCoil'", serialized)
        self.assertIn("CreationTime:123.45", serialized)
        self.assertIn("MutationDate:10", serialized)
        self.assertIn("RevisionDate:20", serialized)
        self.assertIn("Variant:True", serialized)
        self.assertIn("SwitchState1:1", serialized)
        self.assertIn("SwitchState2:1", serialized)
        self.assertIn("FieldName1:'Field1'", serialized)
        self.assertIn("FieldName2:'Field2'", serialized)
        self.assertIn("SubnetBorder:True", serialized)
        self.assertIn("Source1:'Source1'", serialized)
        self.assertIn("Source2:'Source2'", serialized)
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("RepairDuration:2.5", serialized)
        self.assertIn("MaintenanceFrequency:0.1", serialized)
        self.assertIn("MaintenanceDuration:4.0", serialized)
        self.assertIn("MaintenanceCancelDuration:1.0", serialized)
        self.assertIn("AsynchronousGeneratorType:'GenType'", serialized)

        # Verify node references
        self.assertIn(f"Node1:'{{{str(self.node1_guid).upper()}}}'", serialized)
        self.assertIn(f"Node2:'{{{str(self.node2_guid).upper()}}}'", serialized)

        # Verify reactance coil type properties
        self.assertIn("ShortName:'FullType'", serialized)
        self.assertIn("Unom:20", serialized)
        self.assertIn("Inom:100", serialized)
        self.assertIn("R:0.1", serialized)
        self.assertIn("X:0.2", serialized)
        self.assertIn("R0:0.05", serialized)
        self.assertIn("X0:0.15", serialized)
        self.assertIn("R2:0.08", serialized)
        self.assertIn("X2:0.18", serialized)
        self.assertIn("Ik2s:150", serialized)

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
        """Test that registering a reactance coil with the same GUID overwrites the existing one."""
        general1 = ReactanceCoilMV.General(
            guid=self.reactance_coil_guid,
            name="FirstReactanceCoil",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        reactance_coil_type1 = ReactanceCoilMV.ReactanceCoilType(short_name="Type1")
        reactance_coil1 = ReactanceCoilMV(
            general1, [ElementPresentation(sheet=self.sheet_guid)], reactance_coil_type1
        )
        reactance_coil1.register(self.network)

        general2 = ReactanceCoilMV.General(
            guid=self.reactance_coil_guid,
            name="SecondReactanceCoil",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        reactance_coil_type2 = ReactanceCoilMV.ReactanceCoilType(short_name="Type2")
        reactance_coil2 = ReactanceCoilMV(
            general2, [ElementPresentation(sheet=self.sheet_guid)], reactance_coil_type2
        )
        reactance_coil2.register(self.network)

        # Should only have one reactance coil
        self.assertEqual(len(self.network.reactance_coils), 1)
        # Should be the second reactance coil
        self.assertEqual(
            self.network.reactance_coils[self.reactance_coil_guid].general.name,
            "SecondReactanceCoil",
        )

    def test_minimal_reactance_coil_serialization(self) -> None:
        """Test that minimal reactance coils serialize correctly with only required fields."""
        general = ReactanceCoilMV.General(
            guid=self.reactance_coil_guid,
            name="MinimalReactanceCoil",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        reactance_coil_type = ReactanceCoilMV.ReactanceCoilType()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        reactance_coil = ReactanceCoilMV(general, [presentation], reactance_coil_type)
        reactance_coil.register(self.network)

        serialized = reactance_coil.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertEqual(serialized.count("#ReactanceCoilType"), 1)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalReactanceCoil'", serialized)
        self.assertIn(f"Node1:'{{{str(self.node1_guid).upper()}}}'", serialized)
        self.assertIn(f"Node2:'{{{str(self.node2_guid).upper()}}}'", serialized)

        # Default values should be included since using no_skip
        self.assertIn("CreationTime:0", serialized)
        self.assertNotIn("Variant:", serialized)  # False values are skipped
        self.assertIn("SwitchState1:0", serialized)
        self.assertIn("SwitchState2:0", serialized)
        # SubnetBorder:False should be skipped as default

    def test_reactance_coil_with_electrical_properties_serializes_correctly(
        self,
    ) -> None:
        """Test that reactance coils with electrical properties serialize correctly."""
        general = ReactanceCoilMV.General(
            guid=self.reactance_coil_guid,
            name="ElectricalReactanceCoil",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        reactance_coil_type = ReactanceCoilMV.ReactanceCoilType(
            short_name="ElecType",
            unom=20.0,
            inom=100.0,
            R=0.1,
            X=0.2,
            R0=0.05,
            X0=0.15,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        reactance_coil = ReactanceCoilMV(general, [presentation], reactance_coil_type)
        reactance_coil.register(self.network)

        serialized = reactance_coil.serialize()
        self.assertIn("ShortName:'ElecType'", serialized)
        self.assertIn("Unom:20", serialized)
        self.assertIn("Inom:100", serialized)
        self.assertIn("R:0.1", serialized)
        self.assertIn("X:0.2", serialized)
        self.assertIn("R0:0.05", serialized)
        self.assertIn("X0:0.15", serialized)

    def test_reactance_coil_with_sequence_impedances_serializes_correctly(self) -> None:
        """Test that reactance coils with sequence impedances serialize correctly."""
        general = ReactanceCoilMV.General(
            guid=self.reactance_coil_guid,
            name="SequenceReactanceCoil",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        reactance_coil_type = ReactanceCoilMV.ReactanceCoilType(
            short_name="SeqType",
            R2=0.08,
            X2=0.18,
            Ik2s=150.0,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        reactance_coil = ReactanceCoilMV(general, [presentation], reactance_coil_type)
        reactance_coil.register(self.network)

        serialized = reactance_coil.serialize()
        self.assertIn("R2:0.08", serialized)
        self.assertIn("X2:0.18", serialized)
        self.assertIn("Ik2s:150", serialized)

    def test_reactance_coil_with_maintenance_properties_serializes_correctly(
        self,
    ) -> None:
        """Test that reactance coils with maintenance properties serialize correctly."""
        general = ReactanceCoilMV.General(
            guid=self.reactance_coil_guid,
            name="MaintenanceReactanceCoil",
            node1=self.node1_guid,
            node2=self.node2_guid,
            failure_frequency=0.01,
            repair_duration=2.5,
            maintenance_frequency=0.1,
            maintenance_duration=4.0,
            maintenance_cancel_duration=1.0,
        )
        reactance_coil_type = ReactanceCoilMV.ReactanceCoilType(short_name="MainType")
        presentation = ElementPresentation(sheet=self.sheet_guid)

        reactance_coil = ReactanceCoilMV(general, [presentation], reactance_coil_type)
        reactance_coil.register(self.network)

        serialized = reactance_coil.serialize()
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("RepairDuration:2.5", serialized)
        self.assertIn("MaintenanceFrequency:0.1", serialized)
        self.assertIn("MaintenanceDuration:4.0", serialized)
        self.assertIn("MaintenanceCancelDuration:1.0", serialized)

    def test_reactance_coil_with_switch_states_serializes_correctly(self) -> None:
        """Test that reactance coils with switch states serialize correctly."""
        general = ReactanceCoilMV.General(
            guid=self.reactance_coil_guid,
            name="SwitchStateReactanceCoil",
            node1=self.node1_guid,
            node2=self.node2_guid,
            switch_state1=True,
            switch_state2=True,
        )
        reactance_coil_type = ReactanceCoilMV.ReactanceCoilType(short_name="SwitchType")
        presentation = ElementPresentation(sheet=self.sheet_guid)

        reactance_coil = ReactanceCoilMV(general, [presentation], reactance_coil_type)
        reactance_coil.register(self.network)

        serialized = reactance_coil.serialize()
        self.assertIn("SwitchState1:1", serialized)
        self.assertIn("SwitchState2:1", serialized)

    def test_reactance_coil_with_field_names_serializes_correctly(self) -> None:
        """Test that reactance coils with field names serialize correctly."""
        general = ReactanceCoilMV.General(
            guid=self.reactance_coil_guid,
            name="FieldNameReactanceCoil",
            node1=self.node1_guid,
            node2=self.node2_guid,
            field_name1="Field1",
            field_name2="Field2",
        )
        reactance_coil_type = ReactanceCoilMV.ReactanceCoilType(short_name="FieldType")
        presentation = ElementPresentation(sheet=self.sheet_guid)

        reactance_coil = ReactanceCoilMV(general, [presentation], reactance_coil_type)
        reactance_coil.register(self.network)

        serialized = reactance_coil.serialize()
        self.assertIn("FieldName1:'Field1'", serialized)
        self.assertIn("FieldName2:'Field2'", serialized)

    def test_reactance_coil_with_sources_serializes_correctly(self) -> None:
        """Test that reactance coils with sources serialize correctly."""
        general = ReactanceCoilMV.General(
            guid=self.reactance_coil_guid,
            name="SourceReactanceCoil",
            node1=self.node1_guid,
            node2=self.node2_guid,
            source1="Source1",
            source2="Source2",
        )
        reactance_coil_type = ReactanceCoilMV.ReactanceCoilType(short_name="SourceType")
        presentation = ElementPresentation(sheet=self.sheet_guid)

        reactance_coil = ReactanceCoilMV(general, [presentation], reactance_coil_type)
        reactance_coil.register(self.network)

        serialized = reactance_coil.serialize()
        self.assertIn("Source1:'Source1'", serialized)
        self.assertIn("Source2:'Source2'", serialized)

    def test_reactance_coil_with_subnet_border_serializes_correctly(self) -> None:
        """Test that reactance coils with subnet border serialize correctly."""
        general = ReactanceCoilMV.General(
            guid=self.reactance_coil_guid,
            name="SubnetBorderReactanceCoil",
            node1=self.node1_guid,
            node2=self.node2_guid,
            subnet_border=True,
        )
        reactance_coil_type = ReactanceCoilMV.ReactanceCoilType(short_name="SubnetType")
        presentation = ElementPresentation(sheet=self.sheet_guid)

        reactance_coil = ReactanceCoilMV(general, [presentation], reactance_coil_type)
        reactance_coil.register(self.network)

        serialized = reactance_coil.serialize()
        self.assertIn("SubnetBorder:True", serialized)

    def test_reactance_coil_with_generator_type_serializes_correctly(self) -> None:
        """Test that reactance coils with generator type serialize correctly."""
        general = ReactanceCoilMV.General(
            guid=self.reactance_coil_guid,
            name="GeneratorTypeReactanceCoil",
            node1=self.node1_guid,
            node2=self.node2_guid,
            type="GenType",
        )
        reactance_coil_type = ReactanceCoilMV.ReactanceCoilType(short_name="GenType")
        presentation = ElementPresentation(sheet=self.sheet_guid)

        reactance_coil = ReactanceCoilMV(general, [presentation], reactance_coil_type)
        reactance_coil.register(self.network)

        serialized = reactance_coil.serialize()
        self.assertIn("AsynchronousGeneratorType:'GenType'", serialized)


if __name__ == "__main__":
    unittest.main()
