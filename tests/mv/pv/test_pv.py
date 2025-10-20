"""Tests for TPvMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid
from pyptp.elements.mixins import Extra, Note
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import ElementPresentation, NodePresentation
from pyptp.elements.mv.pv import PVMV
from pyptp.elements.mv.sheet import SheetMV
from pyptp.network_mv import NetworkMV


class TestPvRegistration(unittest.TestCase):
    """Test PV registration and functionality."""

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

        # Create and register a node for the PV
        node = NodeMV(
            NodeMV.General(
                guid=Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5")), name="TestNode"
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node.register(self.network)
        self.node_guid = node.general.guid

        self.pv_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_pv_registration_works(self) -> None:
        """Test that PVs can register themselves with the network."""
        general = PVMV.General(guid=self.pv_guid, name="TestPV", node=self.node_guid)
        inverter = PVMV.Inverter(snom=100.0, unom=0.4)
        presentation = ElementPresentation(sheet=self.sheet_guid)

        pv = PVMV(general, [presentation], inverter)
        pv.register(self.network)

        # Verify PV is in network
        self.assertIn(self.pv_guid, self.network.pvs)
        self.assertIs(self.network.pvs[self.pv_guid], pv)

    def test_pv_with_full_properties_serializes_correctly(self) -> None:
        """Test that PVs with all properties serialize correctly."""
        general = PVMV.General(
            guid=self.pv_guid,
            node=self.node_guid,
            creation_time=123.45,
            mutation_date=10,
            revision_date=20.5,
            variant=True,
            name="FullPV",
            switch_state=True,
            field_name=10.0,
            failure_frequency=0.01,
            repair_duration=2.5,
            maintenance_frequency=0.1,
            maintenance_duration=4.0,
            maintenance_cancel_duration=1.0,
            not_preferred=True,
            scaling=0.8,
            longitude=52.3676,
            latitude=4.9041,
            panel1_pnom=50.0,
            panel1_orientation=180.0,
            panel1_slope=30.0,
            panel2_pnom=25.0,
            panel2_orientation=160.0,
            panel2_slope=25.0,
            panel3_pnom=25.0,
            panel3_orientation=200.0,
            panel3_slope=25.0,
            harmonics_type="TestHarmonics",
        )

        inverter = PVMV.Inverter(
            snom=100.0,
            unom=0.4,
            ik_inom=1.1,  # Back to float - Delphi allows int assignment to double fields
            efficiency_type="TestEfficiency",
            u_off=0.85,
        )

        pu_control = PVMV.PUControl(
            input1=0.9,
            output1=1.0,
            input2=1.1,
            output2=0.5,
            input3=1.2,
            output3=0.0,
        )

        pf_control = PVMV.PFControl(
            input1=49.8,
            output1=1.0,
            input2=50.2,
            output2=0.5,
        )

        pi_control = PVMV.PIControl(
            input1=1.0,
            output1=0.5,
            input2=2.0,
            output2=1.0,
            measure_field1="Field1",
            measure_field2="Field2",
            measure_field3="Field3",
        )

        capacity = PVMV.Capacity(
            sort="TestSort",
            begin_date=20230101,
            end_date=20231231,
            begin_time=8.0,
            end_time=18.0,
            p_max=75.0,
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

        pv = PVMV(
            general,
            [presentation],
            inverter,
            pu_control=pu_control,
            pf_control=pf_control,
            pi_control=pi_control,
            restrictions=capacity,
        )
        pv.extras.append(Extra(text="foo=bar"))
        pv.notes.append(Note(text="Test note"))
        pv.register(self.network)

        # Test serialization
        serialized = pv.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertEqual(serialized.count("#Inverter"), 1)
        self.assertIn("#P(U)Control", serialized)
        self.assertIn("#P(f)Control", serialized)
        self.assertIn("#P(I)Control", serialized)
        self.assertIn("#Restriction", serialized)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify general properties
        self.assertIn("Name:'FullPV'", serialized)
        self.assertIn("Variant:True", serialized)
        self.assertIn("SwitchState:1", serialized)
        self.assertIn("NotPreferred:True", serialized)
        self.assertIn("FieldName:10", serialized)
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("RepairDuration:2.5", serialized)
        self.assertIn("MaintenanceFrequency:0.1", serialized)
        self.assertIn("MaintenanceDuration:4.0", serialized)
        self.assertIn("MaintenanceCancelDuration:1.0", serialized)
        self.assertIn("Scaling:0.8", serialized)
        self.assertIn("Longitude:52.3676", serialized)
        self.assertIn("Latitude:4.9041", serialized)
        self.assertIn("Panel1Pnom:50", serialized)
        self.assertIn("Panel1Orientation:180", serialized)
        self.assertIn("Panel1Slope:30", serialized)
        self.assertIn("Panel2Pnom:25", serialized)
        self.assertIn("Panel2Orientation:160", serialized)
        self.assertIn("Panel2Slope:25", serialized)
        self.assertIn("Panel3Pnom:25", serialized)
        self.assertIn("Panel3Orientation:200", serialized)
        self.assertIn("Panel3Slope:25", serialized)
        self.assertIn("HarmonicsType:'TestHarmonics'", serialized)

        # Verify node reference
        self.assertIn(f"Node:'{{{str(self.node_guid).upper()}}}'", serialized)

        # Verify inverter properties
        self.assertIn("Snom:100", serialized)
        self.assertIn("Unom:0.4", serialized)
        self.assertIn("Ik/Inom:1.1", serialized)
        self.assertIn("EfficiencyType:'TestEfficiency'", serialized)
        self.assertIn("Uoff:0.85", serialized)

        # Verify control properties
        self.assertIn("Input1:0.9", serialized)
        self.assertIn("Output1:1.0", serialized)
        self.assertIn("Input2:1.1", serialized)
        self.assertIn("Output2:0.5", serialized)
        self.assertIn("Input3:1.2", serialized)

        # Verify capacity restriction
        self.assertIn("Sort:'TestSort'", serialized)
        self.assertIn("BeginDate:20230101", serialized)
        self.assertIn("EndDate:20231231", serialized)
        self.assertIn("BeginTime:8.0", serialized)
        self.assertIn("EndTime:18.0", serialized)
        self.assertIn("Pmax:75.0", serialized)

        # Verify extras and notes
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a PV with the same GUID overwrites the existing one."""
        general1 = PVMV.General(guid=self.pv_guid, name="FirstPV", node=self.node_guid)
        inverter1 = PVMV.Inverter(snom=50.0)
        pv1 = PVMV(general1, [ElementPresentation(sheet=self.sheet_guid)], inverter1)
        pv1.register(self.network)

        general2 = PVMV.General(guid=self.pv_guid, name="SecondPV", node=self.node_guid)
        inverter2 = PVMV.Inverter(snom=100.0)
        pv2 = PVMV(general2, [ElementPresentation(sheet=self.sheet_guid)], inverter2)
        pv2.register(self.network)

        # Should only have one PV
        self.assertEqual(len(self.network.pvs), 1)
        # Should be the second PV
        self.assertEqual(self.network.pvs[self.pv_guid].general.name, "SecondPV")

    def test_minimal_pv_serialization(self) -> None:
        """Test that minimal PVs serialize correctly with only required fields."""
        general = PVMV.General(guid=self.pv_guid, name="MinimalPV", node=self.node_guid)
        inverter = PVMV.Inverter()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        pv = PVMV(general, [presentation], inverter)
        pv.register(self.network)

        serialized = pv.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertEqual(serialized.count("#Inverter"), 1)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalPV'", serialized)
        # Default values like Variant:False, SwitchState:False, NotPreferred:False, etc. are skipped in serialization

        # Should have default inverter properties
        self.assertIn("Snom:12.5", serialized)
        # Default values like Unom:0, Ik/Inom:0, Uoff:0 are skipped in serialization

        # Should not have optional sections
        self.assertNotIn("#P(U)Control", serialized)
        self.assertNotIn("#P(f)Control", serialized)
        self.assertNotIn("#P(I)Control", serialized)
        self.assertNotIn("#Restriction", serialized)

    def test_pv_with_solar_panels_serializes_correctly(self) -> None:
        """Test that PVs with solar panel properties serialize correctly."""
        general = PVMV.General(
            guid=self.pv_guid,
            name="SolarPV",
            node=self.node_guid,
            panel1_pnom=50.0,
            panel1_orientation=180.0,
            panel1_slope=30.0,
            panel2_pnom=25.0,
            panel2_orientation=160.0,
            panel2_slope=25.0,
            panel3_pnom=25.0,
            panel3_orientation=200.0,
            panel3_slope=25.0,
        )
        inverter = PVMV.Inverter(snom=100.0)
        presentation = ElementPresentation(sheet=self.sheet_guid)

        pv = PVMV(general, [presentation], inverter)
        pv.register(self.network)

        serialized = pv.serialize()
        self.assertIn("Panel1Pnom:50", serialized)
        self.assertIn("Panel1Orientation:180", serialized)
        self.assertIn("Panel1Slope:30", serialized)
        self.assertIn("Panel2Pnom:25", serialized)
        self.assertIn("Panel2Orientation:160", serialized)
        self.assertIn("Panel2Slope:25", serialized)
        self.assertIn("Panel3Pnom:25", serialized)
        self.assertIn("Panel3Orientation:200", serialized)
        self.assertIn("Panel3Slope:25", serialized)

    def test_pv_with_location_serializes_correctly(self) -> None:
        """Test that PVs with location properties serialize correctly."""
        general = PVMV.General(
            guid=self.pv_guid,
            name="LocationPV",
            node=self.node_guid,
            longitude=52.3676,
            latitude=4.9041,
        )
        inverter = PVMV.Inverter(snom=100.0)
        presentation = ElementPresentation(sheet=self.sheet_guid)

        pv = PVMV(general, [presentation], inverter)
        pv.register(self.network)

        serialized = pv.serialize()
        self.assertIn("Longitude:52.3676", serialized)
        self.assertIn("Latitude:4.9041", serialized)

    def test_pv_with_inverter_properties_serializes_correctly(self) -> None:
        """Test that PVs with inverter properties serialize correctly."""
        general = PVMV.General(
            guid=self.pv_guid, name="InverterPV", node=self.node_guid
        )
        inverter = PVMV.Inverter(
            snom=100.0,
            unom=0.4,
            ik_inom=1.1,  # Back to float - Delphi allows int assignment to double fields
            efficiency_type="TestEfficiency",
            u_off=0.85,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        pv = PVMV(general, [presentation], inverter)
        pv.register(self.network)

        serialized = pv.serialize()
        self.assertIn("Snom:100", serialized)
        self.assertIn("Unom:0.4", serialized)
        self.assertIn("Ik/Inom:1.1", serialized)
        self.assertIn("EfficiencyType:'TestEfficiency'", serialized)
        self.assertIn("Uoff:0.85", serialized)

    def test_pv_with_pu_control_serializes_correctly(self) -> None:
        """Test that PVs with P(U) control serialize correctly."""
        general = PVMV.General(
            guid=self.pv_guid, name="PUControlPV", node=self.node_guid
        )
        inverter = PVMV.Inverter(snom=100.0)
        pu_control = PVMV.PUControl(
            input1=0.9,
            output1=1.0,
            input2=1.1,
            output2=0.5,
            input3=1.2,
            output3=0.0,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        pv = PVMV(general, [presentation], inverter, pu_control=pu_control)
        pv.register(self.network)

        serialized = pv.serialize()
        self.assertIn("#P(U)Control", serialized)
        self.assertIn("Input1:0.9", serialized)
        self.assertIn("Output1:1.0", serialized)
        self.assertIn("Input2:1.1", serialized)
        self.assertIn("Output2:0.5", serialized)
        self.assertIn("Input3:1.2", serialized)

    def test_pv_with_pi_control_serializes_correctly(self) -> None:
        """Test that PVs with P(I) control serialize correctly."""
        general = PVMV.General(
            guid=self.pv_guid, name="PIControlPV", node=self.node_guid
        )
        inverter = PVMV.Inverter(snom=100.0)
        pi_control = PVMV.PIControl(
            input1=1.0,
            output1=0.5,
            input2=2.0,
            output2=1.0,
            measure_field1="Field1",
            measure_field2="Field2",
            measure_field3="Field3",
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        pv = PVMV(general, [presentation], inverter, pi_control=pi_control)
        pv.register(self.network)

        serialized = pv.serialize()
        self.assertIn("#P(I)Control", serialized)
        self.assertIn("Input1:1.0", serialized)
        self.assertIn("Output1:0.5", serialized)
        self.assertIn("Input2:2.0", serialized)
        self.assertIn("Output2:1.0", serialized)
        self.assertIn("MeasureField1:'Field1'", serialized)
        self.assertIn("MeasureField2:'Field2'", serialized)
        self.assertIn("MeasureField3:'Field3'", serialized)

    def test_pv_with_capacity_restriction_serializes_correctly(self) -> None:
        """Test that PVs with capacity restrictions serialize correctly."""
        general = PVMV.General(
            guid=self.pv_guid, name="CapacityPV", node=self.node_guid
        )
        inverter = PVMV.Inverter(snom=100.0)
        capacity = PVMV.Capacity(
            sort="TestSort",
            begin_date=20230101,
            end_date=20231231,
            begin_time=8.0,
            end_time=18.0,
            p_max=75.0,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        pv = PVMV(general, [presentation], inverter, restrictions=capacity)
        pv.register(self.network)

        serialized = pv.serialize()
        self.assertIn("#Restriction", serialized)
        self.assertIn("Sort:'TestSort'", serialized)
        self.assertIn("BeginDate:20230101", serialized)
        self.assertIn("EndDate:20231231", serialized)
        self.assertIn("BeginTime:8.0", serialized)
        self.assertIn("EndTime:18.0", serialized)
        self.assertIn("Pmax:75.0", serialized)


if __name__ == "__main__":
    unittest.main()
