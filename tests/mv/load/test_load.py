"""Tests for TLoadMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid
from pyptp.elements.mixins import Extra, Note
from pyptp.elements.mv.load import LoadMV
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import ElementPresentation, NodePresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.network_mv import NetworkMV


class TestLoadRegistration(unittest.TestCase):
    """Test load registration and functionality."""

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

        # Create and register a node for the load
        node = NodeMV(
            NodeMV.General(
                guid=Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5")), name="TestNode"
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node.register(self.network)
        self.node_guid = node.general.guid

        self.load_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_load_registration_works(self) -> None:
        """Test that loads can register themselves with the network."""
        general = LoadMV.General(
            guid=self.load_guid, name="TestLoad", node=self.node_guid
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        load = LoadMV(general, [presentation])
        load.register(self.network)

        # Verify load is in network
        self.assertIn(self.load_guid, self.network.loads)
        self.assertIs(self.network.loads[self.load_guid], load)

    def test_load_with_full_properties_serializes_correctly(self) -> None:
        """Test that loads with all properties serialize correctly."""
        general = LoadMV.General(
            guid=self.load_guid,
            node=self.node_guid,
            creation_time=123.45,
            mutation_date=10,
            revision_date=20.5,
            variant=True,
            name="FullLoad",
            switch_state=True,
            field_name="TestField",
            failure_frequency=0.01,
            repair_duration=2.5,
            maintenance_frequency=0.1,
            maintenance_duration=4.0,
            maintenance_cancel_duration=1.0,
            not_preferred=True,
            P=100.0,
            Q=50.0,
            unbalanced=True,
            delta=True,
            fp1=0.9,
            fq1=0.8,
            fp2=0.85,
            fq2=0.75,
            fp3=0.88,
            fq3=0.78,
            earthing=1,
            re=0.5,
            xe=0.8,
            harmonics_type="TestHarmonics",
            large_consumers=5,
            generous_consumers=3,
            small_consumers=10,
            harmonic_impedance=True,
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

        load = LoadMV(general, [presentation])
        load.extras.append(Extra(text="foo=bar"))
        load.notes.append(Note(text="Test note"))
        load.register(self.network)

        # Test serialization
        serialized = load.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify key properties are serialized
        self.assertIn("Name:'FullLoad'", serialized)
        self.assertIn("FieldName:'TestField'", serialized)
        self.assertIn("Variant:True", serialized)
        self.assertIn("SwitchState:1", serialized)
        self.assertIn("NotPreferred:True", serialized)
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("RepairDuration:2.5", serialized)
        self.assertIn("MaintenanceFrequency:0.1", serialized)
        self.assertIn("MaintenanceDuration:4.0", serialized)
        self.assertIn("MaintenanceCancelDuration:1.0", serialized)
        self.assertIn("P:100", serialized)
        self.assertIn("Q:50", serialized)
        self.assertIn("Unbalanced:True", serialized)
        self.assertIn("Delta:True", serialized)
        self.assertIn("Fp1:0.9", serialized)
        self.assertIn("Fq1:0.8", serialized)
        self.assertIn("Fp2:0.85", serialized)
        self.assertIn("Fq2:0.75", serialized)
        self.assertIn("Fp3:0.88", serialized)
        self.assertIn("Fq3:0.78", serialized)
        self.assertIn("Earthing:1", serialized)
        self.assertIn("Re:0.5", serialized)
        self.assertIn("Xe:0.8", serialized)
        self.assertIn("HarmonicsType:'TestHarmonics'", serialized)
        self.assertIn("LargeConsumers:5", serialized)
        self.assertIn("GenerousConsumers:3", serialized)
        self.assertIn("SmallConsumers:10", serialized)
        self.assertIn("HarmonicImpedance:True", serialized)

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
        """Test that registering a load with the same GUID overwrites the existing one."""
        general1 = LoadMV.General(
            guid=self.load_guid, name="FirstLoad", node=self.node_guid
        )
        load1 = LoadMV(general1, [ElementPresentation(sheet=self.sheet_guid)])
        load1.register(self.network)

        general2 = LoadMV.General(
            guid=self.load_guid, name="SecondLoad", node=self.node_guid
        )
        load2 = LoadMV(general2, [ElementPresentation(sheet=self.sheet_guid)])
        load2.register(self.network)

        # Should only have one load
        self.assertEqual(len(self.network.loads), 1)
        # Should be the second load
        self.assertEqual(self.network.loads[self.load_guid].general.name, "SecondLoad")

    def test_minimal_load_serialization(self) -> None:
        """Test that minimal loads serialize correctly with only required fields."""
        general = LoadMV.General(
            guid=self.load_guid, name="MinimalLoad", node=self.node_guid
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        load = LoadMV(general, [presentation])
        load.register(self.network)

        serialized = load.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalLoad'", serialized)
        # Default values like Variant:False, SwitchState:False, NotPreferred:False, etc. are skipped in serialization

        # Should not have optional sections
        self.assertNotIn("#Extra", serialized)
        self.assertNotIn("#Note", serialized)

    def test_multiple_presentations_serialize_correctly(self) -> None:
        """Test that loads with multiple presentations serialize correctly."""
        general = LoadMV.General(
            guid=self.load_guid, name="MultiPresLoad", node=self.node_guid
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

        load = LoadMV(general, [pres1, pres2])
        load.register(self.network)

        serialized = load.serialize()

        # Should have two presentations
        self.assertEqual(serialized.count("#Presentation"), 2)
        self.assertIn("Color:$FF0000", serialized)
        self.assertIn("Color:$00FF00", serialized)

    def test_load_with_power_values_serializes_correctly(self) -> None:
        """Test that loads with power values serialize correctly."""
        general = LoadMV.General(
            guid=self.load_guid,
            name="PowerLoad",
            node=self.node_guid,
            P=100.0,
            Q=50.0,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        load = LoadMV(general, [presentation])
        load.register(self.network)

        serialized = load.serialize()
        self.assertIn("P:100", serialized)
        self.assertIn("Q:50", serialized)

    def test_load_with_phase_factors_serializes_correctly(self) -> None:
        """Test that loads with phase factors serialize correctly."""
        general = LoadMV.General(
            guid=self.load_guid,
            name="PhaseFactorLoad",
            node=self.node_guid,
            fp1=0.9,
            fq1=0.8,
            fp2=0.85,
            fq2=0.75,
            fp3=0.88,
            fq3=0.78,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        load = LoadMV(general, [presentation])
        load.register(self.network)

        serialized = load.serialize()
        self.assertIn("Fp1:0.9", serialized)
        self.assertIn("Fq1:0.8", serialized)
        self.assertIn("Fp2:0.85", serialized)
        self.assertIn("Fq2:0.75", serialized)
        self.assertIn("Fp3:0.88", serialized)
        self.assertIn("Fq3:0.78", serialized)

    def test_load_with_unbalanced_delta_serializes_correctly(self) -> None:
        """Test that loads with unbalanced and delta flags serialize correctly."""
        general = LoadMV.General(
            guid=self.load_guid,
            name="UnbalancedDeltaLoad",
            node=self.node_guid,
            unbalanced=True,
            delta=True,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        load = LoadMV(general, [presentation])
        load.register(self.network)

        serialized = load.serialize()
        self.assertIn("Unbalanced:True", serialized)
        self.assertIn("Delta:True", serialized)

    def test_load_with_earthing_properties_serializes_correctly(self) -> None:
        """Test that loads with earthing properties serialize correctly."""
        general = LoadMV.General(
            guid=self.load_guid,
            name="EarthingLoad",
            node=self.node_guid,
            earthing=1,
            re=0.5,
            xe=0.8,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        load = LoadMV(general, [presentation])
        load.register(self.network)

        serialized = load.serialize()
        self.assertIn("Earthing:1", serialized)
        self.assertIn("Re:0.5", serialized)
        self.assertIn("Xe:0.8", serialized)

    def test_load_with_consumer_counts_serializes_correctly(self) -> None:
        """Test that loads with consumer counts serialize correctly."""
        general = LoadMV.General(
            guid=self.load_guid,
            name="ConsumerLoad",
            node=self.node_guid,
            large_consumers=5,
            generous_consumers=3,
            small_consumers=10,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        load = LoadMV(general, [presentation])
        load.register(self.network)

        serialized = load.serialize()
        self.assertIn("LargeConsumers:5", serialized)
        self.assertIn("GenerousConsumers:3", serialized)
        self.assertIn("SmallConsumers:10", serialized)

    def test_load_with_harmonics_serializes_correctly(self) -> None:
        """Test that loads with harmonics properties serialize correctly."""
        general = LoadMV.General(
            guid=self.load_guid,
            name="HarmonicsLoad",
            node=self.node_guid,
            harmonics_type="TestHarmonics",
            harmonic_impedance=True,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        load = LoadMV(general, [presentation])
        load.register(self.network)

        serialized = load.serialize()
        self.assertIn("HarmonicsType:'TestHarmonics'", serialized)
        self.assertIn("HarmonicImpedance:True", serialized)

    def test_load_with_maintenance_properties_serializes_correctly(self) -> None:
        """Test that loads with maintenance properties serialize correctly."""
        general = LoadMV.General(
            guid=self.load_guid,
            name="MaintenanceLoad",
            node=self.node_guid,
            failure_frequency=0.01,
            repair_duration=2.5,
            maintenance_frequency=0.1,
            maintenance_duration=4.0,
            maintenance_cancel_duration=1.0,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        load = LoadMV(general, [presentation])
        load.register(self.network)

        serialized = load.serialize()
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("RepairDuration:2.5", serialized)
        self.assertIn("MaintenanceFrequency:0.1", serialized)
        self.assertIn("MaintenanceDuration:4.0", serialized)
        self.assertIn("MaintenanceCancelDuration:1.0", serialized)

    def test_load_with_pi_control_serializes_correctly(self) -> None:
        """Test that loads with PI control serialize correctly."""
        general = LoadMV.General(
            guid=self.load_guid, name="PIControlLoad", node=self.node_guid
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        pi_control = LoadMV.PIControl(
            input1=1.0,
            output1=0.5,
            input2=2.0,
            output2=1.0,
            measure_field1="Field1",
            measure_field2="Field2",
            measure_field3="Field3",
        )

        load = LoadMV(general, [presentation], pi_control=pi_control)
        load.register(self.network)

        serialized = load.serialize()
        self.assertIn("#P(I)Control", serialized)
        self.assertIn("Input1:1.0", serialized)
        self.assertIn("Output1:0.5", serialized)
        self.assertIn("Input2:2.0", serialized)
        self.assertIn("Output2:1.0", serialized)
        self.assertIn("MeasureField1:'Field1'", serialized)
        self.assertIn("MeasureField2:'Field2'", serialized)
        self.assertIn("MeasureField3:'Field3'", serialized)

    def test_load_with_capacity_restriction_serializes_correctly(self) -> None:
        """Test that loads with capacity restrictions serialize correctly."""
        general = LoadMV.General(
            guid=self.load_guid, name="CapacityLoad", node=self.node_guid
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        capacity = LoadMV.Capacity(
            sort="TestSort",
            begin_date=20230101,
            end_date=20231231,
            begin_time=8.0,
            end_time=18.0,
            p_max=100.0,
        )

        load = LoadMV(general, [presentation], restrictions=capacity)
        load.register(self.network)

        serialized = load.serialize()
        self.assertIn("#Restriction", serialized)
        self.assertIn("Sort:'TestSort'", serialized)
        self.assertIn("BeginDate:20230101", serialized)
        self.assertIn("EndDate:20231231", serialized)
        self.assertIn("BeginTime:8.0", serialized)
        self.assertIn("EndTime:18.0", serialized)
        self.assertIn("Pmax:100.0", serialized)


if __name__ == "__main__":
    unittest.main()
