"""Tests for TAsynchronousMotorMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid
from pyptp.elements.mixins import Extra, Note
from pyptp.elements.mv.async_motor import AsynchronousMotorMV
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import ElementPresentation, NodePresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.network_mv import NetworkMV


class TestAsynchronousMotorRegistration(unittest.TestCase):
    """Test asynchronous motor registration and functionality."""

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

        # Create and register a node for the motor
        node = NodeMV(
            NodeMV.General(
                guid=Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5")), name="TestNode"
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node.register(self.network)
        self.node_guid = node.general.guid

        self.motor_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_async_motor_registration_works(self) -> None:
        """Test that asynchronous motors can register themselves with the network."""
        general = AsynchronousMotorMV.General(
            guid=self.motor_guid, name="TestMotor", node=self.node_guid
        )
        motor_type = AsynchronousMotorMV.AsynchronousMotorType()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        motor = AsynchronousMotorMV(general, [presentation], motor_type, None)
        motor.register(self.network)

        # Verify motor is in network
        self.assertIn(self.motor_guid, self.network.asynchronous_motors)
        self.assertIs(self.network.asynchronous_motors[self.motor_guid], motor)

    def test_async_motor_with_full_properties_serializes_correctly(self) -> None:
        """Test that asynchronous motors with all properties serialize correctly."""
        general = AsynchronousMotorMV.General(
            guid=self.motor_guid,
            node=self.node_guid,
            creation_time=123.45,
            mutation_date=10,
            revision_date=20,
            variant=True,
            name="FullMotor",
            switch_state=True,
            field_name="TestField",
            failure_frequency=0.01,
            repair_duration=2.5,
            maintenance_frequency=0.1,
            maintenance_duration=4.0,
            maintenance_cancel_duration=1.0,
            not_preferred=True,
            number_of=5,
            p_mechanic=75.0,
            earthing=True,
            earthing_resistance=1.5,
            earthing_reactance=2.0,
            connection_type=1,
            cos_inverter=0.85,
            istart_inom=5.0,
            ta=0.5,
            no_short_circuit_contribution=True,
            type="TestGenType",
            harmonics_type="TestHarmonics",
        )

        motor_type = AsynchronousMotorMV.AsynchronousMotorType(
            unom=400.0,
            pnom=100.0,
            r_x=0.1,
            istart_inom=5.0,
            poles=4,
            cosnom=0.85,
            efficiency=0.95,
            p2=0.8,
            cos2=0.9,
            n2=1450.0,
            p3=0.6,
            cos3=0.8,
            n3=1400.0,
            p4=0.4,
            cos4=0.7,
            n4=1350.0,
            p5=0.2,
            cos5=0.6,
            n5=1300.0,
            starting_torque=1.5,
            nom_speed=1450.0,
            critical_speed=1500.0,
            critical_torque=200.0,
            j=0.1,
            k2=1.0,
            k1=0.8,
            k0=0.6,
            double_cage=True,
            own_parameters=True,
            rs=0.02,
            xsl=0.05,
            xm=2.0,
            rr=0.015,
            xrl=0.04,
            rr2=0.01,
            xr2l=0.03,
            mechanical_torque_speed_characteristic=True,
            electrical_torque_speed_characteristic=True,
            m1=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
            m2=[11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0],
            e1=[21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0],
            e2=[31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0, 38.0, 39.0, 40.0],
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

        motor = AsynchronousMotorMV(general, [presentation], motor_type, None)
        motor.extras.append(Extra(text="foo=bar"))
        motor.notes.append(Note(text="Test note"))
        motor.register(self.network)

        # Test serialization
        serialized = motor.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertEqual(serialized.count("#AsynchronousMotorType"), 1)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify general properties
        self.assertIn("Name:'FullMotor'", serialized)
        self.assertIn("Variant:True", serialized)
        self.assertIn("SwitchState:True", serialized)
        self.assertIn("FieldName:'TestField'", serialized)
        self.assertIn("NotPreferred:True", serialized)
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("RepairDuration:2.5", serialized)
        self.assertIn("MaintenanceFrequency:0.1", serialized)
        self.assertIn("MaintenanceDuration:4.0", serialized)
        self.assertIn("MaintenanceCancelDuration:1.0", serialized)
        self.assertIn("NumberOf:5", serialized)
        self.assertIn("Pmechanic:75", serialized)
        self.assertIn("Earthing:True", serialized)
        self.assertIn("Re:1.5", serialized)
        self.assertIn("Xe:2", serialized)
        self.assertIn("ConnectionType:1", serialized)
        self.assertIn("CosInverter:0.85", serialized)
        self.assertIn("Istart/Inom:5", serialized)
        self.assertIn("ta:0.5", serialized)
        self.assertIn("NoShortCircuitContribution:True", serialized)
        self.assertIn("AsynchronousMotorType:'TestGenType'", serialized)
        self.assertIn("HarmonicsType:'TestHarmonics'", serialized)

        # Verify node reference
        self.assertIn(f"Node:'{{{str(self.node_guid).upper()}}}'", serialized)

        # Verify type properties
        self.assertIn("Unom:400", serialized)
        self.assertIn("Pnom:100", serialized)
        self.assertIn("R/X:0.1", serialized)
        self.assertIn("Istart/Inom:5", serialized)
        self.assertIn("Poles:4", serialized)
        self.assertIn("CosNom:0.85", serialized)
        self.assertIn("Efficiency:0.95", serialized)
        self.assertIn("p2:0.8", serialized)
        self.assertIn("cos2:0.9", serialized)
        self.assertIn("n2:1450", serialized)
        self.assertIn("p3:0.6", serialized)
        self.assertIn("cos3:0.8", serialized)
        self.assertIn("n3:1400", serialized)
        self.assertIn("p4:0.4", serialized)
        self.assertIn("cos4:0.7", serialized)
        self.assertIn("n4:1350", serialized)
        self.assertIn("p5:0.2", serialized)
        self.assertIn("cos5:0.6", serialized)
        self.assertIn("n5:1300", serialized)
        self.assertIn("StartingTorque:1.5", serialized)
        self.assertIn("NomSpeed:1450", serialized)
        self.assertIn("CriticalSpeed:1500", serialized)
        self.assertIn("CriticalTorque:200", serialized)
        self.assertIn("j:0.1", serialized)
        self.assertIn("k2:1", serialized)
        self.assertIn("k1:0.8", serialized)
        self.assertIn("k0:0.6", serialized)
        self.assertIn("DoubleCage:True", serialized)
        self.assertIn("OwnParameters:True", serialized)
        self.assertIn("Rs:0.02", serialized)
        self.assertIn("Xsl:0.05", serialized)
        self.assertIn("Xm:2", serialized)
        self.assertIn("Rr:0.015", serialized)
        self.assertIn("Xrl:0.04", serialized)
        self.assertIn("Rr2:0.01", serialized)
        self.assertIn("Xr2l:0.03", serialized)
        self.assertIn("MechanicalTorqueSpeedCharacteristic:True", serialized)
        self.assertIn("ElectricalTorqueSpeedCharacteristic:True", serialized)

        # Verify arrays
        self.assertIn("M11:1", serialized)
        self.assertIn("M110:10", serialized)
        self.assertIn("M21:11", serialized)
        self.assertIn("M210:20", serialized)
        self.assertIn("E11:21", serialized)
        self.assertIn("E110:30", serialized)
        self.assertIn("E21:31", serialized)
        self.assertIn("E210:40", serialized)

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
        """Test that registering a motor with the same GUID overwrites the existing one."""
        general1 = AsynchronousMotorMV.General(
            guid=self.motor_guid, name="FirstMotor", node=self.node_guid
        )
        type1 = AsynchronousMotorMV.AsynchronousMotorType(pnom=50.0)
        motor1 = AsynchronousMotorMV(
            general1, [ElementPresentation(sheet=self.sheet_guid)], type1, None
        )
        motor1.register(self.network)

        general2 = AsynchronousMotorMV.General(
            guid=self.motor_guid, name="SecondMotor", node=self.node_guid
        )
        type2 = AsynchronousMotorMV.AsynchronousMotorType(pnom=100.0)
        motor2 = AsynchronousMotorMV(
            general2, [ElementPresentation(sheet=self.sheet_guid)], type2, None
        )
        motor2.register(self.network)

        # Should only have one motor
        self.assertEqual(len(self.network.asynchronous_motors), 1)
        # Should be the second motor
        self.assertEqual(
            self.network.asynchronous_motors[self.motor_guid].general.name,
            "SecondMotor",
        )

    def test_minimal_async_motor_serialization(self) -> None:
        """Test that minimal asynchronous motors serialize correctly with only required fields."""
        general = AsynchronousMotorMV.General(
            guid=self.motor_guid, name="MinimalMotor", node=self.node_guid
        )
        motor_type = AsynchronousMotorMV.AsynchronousMotorType()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        motor = AsynchronousMotorMV(general, [presentation], motor_type, None)
        motor.register(self.network)

        serialized = motor.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertEqual(serialized.count("#AsynchronousMotorType"), 1)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalMotor'", serialized)

        # Should not have optional sections
        self.assertNotIn("#Harmonics", serialized)

    def test_async_motor_with_earthing_serializes_correctly(self) -> None:
        """Test that asynchronous motors with earthing serialize correctly."""
        general = AsynchronousMotorMV.General(
            guid=self.motor_guid,
            name="EarthingMotor",
            node=self.node_guid,
            earthing=True,
            earthing_resistance=1.5,
            earthing_reactance=2.0,
        )
        motor_type = AsynchronousMotorMV.AsynchronousMotorType()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        motor = AsynchronousMotorMV(general, [presentation], motor_type, None)
        motor.register(self.network)

        serialized = motor.serialize()
        self.assertIn("Earthing:True", serialized)
        self.assertIn("Re:1.5", serialized)
        self.assertIn("Xe:2", serialized)

    def test_async_motor_with_mechanical_power_serializes_correctly(self) -> None:
        """Test that asynchronous motors with mechanical power serialize correctly."""
        general = AsynchronousMotorMV.General(
            guid=self.motor_guid,
            name="MechanicalPowerMotor",
            node=self.node_guid,
            p_mechanic=75.0,
        )
        motor_type = AsynchronousMotorMV.AsynchronousMotorType()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        motor = AsynchronousMotorMV(general, [presentation], motor_type, None)
        motor.register(self.network)

        serialized = motor.serialize()
        self.assertIn("Pmechanic:75", serialized)

    def test_async_motor_with_type_properties_serializes_correctly(self) -> None:
        """Test that asynchronous motors with type properties serialize correctly."""
        general = AsynchronousMotorMV.General(
            guid=self.motor_guid, name="TypeMotor", node=self.node_guid
        )
        motor_type = AsynchronousMotorMV.AsynchronousMotorType(
            unom=400.0,
            pnom=100.0,
            r_x=0.1,
            istart_inom=5.0,
            poles=4,
            cosnom=0.85,
            efficiency=0.95,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        motor = AsynchronousMotorMV(general, [presentation], motor_type, None)
        motor.register(self.network)

        serialized = motor.serialize()
        self.assertIn("Unom:400", serialized)
        self.assertIn("Pnom:100", serialized)
        self.assertIn("R/X:0.1", serialized)
        self.assertIn("Istart/Inom:5", serialized)
        self.assertIn("Poles:4", serialized)
        self.assertIn("CosNom:0.85", serialized)
        self.assertIn("Efficiency:0.95", serialized)

    def test_async_motor_with_maintenance_properties_serializes_correctly(self) -> None:
        """Test that asynchronous motors with maintenance properties serialize correctly."""
        general = AsynchronousMotorMV.General(
            guid=self.motor_guid,
            name="MaintenanceMotor",
            node=self.node_guid,
            failure_frequency=0.01,
            repair_duration=2.5,
            maintenance_frequency=0.1,
            maintenance_duration=4.0,
            maintenance_cancel_duration=1.0,
        )
        motor_type = AsynchronousMotorMV.AsynchronousMotorType()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        motor = AsynchronousMotorMV(general, [presentation], motor_type, None)
        motor.register(self.network)

        serialized = motor.serialize()
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("RepairDuration:2.5", serialized)
        self.assertIn("MaintenanceFrequency:0.1", serialized)
        self.assertIn("MaintenanceDuration:4.0", serialized)
        self.assertIn("MaintenanceCancelDuration:1.0", serialized)

    def test_async_motor_with_switch_state_serializes_correctly(self) -> None:
        """Test that asynchronous motors with switch state serialize correctly."""
        general = AsynchronousMotorMV.General(
            guid=self.motor_guid,
            name="SwitchStateMotor",
            node=self.node_guid,
            switch_state=True,
        )
        motor_type = AsynchronousMotorMV.AsynchronousMotorType()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        motor = AsynchronousMotorMV(general, [presentation], motor_type, None)
        motor.register(self.network)

        serialized = motor.serialize()
        self.assertIn("SwitchState:True", serialized)

    def test_async_motor_with_connection_type_serializes_correctly(self) -> None:
        """Test that asynchronous motors with connection type serialize correctly."""
        general = AsynchronousMotorMV.General(
            guid=self.motor_guid,
            name="ConnectionTypeMotor",
            node=self.node_guid,
            connection_type=1,
        )
        motor_type = AsynchronousMotorMV.AsynchronousMotorType()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        motor = AsynchronousMotorMV(general, [presentation], motor_type, None)
        motor.register(self.network)

        serialized = motor.serialize()
        self.assertIn("ConnectionType:1", serialized)

    def test_async_motor_with_number_of_serializes_correctly(self) -> None:
        """Test that asynchronous motors with number of units serialize correctly."""
        general = AsynchronousMotorMV.General(
            guid=self.motor_guid,
            name="NumberOfMotor",
            node=self.node_guid,
            number_of=5,
        )
        motor_type = AsynchronousMotorMV.AsynchronousMotorType()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        motor = AsynchronousMotorMV(general, [presentation], motor_type, None)
        motor.register(self.network)

        serialized = motor.serialize()
        self.assertIn("NumberOf:5", serialized)

    def test_async_motor_with_short_circuit_contribution_serializes_correctly(
        self,
    ) -> None:
        """Test that asynchronous motors with short circuit contribution serialize correctly."""
        general = AsynchronousMotorMV.General(
            guid=self.motor_guid,
            name="ShortCircuitMotor",
            node=self.node_guid,
            no_short_circuit_contribution=True,
        )
        motor_type = AsynchronousMotorMV.AsynchronousMotorType()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        motor = AsynchronousMotorMV(general, [presentation], motor_type, None)
        motor.register(self.network)

        serialized = motor.serialize()
        self.assertIn("NoShortCircuitContribution:True", serialized)

    def test_async_motor_with_field_name_serializes_correctly(self) -> None:
        """Test that asynchronous motors with field name serialize correctly."""
        general = AsynchronousMotorMV.General(
            guid=self.motor_guid,
            name="FieldNameMotor",
            node=self.node_guid,
            field_name="TestField",
        )
        motor_type = AsynchronousMotorMV.AsynchronousMotorType()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        motor = AsynchronousMotorMV(general, [presentation], motor_type, None)
        motor.register(self.network)

        serialized = motor.serialize()
        self.assertIn("FieldName:'TestField'", serialized)

    def test_async_motor_with_not_preferred_serializes_correctly(self) -> None:
        """Test that asynchronous motors with not preferred flag serialize correctly."""
        general = AsynchronousMotorMV.General(
            guid=self.motor_guid,
            name="NotPreferredMotor",
            node=self.node_guid,
            not_preferred=True,
        )
        motor_type = AsynchronousMotorMV.AsynchronousMotorType()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        motor = AsynchronousMotorMV(general, [presentation], motor_type, None)
        motor.register(self.network)

        serialized = motor.serialize()
        self.assertIn("NotPreferred:True", serialized)


if __name__ == "__main__":
    unittest.main()
