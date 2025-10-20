"""Tests for TShuntCapacitorMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import DEFAULT_PROFILE_GUID, Guid
from pyptp.elements.mixins import Extra, Note
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import ElementPresentation, NodePresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.elements.mv.shunt_capacitor import ShuntCapacitorMV
from pyptp.network_mv import NetworkMV


class TestShuntCapacitorRegistration(unittest.TestCase):
    """Test shunt capacitor registration and functionality."""

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

        # Create and register a node for the shunt capacitor
        node = NodeMV(
            NodeMV.General(
                guid=Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5")), name="TestNode"
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node.register(self.network)
        self.node_guid = node.general.guid

        self.shunt_capacitor_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_shunt_capacitor_registration_works(self) -> None:
        """Test that shunt capacitors can register themselves with the network."""
        general = ShuntCapacitorMV.General(
            guid=self.shunt_capacitor_guid,
            name="TestShuntCapacitor",
            node=self.node_guid,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        shunt_capacitor = ShuntCapacitorMV(general, [presentation])
        shunt_capacitor.register(self.network)

        # Verify shunt capacitor is in network
        self.assertIn(self.shunt_capacitor_guid, self.network.shunt_capacitors)
        self.assertIs(
            self.network.shunt_capacitors[self.shunt_capacitor_guid], shunt_capacitor
        )

    def test_shunt_capacitor_with_full_properties_serializes_correctly(self) -> None:
        """Test that shunt capacitors with all properties serialize correctly."""
        earthing_node_guid = Guid(UUID("8b7d4c3e-2f1a-4e5d-9c8b-7a6f5e4d3c2b"))
        profile_guid = Guid(UUID("1a2b3c4d-5e6f-7890-abcd-ef1234567890"))

        general = ShuntCapacitorMV.General(
            guid=self.shunt_capacitor_guid,
            node=self.node_guid,
            creation_time=123.45,
            mutation_date=10,
            revision_date=20,
            variant=True,
            name="FullShuntCapacitor",
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
            earthing=True,
            re=0.1,
            xe=0.2,
            earthing_node=earthing_node_guid,
            voltage_control=True,
            u_on=21.0,
            u_off=19.0,
            only_during_motorstart=True,
            passive_filter_frequency=50.0,
            passive_filter_quality_factor=10.0,
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

        shunt_capacitor = ShuntCapacitorMV(general, [presentation])
        shunt_capacitor.extras.append(Extra(text="foo=bar"))
        shunt_capacitor.notes.append(Note(text="Test note"))
        shunt_capacitor.register(self.network)

        # Test serialization
        serialized = shunt_capacitor.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify general properties
        self.assertIn("Name:'FullShuntCapacitor'", serialized)
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
        self.assertIn("Earthing:True", serialized)
        self.assertIn("Re:0.1", serialized)
        self.assertIn("Xe:0.2", serialized)
        self.assertIn("VoltageControl:True", serialized)
        self.assertIn("Uon:21", serialized)
        self.assertIn("Uoff:19", serialized)
        self.assertIn("OnlyDuringMotorstart:True", serialized)
        self.assertIn("PassiveFilterFrequency:50", serialized)
        self.assertIn("PassiveFilterQualityFactor:10", serialized)

        # Verify node reference
        self.assertIn(f"Node:'{{{str(self.node_guid).upper()}}}'", serialized)
        self.assertIn(f"Profile:'{{{str(profile_guid).upper()}}}'", serialized)
        self.assertIn(
            f"EarthingNode:'{{{str(earthing_node_guid).upper()}}}'", serialized
        )

        # Verify presentation properties
        self.assertIn(f"Sheet:'{{{str(self.sheet_guid).upper()}}}'", serialized)
        self.assertIn("X:100", serialized)
        self.assertIn("Y:200", serialized)
        self.assertIn("Color:$FF0000", serialized)
        self.assertIn("Size:2", serialized)
        self.assertIn("Width:3", serialized)
        self.assertIn("TextColor:$00FF00", serialized)
        self.assertIn("TextSize:12", serialized)
        self.assertIn("NoText:True", serialized)
        self.assertIn("UpsideDownText:True", serialized)
        self.assertIn("Strings1X:10", serialized)
        self.assertIn("Strings1Y:20", serialized)
        self.assertIn("SymbolStringsX:30", serialized)
        self.assertIn("SymbolStringsY:40", serialized)
        self.assertIn("NoteX:50", serialized)
        self.assertIn("NoteY:60", serialized)
        self.assertIn("FlagFlipped:True", serialized)

        # Verify extras and notes
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a shunt capacitor with the same GUID overwrites the existing one."""
        general1 = ShuntCapacitorMV.General(
            guid=self.shunt_capacitor_guid,
            name="FirstShuntCapacitor",
            node=self.node_guid,
        )
        shunt_capacitor1 = ShuntCapacitorMV(
            general1, [ElementPresentation(sheet=self.sheet_guid)]
        )
        shunt_capacitor1.register(self.network)

        general2 = ShuntCapacitorMV.General(
            guid=self.shunt_capacitor_guid,
            name="SecondShuntCapacitor",
            node=self.node_guid,
        )
        shunt_capacitor2 = ShuntCapacitorMV(
            general2, [ElementPresentation(sheet=self.sheet_guid)]
        )
        shunt_capacitor2.register(self.network)

        # Should only have one shunt capacitor
        self.assertEqual(len(self.network.shunt_capacitors), 1)
        # Should be the second shunt capacitor
        self.assertEqual(
            self.network.shunt_capacitors[self.shunt_capacitor_guid].general.name,
            "SecondShuntCapacitor",
        )

    def test_minimal_shunt_capacitor_serialization(self) -> None:
        """Test that minimal shunt capacitors serialize correctly with only required fields."""
        general = ShuntCapacitorMV.General(
            guid=self.shunt_capacitor_guid,
            name="MinimalShuntCapacitor",
            node=self.node_guid,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        shunt_capacitor = ShuntCapacitorMV(general, [presentation])
        shunt_capacitor.register(self.network)

        serialized = shunt_capacitor.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalShuntCapacitor'", serialized)
        self.assertIn(f"Node:'{{{str(self.node_guid).upper()}}}'", serialized)

        # Default values should be included since using no_skip
        self.assertIn("CreationTime:0", serialized)
        self.assertNotIn("Variant:", serialized)  # False values are skipped
        self.assertIn("SwitchState:0", serialized)
        self.assertIn("NotPreferred:False", serialized)
        self.assertIn("Q:0", serialized)
        self.assertIn("Unom:0", serialized)
        self.assertIn("Earthing:False", serialized)
        self.assertIn("Re:0", serialized)
        self.assertIn("Xe:0", serialized)
        self.assertIn("VoltageControl:False", serialized)
        self.assertIn("Uon:0", serialized)
        self.assertIn("Uoff:0", serialized)
        self.assertIn("OnlyDuringMotorstart:False", serialized)
        self.assertIn("PassiveFilterFrequency:0", serialized)
        self.assertIn("PassiveFilterQualityFactor:0", serialized)

    def test_shunt_capacitor_with_reactive_power_serializes_correctly(self) -> None:
        """Test that shunt capacitors with reactive power serialize correctly."""
        general = ShuntCapacitorMV.General(
            guid=self.shunt_capacitor_guid,
            name="ReactiveShuntCapacitor",
            node=self.node_guid,
            Q=100.0,
            unom=20.0,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        shunt_capacitor = ShuntCapacitorMV(general, [presentation])
        shunt_capacitor.register(self.network)

        serialized = shunt_capacitor.serialize()
        self.assertIn("Q:100", serialized)
        self.assertIn("Unom:20", serialized)

    def test_shunt_capacitor_with_maintenance_properties_serializes_correctly(
        self,
    ) -> None:
        """Test that shunt capacitors with maintenance properties serialize correctly."""
        general = ShuntCapacitorMV.General(
            guid=self.shunt_capacitor_guid,
            name="MaintenanceShuntCapacitor",
            node=self.node_guid,
            failure_frequency=0.01,
            repair_duration=2.5,
            maintenance_frequency=0.1,
            maintenance_duration=4.0,
            maintenance_cancel_duration=1.0,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        shunt_capacitor = ShuntCapacitorMV(general, [presentation])
        shunt_capacitor.register(self.network)

        serialized = shunt_capacitor.serialize()
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("RepairDuration:2.5", serialized)
        self.assertIn("MaintenanceFrequency:0.1", serialized)
        self.assertIn("MaintenanceDuration:4.0", serialized)
        self.assertIn("MaintenanceCancelDuration:1.0", serialized)

    def test_shunt_capacitor_with_earthing_properties_serializes_correctly(
        self,
    ) -> None:
        """Test that shunt capacitors with earthing properties serialize correctly."""
        earthing_node_guid = Guid(UUID("8b7d4c3e-2f1a-4e5d-9c8b-7a6f5e4d3c2b"))

        general = ShuntCapacitorMV.General(
            guid=self.shunt_capacitor_guid,
            name="EarthingShuntCapacitor",
            node=self.node_guid,
            earthing=True,
            re=0.1,
            xe=0.2,
            earthing_node=earthing_node_guid,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        shunt_capacitor = ShuntCapacitorMV(general, [presentation])
        shunt_capacitor.register(self.network)

        serialized = shunt_capacitor.serialize()
        self.assertIn("Earthing:True", serialized)
        self.assertIn("Re:0.1", serialized)
        self.assertIn("Xe:0.2", serialized)
        self.assertIn(
            f"EarthingNode:'{{{str(earthing_node_guid).upper()}}}'", serialized
        )

    def test_shunt_capacitor_with_voltage_control_serializes_correctly(self) -> None:
        """Test that shunt capacitors with voltage control serialize correctly."""
        general = ShuntCapacitorMV.General(
            guid=self.shunt_capacitor_guid,
            name="VoltageControlShuntCapacitor",
            node=self.node_guid,
            voltage_control=True,
            u_on=21.0,
            u_off=19.0,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        shunt_capacitor = ShuntCapacitorMV(general, [presentation])
        shunt_capacitor.register(self.network)

        serialized = shunt_capacitor.serialize()
        self.assertIn("VoltageControl:True", serialized)
        self.assertIn("Uon:21", serialized)
        self.assertIn("Uoff:19", serialized)

    def test_shunt_capacitor_with_passive_filter_serializes_correctly(self) -> None:
        """Test that shunt capacitors with passive filter serialize correctly."""
        general = ShuntCapacitorMV.General(
            guid=self.shunt_capacitor_guid,
            name="PassiveFilterShuntCapacitor",
            node=self.node_guid,
            passive_filter_frequency=50.0,
            passive_filter_quality_factor=10.0,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        shunt_capacitor = ShuntCapacitorMV(general, [presentation])
        shunt_capacitor.register(self.network)

        serialized = shunt_capacitor.serialize()
        self.assertIn("PassiveFilterFrequency:50", serialized)
        self.assertIn("PassiveFilterQualityFactor:10", serialized)

    def test_shunt_capacitor_with_switch_state_serializes_correctly(self) -> None:
        """Test that shunt capacitors with switch state serialize correctly."""
        general = ShuntCapacitorMV.General(
            guid=self.shunt_capacitor_guid,
            name="SwitchStateShuntCapacitor",
            node=self.node_guid,
            switch_state=True,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        shunt_capacitor = ShuntCapacitorMV(general, [presentation])
        shunt_capacitor.register(self.network)

        serialized = shunt_capacitor.serialize()
        self.assertIn("SwitchState:1", serialized)

    def test_shunt_capacitor_with_field_name_serializes_correctly(self) -> None:
        """Test that shunt capacitors with field name serialize correctly."""
        general = ShuntCapacitorMV.General(
            guid=self.shunt_capacitor_guid,
            name="FieldNameShuntCapacitor",
            node=self.node_guid,
            field_name="TestField",
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        shunt_capacitor = ShuntCapacitorMV(general, [presentation])
        shunt_capacitor.register(self.network)

        serialized = shunt_capacitor.serialize()
        self.assertIn("FieldName:'TestField'", serialized)

    def test_shunt_capacitor_with_not_preferred_serializes_correctly(self) -> None:
        """Test that shunt capacitors with not preferred flag serialize correctly."""
        general = ShuntCapacitorMV.General(
            guid=self.shunt_capacitor_guid,
            name="NotPreferredShuntCapacitor",
            node=self.node_guid,
            not_preferred=True,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        shunt_capacitor = ShuntCapacitorMV(general, [presentation])
        shunt_capacitor.register(self.network)

        serialized = shunt_capacitor.serialize()
        self.assertIn("NotPreferred:True", serialized)

    def test_shunt_capacitor_with_only_during_motorstart_serializes_correctly(
        self,
    ) -> None:
        """Test that shunt capacitors with only during motorstart flag serialize correctly."""
        general = ShuntCapacitorMV.General(
            guid=self.shunt_capacitor_guid,
            name="OnlyDuringMotorstartShuntCapacitor",
            node=self.node_guid,
            only_during_motorstart=True,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        shunt_capacitor = ShuntCapacitorMV(general, [presentation])
        shunt_capacitor.register(self.network)

        serialized = shunt_capacitor.serialize()
        self.assertIn("OnlyDuringMotorstart:True", serialized)

    def test_shunt_capacitor_with_custom_profile_serializes_correctly(self) -> None:
        """Test that shunt capacitors with custom profile serialize correctly."""
        profile_guid = Guid(UUID("1a2b3c4d-5e6f-7890-abcd-ef1234567890"))

        general = ShuntCapacitorMV.General(
            guid=self.shunt_capacitor_guid,
            name="CustomProfileShuntCapacitor",
            node=self.node_guid,
            profile=profile_guid,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        shunt_capacitor = ShuntCapacitorMV(general, [presentation])
        shunt_capacitor.register(self.network)

        serialized = shunt_capacitor.serialize()
        self.assertIn(f"Profile:'{{{str(profile_guid).upper()}}}'", serialized)

    def test_shunt_capacitor_with_default_profile_skips_serialization(self) -> None:
        """Test that shunt capacitors with default profile skip profile serialization."""
        general = ShuntCapacitorMV.General(
            guid=self.shunt_capacitor_guid,
            name="DefaultProfileShuntCapacitor",
            node=self.node_guid,
            profile=DEFAULT_PROFILE_GUID,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        shunt_capacitor = ShuntCapacitorMV(general, [presentation])
        shunt_capacitor.register(self.network)

        serialized = shunt_capacitor.serialize()
        # Should not include profile since it's the default
        self.assertNotIn("Profile:", serialized)

    def test_shunt_capacitor_active_filter_serialization_works(self) -> None:
        """Test that shunt capacitor active filter serialization works correctly."""
        measure_field_guid = Guid(UUID("1a2b3c4d-5e6f-7890-abcd-ef1234567890"))

        active_filter = ShuntCapacitorMV.ActiveFilter(
            measure_field=measure_field_guid,
            inom=100.0,
            h={1: 1.0, 2: 2.0, 3: 3.0},
        )

        serialized = active_filter.serialize()

        self.assertIn(
            f"MeasureField:'{{{str(measure_field_guid).upper()}}}'", serialized
        )
        self.assertIn("Inom:100", serialized)
        self.assertIn("h1:1", serialized)
        self.assertIn("h2:2", serialized)
        self.assertIn("h3:3", serialized)

    def test_shunt_capacitor_active_filter_deserialization_works(self) -> None:
        """Test that shunt capacitor active filter deserialization works correctly."""
        measure_field_guid = Guid(UUID("1a2b3c4d-5e6f-7890-abcd-ef1234567890"))

        data = {
            "MeasureField": str(measure_field_guid),
            "Inom": 100.0,
            "h1": 1.0,
            "h2": 2.0,
            "h3": 3.0,
        }

        active_filter = ShuntCapacitorMV.ActiveFilter.deserialize(data)

        self.assertEqual(active_filter.measure_field, measure_field_guid)
        self.assertEqual(active_filter.inom, 100.0)
        if active_filter.h:
            self.assertEqual(active_filter.h[1], 1.0)
            self.assertEqual(active_filter.h[2], 2.0)
            self.assertEqual(active_filter.h[3], 3.0)


if __name__ == "__main__":
    unittest.main()
