"""Tests for TBatteryLS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid, encode_guid
from pyptp.elements.lv.battery import BatteryLV
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import ElementPresentation, NodePresentation
from pyptp.elements.lv.shared import EfficiencyType, HarmonicsType, PControl
from pyptp.elements.lv.sheet import SheetLV
from pyptp.elements.mixins import Extra, Note
from pyptp.network_lv import NetworkLV


class TestBatteryRegistration(unittest.TestCase):
    """Test battery registration and functionality."""

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

        self.battery_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_battery_registration_works(self) -> None:
        """Test that batteries can register themselves with the network."""
        general = BatteryLV.General(
            guid=self.battery_guid, name="TestBattery", node=self.node_guid
        )
        charge_efficiency = EfficiencyType()
        discharge_efficiency = EfficiencyType()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        battery = BatteryLV(
            general, [presentation], charge_efficiency, discharge_efficiency
        )
        battery.register(self.network)

        # Verify battery is in network
        self.assertIn(self.battery_guid, self.network.batteries)
        self.assertIs(self.network.batteries[self.battery_guid], battery)

    def test_battery_with_full_properties_serializes_correctly(self) -> None:
        """Test that batteries with all properties serialize correctly."""
        battery = self._create_full_battery()
        battery.register(self.network)

        # Test serialization
        serialized = battery.serialize()

        # Verify all sections are present
        self._verify_sections_present(serialized)

        # Verify key general properties are serialized
        self._verify_general_properties(serialized)

        # Verify inverter properties
        self._verify_inverter_properties(serialized)

        # Verify efficiency properties
        self._verify_efficiency_properties(serialized)

        # Verify power control properties
        self._verify_power_control_properties(serialized)

        # Verify harmonics properties
        self._verify_harmonics_properties(serialized)

        # Verify presentation properties
        self._verify_presentation_properties(serialized)

        # Verify extras and notes
        self._verify_extras_and_notes(serialized)

        # Verify efficiency data is present
        self._verify_efficiency_data(serialized)

    def _create_full_battery(self) -> BatteryLV:
        """Create a battery with all properties set."""
        general = BatteryLV.General(
            guid=self.battery_guid,
            node=self.node_guid,
            name="FullBattery",
            s_L1=True,
            s_L2=False,
            s_L3=True,
            s_N=False,
            field_name="BatteryField",
            single_phase=True,
            phase=2,
            pref=50.0,
            state_of_charge=75.0,
            capacity=200.0,
            c_rate=1.0,
            harmonics_type="Type1",
        )

        inverter = BatteryLV.Inverter(
            s_nom=25.0,
            charge_efficiency_type="ChargeType",
            discharge_efficiency_type="DischargeType",
            cos_ref=0.95,
        )

        harmonics = HarmonicsType(
            h=[1.0, 2.0, 3.0] + [0.0] * 96, angle=[0.0, 90.0, 180.0] + [0.0] * 96
        )

        charge_efficiency = EfficiencyType(
            input1=10.0,
            output1=9.0,
            input2=20.0,
            output2=17.0,
            input3=30.0,
            output3=24.0,
        )

        discharge_efficiency = EfficiencyType(
            input1=15.0,
            output1=13.2,
            input2=25.0,
            output2=20.75,
            input3=35.0,
            output3=27.3,
        )

        power_control = PControl(
            sort=1,
            input1=10.0,
            output1=8.0,
            input2=20.0,
            output2=16.0,
            input3=30.0,
            output3=24.0,
            measure_field="PowerControl",
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

        battery = BatteryLV(
            general,
            [presentation],
            charge_efficiency,
            discharge_efficiency,
            power_control,
            inverter,
            harmonics,
        )
        battery.extras.append(Extra(text="foo=bar"))
        battery.notes.append(Note(text="Test note"))
        return battery

    def _verify_sections_present(self, serialized: str) -> None:
        """Verify all required sections are present in serialized output."""
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#Inverter", serialized)
        self.assertIn("#PControl", serialized)
        self.assertIn("#ChargeEfficiencyType", serialized)
        self.assertIn("#DischargeEfficiencyType", serialized)
        self.assertIn("#HarmonicsType", serialized)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

    def _verify_general_properties(self, serialized: str) -> None:
        """Verify general properties are serialized correctly."""
        self.assertIn("Name:'FullBattery'", serialized)
        self.assertIn("FieldName:'BatteryField'", serialized)
        self.assertIn("s_L1:True", serialized)
        self.assertIn("s_L2:False", serialized)
        self.assertIn("s_L3:True", serialized)
        self.assertIn("s_N:False", serialized)
        self.assertIn("OnePhase:True", serialized)
        self.assertIn("Phase:2", serialized)
        self.assertIn("Pref:50.0", serialized)
        self.assertIn("StateOfCharge:75.0", serialized)
        self.assertIn("Capacity:200.0", serialized)
        self.assertIn("Crate:1.0", serialized)
        self.assertIn("HarmonicsType:'Type1'", serialized)

    def _verify_inverter_properties(self, serialized: str) -> None:
        """Verify inverter properties are serialized correctly."""
        self.assertIn("Snom:25.0", serialized)
        self.assertIn("ChargeEfficiencyType:'ChargeType'", serialized)
        self.assertIn("DischargeEfficiencyType:'DischargeType'", serialized)
        self.assertIn("Cosref:0.95", serialized)

    def _verify_efficiency_properties(self, serialized: str) -> None:
        """Verify efficiency properties are serialized correctly."""
        self.assertIn("Input1:10.0", serialized)
        self.assertIn("Output1:9.0", serialized)
        self.assertIn("Input2:20.0", serialized)
        self.assertIn("Output2:17.0", serialized)
        self.assertIn("Input3:30.0", serialized)
        self.assertIn("Output3:24.0", serialized)
        self.assertIn("Input1:15.0", serialized)
        self.assertIn("Output1:13.2", serialized)
        self.assertIn("Input2:25.0", serialized)
        self.assertIn("Output2:20.75", serialized)
        self.assertIn("Input3:35.0", serialized)
        self.assertIn("Output3:27.3", serialized)

    def _verify_power_control_properties(self, serialized: str) -> None:
        """Verify power control properties are serialized correctly."""
        self.assertIn("Sort:1", serialized)
        self.assertIn("StartTime1:0.0", serialized)
        self.assertIn("EndTime1:0.0", serialized)
        self.assertIn("Input1:10.0", serialized)
        self.assertIn("Output1:8.0", serialized)
        self.assertIn("StartTime2:0.0", serialized)
        self.assertIn("EndTime2:0.0", serialized)
        self.assertIn("Input2:20.0", serialized)
        self.assertIn("Output2:16.0", serialized)
        self.assertIn("StartTime3:0.0", serialized)
        self.assertIn("EndTime3:0.0", serialized)
        self.assertIn("Input3:30.0", serialized)
        self.assertIn("Output3:24.0", serialized)
        self.assertIn("MeasureField:'PowerControl'", serialized)

    def _verify_harmonics_properties(self, serialized: str) -> None:
        """Verify harmonics properties are serialized correctly."""
        self.assertIn("h1:1.0", serialized)
        self.assertIn("h2:2.0", serialized)
        self.assertIn("h3:3.0", serialized)
        self.assertIn("Angle2:90.0", serialized)
        self.assertIn("Angle3:180.0", serialized)

    def _verify_presentation_properties(self, serialized: str) -> None:
        """Verify presentation properties are serialized correctly."""
        self.assertIn(f"Sheet:{encode_guid(self.sheet_guid)}", serialized)
        self.assertIn("X:100", serialized)
        self.assertIn("Y:200", serialized)
        self.assertIn("Color:$00FF00", serialized)
        self.assertIn("TextColor:$FF0000", serialized)

    def _verify_extras_and_notes(self, serialized: str) -> None:
        """Verify extras and notes are serialized correctly."""
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)

    def _verify_efficiency_data(self, serialized: str) -> None:
        """Verify efficiency data is present in serialized output."""
        self.assertIn("Input1:10.0", serialized)
        self.assertIn("Output1:9.0", serialized)
        self.assertIn("Input2:20.0", serialized)
        self.assertIn("Output2:17.0", serialized)
        self.assertIn("Input3:30.0", serialized)
        self.assertIn("Output3:24.0", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a battery with the same GUID overwrites the existing one."""
        general1 = BatteryLV.General(
            guid=self.battery_guid, name="FirstBattery", node=self.node_guid
        )
        battery1 = BatteryLV(
            general1,
            [ElementPresentation(sheet=self.sheet_guid)],
            EfficiencyType(),
            EfficiencyType(),
        )
        battery1.register(self.network)

        general2 = BatteryLV.General(
            guid=self.battery_guid, name="SecondBattery", node=self.node_guid
        )
        battery2 = BatteryLV(
            general2,
            [ElementPresentation(sheet=self.sheet_guid)],
            EfficiencyType(),
            EfficiencyType(),
        )
        battery2.register(self.network)

        # Should only have one battery
        self.assertEqual(len(self.network.batteries), 1)
        # Should be the second battery
        self.assertEqual(
            self.network.batteries[self.battery_guid].general.name, "SecondBattery"
        )

    def test_battery_with_profile_guid_serializes_correctly(self) -> None:
        """Test that batteries with profile GUID serialize correctly."""
        profile_guid = Guid(UUID("12345678-1234-5678-9abc-123456789abc"))

        general = BatteryLV.General(
            guid=self.battery_guid,
            name="ProfileBattery",
            node=self.node_guid,
            profile=profile_guid,
        )
        charge_efficiency = EfficiencyType()
        discharge_efficiency = EfficiencyType()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        battery = BatteryLV(
            general, [presentation], charge_efficiency, discharge_efficiency
        )
        battery.register(self.network)

        serialized = battery.serialize()

        # Verify profile GUID is serialized
        self.assertIn(f"Profile:'{{{str(profile_guid).upper()}}}'", serialized)

    def test_minimal_battery_serialization(self) -> None:
        """Test that minimal batteries serialize correctly with only required fields."""
        general = BatteryLV.General(
            guid=self.battery_guid, name="MinimalBattery", node=self.node_guid
        )
        charge_efficiency = EfficiencyType()
        discharge_efficiency = EfficiencyType()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        battery = BatteryLV(
            general, [presentation], charge_efficiency, discharge_efficiency
        )
        battery.register(self.network)

        serialized = battery.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#ChargeEfficiencyType", serialized)
        self.assertIn("#DischargeEfficiencyType", serialized)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalBattery'", serialized)
        self.assertIn("s_L1:True", serialized)  # Default values
        self.assertIn("s_L2:True", serialized)
        self.assertIn("s_L3:True", serialized)
        self.assertIn("s_N:True", serialized)
        self.assertIn("OnePhase:False", serialized)  # Default value
        self.assertIn("Pref:0.0", serialized)  # Default value
        self.assertIn("StateOfCharge:0.0", serialized)  # Default value
        self.assertIn("Capacity:100", serialized)  # Default value
        self.assertIn("Crate:0.5", serialized)  # Default value

        # Should not have optional sections
        self.assertNotIn("#Inverter", serialized)
        self.assertNotIn("#PControl", serialized)
        self.assertNotIn("#HarmonicsType", serialized)
        self.assertNotIn("#Extra", serialized)
        self.assertNotIn("#Note", serialized)

    def test_multiple_presentations_serialize_correctly(self) -> None:
        """Test that batteries with multiple presentations serialize correctly."""
        general = BatteryLV.General(
            guid=self.battery_guid, name="MultiPresBattery", node=self.node_guid
        )
        charge_efficiency = EfficiencyType()
        discharge_efficiency = EfficiencyType()

        pres1 = ElementPresentation(
            sheet=self.sheet_guid, x=100, y=100, color=DelphiColor("$FF0000")
        )
        pres2 = ElementPresentation(
            sheet=self.sheet_guid, x=200, y=200, color=DelphiColor("$00FF00")
        )

        battery = BatteryLV(
            general, [pres1, pres2], charge_efficiency, discharge_efficiency
        )
        battery.register(self.network)

        serialized = battery.serialize()

        # Should have two presentations
        self.assertEqual(serialized.count("#Presentation"), 2)
        self.assertIn("Color:$FF0000", serialized)
        self.assertIn("Color:$00FF00", serialized)
        self.assertIn("X:100", serialized)
        self.assertIn("X:200", serialized)

    def test_battery_with_complex_efficiency_data_serializes_correctly(self) -> None:
        """Test that batteries with complex efficiency data serialize correctly."""
        general = BatteryLV.General(
            guid=self.battery_guid, name="EfficiencyBattery", node=self.node_guid
        )

        # Create efficiency data with more complex values
        charge_input_values = [i * 5.0 for i in range(1, 11)]
        charge_output_values = [i * 4.5 for i in range(1, 11)]

        discharge_input_values = [i * 6.0 for i in range(1, 11)]
        discharge_output_values = [i * 5.4 for i in range(1, 11)]

        charge_efficiency = EfficiencyType(
            input1=charge_input_values[0],
            output1=charge_output_values[0],
            input2=charge_input_values[1],
            output2=charge_output_values[1],
            input3=charge_input_values[2],
            output3=charge_output_values[2],
            input4=charge_input_values[3],
            output4=charge_output_values[3],
            input5=charge_input_values[4],
            output5=charge_output_values[4],
        )
        discharge_efficiency = EfficiencyType(
            input1=discharge_input_values[0],
            output1=discharge_output_values[0],
            input2=discharge_input_values[1],
            output2=discharge_output_values[1],
            input3=discharge_input_values[2],
            output3=discharge_output_values[2],
            input4=discharge_input_values[3],
            output4=discharge_output_values[3],
            input5=discharge_input_values[4],
            output5=discharge_output_values[4],
        )

        presentation = ElementPresentation(sheet=self.sheet_guid)

        battery = BatteryLV(
            general, [presentation], charge_efficiency, discharge_efficiency
        )
        battery.register(self.network)

        serialized = battery.serialize()

        # Verify efficiency sections are present
        self.assertIn("#ChargeEfficiencyType", serialized)
        self.assertIn("#DischargeEfficiencyType", serialized)

        # Verify efficiency data is serialized (check for some key values)
        self.assertIn("Input1:5.0", serialized)
        self.assertIn("Output1:4.5", serialized)
        self.assertIn("Input2:10.0", serialized)
        self.assertIn("Output2:9.0", serialized)
        self.assertIn("Input3:15.0", serialized)
        self.assertIn("Output3:13.5", serialized)
        self.assertIn("Input4:20.0", serialized)
        self.assertIn("Output4:18.0", serialized)
        self.assertIn("Input5:25.0", serialized)
        self.assertIn("Output5:22.5", serialized)

        # Verify discharge efficiency data is present
        self.assertIn("Input1:6.0", serialized)
        self.assertIn("Output1:5.4", serialized)
        self.assertIn("Input2:12.0", serialized)
        self.assertIn("Output2:10.8", serialized)
        self.assertIn("Input3:18.0", serialized)
        self.assertIn("Output3:16.2", serialized)
        self.assertIn("Input4:24.0", serialized)
        self.assertIn("Output4:21.6", serialized)
        self.assertIn("Input5:30.0", serialized)
        self.assertIn("Output5:27.0", serialized)


if __name__ == "__main__":
    unittest.main()
