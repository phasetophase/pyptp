"""Tests for TTransformerMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid
from pyptp.elements.mixins import Extra, Note
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import BranchPresentation, NodePresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.elements.mv.transformer import TransformerMV
from pyptp.network_mv import NetworkMV


class TestTransformerRegistration(unittest.TestCase):
    """Test transformer registration and functionality."""

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

        # Create and register two nodes for the transformer
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
                guid=Guid(UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")),
                name="TestNode2",
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node2.register(self.network)
        self.node2_guid = node2.general.guid

        self.transformer_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_transformer_registration_works(self) -> None:
        """Test that transformers can register themselves with the network."""
        general = TransformerMV.General(
            guid=self.transformer_guid,
            name="TestTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        transformer_type = TransformerMV.TransformerType(
            short_name="TestType", snom=1000.0
        )
        presentation = BranchPresentation(sheet=self.sheet_guid)

        transformer = TransformerMV(general, [presentation], transformer_type)
        transformer.register(self.network)

        # Verify transformer is in network
        self.assertIn(self.transformer_guid, self.network.transformers)
        self.assertIs(self.network.transformers[self.transformer_guid], transformer)

    def test_transformer_with_full_properties_serializes_correctly(self) -> None:
        """Test that transformers with all properties serialize correctly."""
        general = TransformerMV.General(
            guid=self.transformer_guid,
            creation_time=123.45,
            mutation_date=10,
            revision_date=20,
            variant=True,
            name="FullTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
            switch_state1=1,
            switch_state2=0,
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
            loadrate_max=100.0,
            loadrate_max_winter=120.0,
            loadrate_max_emergency=150.0,
            loadrate_max_emergency_winter=180.0,
            type="FullType",
            snom=1000.0,
            step_up=True,
            clock_number=11,
            phase_shift=30.0,
            earthing1=1,
            re1=0.1,
            xe1=0.2,
            earthing2=2,
            re2=0.15,
            xe2=0.25,
            tap_position=3.5,
        )

        transformer_type = TransformerMV.TransformerType(
            short_name="FullType",
            snom=1000.0,
            unom1=20.0,
            unom2=0.4,
            Uk=4.0,
            Pk=10.0,
            Po=2.0,
            Io=0.5,
            R0=0.1,
            Z0=0.2,
            side_z0=1,
            Ik2s=25000.0,
            C1=0.01,
            C2=0.02,
            C12=0.015,
            winding_connection1="Dyn",
            winding_connection2="yn",
            clock_number=11,
            tap_side=1,
            tap_size=2.5,
            tap_min=-5,
            tap_nom=0,
            tap_max=5,
            ki=1.2,
            tau=0.1,
        )

        voltage_control = TransformerMV.VoltageControl(
            own_control=True,
            control_status=1,
            measure_side=2,
            set_point=1.05,
            dead_band=0.02,
            control_sort=1,
            rc=0.5,
            xc=1.5,
            compounding_at_generation=False,
            pmin1=-50,
            umin1=0.95,
            pmax1=50,
            umax1=1.05,
            pmin2=-25,
            umin2=0.98,
            pmax2=25,
            umax2=1.02,
        )

        dynamics = TransformerMV.Dynamics(
            non_linear_model=True,
            knee_flux_leg1=1.1,
            knee_flux_leg2=1.05,
            knee_flux_leg3=1.08,
            magnetizing_inductance_ratio_leg1=800.0,
            magnetizing_inductance_ratio_leg2=900.0,
            magnetizing_inductance_ratio_leg3=850.0,
            remanent_flux=True,
            remanent_flux_leg1=0.6,
            remanent_flux_leg2=0.65,
            remanent_flux_leg3=0.75,
        )

        presentation = BranchPresentation(
            sheet=self.sheet_guid,
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
            strings2_x=30,
            strings2_y=40,
            mid_strings_x=50,
            mid_strings_y=60,
            fault_strings_x=70,
            fault_strings_y=80,
            note_x=90,
            note_y=100,
            flag_flipped1=False,
            flag_flipped2=True,
            first_corners=[(100, 100), (200, 200)],
            second_corners=[(300, 300), (400, 400)],
        )

        transformer = TransformerMV(
            general, [presentation], transformer_type, voltage_control, dynamics
        )
        transformer.extras.append(Extra(text="foo=bar"))
        transformer.notes.append(Note(text="Test note"))
        transformer.register(self.network)

        # Test serialization
        serialized = transformer.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertEqual(serialized.count("#VoltageControl"), 1)
        self.assertEqual(serialized.count("#TransformerType"), 1)
        self.assertEqual(serialized.count("#Dynamics"), 1)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify general properties
        self.assertIn("Variant:True", serialized)
        self.assertIn("Name:'FullTransformer'", serialized)
        self.assertIn("SwitchState1:1", serialized)
        self.assertIn("SwitchState2:0", serialized)
        self.assertIn("FieldName1:'Field1'", serialized)
        self.assertIn("FieldName2:'Field2'", serialized)
        self.assertIn("SubnetBorder:True", serialized)
        self.assertIn("Source1:'Source1'", serialized)
        self.assertIn("Source2:'Source2'", serialized)
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("RepairDuration:2.5", serialized)
        self.assertIn("LoadrateMax:100", serialized)
        self.assertIn("LoadrateMaxWinter:120", serialized)
        self.assertIn("TransformerType:'FullType'", serialized)
        self.assertIn("Snom:1000", serialized)
        self.assertIn("StepUp:True", serialized)
        self.assertIn("ClockNumber:11", serialized)
        self.assertIn("PhaseShift:30", serialized)
        self.assertIn("Earthing1:1", serialized)
        self.assertIn("Re1:0.1", serialized)
        self.assertIn("Xe1:0.2", serialized)
        self.assertIn("Earthing2:2", serialized)
        self.assertIn("Re2:0.15", serialized)
        self.assertIn("Xe2:0.25", serialized)
        self.assertIn("TapPosition:3.5", serialized)

        # Verify node references
        self.assertIn(f"Node1:'{{{str(self.node1_guid).upper()}}}'", serialized)
        self.assertIn(f"Node2:'{{{str(self.node2_guid).upper()}}}'", serialized)

        # Verify voltage control properties
        self.assertIn("OwnControl:True", serialized)
        self.assertIn("ControlStatus:1", serialized)
        self.assertIn("MeasureSide:2", serialized)
        self.assertIn("SetPoint:1.05", serialized)
        self.assertIn("DeadBand:0.02", serialized)
        self.assertIn("ControlSort:1", serialized)
        self.assertIn("Rc:0.5", serialized)
        self.assertIn("Xc:1.5", serialized)
        self.assertIn("CompoundingAtGeneration:False", serialized)
        self.assertIn("Pmin1:-50", serialized)
        self.assertIn("Umin1:0.95", serialized)
        self.assertIn("Pmax1:50", serialized)
        self.assertIn("Umax1:1.05", serialized)

        # Verify transformer type properties
        self.assertIn("ShortName:'FullType'", serialized)
        self.assertIn("Snom:1000", serialized)
        self.assertIn("Unom1:20", serialized)
        self.assertIn("Unom2:0.4", serialized)
        self.assertIn("Uk:4", serialized)
        self.assertIn("Pk:10", serialized)
        self.assertIn("Po:2", serialized)
        self.assertIn("Io:0.5", serialized)
        self.assertIn("R0:0.1", serialized)
        self.assertIn("Z0:0.2", serialized)
        self.assertIn("Side_Z0:1", serialized)
        self.assertIn("Ik2s:25000", serialized)
        self.assertIn("C1:0.01", serialized)
        self.assertIn("C2:0.02", serialized)
        self.assertIn("C12:0.015", serialized)
        self.assertIn("WindingConnection1:'Dyn'", serialized)
        self.assertIn("WindingConnection2:'yn'", serialized)
        self.assertIn("TapSide:1", serialized)
        self.assertIn("TapSize:2.5", serialized)
        self.assertIn("TapMin:-5", serialized)
        self.assertIn("TapNom:0", serialized)
        self.assertIn("TapMax:5", serialized)
        self.assertIn("Ki:1.2", serialized)
        self.assertIn("Tau:0.1", serialized)

        # Verify dynamics properties
        self.assertIn("NonlinearModel:True", serialized)
        self.assertIn("KneeFluxLeg1:1.1", serialized)
        self.assertIn("KneeFluxLeg2:1.05", serialized)
        self.assertIn("KneeFluxLeg3:1.08", serialized)
        self.assertIn("MagnetizingInductanceRatioLeg1:800", serialized)
        self.assertIn("RemanentFlux:True", serialized)
        self.assertIn("RemanentFluxLeg1:0.6", serialized)

        # Verify extras and notes
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a transformer with the same GUID overwrites the existing one."""
        general1 = TransformerMV.General(
            guid=self.transformer_guid,
            name="FirstTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        type1 = TransformerMV.TransformerType(short_name="Type1", snom=500.0)
        transformer1 = TransformerMV(
            general1, [BranchPresentation(sheet=self.sheet_guid)], type1
        )
        transformer1.register(self.network)

        general2 = TransformerMV.General(
            guid=self.transformer_guid,
            name="SecondTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        type2 = TransformerMV.TransformerType(short_name="Type2", snom=1000.0)
        transformer2 = TransformerMV(
            general2, [BranchPresentation(sheet=self.sheet_guid)], type2
        )
        transformer2.register(self.network)

        # Should only have one transformer
        self.assertEqual(len(self.network.transformers), 1)
        # Should be the second transformer
        self.assertEqual(
            self.network.transformers[self.transformer_guid].general.name,
            "SecondTransformer",
        )

    def test_minimal_transformer_serialization(self) -> None:
        """Test that minimal transformers serialize correctly with only required fields."""
        general = TransformerMV.General(
            guid=self.transformer_guid,
            name="MinimalTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        transformer_type = TransformerMV.TransformerType(short_name="MinimalType")
        presentation = BranchPresentation(sheet=self.sheet_guid)

        transformer = TransformerMV(general, [presentation], transformer_type)
        transformer.register(self.network)

        serialized = transformer.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertEqual(serialized.count("#TransformerType"), 1)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalTransformer'", serialized)
        self.assertIn("SwitchState1:1", serialized)
        self.assertIn("SwitchState2:1", serialized)
        self.assertIn("ClockNumber:0", serialized)
        self.assertIn("Earthing1:0", serialized)
        self.assertIn("Earthing2:0", serialized)
        self.assertIn("TapPosition:0", serialized)

        # Should have transformer type
        self.assertIn("ShortName:'MinimalType'", serialized)

        # Should not have voltage control or dynamics
        self.assertNotIn("#VoltageControl", serialized)
        self.assertNotIn("#Dynamics", serialized)

    def test_transformer_with_voltage_control_only(self) -> None:
        """Test that transformers with only voltage control serialize correctly."""
        general = TransformerMV.General(
            guid=self.transformer_guid,
            name="VoltageControlTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        transformer_type = TransformerMV.TransformerType(short_name="VCType")
        voltage_control = TransformerMV.VoltageControl(
            own_control=True,
            control_status=1,
            measure_side=2,
            set_point=1.05,
            dead_band=0.02,
        )
        presentation = BranchPresentation(sheet=self.sheet_guid)

        transformer = TransformerMV(
            general, [presentation], transformer_type, voltage_control
        )
        transformer.register(self.network)

        serialized = transformer.serialize()
        self.assertIn("#VoltageControl", serialized)
        self.assertIn("OwnControl:True", serialized)
        self.assertIn("ControlStatus:1", serialized)
        self.assertIn("MeasureSide:2", serialized)
        self.assertIn("SetPoint:1.05", serialized)
        self.assertIn("DeadBand:0.02", serialized)
        # Should have defaults
        self.assertIn("CompoundingAtGeneration:True", serialized)
        self.assertIn("Pmin1:-100", serialized)
        self.assertIn("Pmax1:100", serialized)

    def test_transformer_with_dynamics_only(self) -> None:
        """Test that transformers with only dynamics serialize correctly."""
        general = TransformerMV.General(
            guid=self.transformer_guid,
            name="DynamicsTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        transformer_type = TransformerMV.TransformerType(short_name="DynType")
        dynamics = TransformerMV.Dynamics(non_linear_model=True)
        presentation = BranchPresentation(sheet=self.sheet_guid)

        transformer = TransformerMV(
            general, [presentation], transformer_type, None, dynamics
        )
        transformer.register(self.network)

        serialized = transformer.serialize()
        self.assertIn("#Dynamics", serialized)
        self.assertIn("NonlinearModel:True", serialized)
        # Should have defaults
        self.assertIn("KneeFluxLeg1:1.04", serialized)
        self.assertIn("MagnetizingInductanceRatioLeg1:1000", serialized)
        self.assertIn("RemanentFluxLeg1:0.7", serialized)

    def test_transformer_electrical_properties_complete(self) -> None:
        """Test that all electrical properties are serialized correctly."""
        general = TransformerMV.General(
            guid=self.transformer_guid,
            name="ElectricalTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        transformer_type = TransformerMV.TransformerType(
            short_name="ElectricalType",
            snom=1000.0,
            unom1=20.0,
            unom2=0.4,
            Uk=4.0,
            Pk=10.0,
            Po=2.0,
            Io=0.5,
            R0=0.1,
            Z0=0.2,
            side_z0=1,
            Ik2s=25000.0,
            C1=0.01,
            C2=0.02,
            C12=0.015,
        )
        presentation = BranchPresentation(sheet=self.sheet_guid)

        transformer = TransformerMV(general, [presentation], transformer_type)
        transformer.register(self.network)

        serialized = transformer.serialize()
        self.assertIn("Snom:1000", serialized)
        self.assertIn("Unom1:20", serialized)
        self.assertIn("Unom2:0.4", serialized)
        self.assertIn("Uk:4", serialized)
        self.assertIn("Pk:10", serialized)
        self.assertIn("Po:2", serialized)
        self.assertIn("Io:0.5", serialized)
        self.assertIn("R0:0.1", serialized)
        self.assertIn("Z0:0.2", serialized)
        self.assertIn("Side_Z0:1", serialized)
        self.assertIn("Ik2s:25000", serialized)
        self.assertIn("C1:0.01", serialized)
        self.assertIn("C2:0.02", serialized)
        self.assertIn("C12:0.015", serialized)

    def test_transformer_maintenance_properties(self) -> None:
        """Test that maintenance and reliability properties are serialized correctly."""
        general = TransformerMV.General(
            guid=self.transformer_guid,
            name="MaintenanceTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
            failure_frequency=0.01,
            repair_duration=2.5,
            maintenance_frequency=0.1,
            maintenance_duration=4.0,
            maintenance_cancel_duration=1.0,
        )
        transformer_type = TransformerMV.TransformerType(short_name="MaintenanceType")
        presentation = BranchPresentation(sheet=self.sheet_guid)

        transformer = TransformerMV(general, [presentation], transformer_type)
        transformer.register(self.network)

        serialized = transformer.serialize()
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("RepairDuration:2.5", serialized)
        self.assertIn("MaintenanceFrequency:0.1", serialized)
        self.assertIn("MaintenanceDuration:4", serialized)
        self.assertIn("MaintenanceCancelDuration:1", serialized)

    def test_transformer_section_order_correct(self) -> None:
        """Test that sections are serialized in the correct order matching Delphi."""
        general = TransformerMV.General(
            guid=self.transformer_guid,
            name="OrderTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        transformer_type = TransformerMV.TransformerType(short_name="OrderType")
        voltage_control = TransformerMV.VoltageControl()
        dynamics = TransformerMV.Dynamics()
        presentation = BranchPresentation(sheet=self.sheet_guid)

        transformer = TransformerMV(
            general, [presentation], transformer_type, voltage_control, dynamics
        )
        transformer.register(self.network)

        serialized = transformer.serialize()
        lines = serialized.split("\n")

        # Find positions of each section
        general_pos = next(
            i for i, line in enumerate(lines) if line.startswith("#General")
        )
        voltage_control_pos = next(
            i for i, line in enumerate(lines) if line.startswith("#VoltageControl")
        )
        transformer_type_pos = next(
            i for i, line in enumerate(lines) if line.startswith("#TransformerType")
        )
        dynamics_pos = next(
            i for i, line in enumerate(lines) if line.startswith("#Dynamics")
        )

        # Verify correct order: General -> VoltageControl -> TransformerType -> Dynamics
        self.assertLess(general_pos, voltage_control_pos)
        self.assertLess(voltage_control_pos, transformer_type_pos)
        self.assertLess(transformer_type_pos, dynamics_pos)


if __name__ == "__main__":
    unittest.main()
