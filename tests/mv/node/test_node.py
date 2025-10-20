"""Tests for TNodeMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid
from pyptp.elements.mixins import Extra, Note
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import NodePresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.network_mv import NetworkMV


class TestNodeRegistration(unittest.TestCase):
    """Test node registration and functionality."""

    def setUp(self) -> None:
        """Create a fresh network with sheet for testing."""
        self.network = NetworkMV()

        # Create and register a sheet for presentations
        sheet = SheetMV(
            SheetMV.General(
                guid=Guid(UUID("9c038adb-5a44-4f33-8cb4-8f0518f2b4c2")),
                name="TestSheet",
            ),
        )
        sheet.register(self.network)
        self.sheet_guid = sheet.general.guid

        self.node_guid = Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5"))

    def test_node_registration_works(self) -> None:
        """Test that nodes can register themselves with the network."""
        general = NodeMV.General(guid=self.node_guid, name="TestNode")
        presentation = NodePresentation(sheet=self.sheet_guid)

        node = NodeMV(general, [presentation])
        node.register(self.network)

        # Verify node is in network
        self.assertIn(self.node_guid, self.network.nodes)
        self.assertIs(self.network.nodes[self.node_guid], node)

    def test_node_with_full_properties_serializes_correctly(self) -> None:
        """Test that nodes with all properties serialize correctly."""
        general = NodeMV.General(
            guid=self.node_guid,
            creation_time=123.45,
            mutation_date=10,
            revision_date=20.5,
            variant=True,
            name="FullNode",
            short_name="FN",
            id="TestID",
            unom=20.0,
            simultaneity_factor=0.8,
            function="TestFunction",
            railtype="TestRailtype",
            failure_frequency=0.01,
            repair_duration=2.5,
            maintenace_frequency=0.1,
            maintenace_duration=4.0,
            maintenace_cancel_duration=1.0,
            remote_status_indication=True,
            gx=100.0,
            gy=200.0,
            badly_accessible=True,
            ripple_control_frequency=500.0,
            ripple_control_voltage=230.0,
            ripple_control_angle=45.0,
            earthing=True,
            re=0.5,
            xe=0.8,
            no_voltage_check=1,
            umin=0.9,
            umax=1.1,
            d_umax=0.1,
        )

        presentation = NodePresentation(
            sheet=self.sheet_guid,
            x=100,
            y=200,
            symbol=15,
            color=DelphiColor("$FF0000"),
            size=2,
            width=3,
            text_color=DelphiColor("$00FF00"),
            text_size=12,
            font="Arial",
            text_style=1,
            is_text_hidden=True,
            is_text_upside_down=True,
            text_rotation=45,
            upstrings_x=10,
            upstrings_y=20,
            fault_strings_x=30,
            fault_strings_y=40,
            note_x=50,
            note_y=60,
            icon_x=70,
            icon_y=80,
        )

        # Create test instances for all sections
        railtype = NodeMV.Railtype(
            name="TestRailtype",
            unom=20.0,
            inom=1000.0,
            ik_dynamic=25000.0,
            ik_thermal=10000.0,
            t_thermal=1.0,
        )

        field1 = NodeMV.Field(
            name="Field1",
            sort="TestSort",
            installation_type=1,
            conductor_distance=2.5,
            electrode_configuration=3,
            enclosed_height=1.5,
            enclosed_width=2.0,
            enclosed_depth=1.0,
            to="Node2",
            info="Test field info",
        )

        customer = NodeMV.Customer(
            ean="123456789012345678",
            name="Test Customer",
            address="123 Test St",
            postal_code="12345",
            city="Test City",
            physical_network_area="Area1",
            connection_capacity=100.0,
            contracted_power=80.0,
            contracted_power_returned=20.0,
            contract="Test contract terms",
        )

        installation = NodeMV.Installation(
            type=1,
            earthed=True,
            conductor_distance=2.5,
            person_distance=3.0,
            enclosed=True,
            kb=1.2,
            kp=1.5,
            kp_max=True,
            kp_auto=True,
            kt=0.8,
            electrode_configuration=2,
            enclosed_height=2.5,
            enclosed_width=3.0,
            enclosed_depth=2.0,
            light_arc_protection=True,
        )

        icon = NodeMV.Icon(
            text="TestIcon",
            text_color=255,
            background_color=65535,
            shape=1,
            size=16,
        )

        diff_protection = NodeMV.DifferentialProtection(
            present=True,
            type_name="TestDiffType",
            t_input=0.1,
            t_output=0.2,
            setting_sort=1,
            dIg=0.3,
            tg=0.4,
            dIgg=0.5,
            tgg=0.6,
            m=0.7,
            dId=0.8,
            k1=0.9,
            k2=1.0,
        )

        diff_switch = NodeMV.DifferentialProtectionSwitch(
            switch=Guid(UUID("12345678-1234-1234-1234-123456789012")),
        )

        diff_transfer = NodeMV.DifferentialProtectionTransferTripSwitch(
            transfer_circuit_breaker=Guid(UUID("87654321-4321-4321-4321-210987654321")),
        )

        node = NodeMV(
            general=general,
            presentations=[presentation],
            railtype=railtype,
            fields=[field1],
            customer=customer,
            installation=installation,
            icon=icon,
            differential_protection=diff_protection,
            differential_protection_switches=[diff_switch],
            differential_protection_transfer_trip_switch=diff_transfer,
        )
        node.extras.append(Extra(text="foo=bar"))
        node.notes.append(Note(text="Test note"))
        node.register(self.network)

        # Test serialization
        serialized = node.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertGreaterEqual(serialized.count("#Railtype"), 1)
        self.assertGreaterEqual(serialized.count("#Field"), 1)
        self.assertGreaterEqual(serialized.count("#Customer"), 1)
        self.assertGreaterEqual(serialized.count("#Installation"), 1)
        self.assertGreaterEqual(serialized.count("#Icon"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#DifferentialProtection"), 1)
        self.assertGreaterEqual(serialized.count("#DifferentialProtectionSwitch"), 1)
        self.assertGreaterEqual(
            serialized.count("#DifferentialProtectionTransferTripSwitch"), 1
        )

        # Verify key properties are serialized
        self.assertIn("Name:'FullNode'", serialized)
        self.assertIn("ShortName:'FN'", serialized)
        self.assertIn("ID:'TestID'", serialized)
        self.assertIn("Unom:20", serialized)
        self.assertIn("SimultaneityFactor:0.8", serialized)
        self.assertIn("Function:'TestFunction'", serialized)
        self.assertIn("Railtype:'TestRailtype'", serialized)
        self.assertIn("Variant:True", serialized)
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("RepairDuration:2.5", serialized)
        self.assertIn("MaintenanceFrequency:0.1", serialized)
        self.assertIn("MaintenanceDuration:4.0", serialized)
        self.assertIn("MaintenanceCancelDuration:1.0", serialized)
        self.assertIn("RemoteStatusIndication:True", serialized)
        self.assertIn("GX:100", serialized)
        self.assertIn("GY:200", serialized)
        self.assertIn("BadlyAccessible:True", serialized)
        self.assertIn("RippleControlFrequency:500", serialized)
        self.assertIn("RippleControlVoltage:230", serialized)
        self.assertIn("RippleControlAngle:45", serialized)
        self.assertIn("Earthing:True", serialized)
        self.assertIn("Re:0.5", serialized)
        self.assertIn("Xe:0.8", serialized)
        self.assertIn("NoVoltageCheck:1", serialized)
        self.assertIn("Umin:0.9", serialized)
        self.assertIn("Umax:1.1", serialized)
        self.assertIn("dUmax:0.1", serialized)

        # Verify presentation properties
        self.assertIn(f"Sheet:'{{{str(self.sheet_guid).upper()}}}'", serialized)
        self.assertIn("X:100", serialized)
        self.assertIn("Y:200", serialized)
        self.assertIn("Symbol:15", serialized)
        self.assertIn("Color:$FF0000", serialized)
        self.assertIn("Size:2", serialized)
        self.assertIn("Width:3", serialized)
        self.assertIn("TextColor:$00FF00", serialized)
        self.assertIn("TextSize:12", serialized)
        self.assertIn("NoText:True", serialized)
        self.assertIn("UpsideDownText:True", serialized)
        self.assertIn("TextRotation:45", serialized)
        self.assertIn("UpstringsX:10", serialized)
        self.assertIn("UpstringsY:20", serialized)
        self.assertIn("FaultStringsX:30", serialized)
        self.assertIn("FaultStringsY:40", serialized)
        self.assertIn("NoteX:50", serialized)
        self.assertIn("NoteY:60", serialized)
        self.assertIn("IconX:70", serialized)
        self.assertIn("IconY:80", serialized)

        # Verify new section properties
        self.assertIn("Name:'TestRailtype'", serialized)
        self.assertIn("Inom:1000", serialized)
        self.assertIn("Name:'Field1'", serialized)
        self.assertIn("Sort:'TestSort'", serialized)
        self.assertIn("EAN:'123456789012345678'", serialized)
        self.assertIn("Adress:'123 Test St'", serialized)
        self.assertIn("Text:'TestIcon'", serialized)
        self.assertIn("TextColor:255", serialized)
        self.assertIn("TypeName:'TestDiffType'", serialized)
        self.assertIn("Switch:'{12345678-1234-1234-1234-123456789012}'", serialized)
        self.assertIn(
            "TransferCircuitBreaker:'{87654321-4321-4321-4321-210987654321}'",
            serialized,
        )

        # Verify extras and notes
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a node with the same GUID overwrites the existing one."""
        general1 = NodeMV.General(guid=self.node_guid, name="FirstNode")
        node1 = NodeMV(general1, [NodePresentation(sheet=self.sheet_guid)])
        node1.register(self.network)

        general2 = NodeMV.General(guid=self.node_guid, name="SecondNode")
        node2 = NodeMV(general2, [NodePresentation(sheet=self.sheet_guid)])
        node2.register(self.network)

        # Should only have one node
        self.assertEqual(len(self.network.nodes), 1)
        # Should be the second node
        self.assertEqual(self.network.nodes[self.node_guid].general.name, "SecondNode")

    def test_minimal_node_serialization(self) -> None:
        """Test that minimal nodes serialize correctly with only required fields."""
        general = NodeMV.General(guid=self.node_guid, name="MinimalNode")
        presentation = NodePresentation(sheet=self.sheet_guid)

        node = NodeMV(general, [presentation])
        node.register(self.network)

        serialized = node.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalNode'", serialized)
        self.assertIn("Unom:0.4", serialized)

        # Should not have optional sections
        self.assertNotIn("#Extra", serialized)
        self.assertNotIn("#Note", serialized)

    def test_multiple_presentations_serialize_correctly(self) -> None:
        """Test that nodes with multiple presentations serialize correctly."""
        general = NodeMV.General(guid=self.node_guid, name="MultiPresNode")

        pres1 = NodePresentation(
            sheet=self.sheet_guid,
            x=100,
            y=200,
            color=DelphiColor("$FF0000"),
            symbol=11,
        )
        pres2 = NodePresentation(
            sheet=self.sheet_guid,
            x=300,
            y=400,
            color=DelphiColor("$00FF00"),
            symbol=12,
        )

        node = NodeMV(general, [pres1, pres2])
        node.register(self.network)

        serialized = node.serialize()

        # Should have two presentations
        self.assertEqual(serialized.count("#Presentation"), 2)
        self.assertIn("Color:$FF0000", serialized)
        self.assertIn("Color:$00FF00", serialized)
        self.assertIn("Symbol:11", serialized)
        self.assertIn("Symbol:12", serialized)

    def test_node_with_default_unom_validation(self) -> None:
        """Test that nodes have correct default Unom value."""
        general = NodeMV.General(guid=self.node_guid, name="DefaultNode")
        presentation = NodePresentation(sheet=self.sheet_guid)

        node = NodeMV(general, [presentation])
        node.register(self.network)

        # Default Unom should be 0.4
        self.assertEqual(node.general.unom, 0.4)

        serialized = node.serialize()
        self.assertIn("Unom:0.4", serialized)

    def test_node_with_custom_unom_serializes_correctly(self) -> None:
        """Test that nodes with custom Unom values serialize correctly."""
        general = NodeMV.General(guid=self.node_guid, name="CustomNode", unom=10.0)
        presentation = NodePresentation(sheet=self.sheet_guid)

        node = NodeMV(general, [presentation])
        node.register(self.network)

        serialized = node.serialize()
        self.assertIn("Unom:10", serialized)

    def test_node_with_geographic_coordinates_serializes_correctly(self) -> None:
        """Test that nodes with geographic coordinates serialize correctly."""
        general = NodeMV.General(
            guid=self.node_guid,
            name="GeoNode",
            gx=100.5,
            gy=200.5,
        )
        presentation = NodePresentation(sheet=self.sheet_guid)

        node = NodeMV(general, [presentation])
        node.register(self.network)

        serialized = node.serialize()
        self.assertIn("GX:100.5", serialized)
        self.assertIn("GY:200.5", serialized)

    def test_node_with_earthing_properties_serializes_correctly(self) -> None:
        """Test that nodes with earthing properties serialize correctly."""
        general = NodeMV.General(
            guid=self.node_guid,
            name="EarthingNode",
            earthing=True,
            re=0.5,
            xe=0.8,
        )
        presentation = NodePresentation(sheet=self.sheet_guid)

        node = NodeMV(general, [presentation])
        node.register(self.network)

        serialized = node.serialize()
        self.assertIn("Earthing:True", serialized)
        self.assertIn("Re:0.5", serialized)
        self.assertIn("Xe:0.8", serialized)

    def test_node_with_voltage_limits_serializes_correctly(self) -> None:
        """Test that nodes with voltage limits serialize correctly."""
        general = NodeMV.General(
            guid=self.node_guid,
            name="VoltageLimitsNode",
            umin=0.95,
            umax=1.05,
            d_umax=0.05,
            no_voltage_check=1,
        )
        presentation = NodePresentation(sheet=self.sheet_guid)

        node = NodeMV(general, [presentation])
        node.register(self.network)

        serialized = node.serialize()
        self.assertIn("Umin:0.95", serialized)
        self.assertIn("Umax:1.05", serialized)
        self.assertIn("dUmax:0.05", serialized)
        self.assertIn("NoVoltageCheck:1", serialized)

    def test_node_with_ripple_control_properties_serializes_correctly(self) -> None:
        """Test that nodes with ripple control properties serialize correctly."""
        general = NodeMV.General(
            guid=self.node_guid,
            name="RippleControlNode",
            ripple_control_frequency=500.0,
            ripple_control_voltage=230.0,
            ripple_control_angle=45.0,
        )
        presentation = NodePresentation(sheet=self.sheet_guid)

        node = NodeMV(general, [presentation])
        node.register(self.network)

        serialized = node.serialize()
        self.assertIn("RippleControlFrequency:500", serialized)
        self.assertIn("RippleControlVoltage:230", serialized)
        self.assertIn("RippleControlAngle:45", serialized)


if __name__ == "__main__":
    unittest.main()
