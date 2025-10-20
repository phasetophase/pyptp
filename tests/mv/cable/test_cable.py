"""Tests for TCableMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid
from pyptp.elements.mixins import Extra, Note
from pyptp.elements.mv.cable import CableMV
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import BranchPresentation, NodePresentation
from pyptp.elements.mv.shared import CableType
from pyptp.elements.mv.sheet import SheetMV
from pyptp.network_mv import NetworkMV


class TestCableRegistration(unittest.TestCase):
    """Test cable registration and functionality."""

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

        # Create and register two nodes for the cable
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

        self.cable_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_cable_registration_works(self) -> None:
        """Test that cables can register themselves with the network."""
        general = CableMV.General(
            guid=self.cable_guid,
            name="TestCable",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        cable_part = CableMV.CablePart(length=100.0, cable_type="TestCableType")
        cable_type = CableType(short_name="TestCableType", unom=20.0)
        presentation = BranchPresentation(sheet=self.sheet_guid)

        cable = CableMV(general, [cable_part], [cable_type], [presentation])
        cable.register(self.network)

        # Verify cable is in network
        self.assertIn(self.cable_guid, self.network.cables)
        self.assertIs(self.network.cables[self.cable_guid], cable)

    def test_cable_with_full_properties_serializes_correctly(self) -> None:
        """Test that cables with all properties serialize correctly."""
        general = CableMV.General(
            guid=self.cable_guid,
            creation_time=123.45,
            mutation_date=10,
            revision_date=20.5,
            variant=True,
            subnet_border=True,
            field_name1="Field1",
            field_name2="Field2",
            source1="Source1",
            source2="Source2",
            name="FullCable",
            repair_duration=2.5,
            failure_frequency=0.01,
            maintenance_frequency=0.1,
            maintenance_duration=4.0,
            maintenance_cancel_duration=1.0,
            joint_failure_frequency=0.005,
            loadrate_max=0.8,
            loadrate_max_emergency=1.2,
            switch_state1=1,
            switch_state2=0,
            rail_connectivity=1,
            dyn_model="Q",
            dyn_number_of_sections=2,
            dyn_neglect_capacitance=True,
            node1=self.node1_guid,
            node2=self.node2_guid,
        )

        cable_part = CableMV.CablePart(
            length=500.0,
            cable_type="FullCableType",
            year="2023",
            parallel_cable_count=2,
            ground_resistivity_index=3,
            ampacity_factor=2,
        )

        cable_type = CableType(
            short_name="FullCableType",
            unom=20.0,
            price=100.0,
            r=0.1,
            x=0.2,
            c=0.001,
            r0=0.3,
            x0=0.4,
            c0=0.002,
            inom1=100.0,
            inom2=150.0,
            inom3=200.0,
            ik1s=1000.0,
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

        cable = CableMV(general, [cable_part], [cable_type], [presentation])
        cable.extras.append(Extra(text="foo=bar"))
        cable.notes.append(Note(text="Test note"))
        cable.register(self.network)

        # Test serialization
        serialized = cable.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertGreaterEqual(serialized.count("#CablePart"), 1)
        self.assertGreaterEqual(serialized.count("#CableType"), 1)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify key properties are serialized
        self.assertIn("Name:'FullCable'", serialized)
        self.assertIn("FieldName1:'Field1'", serialized)
        self.assertIn("FieldName2:'Field2'", serialized)
        self.assertIn("Source1:'Source1'", serialized)
        self.assertIn("Source2:'Source2'", serialized)
        self.assertIn("Variant:True", serialized)
        self.assertIn("SubnetBorder:True", serialized)
        self.assertIn("RepairDuration:2.5", serialized)
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("MaintenanceFrequency:0.1", serialized)
        self.assertIn("MaintenanceDuration:4.0", serialized)
        self.assertIn("MaintenanceCancelDuration:1.0", serialized)
        self.assertIn("JointFailureFrequency:0.005", serialized)
        self.assertIn("LoadrateMax:0.8", serialized)
        self.assertIn("LoadrateMaxmax:1.2", serialized)
        self.assertIn("SwitchState1:1", serialized)
        # SwitchState2:0 is skipped as a default value
        self.assertIn("RailConnectivity:1", serialized)
        self.assertIn("DynModel:'Q'", serialized)
        self.assertIn("DynSection:2", serialized)
        self.assertIn("DynNoC:True", serialized)

        # Verify node references
        self.assertIn(f"Node1:'{{{str(self.node1_guid).upper()}}}'", serialized)
        self.assertIn(f"Node2:'{{{str(self.node2_guid).upper()}}}'", serialized)

        # Verify cable part properties
        self.assertIn("Length:500", serialized)
        self.assertIn("CableType:'FullCableType'", serialized)
        self.assertIn("Year:'2023'", serialized)
        self.assertIn("ParallelCableCount:2", serialized)
        self.assertIn("GroundResistivityIndex:3", serialized)
        self.assertIn("AmpacityFactor:2", serialized)

        # Verify cable type properties
        self.assertIn("ShortName:'FullCableType'", serialized)
        self.assertIn("Unom:20", serialized)
        self.assertIn("Price:100", serialized)
        self.assertIn("R:0.1", serialized)
        self.assertIn("X:0.2", serialized)
        self.assertIn("C:0.001", serialized)
        self.assertIn("R0:0.3", serialized)
        self.assertIn("X0:0.4", serialized)
        self.assertIn("C0:0.002", serialized)
        self.assertIn("Inom1:100", serialized)
        self.assertIn("Inom2:150", serialized)
        self.assertIn("Inom3:200", serialized)
        self.assertIn("Ik1s:1000", serialized)

        # Verify presentation properties
        self.assertIn(f"Sheet:'{{{str(self.sheet_guid).upper()}}}'", serialized)
        self.assertIn("Color:$FF0000", serialized)
        self.assertIn("TextColor:$00FF00", serialized)
        self.assertIn("Size:2", serialized)
        self.assertIn("Width:3", serialized)
        self.assertIn("TextSize:12", serialized)
        self.assertIn("NoText:True", serialized)
        self.assertIn("UpsideDownText:True", serialized)

        # Verify extras and notes
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a cable with the same GUID overwrites the existing one."""
        general1 = CableMV.General(
            guid=self.cable_guid,
            name="FirstCable",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        cable_part1 = CableMV.CablePart(length=100.0, cable_type="Type1")
        cable_type1 = CableType(short_name="Type1", unom=10.0)
        cable1 = CableMV(
            general1,
            [cable_part1],
            [cable_type1],
            [BranchPresentation(sheet=self.sheet_guid)],
        )
        cable1.register(self.network)

        general2 = CableMV.General(
            guid=self.cable_guid,
            name="SecondCable",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        cable_part2 = CableMV.CablePart(length=200.0, cable_type="Type2")
        cable_type2 = CableType(short_name="Type2", unom=20.0)
        cable2 = CableMV(
            general2,
            [cable_part2],
            [cable_type2],
            [BranchPresentation(sheet=self.sheet_guid)],
        )
        cable2.register(self.network)

        # Should only have one cable
        self.assertEqual(len(self.network.cables), 1)
        # Should be the second cable
        self.assertEqual(
            self.network.cables[self.cable_guid].general.name, "SecondCable"
        )

    def test_minimal_cable_serialization(self) -> None:
        """Test that minimal cables serialize correctly with only required fields."""
        general = CableMV.General(
            guid=self.cable_guid,
            name="MinimalCable",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        cable_part = CableMV.CablePart(length=100.0, cable_type="MinimalType")
        cable_type = CableType(short_name="MinimalType", unom=10.0)
        presentation = BranchPresentation(sheet=self.sheet_guid)

        cable = CableMV(general, [cable_part], [cable_type], [presentation])
        cable.register(self.network)

        serialized = cable.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertEqual(serialized.count("#CablePart"), 1)
        self.assertEqual(serialized.count("#CableType"), 1)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalCable'", serialized)
        # Default values like Variant:False, SubnetBorder:False, RailConnectivity:0 are skipped in serialization
        self.assertIn("SwitchState1:1", serialized)
        self.assertIn("SwitchState2:1", serialized)
        self.assertIn("DynModel:'P'", serialized)
        self.assertIn("DynSection:1", serialized)
        # DynNoC:False is skipped as a default value

        # Should have cable part properties
        self.assertIn("Length:100", serialized)
        self.assertIn("CableType:'MinimalType'", serialized)
        self.assertIn("ParallelCableCount:1", serialized)
        self.assertIn("GroundResistivityIndex:1", serialized)
        self.assertIn("AmpacityFactor:1", serialized)

        # Should not have optional sections
        self.assertNotIn("#Extra", serialized)
        self.assertNotIn("#Note", serialized)

    def test_cable_length_validation(self) -> None:
        """Test that cable part length is validated to be at least 1 meter."""
        general = CableMV.General(
            guid=self.cable_guid,
            name="LengthTestCable",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        cable_part = CableMV.CablePart(
            length=0.5, cable_type="TestType"
        )  # Length less than 1
        cable_type = CableType(short_name="TestType", unom=10.0)
        presentation = BranchPresentation(sheet=self.sheet_guid)

        cable = CableMV(general, [cable_part], [cable_type], [presentation])
        cable.register(self.network)

        # Length should be adjusted to 1
        self.assertEqual(cable.cable_parts[0].length, 1.0)

        serialized = cable.serialize()
        self.assertIn("Length:1", serialized)

    def test_cable_with_multiple_cable_parts_serializes_correctly(self) -> None:
        """Test that cables with multiple cable parts serialize correctly."""
        general = CableMV.General(
            guid=self.cable_guid,
            name="MultiPartCable",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )

        cable_part1 = CableMV.CablePart(length=200.0, cable_type="Type1", year="2020")
        cable_part2 = CableMV.CablePart(length=300.0, cable_type="Type2", year="2021")

        cable_type1 = CableType(short_name="Type1", unom=10.0, r=0.1, x=0.2)
        cable_type2 = CableType(short_name="Type2", unom=20.0, r=0.2, x=0.3)

        presentation = BranchPresentation(sheet=self.sheet_guid)

        cable = CableMV(
            general,
            [cable_part1, cable_part2],
            [cable_type1, cable_type2],
            [presentation],
        )
        cable.register(self.network)

        serialized = cable.serialize()

        # Should have two cable parts and types
        self.assertEqual(serialized.count("#CablePart"), 2)
        self.assertEqual(serialized.count("#CableType"), 2)
        self.assertIn("CableType:'Type1'", serialized)
        self.assertIn("CableType:'Type2'", serialized)
        self.assertIn("Year:'2020'", serialized)
        self.assertIn("Year:'2021'", serialized)
        self.assertIn("Length:200", serialized)
        self.assertIn("Length:300", serialized)

    def test_cable_with_joints_serializes_correctly(self) -> None:
        """Test that cables with joints serialize correctly."""
        general = CableMV.General(
            guid=self.cable_guid,
            name="JointCable",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        cable_part = CableMV.CablePart(length=100.0, cable_type="TestType")
        cable_type = CableType(short_name="TestType", unom=10.0)
        presentation = BranchPresentation(sheet=self.sheet_guid)

        joint1 = CableMV.Joint(
            x=100.0, y=200.0, type="Type1", year="2020", failure_frequency=0.01
        )
        joint2 = CableMV.Joint(
            x=300.0, y=400.0, type="Type2", year="2021", failure_frequency=0.02
        )

        cable = CableMV(
            general, [cable_part], [cable_type], [presentation], joints=[joint1, joint2]
        )
        cable.register(self.network)

        serialized = cable.serialize()

        # Should have two joints
        self.assertEqual(serialized.count("#Joint"), 2)
        self.assertIn("Type:'Type1'", serialized)
        self.assertIn("Type:'Type2'", serialized)
        self.assertIn("Year:'2020'", serialized)
        self.assertIn("Year:'2021'", serialized)
        self.assertIn("X:100", serialized)
        self.assertIn("Y:200", serialized)
        self.assertIn("X:300", serialized)
        self.assertIn("Y:400", serialized)
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("FailureFrequency:0.02", serialized)

    def test_cable_with_geo_coordinates_serializes_correctly(self) -> None:
        """Test that cables with geo coordinates serialize correctly."""
        general = CableMV.General(
            guid=self.cable_guid,
            name="GeoCable",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        cable_part = CableMV.CablePart(length=100.0, cable_type="TestType")
        cable_type = CableType(short_name="TestType", unom=10.0)
        presentation = BranchPresentation(sheet=self.sheet_guid)

        geo = CableMV.Geo(coordinates=[(100.0, 200.0), (300.0, 400.0), (500.0, 600.0)])

        cable = CableMV(general, [cable_part], [cable_type], [presentation], geo=geo)
        cable.register(self.network)

        serialized = cable.serialize()

        # Should have geo coordinates
        self.assertIn("#Geo", serialized)
        self.assertIn("Coordinates:", serialized)
        # Check that coordinates are properly formatted with coordinate pairs
        self.assertIn("(100,0 200,0)", serialized)
        self.assertIn("(300,0 400,0)", serialized)
        self.assertIn("(500,0 600,0)", serialized)

    def test_cable_with_dynamic_properties_serializes_correctly(self) -> None:
        """Test that cables with dynamic properties serialize correctly."""
        general = CableMV.General(
            guid=self.cable_guid,
            name="DynCable",
            node1=self.node1_guid,
            node2=self.node2_guid,
            dyn_model="Q",
            dyn_number_of_sections=3,
            dyn_neglect_capacitance=True,
        )
        cable_part = CableMV.CablePart(length=100.0, cable_type="TestType")
        cable_type = CableType(short_name="TestType", unom=10.0)
        presentation = BranchPresentation(sheet=self.sheet_guid)

        cable = CableMV(general, [cable_part], [cable_type], [presentation])
        cable.register(self.network)

        serialized = cable.serialize()
        self.assertIn("DynModel:'Q'", serialized)
        self.assertIn("DynSection:3", serialized)
        self.assertIn("DynNoC:True", serialized)

    def test_cable_with_rail_connectivity_serializes_correctly(self) -> None:
        """Test that cables with rail connectivity serialize correctly."""
        general = CableMV.General(
            guid=self.cable_guid,
            name="RailCable",
            node1=self.node1_guid,
            node2=self.node2_guid,
            rail_connectivity=2,
        )
        cable_part = CableMV.CablePart(length=100.0, cable_type="TestType")
        cable_type = CableType(short_name="TestType", unom=10.0)
        presentation = BranchPresentation(sheet=self.sheet_guid)

        cable = CableMV(general, [cable_part], [cable_type], [presentation])
        cable.register(self.network)

        serialized = cable.serialize()
        self.assertIn("RailConnectivity:2", serialized)


if __name__ == "__main__":
    unittest.main()
