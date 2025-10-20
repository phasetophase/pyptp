"""Tests for TPvLS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid, encode_guid
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import ElementPresentation, NodePresentation
from pyptp.elements.lv.pv import PVLV
from pyptp.elements.lv.shared import EfficiencyType, HarmonicsType
from pyptp.elements.lv.sheet import SheetLV
from pyptp.elements.mixins import Extra, Note
from pyptp.network_lv import NetworkLV


class TestPvRegistration(unittest.TestCase):
    """Test PV registration and functionality."""

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

        self.pv_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_pv_registration_works(self) -> None:
        """Test that PVs can register themselves with the network."""
        general = PVLV.General(guid=self.pv_guid, name="TestPv", node=self.node_guid)
        inverter = PVLV.Inverter()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        pv = PVLV(general, [presentation], inverter)
        pv.register(self.network)

        # Verify PV is in network
        self.assertIn(self.pv_guid, self.network.pvs)
        self.assertIs(self.network.pvs[self.pv_guid], pv)

    def test_pv_with_full_properties_serializes_correctly(self) -> None:
        """Test that PV systems with all properties serialize correctly."""
        general = PVLV.General(
            guid=self.pv_guid,
            node=self.node_guid,
            name="FullPv",
            s_L1=True,
            s_L2=False,
            s_L3=True,
            s_N=False,
            field_name="PvField",
            single_phase=True,
            phase=2,
            scaling=1500.0,
            longitude=4.5,
            latitude=52.0,
            panel1_pnom=100.0,
            panel1_orientation=180.0,
            panel1_slope=30.0,
            panel2_pnom=150.0,
            panel2_orientation=225.0,
            panel2_slope=35.0,
            panel3_pnom=200.0,
            panel3_orientation=270.0,
            panel3_slope=60.0,
            harmonics_type="Type1",
        )

        inverter = PVLV.Inverter(snom=25.0, efficiency_type="InverterType", u_off=0.35)

        efficiency_type = EfficiencyType(
            input1=10.0,
            output1=9.5,
            input2=20.0,
            output2=18.4,
            input3=30.0,
            output3=26.4,
        )

        q_control = PVLV.QControl(
            sort=1,
            cos_ref=0.95,
            no_p_no_q=True,
            input1=0.1,
            output1=0.2,
            input2=0.3,
            output2=0.4,
            input3=0.5,
            output3=0.6,
            input4=0.7,
            output4=0.8,
            input5=0.9,
            output5=1.0,
        )

        pu_control = PVLV.PUControl(
            input1=0.38,
            output1=0.5,
            input2=0.39,
            output2=0.6,
            input3=0.40,
            output3=0.7,
            input4=0.41,
            output4=0.8,
            input5=0.42,
            output5=0.9,
        )

        harmonics = HarmonicsType(
            h=[1.0, 2.0, 3.0] + [0.0] * 96, angle=[0.0, 90.0, 180.0] + [0.0] * 96
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

        pv = PVLV(
            general,
            [presentation],
            inverter,
            efficiency_type,
            q_control,
            pu_control,
            harmonics,
        )
        pv.extras.append(Extra(text="foo=bar"))
        pv.notes.append(Note(text="Test note"))
        pv.register(self.network)

        # Test serialization
        serialized = pv.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#Inverter", serialized)
        self.assertIn("#EfficiencyType", serialized)
        self.assertIn("#QControl", serialized)
        self.assertIn("#P(U)Control", serialized)
        self.assertIn("#HarmonicsType", serialized)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify key general properties are serialized
        self.assertIn("Name:'FullPv'", serialized)
        self.assertIn("FieldName:'PvField'", serialized)
        self.assertIn("s_L1:True", serialized)
        self.assertIn("s_L2:False", serialized)
        self.assertIn("s_L3:True", serialized)
        self.assertIn("s_N:False", serialized)
        self.assertIn("OnePhase:True", serialized)
        self.assertIn("Phase:2", serialized)
        self.assertIn("Scaling:1500.0", serialized)
        self.assertIn("Longitude:4.5", serialized)
        self.assertIn("Latitude:52.0", serialized)
        self.assertIn("Panel1Pnom:100.0", serialized)
        self.assertIn("Panel1Orientation:180.0", serialized)
        self.assertIn("Panel1Slope:30.0", serialized)
        self.assertIn("Panel2Pnom:150.0", serialized)
        self.assertIn("Panel2Orientation:225.0", serialized)
        self.assertIn("Panel2Slope:35.0", serialized)
        self.assertIn("Panel3Pnom:200.0", serialized)
        self.assertIn("Panel3Orientation:270.0", serialized)
        self.assertIn("Panel3Slope:60.0", serialized)
        self.assertIn("HarmonicsType:'Type1'", serialized)

        # Verify inverter properties
        self.assertIn("Snom:25.0", serialized)
        self.assertIn("EfficiencyType:'InverterType'", serialized)
        self.assertIn("Uoff:0.35", serialized)

        # Verify efficiency properties
        self.assertIn("Input1:10.0", serialized)
        self.assertIn("Output1:9.5", serialized)
        self.assertIn("Input2:20.0", serialized)
        self.assertIn("Output2:18.4", serialized)
        self.assertIn("Input3:30.0", serialized)
        self.assertIn("Output3:26.4", serialized)

        # Verify Q control properties
        self.assertIn("Sort:1", serialized)
        self.assertIn("CosRef:0.95", serialized)
        self.assertIn("NoPNoQ:True", serialized)
        self.assertIn("Input1:0.1", serialized)
        self.assertIn("Output1:0.2", serialized)
        self.assertIn("Input5:0.9", serialized)
        self.assertIn("Output5:1.0", serialized)

        # Verify P(U) control properties
        self.assertIn("Input1:0.38", serialized)
        self.assertIn("Output1:0.5", serialized)
        self.assertIn("Input5:0.42", serialized)
        self.assertIn("Output5:0.9", serialized)

        # Verify harmonics properties
        self.assertIn("h1:1.0", serialized)
        self.assertIn("h2:2.0", serialized)
        self.assertIn("h3:3.0", serialized)
        self.assertIn("Angle2:90.0", serialized)
        self.assertIn("Angle3:180.0", serialized)

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
        """Test that registering a PV with the same GUID overwrites the existing one."""
        general1 = PVLV.General(guid=self.pv_guid, name="FirstPv", node=self.node_guid)
        pv1 = PVLV(
            general1, [ElementPresentation(sheet=self.sheet_guid)], PVLV.Inverter()
        )
        pv1.register(self.network)

        general2 = PVLV.General(guid=self.pv_guid, name="SecondPv", node=self.node_guid)
        pv2 = PVLV(
            general2, [ElementPresentation(sheet=self.sheet_guid)], PVLV.Inverter()
        )
        pv2.register(self.network)

        # Should only have one PV
        self.assertEqual(len(self.network.pvs), 1)
        # Should be the second PV
        self.assertEqual(self.network.pvs[self.pv_guid].general.name, "SecondPv")

    def test_pv_with_profile_guid_serializes_correctly(self) -> None:
        """Test that PVs with profile GUID serialize correctly."""
        profile_guid = Guid(UUID("12345678-1234-5678-9abc-123456789abc"))

        general = PVLV.General(
            guid=self.pv_guid,
            name="ProfilePv",
            node=self.node_guid,
            profile=profile_guid,
        )
        inverter = PVLV.Inverter()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        pv = PVLV(general, [presentation], inverter)
        pv.register(self.network)

        serialized = pv.serialize()

        # Verify profile GUID is serialized
        self.assertIn(f"Profile:'{{{str(profile_guid).upper()}}}'", serialized)

    def test_minimal_pv_serialization(self) -> None:
        """Test that minimal PVs serialize correctly with only required fields."""
        general = PVLV.General(guid=self.pv_guid, name="MinimalPv", node=self.node_guid)
        inverter = PVLV.Inverter()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        pv = PVLV(general, [presentation], inverter)
        pv.register(self.network)

        serialized = pv.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#Inverter", serialized)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalPv'", serialized)
        self.assertIn("s_L1:True", serialized)  # Default values
        self.assertIn("s_L2:True", serialized)
        self.assertIn("s_L3:True", serialized)
        self.assertIn("s_N:True", serialized)
        self.assertIn("OnePhase:False", serialized)  # Default value
        self.assertIn("Scaling:1000.0", serialized)  # Default value
        self.assertIn("Longitude:0.0", serialized)  # Default value
        self.assertIn("Latitude:0.0", serialized)  # Default value

        # Should not have optional sections
        self.assertNotIn("#EfficiencyType", serialized)
        self.assertNotIn("#QControl", serialized)
        self.assertNotIn("#P(U)Control", serialized)
        self.assertNotIn("#HarmonicsType", serialized)
        self.assertNotIn("#Extra", serialized)
        self.assertNotIn("#Note", serialized)

    def test_multiple_presentations_serialize_correctly(self) -> None:
        """Test that PVs with multiple presentations serialize correctly."""
        general = PVLV.General(
            guid=self.pv_guid, name="MultiPresPv", node=self.node_guid
        )
        inverter = PVLV.Inverter()

        pres1 = ElementPresentation(
            sheet=self.sheet_guid, x=100, y=100, color=DelphiColor("$FF0000")
        )
        pres2 = ElementPresentation(
            sheet=self.sheet_guid, x=200, y=200, color=DelphiColor("$00FF00")
        )

        pv = PVLV(general, [pres1, pres2], inverter)
        pv.register(self.network)

        serialized = pv.serialize()

        # Should have two presentations
        self.assertEqual(serialized.count("#Presentation"), 2)
        self.assertIn("Color:$FF0000", serialized)
        self.assertIn("Color:$00FF00", serialized)
        self.assertIn("X:100", serialized)
        self.assertIn("X:200", serialized)

    def test_pv_with_panel_configuration_serializes_correctly(self) -> None:
        """Test that PVs with panel configuration serialize correctly."""
        general = PVLV.General(
            guid=self.pv_guid,
            name="PanelPv",
            node=self.node_guid,
            panel1_pnom=50.0,
            panel1_orientation=135.0,
            panel1_slope=25.0,
            panel2_pnom=75.0,
            panel2_orientation=225.0,
            panel2_slope=35.0,
        )
        inverter = PVLV.Inverter()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        pv = PVLV(general, [presentation], inverter)
        pv.register(self.network)

        serialized = pv.serialize()

        # Verify panel properties are serialized
        self.assertIn("Panel1Pnom:50.0", serialized)
        self.assertIn("Panel1Orientation:135.0", serialized)
        self.assertIn("Panel1Slope:25.0", serialized)
        self.assertIn("Panel2Pnom:75.0", serialized)
        self.assertIn("Panel2Orientation:225.0", serialized)
        self.assertIn("Panel2Slope:35.0", serialized)


if __name__ == "__main__":
    unittest.main()
