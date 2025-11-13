"""Tests for TLinkMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import NIL_GUID, Guid
from pyptp.elements.mixins import Extra, Note
from pyptp.elements.mv.link import LinkMV
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import BranchPresentation, NodePresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.network_mv import NetworkMV


class TestLinkRegistration(unittest.TestCase):
    """Test link registration and functionality."""

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

        # Create and register nodes for the link
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
                guid=Guid(UUID("aec2228f-a78e-4f54-9ed2-0a7dbd48b3f6")),
                name="TestNode2",
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node2.register(self.network)
        self.node2_guid = node2.general.guid

        self.link_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_link_registration_works(self) -> None:
        """Test that links can register themselves with the network."""
        general = LinkMV.General(
            guid=self.link_guid,
            name="TestLink",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        presentation = BranchPresentation(sheet=self.sheet_guid)

        link = LinkMV(general, [presentation])
        link.register(self.network)

        # Verify link is in network
        self.assertIn(self.link_guid, self.network.links)
        self.assertIs(self.network.links[self.link_guid], link)

    def test_link_with_full_properties_serializes_correctly(self) -> None:
        """Test that links with all properties serialize correctly."""
        general = LinkMV.General(
            guid=self.link_guid,
            creation_time=123.45,
            mutation_date=10,
            revision_date=20.5,
            variant=True,
            node1=self.node1_guid,
            node2=self.node2_guid,
            name="FullLink",
            switch_state1=1,
            switch_state2=1,
            field_name1="Field1",
            field_name2="Field2",
            subnet_border=True,
            source1="Source1",
            source2="Source2",
            rail_connectivity=2,
            failure_frequency=0.01,
            repair_duration=2.5,
            maintenance_frequency=0.1,
            maintenance_duration=4.0,
            maintenance_cancel_duration=1.0,
            loadrate_max=0.8,
            loadrate_max_emergency=1.2,
            limited=True,
            inom=400.0,
            ik1s=25000.0,
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
            flag_flipped1=True,
            flag_flipped2=True,
            first_corners=[(10, 20), (30, 40)],
            second_corners=[(50, 60), (70, 80)],
        )

        link = LinkMV(general, [presentation])
        link.extras.append(Extra(text="ec=ev"))
        link.notes.append(Note(text="Test note"))
        link.register(self.network)

        # Test serialization
        serialized = link.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify general properties
        self.assertIn("Name:'FullLink'", serialized)
        self.assertIn("CreationTime:123.45", serialized)
        self.assertIn("MutationDate:10", serialized)
        self.assertIn("RevisionDate:20.5", serialized)
        self.assertIn("Variant:True", serialized)
        self.assertIn(f"Node1:'{{{str(self.node1_guid).upper()}}}'", serialized)
        self.assertIn(f"Node2:'{{{str(self.node2_guid).upper()}}}'", serialized)
        self.assertIn("SwitchState1:1", serialized)
        self.assertIn("SwitchState2:1", serialized)
        self.assertIn("FieldName1:'Field1'", serialized)
        self.assertIn("FieldName2:'Field2'", serialized)
        self.assertIn("SubnetBorder:True", serialized)
        self.assertIn("Source1:'Source1'", serialized)
        self.assertIn("Source2:'Source2'", serialized)
        self.assertIn("RailConnectivity:2", serialized)
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("RepairDuration:2.5", serialized)
        self.assertIn("MaintenanceFrequency:0.1", serialized)
        self.assertIn("MaintenanceDuration:4.0", serialized)
        self.assertIn("MaintenanceCancelDuration:1.0", serialized)
        self.assertIn("LoadrateMax:0.8", serialized)
        self.assertIn("LoadrateMaxmax:1.2", serialized)
        self.assertIn("Limited:True", serialized)
        self.assertIn("Inom:400", serialized)
        self.assertIn("Ik1s:25000", serialized)

        # Verify presentation properties
        self.assertIn(f"Sheet:'{{{str(self.sheet_guid).upper()}}}'", serialized)
        self.assertIn("Color:$FF0000", serialized)
        self.assertIn("Size:2", serialized)
        self.assertIn("Width:3", serialized)
        self.assertIn("TextColor:$00FF00", serialized)
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
        self.assertIn("FlagFlipped1:True", serialized)
        self.assertIn("FlagFlipped2:True", serialized)
        self.assertIn("FirstCorners:'{(10 20) (30 40) }'", serialized)
        self.assertIn("SecondCorners:'{(50 60) (70 80) }'", serialized)

        # Verify extras and notes
        self.assertIn("#Extra Text:ec=ev", serialized)
        self.assertIn("#Note Text:Test note", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a link with the same GUID overwrites the existing one."""
        general1 = LinkMV.General(
            guid=self.link_guid,
            name="FirstLink",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        link1 = LinkMV(general1, [BranchPresentation(sheet=self.sheet_guid)])
        link1.register(self.network)

        general2 = LinkMV.General(
            guid=self.link_guid,
            name="SecondLink",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        link2 = LinkMV(general2, [BranchPresentation(sheet=self.sheet_guid)])
        link2.register(self.network)

        # Should only have one link
        self.assertEqual(len(self.network.links), 1)
        # Should be the second link
        self.assertEqual(self.network.links[self.link_guid].general.name, "SecondLink")

    def test_minimal_link_serialization(self) -> None:
        """Test that minimal links serialize correctly with only required fields."""
        general = LinkMV.General(
            guid=self.link_guid,
            name="MinimalLink",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        presentation = BranchPresentation(sheet=self.sheet_guid)

        link = LinkMV(general, [presentation])
        link.register(self.network)

        serialized = link.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalLink'", serialized)
        self.assertIn(f"Node1:'{{{str(self.node1_guid).upper()}}}'", serialized)
        self.assertIn(f"Node2:'{{{str(self.node2_guid).upper()}}}'", serialized)
        self.assertIn("SwitchState1:1", serialized)
        self.assertIn("SwitchState2:1", serialized)
        self.assertIn("RailConnectivity:1", serialized)

        # Should not have optional properties with default values
        self.assertNotIn("MutationDate", serialized)
        self.assertNotIn("RevisionDate", serialized)
        self.assertNotIn("Variant:True", serialized)
        self.assertNotIn("SubnetBorder:True", serialized)
        self.assertNotIn("FailureFrequency", serialized)
        self.assertNotIn("RepairDuration", serialized)
        self.assertNotIn("MaintenanceFrequency", serialized)
        self.assertNotIn("MaintenanceDuration", serialized)
        self.assertNotIn("MaintenanceCancelDuration", serialized)
        self.assertNotIn("LoadrateMax", serialized)
        self.assertNotIn("LoadrateMaxmax", serialized)
        self.assertNotIn("Limited:True", serialized)
        self.assertNotIn("Inom", serialized)
        self.assertNotIn("Ik1s", serialized)

    def test_link_with_switch_states_serializes_correctly(self) -> None:
        """Test that links with switch states serialize correctly."""
        general = LinkMV.General(
            guid=self.link_guid,
            name="SwitchStatesLink",
            node1=self.node1_guid,
            node2=self.node2_guid,
            switch_state1=1,
            switch_state2=1,
        )
        presentation = BranchPresentation(sheet=self.sheet_guid)

        link = LinkMV(general, [presentation])
        link.register(self.network)

        serialized = link.serialize()
        self.assertIn("SwitchState1:1", serialized)
        self.assertIn("SwitchState2:1", serialized)

    def test_link_with_field_names_serializes_correctly(self) -> None:
        """Test that links with field names serialize correctly."""
        general = LinkMV.General(
            guid=self.link_guid,
            name="FieldNamesLink",
            node1=self.node1_guid,
            node2=self.node2_guid,
            field_name1="Field1",
            field_name2="Field2",
        )
        presentation = BranchPresentation(sheet=self.sheet_guid)

        link = LinkMV(general, [presentation])
        link.register(self.network)

        serialized = link.serialize()
        self.assertIn("FieldName1:'Field1'", serialized)
        self.assertIn("FieldName2:'Field2'", serialized)

    def test_link_with_subnet_border_serializes_correctly(self) -> None:
        """Test that links with subnet border serialize correctly."""
        general = LinkMV.General(
            guid=self.link_guid,
            name="SubnetBorderLink",
            node1=self.node1_guid,
            node2=self.node2_guid,
            subnet_border=True,
        )
        presentation = BranchPresentation(sheet=self.sheet_guid)

        link = LinkMV(general, [presentation])
        link.register(self.network)

        serialized = link.serialize()
        self.assertIn("SubnetBorder:True", serialized)

    def test_link_with_maintenance_properties_serializes_correctly(self) -> None:
        """Test that links with maintenance properties serialize correctly."""
        general = LinkMV.General(
            guid=self.link_guid,
            name="MaintenanceLink",
            node1=self.node1_guid,
            node2=self.node2_guid,
            failure_frequency=0.01,
            repair_duration=2.5,
            maintenance_frequency=0.1,
            maintenance_duration=4.0,
            maintenance_cancel_duration=1.0,
        )
        presentation = BranchPresentation(sheet=self.sheet_guid)

        link = LinkMV(general, [presentation])
        link.register(self.network)

        serialized = link.serialize()
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("RepairDuration:2.5", serialized)
        self.assertIn("MaintenanceFrequency:0.1", serialized)
        self.assertIn("MaintenanceDuration:4.0", serialized)
        self.assertIn("MaintenanceCancelDuration:1.0", serialized)

    def test_link_with_load_rate_properties_serializes_correctly(self) -> None:
        """Test that links with load rate properties serialize correctly."""
        general = LinkMV.General(
            guid=self.link_guid,
            name="LoadRateLink",
            node1=self.node1_guid,
            node2=self.node2_guid,
            loadrate_max=0.8,
            loadrate_max_emergency=1.2,
            limited=True,
        )
        presentation = BranchPresentation(sheet=self.sheet_guid)

        link = LinkMV(general, [presentation])
        link.register(self.network)

        serialized = link.serialize()
        self.assertIn("LoadrateMax:0.8", serialized)
        self.assertIn("LoadrateMaxmax:1.2", serialized)
        self.assertIn("Limited:True", serialized)

    def test_link_with_electrical_properties_serializes_correctly(self) -> None:
        """Test that links with electrical properties serialize correctly."""
        general = LinkMV.General(
            guid=self.link_guid,
            name="ElectricalLink",
            node1=self.node1_guid,
            node2=self.node2_guid,
            limited=True,
            inom=400.0,
            ik1s=25000.0,
        )
        presentation = BranchPresentation(sheet=self.sheet_guid)

        link = LinkMV(general, [presentation])
        link.register(self.network)

        serialized = link.serialize()
        self.assertIn("Inom:400", serialized)
        self.assertIn("Ik1s:25000", serialized)

    def test_link_with_rail_connectivity_serializes_correctly(self) -> None:
        """Test that links with rail connectivity serialize correctly."""
        general = LinkMV.General(
            guid=self.link_guid,
            name="RailConnectivityLink",
            node1=self.node1_guid,
            node2=self.node2_guid,
            rail_connectivity=2,
        )
        presentation = BranchPresentation(sheet=self.sheet_guid)

        link = LinkMV(general, [presentation])
        link.register(self.network)

        serialized = link.serialize()
        self.assertIn("RailConnectivity:2", serialized)

    def test_link_with_nil_nodes_serializes_correctly(self) -> None:
        """Test that links with NIL nodes serialize correctly."""
        general = LinkMV.General(
            guid=self.link_guid,
            name="NilNodesLink",
            node1=NIL_GUID,
            node2=NIL_GUID,
        )
        presentation = BranchPresentation(sheet=self.sheet_guid)

        link = LinkMV(general, [presentation])
        link.register(self.network)

        serialized = link.serialize()
        self.assertIn("Name:'NilNodesLink'", serialized)
        # NIL_GUID should be skipped in serialization
        self.assertNotIn("Node1:", serialized)
        self.assertNotIn("Node2:", serialized)


if __name__ == "__main__":
    unittest.main()
