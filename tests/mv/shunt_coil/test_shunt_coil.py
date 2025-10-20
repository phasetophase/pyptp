"""Tests for TShuntCoilMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import DEFAULT_PROFILE_GUID, Guid
from pyptp.elements.mixins import Extra, Note
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import ElementPresentation, NodePresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.elements.mv.shunt_coil import ShuntCoilMV
from pyptp.network_mv import NetworkMV


class TestShuntCoilRegistration(unittest.TestCase):
    """Test shunt coil registration and functionality."""

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

        # Create and register a node for the shunt coil
        node = NodeMV(
            NodeMV.General(
                guid=Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5")), name="TestNode"
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node.register(self.network)
        self.node_guid = node.general.guid

        self.shunt_coil_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_shunt_coil_registration_works(self) -> None:
        """Test that shunt coils can register themselves with the network."""
        general = ShuntCoilMV.General(
            guid=self.shunt_coil_guid,
            name="TestShuntCoil",
            node=self.node_guid,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        shunt_coil = ShuntCoilMV(general, [presentation])
        shunt_coil.register(self.network)

        # Verify shunt coil is in network
        self.assertIn(self.shunt_coil_guid, self.network.shunt_coils)
        self.assertIs(self.network.shunt_coils[self.shunt_coil_guid], shunt_coil)

    def test_shunt_coil_with_full_properties_serializes_correctly(self) -> None:
        """Test that shunt coils with all properties serialize correctly."""
        earthing_node_guid = Guid(UUID("8b7d4c3e-2f1a-4e5d-9c8b-7a6f5e4d3c2b"))
        profile_guid = Guid(UUID("1a2b3c4d-5e6f-7890-abcd-ef1234567890"))

        general = ShuntCoilMV.General(
            guid=self.shunt_coil_guid,
            node=self.node_guid,
            creation_time=123.45,
            mutation_date=10,
            revision_date=20,
            variant=True,
            name="FullShuntCoil",
            switch_state=True,
            field_name="TestField",
            failure_frequency=0.01,
            repair_duration=2.5,
            maintenance_frequency=0.1,
            maintenance_duration=4.0,
            maintenance_cancel_duration=1.0,
            not_preferred=True,
            Q=50.0,
            unom=20.0,
            profile=profile_guid,
            earthing=1,
            re=0.1,
            xe=0.2,
            earthing_node=earthing_node_guid,
            voltage_control=True,
            u_on=21.0,
            u_off=19.0,
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

        shunt_coil = ShuntCoilMV(general, [presentation])
        shunt_coil.extras.append(Extra(text="foo=bar"))
        shunt_coil.notes.append(Note(text="Test note"))
        shunt_coil.register(self.network)

        # Test serialization
        serialized = shunt_coil.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify general properties
        self.assertIn("Name:'FullShuntCoil'", serialized)
        self.assertIn("CreationTime:123.45", serialized)
        self.assertIn("MutationDate:10", serialized)
        self.assertIn("RevisionDate:20", serialized)
        self.assertIn("Variant:True", serialized)
        self.assertIn("SwitchState:1", serialized)
        self.assertIn("FieldName:'TestField'", serialized)
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("RepairDuration:2.5", serialized)
        self.assertIn("MaintenanceFrequency:0.1", serialized)
        self.assertIn("MaintenanceDuration:4.0", serialized)
        self.assertIn("MaintenanceCancelDuration:1.0", serialized)
        self.assertIn("NotPreferred:True", serialized)
        self.assertIn("Q:50", serialized)
        self.assertIn("Unom:20", serialized)
        self.assertIn("Earthing:1", serialized)
        self.assertIn("Re:0.1", serialized)
        self.assertIn("Xe:0.2", serialized)
        self.assertIn("VoltageControl:True", serialized)
        self.assertIn("Uon:21", serialized)
        self.assertIn("Uoff:19", serialized)

        # Verify node reference
        self.assertIn(f"Node:'{{{str(self.node_guid).upper()}}}'", serialized)
        self.assertIn(f"Profile:'{{{str(profile_guid).upper()}}}'", serialized)
        self.assertIn(
            f"EarthingNode:'{{{str(earthing_node_guid).upper()}}}'", serialized
        )

        # Verify extras and notes
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a shunt coil with the same GUID overwrites the existing one."""
        general1 = ShuntCoilMV.General(
            guid=self.shunt_coil_guid,
            name="FirstShuntCoil",
            node=self.node_guid,
        )
        shunt_coil1 = ShuntCoilMV(
            general1, [ElementPresentation(sheet=self.sheet_guid)]
        )
        shunt_coil1.register(self.network)

        general2 = ShuntCoilMV.General(
            guid=self.shunt_coil_guid,
            name="SecondShuntCoil",
            node=self.node_guid,
        )
        shunt_coil2 = ShuntCoilMV(
            general2, [ElementPresentation(sheet=self.sheet_guid)]
        )
        shunt_coil2.register(self.network)

        # Should only have one shunt coil
        self.assertEqual(len(self.network.shunt_coils), 1)
        # Should be the second shunt coil
        self.assertEqual(
            self.network.shunt_coils[self.shunt_coil_guid].general.name,
            "SecondShuntCoil",
        )

    def test_minimal_shunt_coil_serialization(self) -> None:
        """Test that minimal shunt coils serialize correctly with only required fields."""
        general = ShuntCoilMV.General(
            guid=self.shunt_coil_guid,
            name="MinimalShuntCoil",
            node=self.node_guid,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        shunt_coil = ShuntCoilMV(general, [presentation])
        shunt_coil.register(self.network)

        serialized = shunt_coil.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalShuntCoil'", serialized)
        self.assertIn(f"Node:'{{{str(self.node_guid).upper()}}}'", serialized)

        # Default values should be included since using no_skip
        self.assertIn("CreationTime:0", serialized)
        self.assertNotIn("Variant:", serialized)  # False values are skipped
        self.assertIn("SwitchState:0", serialized)
        self.assertIn("NotPreferred:False", serialized)
        self.assertIn("Q:0", serialized)
        self.assertIn("Unom:0", serialized)
        self.assertIn("Earthing:0", serialized)
        self.assertIn("Re:0", serialized)
        self.assertIn("Xe:0", serialized)
        self.assertIn("VoltageControl:False", serialized)
        self.assertIn("Uon:0", serialized)
        self.assertIn("Uoff:0", serialized)

    def test_shunt_coil_with_reactive_power_serializes_correctly(self) -> None:
        """Test that shunt coils with reactive power serialize correctly."""
        general = ShuntCoilMV.General(
            guid=self.shunt_coil_guid,
            name="ReactiveShuntCoil",
            node=self.node_guid,
            Q=100.0,
            unom=20.0,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        shunt_coil = ShuntCoilMV(general, [presentation])
        shunt_coil.register(self.network)

        serialized = shunt_coil.serialize()
        self.assertIn("Q:100", serialized)
        self.assertIn("Unom:20", serialized)

    def test_shunt_coil_with_earthing_properties_serializes_correctly(self) -> None:
        """Test that shunt coils with earthing properties serialize correctly."""
        earthing_node_guid = Guid(UUID("8b7d4c3e-2f1a-4e5d-9c8b-7a6f5e4d3c2b"))

        general = ShuntCoilMV.General(
            guid=self.shunt_coil_guid,
            name="EarthingShuntCoil",
            node=self.node_guid,
            earthing=1,
            re=0.1,
            xe=0.2,
            earthing_node=earthing_node_guid,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        shunt_coil = ShuntCoilMV(general, [presentation])
        shunt_coil.register(self.network)

        serialized = shunt_coil.serialize()
        self.assertIn("Earthing:1", serialized)
        self.assertIn("Re:0.1", serialized)
        self.assertIn("Xe:0.2", serialized)
        self.assertIn(
            f"EarthingNode:'{{{str(earthing_node_guid).upper()}}}'", serialized
        )

    def test_shunt_coil_with_voltage_control_serializes_correctly(self) -> None:
        """Test that shunt coils with voltage control serialize correctly."""
        general = ShuntCoilMV.General(
            guid=self.shunt_coil_guid,
            name="VoltageControlShuntCoil",
            node=self.node_guid,
            voltage_control=True,
            u_on=21.0,
            u_off=19.0,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        shunt_coil = ShuntCoilMV(general, [presentation])
        shunt_coil.register(self.network)

        serialized = shunt_coil.serialize()
        self.assertIn("VoltageControl:True", serialized)
        self.assertIn("Uon:21", serialized)
        self.assertIn("Uoff:19", serialized)

    def test_shunt_coil_with_default_profile_skips_serialization(self) -> None:
        """Test that shunt coils with default profile skip profile serialization."""
        general = ShuntCoilMV.General(
            guid=self.shunt_coil_guid,
            name="DefaultProfileShuntCoil",
            node=self.node_guid,
            profile=DEFAULT_PROFILE_GUID,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        shunt_coil = ShuntCoilMV(general, [presentation])
        shunt_coil.register(self.network)

        serialized = shunt_coil.serialize()
        # Should not include profile since it's the default
        self.assertNotIn("Profile:", serialized)


if __name__ == "__main__":
    unittest.main()
