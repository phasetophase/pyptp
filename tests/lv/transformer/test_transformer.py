"""Tests for TTransformerLS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid, encode_guid
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import BranchPresentation, NodePresentation
from pyptp.elements.lv.sheet import SheetLV
from pyptp.elements.lv.transformer import TransformerLV
from pyptp.elements.mixins import Extra, Note
from pyptp.network_lv import NetworkLV


class TestTransformerRegistration(unittest.TestCase):
    """Test transformer registration and functionality."""

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

        # Create and register nodes
        node1 = NodeLV(
            NodeLV.General(
                guid=Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5")), name="Node1"
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node1.register(self.network)
        self.node1_guid = node1.general.guid

        node2 = NodeLV(
            NodeLV.General(
                guid=Guid(UUID("b8b53fef-12b8-4c98-96f2-0da060b51000")), name="Node2"
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node2.register(self.network)
        self.node2_guid = node2.general.guid

        self.transformer_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_transformer_registration_works(self) -> None:
        """Test that transformers can register themselves with the network."""
        general = TransformerLV.General(
            guid=self.transformer_guid,
            name="TestTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        transformer_type = TransformerLV.TransformerType(
            short_name="TestType", snom=100.0, unom1=10.0, unom2=0.4
        )
        presentation = BranchPresentation(sheet=self.sheet_guid)

        transformer = TransformerLV(general, [presentation], transformer_type)
        transformer.register(self.network)

        # Verify transformer is in network
        self.assertIn(self.transformer_guid, self.network.transformers)
        self.assertIs(self.network.transformers[self.transformer_guid], transformer)

    def test_transformer_with_full_properties_serializes_correctly(self) -> None:
        """Test that transformers with all properties serialize correctly."""
        general = TransformerLV.General(
            guid=self.transformer_guid,
            creation_time=123.45,
            mutation_date=10,
            revision_date=20.5,
            node1=self.node1_guid,
            node2=self.node2_guid,
            name="FullTransformer",
            switch_state1_L1=False,
            switch_state1_L2=True,
            switch_state1_L3=False,
            switch_state1_N=True,
            switch_state1_PE=False,
            switch_state2_L1=True,
            switch_state2_L2=False,
            switch_state2_L3=True,
            switch_state2_N=False,
            switch_state2_PE=True,
            field_name1="Field1",
            field_name2="Field2",
            failure_frequency=0.01,
            type="Distribution",
            switch_state_N_PE=True,
            switch_state_PE_e=True,
            re=5.0,
            tap_position=1.0,
            clock_number=6,
            loadrate_max=0.8,
        )

        transformer_type = TransformerLV.TransformerType(
            short_name="DistType",
            snom=200.0,
            unom1=10.0,
            unom2=0.4,
            Uk=4.5,
            Pk=2.5,
            Po=0.5,
            Io=1.0,
            R0=0.1,
            Z0=0.2,
            ik2s=5.0,
            winding_connection1="D",
            winding_connection2="YN",
            clock_number=6,
            tap_side=1,
            tap_size=0.25,
            tap_min=-2,
            tap_nom=0,
            tap_max=2,
            ki=1.0,
            tau=0.1,
            controllable=True,
        )

        voltage_control = TransformerLV.VoltageControl(
            own_control=True,
            control_status=1,
            measure_side=3,
            control_node="ControlNode1",
            setpoint=0.4,
            deadband=0.02,
            control_sort=1,
            Rc=0.1,
            Xc=0.2,
            compounding_at_generation=False,
            p_min1=-100,
            u_min1=0.38,
            p_max1=100,
            u_max1=0.42,
        )

        presentation = BranchPresentation(
            sheet=self.sheet_guid,
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

        transformer = TransformerLV(
            general, [presentation], transformer_type, voltage_control
        )
        transformer.extras.append(Extra(text="foo=bar"))
        transformer.notes.append(Note(text="Test note"))
        transformer.register(self.network)

        # Test serialization
        serialized = transformer.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#TransformerType", serialized)
        self.assertIn("#VoltageControl", serialized)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify key general properties are serialized
        self.assertIn("Name:'FullTransformer'", serialized)
        self.assertIn("FieldName1:'Field1'", serialized)
        self.assertIn("FieldName2:'Field2'", serialized)
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("TransformerType:'Distribution'", serialized)
        self.assertIn("SwitchState_N_PE:True", serialized)
        self.assertIn("SwitchState_PE_e:True", serialized)
        self.assertIn("Re:5.0", serialized)
        self.assertIn("TapPosition:1.0", serialized)
        self.assertIn("ClockNumber:6", serialized)
        self.assertIn("LoadrateMax:0.8", serialized)

        # Verify transformer type properties
        self.assertIn("ShortName:'DistType'", serialized)
        self.assertIn("Snom:200.0", serialized)
        self.assertIn("Unom1:10.0", serialized)
        self.assertIn("Unom2:0.4", serialized)
        self.assertIn("Uk:4.5", serialized)
        self.assertIn("Pk:2.5", serialized)
        self.assertIn("Po:0.5", serialized)
        self.assertIn("Io:1.0", serialized)
        self.assertIn("R0:0.1", serialized)
        self.assertIn("Z0:0.2", serialized)
        self.assertIn("Ik2s:5.0", serialized)
        self.assertIn("WindingConnection1:'D'", serialized)
        self.assertIn("WindingConnection2:'YN'", serialized)
        self.assertIn("TapSide:1", serialized)
        self.assertIn("TapSize:0.25", serialized)
        self.assertIn("TapMin:-2", serialized)
        self.assertIn("TapNom:0", serialized)
        self.assertIn("TapMax:2", serialized)
        self.assertIn("Ki:1.0", serialized)
        self.assertIn("Tau:0.1", serialized)
        self.assertIn("Controllable:True", serialized)

        # Verify voltage control properties
        self.assertIn("OwnControl:True", serialized)
        self.assertIn("ControlStatus:1", serialized)
        self.assertIn("MeasureSide:3", serialized)
        self.assertIn("ControlNode:'ControlNode1'", serialized)
        self.assertIn("Setpoint:0.4", serialized)
        self.assertIn("Deadband:0.02", serialized)
        self.assertIn("ControlSort:1", serialized)
        self.assertIn("Rc:0.1", serialized)
        self.assertIn("Xc:0.2", serialized)
        self.assertIn("CompoundingAtGeneration:False", serialized)
        self.assertIn("Pmin1:-100", serialized)
        self.assertIn("Umin1:0.38", serialized)
        self.assertIn("Pmax1:100", serialized)
        self.assertIn("Umax1:0.42", serialized)

        # Verify presentation properties
        self.assertIn(f"Sheet:{encode_guid(self.sheet_guid)}", serialized)
        self.assertIn("Color:$00FF00", serialized)
        self.assertIn("TextColor:$FF0000", serialized)

        # Verify extras and notes
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a transformer with the same GUID overwrites the existing one."""
        general1 = TransformerLV.General(
            guid=self.transformer_guid,
            name="FirstTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        transformer1 = TransformerLV(
            general1,
            [BranchPresentation(sheet=self.sheet_guid)],
            TransformerLV.TransformerType(),
        )
        transformer1.register(self.network)

        general2 = TransformerLV.General(
            guid=self.transformer_guid,
            name="SecondTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        transformer2 = TransformerLV(
            general2,
            [BranchPresentation(sheet=self.sheet_guid)],
            TransformerLV.TransformerType(),
        )
        transformer2.register(self.network)

        # Should only have one transformer
        self.assertEqual(len(self.network.transformers), 1)
        # Should be the second transformer
        self.assertEqual(
            self.network.transformers[self.transformer_guid].general.name,
            "SecondTransformer",
        )

    def test_transformer_without_voltage_control_serializes_correctly(self) -> None:
        """Test that transformers without voltage control serialize correctly."""
        general = TransformerLV.General(
            guid=self.transformer_guid,
            name="SimpleTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        transformer_type = TransformerLV.TransformerType(
            short_name="SimpleType", snom=100.0, unom1=10.0, unom2=0.4
        )
        presentation = BranchPresentation(sheet=self.sheet_guid)

        transformer = TransformerLV(general, [presentation], transformer_type)
        transformer.register(self.network)

        serialized = transformer.serialize()

        # Should not have voltage control section
        self.assertNotIn("#VoltageControl", serialized)

        # Should have other sections
        self.assertIn("#General", serialized)
        self.assertIn("#TransformerType", serialized)
        self.assertIn("#Presentation", serialized)

    def test_minimal_transformer_serialization(self) -> None:
        """Test that minimal transformers serialize correctly with only required fields."""
        general = TransformerLV.General(
            guid=self.transformer_guid,
            name="MinimalTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        transformer_type = TransformerLV.TransformerType()
        presentation = BranchPresentation(sheet=self.sheet_guid)

        transformer = TransformerLV(general, [presentation], transformer_type)
        transformer.register(self.network)

        serialized = transformer.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#TransformerType", serialized)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalTransformer'", serialized)
        self.assertIn("SwitchState1_L1:True", serialized)  # Default values
        self.assertIn("SwitchState2_PE:True", serialized)
        self.assertIn("TapPosition:0", serialized)  # Default value

        # Should not have voltage control section
        self.assertNotIn("#VoltageControl", serialized)

        # Should not have optional sections
        self.assertNotIn("#Extra", serialized)
        self.assertNotIn("#Note", serialized)

    def test_multiple_presentations_serialize_correctly(self) -> None:
        """Test that transformers with multiple presentations serialize correctly."""
        general = TransformerLV.General(
            guid=self.transformer_guid,
            name="MultiPresTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        transformer_type = TransformerLV.TransformerType()

        pres1 = BranchPresentation(sheet=self.sheet_guid, color=DelphiColor("$FF0000"))
        pres2 = BranchPresentation(sheet=self.sheet_guid, color=DelphiColor("$00FF00"))

        transformer = TransformerLV(general, [pres1, pres2], transformer_type)
        transformer.register(self.network)

        serialized = transformer.serialize()

        # Should have two presentations
        self.assertEqual(serialized.count("#Presentation"), 2)
        self.assertIn("Color:$FF0000", serialized)
        self.assertIn("Color:$00FF00", serialized)

    def test_transformer_with_tap_settings_serializes_correctly(self) -> None:
        """Test that transformers with tap settings serialize correctly."""
        general = TransformerLV.General(
            guid=self.transformer_guid,
            name="TapTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
            tap_position=2.0,
            clock_number=11,
        )
        transformer_type = TransformerLV.TransformerType(
            short_name="TapType",
            tap_side=2,
            tap_size=0.5,
            tap_min=-5,
            tap_nom=0,
            tap_max=5,
        )
        presentation = BranchPresentation(sheet=self.sheet_guid)

        transformer = TransformerLV(general, [presentation], transformer_type)
        transformer.register(self.network)

        serialized = transformer.serialize()

        # Verify tap properties are serialized
        self.assertIn("TapPosition:2.0", serialized)
        self.assertIn("ClockNumber:11", serialized)
        self.assertIn("TapSide:2", serialized)
        self.assertIn("TapSize:0.5", serialized)
        self.assertIn("TapMin:-5", serialized)
        self.assertIn("TapNom:0", serialized)
        self.assertIn("TapMax:5", serialized)


if __name__ == "__main__":
    unittest.main()
