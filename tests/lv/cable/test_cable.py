"""Tests for TCableLS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid
from pyptp.elements.lv.cable import CableLV
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import BranchPresentation, NodePresentation
from pyptp.elements.lv.shared import (
    CableType,
    CurrentType,
    Fields,
    FuseType,
    GeoCablePart,
)
from pyptp.elements.lv.sheet import SheetLV
from pyptp.elements.mixins import Extra, Note
from pyptp.network_lv import NetworkLV


class TestCableRegistration(unittest.TestCase):
    """Test cable registration and functionality."""

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

        self.cable_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_cable_registration_works(self) -> None:
        """Test that cables can register themselves with the network."""
        general = CableLV.General(
            guid=self.cable_guid,
            name="TestCable",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        cable_part = CableLV.CablePart(length=100.0, type="TestType")
        cable_type = CableType(short_name="TestType")
        presentation = BranchPresentation(sheet=self.sheet_guid)

        cable = CableLV(general, [presentation], cable_part, cable_type)
        cable.register(self.network)

        # Verify cable is in network
        self.assertIn(self.cable_guid, self.network.cables)
        self.assertIs(self.network.cables[self.cable_guid], cable)

    def test_cable_with_full_properties_serializes_correctly(self) -> None:
        """Test that cables with all properties serialize correctly."""
        general = CableLV.General(
            guid=self.cable_guid,
            node1=self.node1_guid,
            node2=self.node2_guid,
            name="FullCable",
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
            new=True,
            loadrate_max=0.8,
            k1_L1=2,
            k1_L2=3,
            k1_L3=4,
            k1_h1=7,
            k1_h2=8,
            k1_h3=9,
            k1_h4=10,
            k2_L1=5,
            k2_L2=6,
            k2_L3=7,
            k2_h1=11,
            k2_h2=12,
            k2_h3=13,
            k2_h4=14,
            switch_state1_h1=False,
            switch_state1_h2=True,
            switch_state1_h3=False,
            switch_state1_h4=True,
            switch_state2_h1=True,
            switch_state2_h2=False,
            switch_state2_h3=True,
            switch_state2_h4=False,
            protection_type1_h1="2",
            protection_type1_h2="3",
            protection_type1_h3="4",
            protection_type1_h4="5",
            protection_type2_h1="6",
            protection_type2_h2="7",
            protection_type2_h3="8",
            protection_type2_h4="9",
        )

        cable_part = CableLV.CablePart(length=150.5, type="TestCableType")
        cable_type = CableType(
            short_name="TestCableType",
            unom=0.4,
            price=100.0,
            C=0.1,
            C0=0.05,
            Inom0=100,
            G1=0.2,
            Inom1=150,
            G2=0.3,
            Inom2=200,
            G3=0.4,
            Inom3=250,
            Ik1s=5.0,
            TR=10,
            TInom=20,
            TIk1s=30,
            frequency=50,
            R_c=0.1,
            X_c=0.2,
            R_cc_n=0.3,
            X_cc_n=0.4,
            R_cc_o=0.5,
            X_cc_o=0.6,
            R_e=0.7,
            X_e=0.8,
            R_ce=0.9,
            X_ce=1.0,
            R_h=1.1,
            X_h=1.2,
            R_ch_n=1.3,
            X_ch_n=1.4,
            R_ch_o=1.5,
            X_ch_o=1.6,
            R_hh_n=1.7,
            X_hh_n=1.8,
            R_hh_o=1.9,
            X_hh_o=2.0,
            R_he=2.1,
            X_he=2.2,
            Inom_e=300,
            Ik1s_e=6.0,
            Inom_h=350,
            Ik1s_h=7.0,
            R_cR_n=1.5,
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
            flag_flipped1=True,
            flag_flipped2=False,
        )

        cable = CableLV(general, [presentation], cable_part, cable_type)
        cable.fields = Fields(values=["A", "B", "C"])
        cable.extras.append(Extra(text="foo=bar"))
        cable.notes.append(Note(text="Test note"))
        cable.register(self.network)

        # Test serialization
        serialized = cable.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#CablePart", serialized)
        self.assertIn("#CableType", serialized)
        self.assertIn("#Fields", serialized)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify key properties are serialized
        self.assertIn("Name:'FullCable'", serialized)
        self.assertIn("FieldName1:'Field1'", serialized)
        self.assertIn("FieldName2:'Field2'", serialized)
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("New:True", serialized)
        self.assertIn("LoadrateMax:0.8", serialized)
        self.assertIn("k1_L1:2", serialized)
        self.assertIn("k2_h4:14", serialized)
        self.assertIn("SwitchState1_L1:False", serialized)
        self.assertIn("SwitchState2_PE:True", serialized)
        self.assertIn("ProtectionType1_h1:'2'", serialized)
        self.assertIn("ProtectionType2_h4:'9'", serialized)

        # Verify cable part properties
        self.assertIn("Length:150.5", serialized)
        self.assertIn("CableType:'TestCableType'", serialized)

        # Verify cable type properties
        self.assertIn("ShortName:'TestCableType'", serialized)
        self.assertIn("Unom:0.4", serialized)
        self.assertIn("Price:100.0", serialized)
        self.assertIn("C:0.1", serialized)
        self.assertIn("C0:0.05", serialized)
        self.assertIn("Inom0:100", serialized)
        self.assertIn("G1:0.2", serialized)
        self.assertIn("Inom1:150", serialized)
        self.assertIn("G2:0.3", serialized)
        self.assertIn("Inom2:200", serialized)
        self.assertIn("G3:0.4", serialized)
        self.assertIn("Inom3:250", serialized)
        self.assertIn("Ik1s:5.0", serialized)
        self.assertIn("TR:10", serialized)
        self.assertIn("TInom:20", serialized)
        self.assertIn("TIk1s:30", serialized)
        self.assertIn("Frequency:50", serialized)
        self.assertIn("R_c:0.1", serialized)
        self.assertIn("X_c:0.2", serialized)
        self.assertIn("R_cc_n:0.3", serialized)
        self.assertIn("X_cc_n:0.4", serialized)
        self.assertIn("R_cc_o:0.5", serialized)
        self.assertIn("X_cc_o:0.6", serialized)
        self.assertIn("R_e:0.7", serialized)
        self.assertIn("X_e:0.8", serialized)
        self.assertIn("R_ce:0.9", serialized)
        self.assertIn("X_ce:1.0", serialized)
        self.assertIn("R_h:1.1", serialized)
        self.assertIn("X_h:1.2", serialized)
        self.assertIn("R_ch_n:1.3", serialized)
        self.assertIn("X_ch_n:1.4", serialized)
        self.assertIn("R_ch_o:1.5", serialized)
        self.assertIn("X_ch_o:1.6", serialized)
        self.assertIn("R_hh_n:1.7", serialized)
        self.assertIn("X_hh_n:1.8", serialized)
        self.assertIn("R_hh_o:1.9", serialized)
        self.assertIn("X_hh_o:2.0", serialized)
        self.assertIn("R_he:2.1", serialized)
        self.assertIn("X_he:2.2", serialized)
        self.assertIn("Inom_e:300", serialized)
        self.assertIn("Ik1s_e:6.0", serialized)
        self.assertIn("Inom_h:350", serialized)
        self.assertIn("Ik1s_h:7.0", serialized)
        self.assertIn("R_c/R_n:1.5", serialized)

        # Verify presentation properties
        self.assertIn(f"Sheet:'{{{str(self.sheet_guid).upper()}}}'", serialized)
        self.assertIn("Color:$00FF00", serialized)
        self.assertIn("TextColor:$FF0000", serialized)
        self.assertIn("Strings1X:10", serialized)
        self.assertIn("Strings1Y:20", serialized)
        self.assertIn("Strings2X:30", serialized)
        self.assertIn("Strings2Y:40", serialized)
        self.assertIn("MidStringsX:50", serialized)
        self.assertIn("MidStringsY:60", serialized)
        self.assertIn("FaultStringsX:70", serialized)
        self.assertIn("FaultStringsY:80", serialized)
        self.assertIn("NoteX:90", serialized)
        self.assertIn("NoteY:100", serialized)

        # Verify fields, extras, and notes
        self.assertIn("#Fields Name0:'A' Name1:'B' Name2:'C'", serialized)
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)

    def test_cable_with_fuses_and_currents_serializes_correctly(self) -> None:
        """Test that cables with fuses and currents serialize correctly."""
        general = CableLV.General(
            guid=self.cable_guid,
            name="FuseCable",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        cable_part = CableLV.CablePart(length=50.0, type="FuseType")
        cable_type = CableType(short_name="FuseType")
        presentation = BranchPresentation(sheet=self.sheet_guid)

        cable = CableLV(general, [presentation], cable_part, cable_type)

        # Add fuses
        cable.fuse1_h1 = FuseType(
            short_name="Fuse1h1",
            unom=0.4,
            inom=10.0,
            I=[10.0, 15.0, 20.0] + [0.0] * 13,
            T=[1.0, 2.0, 3.0] + [0.0] * 13,
        )
        cable.fuse1_h2 = FuseType(
            short_name="Fuse1h2",
            unom=0.4,
            inom=20.0,
            I=[20.0, 30.0, 40.0] + [0.0] * 13,
            T=[2.0, 4.0, 6.0] + [0.0] * 13,
        )
        cable.fuse2_h1 = FuseType(
            short_name="Fuse2h1",
            unom=0.4,
            inom=25.0,
            I=[25.0, 35.0, 45.0] + [0.0] * 13,
            T=[3.0, 5.0, 7.0] + [0.0] * 13,
        )
        cable.fuse2_h2 = FuseType(
            short_name="Fuse2h2",
            unom=0.4,
            inom=30.0,
            I=[30.0, 40.0, 50.0] + [0.0] * 13,
            T=[4.0, 6.0, 8.0] + [0.0] * 13,
        )

        # Add currents
        cable.current1_h1 = CurrentType(
            short_name="Current1h1",
            inom=5.0,
            setting_sort=1,
            I_great=8.0,
            T_great=2.0,
            I_greater=12.0,
            T_greater=1.0,
            I_greatest=16.0,
            T_greatest=0.5,
        )
        cable.current1_h2 = CurrentType(
            short_name="Current1h2",
            inom=12.0,
            setting_sort=2,
            I_great=18.0,
            T_great=3.0,
            I_greater=24.0,
            T_greater=1.5,
            I_greatest=30.0,
            T_greatest=0.75,
        )
        cable.current2_h1 = CurrentType(
            short_name="Current2h1",
            inom=15.0,
            setting_sort=1,
            I_great=22.0,
            T_great=4.0,
            I_greater=28.0,
            T_greater=2.0,
            I_greatest=34.0,
            T_greatest=1.0,
        )
        cable.current2_h2 = CurrentType(
            short_name="Current2h2",
            inom=18.0,
            setting_sort=2,
            I_great=25.0,
            T_great=5.0,
            I_greater=32.0,
            T_greater=2.5,
            I_greatest=38.0,
            T_greatest=1.25,
        )

        cable.register(self.network)

        serialized = cable.serialize()

        # Verify fuse sections are present
        self.assertIn("#FuseType1_h1", serialized)
        self.assertIn("#FuseType1_h2", serialized)
        self.assertIn("#FuseType2_h1", serialized)
        self.assertIn("#FuseType2_h2", serialized)

        # Verify current sections are present
        self.assertIn("#CurrentType1_h1", serialized)
        self.assertIn("#CurrentType1_h2", serialized)
        self.assertIn("#CurrentType2_h1", serialized)
        self.assertIn("#CurrentType2_h2", serialized)

        # Verify fuse values
        self.assertIn("Inom:10", serialized)
        self.assertIn("I1:10", serialized)
        self.assertIn("I2:15", serialized)
        self.assertIn("Inom:20", serialized)
        self.assertIn("I1:20", serialized)
        self.assertIn("I2:30", serialized)

        # Verify current values
        self.assertIn("Inom:5.0", serialized)
        self.assertIn("I>:8.0", serialized)
        self.assertIn("Inom:12.0", serialized)
        self.assertIn("I>:18.0", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a cable with the same GUID overwrites the existing one."""
        general1 = CableLV.General(
            guid=self.cable_guid,
            name="FirstCable",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        cable1 = CableLV(
            general1,
            [BranchPresentation(sheet=self.sheet_guid)],
            CableLV.CablePart(),
            CableType(short_name="FirstType"),
        )
        cable1.register(self.network)

        general2 = CableLV.General(
            guid=self.cable_guid,
            name="SecondCable",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        cable2 = CableLV(
            general2,
            [BranchPresentation(sheet=self.sheet_guid)],
            CableLV.CablePart(),
            CableType(short_name="SecondType"),
        )
        cable2.register(self.network)

        # Should only have one cable
        self.assertEqual(len(self.network.cables), 1)
        # Should be the second cable
        self.assertEqual(
            self.network.cables[self.cable_guid].general.name, "SecondCable"
        )

    def test_cable_with_geography_serializes_correctly(self) -> None:
        """Test that cables with geography information serialize correctly."""
        general = CableLV.General(
            guid=self.cable_guid,
            name="GeoCable",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        cable_part = CableLV.CablePart(length=75.0, type="GeoType")
        cable_type = CableType(short_name="GeoType")
        presentation = BranchPresentation(sheet=self.sheet_guid)

        geo_part = GeoCablePart(coordinates=[(10.0, 20.0), (30.0, 40.0)])

        cable = CableLV(general, [presentation], cable_part, cable_type, geo_part)
        cable.register(self.network)

        serialized = cable.serialize()

        # Verify geography section is present
        self.assertIn("#Geo Coordinates:", serialized)
        self.assertIn("Coordinates", serialized)

    def test_minimal_cable_serialization(self) -> None:
        """Test that minimal cables serialize correctly with only required fields."""
        general = CableLV.General(
            guid=self.cable_guid,
            name="MinimalCable",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        cable_part = CableLV.CablePart()
        cable_type = CableType(short_name="MinimalType")
        presentation = BranchPresentation(sheet=self.sheet_guid)

        cable = CableLV(general, [presentation], cable_part, cable_type)
        cable.register(self.network)

        serialized = cable.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#CablePart", serialized)
        self.assertIn("#CableType", serialized)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalCable'", serialized)

        # Should not have optional sections
        self.assertNotIn("#Fields", serialized)
        self.assertNotIn("#Extra", serialized)
        self.assertNotIn("#Note", serialized)
        self.assertNotIn("#GeoCablePart", serialized)

    def test_multiple_presentations_serialize_correctly(self) -> None:
        """Test that cables with multiple presentations serialize correctly."""
        general = CableLV.General(
            guid=self.cable_guid,
            name="MultiPresCable",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        cable_part = CableLV.CablePart()
        cable_type = CableType(short_name="MultiType")

        pres1 = BranchPresentation(sheet=self.sheet_guid, color=DelphiColor("$FF0000"))
        pres2 = BranchPresentation(sheet=self.sheet_guid, color=DelphiColor("$00FF00"))

        cable = CableLV(general, [pres1, pres2], cable_part, cable_type)
        cable.register(self.network)

        serialized = cable.serialize()

        # Should have two presentations
        self.assertEqual(serialized.count("#Presentation"), 2)
        self.assertIn("Color:$FF0000", serialized)
        self.assertIn("Color:$00FF00", serialized)


if __name__ == "__main__":
    unittest.main()
