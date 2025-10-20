"""Tests for TBatteryMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import DEFAULT_PROFILE_GUID, Guid
from pyptp.elements.mixins import Extra, Note
from pyptp.elements.mv.battery import BatteryMV
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import ElementPresentation, NodePresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.network_mv import NetworkMV


class TestBatteryRegistration(unittest.TestCase):
    """Test battery registration and functionality."""

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

        # Create and register a node for the battery
        node = NodeMV(
            NodeMV.General(
                guid=Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5")), name="TestNode"
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node.register(self.network)
        self.node_guid = node.general.guid

        self.battery_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_battery_registration_works(self) -> None:
        """Test that batteries can register themselves with the network."""
        general = BatteryMV.General(
            guid=self.battery_guid, name="TestBattery", node=self.node_guid
        )
        inverter = BatteryMV.Inverter(snom=100.0, unom=0.4)
        presentation = ElementPresentation(sheet=self.sheet_guid)

        battery = BatteryMV(general, inverter, [presentation])
        battery.register(self.network)

        # Verify battery is in network
        self.assertIn(self.battery_guid, self.network.batteries)
        self.assertIs(self.network.batteries[self.battery_guid], battery)

    def test_battery_with_full_properties_serializes_correctly(self) -> None:
        """Test that batteries with all properties serialize correctly."""
        general = BatteryMV.General(
            guid=self.battery_guid,
            node=self.node_guid,
            creation_time=123.45,
            mutation_date=10,
            revision_date=20,
            variant=True,
            name="FullBattery",
            switch_state=True,
            field_name="TestField",
            failure_frequency=0.01,
            repair_duration=2.5,
            maintenance_frequency=0.1,
            maintenance_duration=4.0,
            maintenance_cancel_duration=1.0,
            not_preferred=True,
            pref=50.0,
            state_of_charge=0.8,
            capacity=100.0,
            c_rate=0.5,
            harmonics_type="TestHarmonics",
        )

        inverter = BatteryMV.Inverter(
            snom=100.0,
            unom=0.4,
            ik_inom=1.1,
            charge_efficiency_type="ChargeType",
            discharge_efficiency_type="DischargeType",
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

        battery = BatteryMV(general, inverter, [presentation])
        battery.extras.append(Extra(text="foo=bar"))
        battery.notes.append(Note(text="Test note"))
        battery.register(self.network)

        # Test serialization
        serialized = battery.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertEqual(serialized.count("#Inverter"), 1)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify general properties
        self.assertIn("Name:'FullBattery'", serialized)
        self.assertIn("Variant:True", serialized)
        self.assertIn("SwitchState:1", serialized)  # True -> 1
        self.assertIn("FieldName:'TestField'", serialized)
        self.assertIn("NotPreferred:True", serialized)
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("RepairDuration:2.5", serialized)
        self.assertIn("MaintenanceFrequency:0.1", serialized)
        self.assertIn("MaintenanceDuration:4.0", serialized)
        self.assertIn("MaintenanceCancelDuration:1.0", serialized)
        self.assertIn("Pref:50", serialized)
        self.assertIn("StateOfCharge:0.8", serialized)
        self.assertIn("Capacity:100", serialized)
        self.assertIn("Crate:0.5", serialized)
        self.assertIn("HarmonicsType:'TestHarmonics'", serialized)

        # Verify node reference
        self.assertIn(f"Node:'{{{str(self.node_guid).upper()}}}'", serialized)

        # Verify inverter properties
        self.assertIn("Snom:100", serialized)
        self.assertIn("Unom:0.4", serialized)
        self.assertIn("Ik/Inom:1.1", serialized)
        self.assertIn("ChargeEfficiencyType:'ChargeType'", serialized)
        self.assertIn("DischargeEfficiencyType:'DischargeType'", serialized)

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
        """Test that registering a battery with the same GUID overwrites the existing one."""
        general1 = BatteryMV.General(
            guid=self.battery_guid, name="FirstBattery", node=self.node_guid
        )
        inverter1 = BatteryMV.Inverter(snom=50.0)
        battery1 = BatteryMV(
            general1, inverter1, [ElementPresentation(sheet=self.sheet_guid)]
        )
        battery1.register(self.network)

        general2 = BatteryMV.General(
            guid=self.battery_guid, name="SecondBattery", node=self.node_guid
        )
        inverter2 = BatteryMV.Inverter(snom=100.0)
        battery2 = BatteryMV(
            general2, inverter2, [ElementPresentation(sheet=self.sheet_guid)]
        )
        battery2.register(self.network)

        # Should only have one battery
        self.assertEqual(len(self.network.batteries), 1)
        # Should be the second battery
        self.assertEqual(
            self.network.batteries[self.battery_guid].general.name, "SecondBattery"
        )

    def test_minimal_battery_serialization(self) -> None:
        """Test that minimal batteries serialize correctly with only required fields."""
        general = BatteryMV.General(
            guid=self.battery_guid, name="MinimalBattery", node=self.node_guid
        )
        inverter = BatteryMV.Inverter()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        battery = BatteryMV(general, inverter, [presentation])
        battery.register(self.network)

        serialized = battery.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertEqual(serialized.count("#Inverter"), 1)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties with updated defaults
        self.assertIn("Name:'MinimalBattery'", serialized)
        self.assertIn(
            "SwitchState:0", serialized
        )  # Now always appears as integer due to write_boolean_as_byte_no_skip
        self.assertIn("StateOfCharge:50", serialized)  # New default is 50.0
        self.assertIn("Crate:0.5", serialized)  # New default is 0.5
        self.assertIn("Ik/Inom:1", serialized)  # New default is 1.0 and always appears

        # Should not have optional sections
        self.assertNotIn("#PControl", serialized)
        self.assertNotIn("#QControl", serialized)
        self.assertNotIn("#ChargeEfficiencyType", serialized)
        self.assertNotIn("#DischargeEfficiencyType", serialized)

    def test_battery_with_capacity_properties_serializes_correctly(self) -> None:
        """Test that batteries with capacity properties serialize correctly."""
        general = BatteryMV.General(
            guid=self.battery_guid,
            name="CapacityBattery",
            node=self.node_guid,
            capacity=100.0,
            c_rate=0.5,
            state_of_charge=0.8,
        )
        inverter = BatteryMV.Inverter(snom=100.0)
        presentation = ElementPresentation(sheet=self.sheet_guid)

        battery = BatteryMV(general, inverter, [presentation])
        battery.register(self.network)

        serialized = battery.serialize()
        self.assertIn("Capacity:100", serialized)
        self.assertIn("Crate:0.5", serialized)
        self.assertIn("StateOfCharge:0.8", serialized)

    def test_battery_with_default_capacity_properties_serializes_correctly(
        self,
    ) -> None:
        """Test that batteries with default capacity properties serialize correctly."""
        general = BatteryMV.General(
            guid=self.battery_guid,
            name="DefaultCapacityBattery",
            node=self.node_guid,
            # Using default values: StateOfCharge=50.0, Crate=0.5, Capacity=0.0
        )
        inverter = BatteryMV.Inverter(snom=100.0)
        presentation = ElementPresentation(sheet=self.sheet_guid)

        battery = BatteryMV(general, inverter, [presentation])
        battery.register(self.network)

        serialized = battery.serialize()
        # Default values should appear or be skipped based on Delphi behavior
        self.assertIn("StateOfCharge:50", serialized)  # New default appears
        self.assertIn("Crate:0.5", serialized)  # New default appears

    def test_battery_with_power_reference_serializes_correctly(self) -> None:
        """Test that batteries with power reference serialize correctly."""
        general = BatteryMV.General(
            guid=self.battery_guid,
            name="PowerRefBattery",
            node=self.node_guid,
            pref=50.0,
        )
        inverter = BatteryMV.Inverter(snom=100.0)
        presentation = ElementPresentation(sheet=self.sheet_guid)

        battery = BatteryMV(general, inverter, [presentation])
        battery.register(self.network)

        serialized = battery.serialize()
        self.assertIn("Pref:50", serialized)

    def test_battery_with_inverter_properties_serializes_correctly(self) -> None:
        """Test that batteries with inverter properties serialize correctly."""
        general = BatteryMV.General(
            guid=self.battery_guid, name="InverterBattery", node=self.node_guid
        )
        inverter = BatteryMV.Inverter(
            snom=100.0,
            unom=0.4,
            ik_inom=1.1,
            charge_efficiency_type="ChargeType",
            discharge_efficiency_type="DischargeType",
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        battery = BatteryMV(general, inverter, [presentation])
        battery.register(self.network)

        serialized = battery.serialize()
        self.assertIn("Snom:100", serialized)
        self.assertIn("Unom:0.4", serialized)
        self.assertIn("Ik/Inom:1.1", serialized)
        self.assertIn("ChargeEfficiencyType:'ChargeType'", serialized)
        self.assertIn("DischargeEfficiencyType:'DischargeType'", serialized)

    def test_battery_ik_inom_default_always_appears(self) -> None:
        """Test that Ik/Inom always appears with correct default value."""
        general = BatteryMV.General(
            guid=self.battery_guid, name="DefaultIkInomBattery", node=self.node_guid
        )
        inverter = BatteryMV.Inverter()  # Use all defaults
        presentation = ElementPresentation(sheet=self.sheet_guid)

        battery = BatteryMV(general, inverter, [presentation])
        battery.register(self.network)

        serialized = battery.serialize()
        # Ik/Inom should always appear with default value of 1.0
        self.assertIn("Ik/Inom:1", serialized)

    def test_battery_with_maintenance_properties_serializes_correctly(self) -> None:
        """Test that batteries with maintenance properties serialize correctly."""
        general = BatteryMV.General(
            guid=self.battery_guid,
            name="MaintenanceBattery",
            node=self.node_guid,
            failure_frequency=0.01,
            repair_duration=2.5,
            maintenance_frequency=0.1,
            maintenance_duration=4.0,
            maintenance_cancel_duration=1.0,
        )
        inverter = BatteryMV.Inverter(snom=100.0)
        presentation = ElementPresentation(sheet=self.sheet_guid)

        battery = BatteryMV(general, inverter, [presentation])
        battery.register(self.network)

        serialized = battery.serialize()
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("RepairDuration:2.5", serialized)
        self.assertIn("MaintenanceFrequency:0.1", serialized)
        self.assertIn("MaintenanceDuration:4.0", serialized)
        self.assertIn("MaintenanceCancelDuration:1.0", serialized)

    def test_battery_with_switch_state_serializes_correctly(self) -> None:
        """Test that batteries with switch state serialize correctly."""
        # Test both True and False states since SwitchState now always appears
        general_true = BatteryMV.General(
            guid=self.battery_guid,
            name="SwitchStateBattery",
            node=self.node_guid,
            switch_state=True,
        )
        inverter = BatteryMV.Inverter(snom=100.0)
        presentation = ElementPresentation(sheet=self.sheet_guid)

        battery_true = BatteryMV(general_true, inverter, [presentation])
        battery_true.register(self.network)

        serialized_true = battery_true.serialize()
        self.assertIn("SwitchState:1", serialized_true)

        general_false = BatteryMV.General(
            guid=Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14d")),
            name="SwitchStateBatteryFalse",
            node=self.node_guid,
            switch_state=False,
        )
        battery_false = BatteryMV(general_false, inverter, [presentation])

        serialized_false = battery_false.serialize()
        self.assertIn("SwitchState:0", serialized_false)

    def test_battery_with_harmonics_serializes_correctly(self) -> None:
        """Test that batteries with harmonics properties serialize correctly."""
        general = BatteryMV.General(
            guid=self.battery_guid,
            name="HarmonicsBattery",
            node=self.node_guid,
            harmonics_type="TestHarmonics",
        )
        inverter = BatteryMV.Inverter(snom=100.0)
        presentation = ElementPresentation(sheet=self.sheet_guid)

        battery = BatteryMV(general, inverter, [presentation])
        battery.register(self.network)

        serialized = battery.serialize()
        self.assertIn("HarmonicsType:'TestHarmonics'", serialized)

    def test_battery_with_field_name_serializes_correctly(self) -> None:
        """Test that batteries with field name serialize correctly."""
        general = BatteryMV.General(
            guid=self.battery_guid,
            name="FieldNameBattery",
            node=self.node_guid,
            field_name="TestField",
        )
        inverter = BatteryMV.Inverter(snom=100.0)
        presentation = ElementPresentation(sheet=self.sheet_guid)

        battery = BatteryMV(general, inverter, [presentation])
        battery.register(self.network)

        serialized = battery.serialize()
        self.assertIn("FieldName:'TestField'", serialized)

    def test_battery_with_not_preferred_serializes_correctly(self) -> None:
        """Test that batteries with not preferred flag serialize correctly."""
        general = BatteryMV.General(
            guid=self.battery_guid,
            name="NotPreferredBattery",
            node=self.node_guid,
            not_preferred=True,
        )
        inverter = BatteryMV.Inverter(snom=100.0)
        presentation = ElementPresentation(sheet=self.sheet_guid)

        battery = BatteryMV(general, inverter, [presentation])
        battery.register(self.network)

        serialized = battery.serialize()
        self.assertIn("NotPreferred:True", serialized)

    def test_battery_profile_guid_serialization(self) -> None:
        """Test that Profile GUID serializes correctly when it has meaningful values."""
        # Test with DEFAULT_PROFILE_GUID (should appear in output now)
        profile_guid = Guid(UUID("A4D813DF-1EE1-4153-806C-DC228D251A79"))
        general_with_profile = BatteryMV.General(
            guid=self.battery_guid,
            name="ProfileBattery",
            node=self.node_guid,
            profile=profile_guid,
        )
        inverter = BatteryMV.Inverter()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        battery_with_profile = BatteryMV(general_with_profile, inverter, [presentation])
        battery_with_profile.register(self.network)

        serialized = battery_with_profile.serialize()
        # Profile should appear when it has a meaningful value
        self.assertIn(f"Profile:'{{{str(profile_guid).upper()}}}'", serialized)

        # Test with default profile (should also appear now, unlike before)
        general_default_profile = BatteryMV.General(
            guid=Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14e")),  # Different GUID
            name="DefaultProfileBattery",
            node=self.node_guid,
            profile=DEFAULT_PROFILE_GUID,
        )

        battery_default_profile = BatteryMV(
            general_default_profile, inverter, [presentation]
        )

        serialized_default = battery_default_profile.serialize()
        # DEFAULT_PROFILE_GUID should now appear in output (fixed behavior)
        self.assertIn(
            f"Profile:'{{{str(DEFAULT_PROFILE_GUID).upper()}}}'", serialized_default
        )


if __name__ == "__main__":
    unittest.main()
