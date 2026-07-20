"""Tests for BatteryLV behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid, encode_guid
from pyptp.elements.lv.battery import BatteryLV
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import ElementPresentation, NodePresentation
from pyptp.elements.lv.shared import EfficiencyType, HarmonicsType
from pyptp.elements.lv.sheet import SheetLV
from pyptp.elements.mixins import Extra, Note
from pyptp.IO.importers._gnf_handlers.battery_handler import BatteryHandler
from pyptp.network_lv import NetworkLV


def _line_with_prefix(serialized: str, prefix: str) -> str:
    """Return the single serialized line starting with the given tag prefix."""
    for line in serialized.splitlines():
        if line.startswith(prefix):
            return line
    return ""


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
        self.measure_field_guid = Guid(UUID("aabbccdd-1122-3344-5566-778899aabbcc"))

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

        serialized = battery.serialize()

        self._verify_sections_present(serialized)
        self._verify_general_properties(serialized)
        self._verify_inverter_properties(serialized)
        self._verify_efficiency_properties(serialized)
        self._verify_control_properties(serialized)
        self._verify_harmonics_properties(serialized)
        self._verify_presentation_properties(serialized)
        self._verify_extras_and_notes(serialized)

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

        pu_control = BatteryLV.PUControl(
            input1=0.9,
            output1=1.0,
            input2=1.05,
            output2=0.5,
        )

        pi_control = BatteryLV.PIControl(
            input1=0.1,
            output1=0.8,
            input2=1.2,
            output2=0.2,
            measure_field1=self.measure_field_guid,
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
            pu_control=pu_control,
            pi_control=pi_control,
            inverter=inverter,
            harmonics=harmonics,
        )
        battery.extras.append(Extra(text="foo=bar"))
        battery.notes.append(Note(text="Test note"))
        return battery

    def _verify_sections_present(self, serialized: str) -> None:
        """Verify all required sections are present in serialized output."""
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#Inverter", serialized)
        self.assertIn("#P(U)Control", serialized)
        self.assertIn("#P(I)Control", serialized)
        self.assertNotIn("#PControl", serialized)
        self.assertNotIn("Crate", serialized)
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
        self.assertIn("HarmonicsType:'Type1'", serialized)

    def _verify_inverter_properties(self, serialized: str) -> None:
        """Verify inverter properties are serialized correctly."""
        self.assertIn("Snom:25.0", serialized)
        self.assertIn("ChargeEfficiencyType:'ChargeType'", serialized)
        self.assertIn("DischargeEfficiencyType:'DischargeType'", serialized)
        self.assertIn("Cosref:0.95", serialized)

    def _verify_efficiency_properties(self, serialized: str) -> None:
        """Verify efficiency properties are serialized correctly."""
        charge_line = _line_with_prefix(serialized, "#ChargeEfficiencyType")
        self.assertIn("Input1:10.0", charge_line)
        self.assertIn("Output1:9.0", charge_line)
        self.assertIn("Input3:30.0", charge_line)

        discharge_line = _line_with_prefix(serialized, "#DischargeEfficiencyType")
        self.assertIn("Input1:15.0", discharge_line)
        self.assertIn("Output2:20.75", discharge_line)
        self.assertIn("Output3:27.3", discharge_line)

    def _verify_control_properties(self, serialized: str) -> None:
        """Verify P(U) and P(I) control properties are serialized correctly."""
        pu_line = _line_with_prefix(serialized, "#P(U)Control")
        self.assertIn("Input1:0.9", pu_line)
        self.assertIn("Output1:1.0", pu_line)
        self.assertIn("Input2:1.05", pu_line)
        self.assertNotIn("MeasureField", pu_line)

        pi_line = _line_with_prefix(serialized, "#P(I)Control")
        self.assertIn("Input1:0.1", pi_line)
        self.assertIn("Output1:0.8", pi_line)
        self.assertIn(
            f"MeasureField1:'{{{str(self.measure_field_guid).upper()}}}'", pi_line
        )

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

    def test_full_battery_round_trip_through_handler(self) -> None:
        """Test that a fully-populated battery round-trips through the GNF handler."""
        battery = self._create_full_battery()
        section = battery.serialize()

        reloaded_network = NetworkLV()
        BatteryHandler().handle(reloaded_network, section.rstrip() + "\n#END")

        self.assertEqual(len(reloaded_network.batteries), 1)
        reloaded = reloaded_network.batteries[self.battery_guid]

        # Controls and their measure field survive the round trip.
        assert reloaded.pu_control is not None
        assert reloaded.pi_control is not None
        self.assertEqual(reloaded.pu_control.input1, 0.9)
        self.assertEqual(reloaded.pi_control.output1, 0.8)
        self.assertEqual(
            str(reloaded.pi_control.measure_field1).upper(),
            str(self.measure_field_guid).upper(),
        )

        # Extras and notes are handled by the generic declarative path.
        self.assertEqual([e.text for e in reloaded.extras], ["foo=bar"])
        self.assertEqual([n.text for n in reloaded.notes], ["Test note"])

        # Serializing the reloaded battery reproduces the original section.
        self.assertEqual(reloaded.serialize(), section)

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
        self.assertIn("StateOfCharge:50.0", serialized)  # Default value, always written

        # Defaults that Gaia skips when zero/false must not appear
        self.assertNotIn("OnePhase:", serialized)
        self.assertNotIn("Pref:", serialized)
        self.assertNotIn("Capacity:", serialized)

        # Crate is no longer part of the model (derived in Gaia 8.12)
        self.assertNotIn("Crate", serialized)

        # Should not have optional sections
        self.assertNotIn("#Inverter", serialized)
        self.assertNotIn("#P(U)Control", serialized)
        self.assertNotIn("#P(I)Control", serialized)
        self.assertNotIn("#PControl", serialized)
        self.assertNotIn("#HarmonicsType", serialized)
        self.assertNotIn("#Extra", serialized)
        self.assertNotIn("#Note", serialized)

    def test_defaults_match_gaia_new_battery(self) -> None:
        """Test that creation defaults mirror Gaia's new-battery defaults."""
        general = BatteryLV.General()
        self.assertEqual(general.state_of_charge, 50.0)
        self.assertEqual(general.capacity, 0.0)

        inverter = BatteryLV.Inverter()
        self.assertEqual(inverter.s_nom, 0.0)
        self.assertEqual(inverter.cos_ref, 1.0)
        self.assertEqual(inverter.charge_efficiency_type, "0,1..1 pu: 95 %")
        self.assertEqual(inverter.discharge_efficiency_type, "0,1..1 pu: 95 %")

        self.assertEqual(BatteryLV.PUControl().input1, 1.0)
        self.assertEqual(BatteryLV.PIControl().input1, 1.0)

        battery = BatteryLV(
            BatteryLV.General(guid=self.battery_guid, node=self.node_guid),
            [ElementPresentation(sheet=self.sheet_guid)],
        )
        for efficiency in (battery.charge_efficiency, battery.discharge_efficiency):
            self.assertEqual(efficiency.input1, 0.0)
            self.assertEqual(efficiency.output1, 10.0)
            self.assertEqual(efficiency.input2, 0.1)
            self.assertEqual(efficiency.output2, 95.0)
            self.assertEqual(efficiency.input3, 1.0)
            self.assertEqual(efficiency.output3, 95.0)
        # Distinct instances so mutating one curve does not affect the other
        self.assertIsNot(battery.charge_efficiency, battery.discharge_efficiency)

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

        charge_line = _line_with_prefix(serialized, "#ChargeEfficiencyType")
        self.assertIn("Input1:5.0", charge_line)
        self.assertIn("Output1:4.5", charge_line)
        self.assertIn("Input5:25.0", charge_line)
        self.assertIn("Output5:22.5", charge_line)

        discharge_line = _line_with_prefix(serialized, "#DischargeEfficiencyType")
        self.assertIn("Input1:6.0", discharge_line)
        self.assertIn("Output1:5.4", discharge_line)
        self.assertIn("Input5:30.0", discharge_line)
        self.assertIn("Output5:27.0", discharge_line)


if __name__ == "__main__":
    unittest.main()
