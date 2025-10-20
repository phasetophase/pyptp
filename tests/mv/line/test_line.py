"""Tests for TLineMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid
from pyptp.elements.mixins import Extra, Note
from pyptp.elements.mv.line import LineMV
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import BranchPresentation, NodePresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.network_mv import NetworkMV


class TestLineRegistration(unittest.TestCase):
    """Test line registration and functionality."""

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

        # Create and register two nodes for the line
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

        self.line_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_line_registration_works(self) -> None:
        """Test that lines can register themselves with the network."""
        general = LineMV.General(
            guid=self.line_guid,
            name="TestLine",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        presentation = BranchPresentation(sheet=self.sheet_guid)
        linepart = LineMV.LinePart(length=100.0, description="Test Line Part")

        line = LineMV(
            general, [linepart], joints=[], geo=None, presentations=[presentation]
        )
        line.register(self.network)

        # Verify line is in network
        self.assertIn(self.line_guid, self.network.lines)
        self.assertIs(self.network.lines[self.line_guid], line)

    def test_line_with_full_properties_serializes_correctly(self) -> None:
        """Test that lines with all properties serialize correctly."""
        general = LineMV.General(
            guid=self.line_guid,
            creation_time=123.45,
            mutation_date=10,
            revision_date=20,
            variant=True,
            subnet_border=False,
            field_name1="Field1",
            field_name2="Field2",
            source1="Source1",
            source2="Source2",
            name="FullLine",
            repair_duration=2.5,
            failure_frequency=0.01,
            maintenance_frequency=0.1,
            maintenance_duration=4.0,
            maintenance_cancel_duration=1.0,
            loadrate_max=0.8,
            loadrate_max_emergency=1.2,
            switch_state1=1,
            switch_state2=0,
            node1=self.node1_guid,
            node2=self.node2_guid,
            resistance_symbol=True,
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
            flag_flipped1=False,
            flag_flipped2=True,
            first_corners=[(100, 100), (200, 200)],
            second_corners=[(300, 300), (400, 400)],
        )

        linepart = LineMV.LinePart(
            R=0.1,
            X=0.2,
            C=0.001,
            R0=0.3,
            X0=0.4,
            C0=0.002,
            inom1=100.0,
            inom2=150.0,
            inom3=200.0,
            ik1s=1000.0,
            TR=0.5,
            TI_nom=0.6,
            TIk1s=0.7,
            length=500.0,
            description="Full Line Part",
        )

        line = LineMV(
            general, [linepart], joints=[], geo=None, presentations=[presentation]
        )
        line.extras.append(Extra(text="foo=bar"))
        line.notes.append(Note(text="Test note"))
        line.register(self.network)

        # Test serialization
        serialized = line.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify key properties are serialized
        self.assertIn("Name:'FullLine'", serialized)
        self.assertIn("FieldName1:'Field1'", serialized)
        self.assertIn("FieldName2:'Field2'", serialized)
        self.assertIn("Source1:'Source1'", serialized)
        self.assertIn("Source2:'Source2'", serialized)
        self.assertIn("Variant:True", serialized)
        # SubnetBorder:False is skipped as a default value
        self.assertIn("RepairDuration:2.5", serialized)
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("MaintenanceFrequency:0.1", serialized)
        self.assertIn("MaintenanceDuration:4.0", serialized)
        self.assertIn("MaintenanceCancelDuration:1.0", serialized)
        self.assertIn("LoadrateMax:0.8", serialized)
        self.assertIn("LoadrateMaxmax:1.2", serialized)
        self.assertIn("SwitchState1:1", serialized)
        # SwitchState2:0 is skipped as a default value
        self.assertIn("ResistanceSymbol:True", serialized)

        # Verify node references
        self.assertIn(f"Node1:'{{{str(self.node1_guid).upper()}}}'", serialized)
        self.assertIn(f"Node2:'{{{str(self.node2_guid).upper()}}}'", serialized)

        # Verify presentation properties
        self.assertIn(f"Sheet:'{{{str(self.sheet_guid).upper()}}}'", serialized)
        self.assertIn("Color:$00FF00", serialized)
        self.assertIn("TextColor:$FF0000", serialized)
        self.assertIn("Size:2", serialized)
        self.assertIn("Width:3", serialized)
        self.assertIn("TextSize:12", serialized)
        self.assertIn("NoText:True", serialized)
        self.assertIn("UpsideDownText:True", serialized)
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
        # FlagFlipped1:False is skipped as a default value
        self.assertIn("FlagFlipped2:True", serialized)

        # Verify line part properties
        self.assertIn("R:0.1", serialized)
        self.assertIn("X:0.2", serialized)
        self.assertIn("C:0.001", serialized)
        self.assertIn("R0:0.3", serialized)
        self.assertIn("X0:0.4", serialized)
        self.assertIn("C0:0.002", serialized)
        self.assertIn("Inom1:100.0", serialized)
        self.assertIn("Inom2:150.0", serialized)
        self.assertIn("Inom3:200.0", serialized)
        self.assertIn("Ik1s:1000.0", serialized)
        self.assertIn("TR:0.5", serialized)
        self.assertIn("TInom:0.6", serialized)
        self.assertIn("TIk1s:0.7", serialized)
        self.assertIn("Length:500.0", serialized)
        self.assertIn("Description:'Full Line Part'", serialized)

        # Verify extras and notes
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a line with the same GUID overwrites the existing one."""
        general1 = LineMV.General(
            guid=self.line_guid,
            name="FirstLine",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        linepart1 = LineMV.LinePart(length=100.0, description="First Line Part")
        line1 = LineMV(
            general1,
            [linepart1],
            joints=[],
            geo=None,
            presentations=[BranchPresentation(sheet=self.sheet_guid)],
        )
        line1.register(self.network)

        general2 = LineMV.General(
            guid=self.line_guid,
            name="SecondLine",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        linepart2 = LineMV.LinePart(length=200.0, description="Second Line Part")
        line2 = LineMV(
            general2,
            [linepart2],
            joints=[],
            geo=None,
            presentations=[BranchPresentation(sheet=self.sheet_guid)],
        )
        line2.register(self.network)

        # Should only have one line
        self.assertEqual(len(self.network.lines), 1)
        # Should be the second line
        self.assertEqual(self.network.lines[self.line_guid].general.name, "SecondLine")

    def test_line_with_multiple_lineparts_serializes_correctly(self) -> None:
        """Test that lines with multiple line parts serialize correctly."""
        general = LineMV.General(
            guid=self.line_guid,
            name="MultiPartLine",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )

        linepart1 = LineMV.LinePart(
            R=0.1, X=0.2, C=0.001, length=200.0, description="Part 1"
        )
        linepart2 = LineMV.LinePart(
            R=0.3, X=0.4, C=0.002, length=300.0, description="Part 2"
        )

        presentation = BranchPresentation(sheet=self.sheet_guid)

        line = LineMV(
            general,
            [linepart1, linepart2],
            joints=[],
            geo=None,
            presentations=[presentation],
        )
        line.register(self.network)

        serialized = line.serialize()

        # Verify both line parts are serialized
        self.assertIn("Description:'Part 1'", serialized)
        self.assertIn("Description:'Part 2'", serialized)
        self.assertIn("R:0.1", serialized)
        self.assertIn("R:0.3", serialized)
        self.assertIn("Length:200.0", serialized)
        self.assertIn("Length:300.0", serialized)

    def test_minimal_line_serialization(self) -> None:
        """Test that minimal lines serialize correctly with only required fields."""
        general = LineMV.General(
            guid=self.line_guid,
            name="MinimalLine",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        linepart = LineMV.LinePart(length=100.0, description="Minimal Part")
        presentation = BranchPresentation(sheet=self.sheet_guid)

        line = LineMV(
            general, [linepart], joints=[], geo=None, presentations=[presentation]
        )
        line.register(self.network)

        serialized = line.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalLine'", serialized)
        # Default values like Variant:False, SubnetBorder:False, ResistanceSymbol:False are skipped in serialization
        self.assertIn("SwitchState1:1", serialized)
        self.assertIn("SwitchState2:1", serialized)

        # Should have line part properties
        self.assertIn("Length:100.0", serialized)
        self.assertIn("Description:'Minimal Part'", serialized)
        # Default values like R:0, X:0 are skipped in serialization

        # Should not have optional sections
        self.assertNotIn("#Extra", serialized)
        self.assertNotIn("#Note", serialized)

    def test_multiple_presentations_serialize_correctly(self) -> None:
        """Test that lines with multiple presentations serialize correctly."""
        general = LineMV.General(
            guid=self.line_guid,
            name="MultiPresLine",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )

        linepart = LineMV.LinePart(length=100.0, description="Test Part")

        pres1 = BranchPresentation(
            sheet=self.sheet_guid,
            color=DelphiColor("$FF0000"),
            first_corners=[(100, 100), (200, 200)],
        )
        pres2 = BranchPresentation(
            sheet=self.sheet_guid,
            color=DelphiColor("$00FF00"),
            first_corners=[(300, 300), (400, 400)],
        )

        line = LineMV(
            general, [linepart], joints=[], geo=None, presentations=[pres1, pres2]
        )
        line.register(self.network)

        serialized = line.serialize()

        # Should have two presentations
        self.assertEqual(serialized.count("#Presentation"), 2)
        self.assertIn("Color:$FF0000", serialized)
        self.assertIn("Color:$00FF00", serialized)

    def test_linepart_length_validation(self) -> None:
        """Test that line part length is validated to be at least 1 meter."""
        general = LineMV.General(
            guid=self.line_guid,
            name="LengthTestLine",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )

        # Test with length less than 1
        linepart = LineMV.LinePart(length=0.5, description="Short Part")
        presentation = BranchPresentation(sheet=self.sheet_guid)

        line = LineMV(
            general, [linepart], joints=[], geo=None, presentations=[presentation]
        )
        line.register(self.network)

        # Length should be adjusted to 1
        self.assertEqual(line.lineparts[0].length, 1.0)

        serialized = line.serialize()
        self.assertIn("Length:1", serialized)

    def test_line_with_corner_coordinates_serializes_correctly(self) -> None:
        """Test that lines with corner coordinates serialize correctly."""
        general = LineMV.General(
            guid=self.line_guid,
            name="CornerLine",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )

        linepart = LineMV.LinePart(length=100.0, description="Corner Part")

        presentation = BranchPresentation(
            sheet=self.sheet_guid,
            first_corners=[(100, 100), (200, 200), (300, 300)],
            second_corners=[(400, 400), (500, 500)],
        )

        line = LineMV(
            general, [linepart], joints=[], geo=None, presentations=[presentation]
        )
        line.register(self.network)

        serialized = line.serialize()

        # Verify corner coordinates are serialized (using the actual format)
        self.assertIn("FirstCorners:'{(100 100) (200 200) (300 300) }'", serialized)
        self.assertIn("SecondCorners:'{(400 400) (500 500) }'", serialized)

    def test_line_with_joints_serializes_correctly(self) -> None:
        """Test that lines with joints serialize correctly following Delphi order."""
        general = LineMV.General(
            guid=self.line_guid,
            name="JointLine",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )

        linepart = LineMV.LinePart(length=100.0, description="Joint Part")

        joint1 = LineMV.Joint(x=100.5, y=200.75, type="Type1")
        joint2 = LineMV.Joint(x=300.25, y=400.0, type="Type2")

        presentation = BranchPresentation(sheet=self.sheet_guid)

        line = LineMV(
            general,
            [linepart],
            joints=[joint1, joint2],
            geo=None,
            presentations=[presentation],
        )
        line.register(self.network)

        serialized = line.serialize()

        # Verify joints are serialized in correct order after LineParts
        lines = serialized.split("\n")
        general_idx = next(
            i for i, line in enumerate(lines) if line.startswith("#General")
        )
        linepart_idx = next(
            i for i, line in enumerate(lines) if line.startswith("#LinePart")
        )
        joint_indices = [i for i, line in enumerate(lines) if line.startswith("#Joint")]

        # Verify order: General < LinePart < Joint sections
        self.assertLess(general_idx, linepart_idx)
        for joint_idx in joint_indices:
            self.assertLess(linepart_idx, joint_idx)

        # Verify joint content
        self.assertEqual(len(joint_indices), 2)
        self.assertIn("#Joint X:100.5 Y:200.75 Type:'Type1'", serialized)
        self.assertIn("#Joint X:300.25 Y:400.0 Type:'Type2'", serialized)

    def test_line_without_joints_serializes_correctly(self) -> None:
        """Test that lines without joints serialize correctly (no Joint sections)."""
        general = LineMV.General(
            guid=self.line_guid,
            name="NoJointLine",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        linepart = LineMV.LinePart(length=100.0, description="No Joint Part")
        presentation = BranchPresentation(sheet=self.sheet_guid)

        line = LineMV(
            general, [linepart], joints=[], geo=None, presentations=[presentation]
        )
        line.register(self.network)

        serialized = line.serialize()

        # Verify no Joint sections are present
        self.assertNotIn("#Joint", serialized)
        self.assertEqual(serialized.count("#General"), 1)
        self.assertEqual(serialized.count("#LinePart"), 1)


if __name__ == "__main__":
    unittest.main()
