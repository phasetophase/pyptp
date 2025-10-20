"""Tests for TAsyncMotorLS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid, encode_guid
from pyptp.elements.lv.async_motor import AsynchronousMotorLV
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import ElementPresentation, NodePresentation
from pyptp.elements.lv.shared import HarmonicsType
from pyptp.elements.lv.sheet import SheetLV
from pyptp.elements.mixins import Extra, Note
from pyptp.network_lv import NetworkLV


class TestAsyncMotorRegistration(unittest.TestCase):
    """Test async motor registration and functionality."""

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

        self.motor_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_async_motor_registration_works(self) -> None:
        """Test that async motors can register themselves with the network."""
        general = AsynchronousMotorLV.General(
            guid=self.motor_guid,
            name="TestMotor",
            node=self.node_guid,
            field_name="MotorField",
            type="Type1",
            harmonics_type="HType1",
        )
        type_ = AsynchronousMotorLV.AsynchronousMotorType()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        motor = AsynchronousMotorLV(general, [presentation], type_)
        motor.register(self.network)

        # Verify motor is in network
        self.assertIn(self.motor_guid, self.network.async_motors)
        self.assertIs(self.network.async_motors[self.motor_guid], motor)

    def test_async_motor_with_full_properties_serializes_correctly(self) -> None:
        """Test that async motors with all properties serialize correctly."""
        motor = self._create_full_motor()
        motor.register(self.network)

        # Test serialization
        serialized = motor.serialize()

        # Verify all sections are present
        self._verify_sections_present(serialized)

        # Verify key general properties are serialized
        self._verify_general_properties(serialized)

        # Verify type properties
        self._verify_type_properties(serialized)

        # Verify harmonics properties
        self._verify_harmonics_properties(serialized)

        # Verify presentation properties
        self._verify_presentation_properties(serialized)

        # Verify extras and notes
        self._verify_extras_and_notes(serialized)

    def _create_full_motor(self) -> AsynchronousMotorLV:
        """Create an async motor with all properties set."""
        general = AsynchronousMotorLV.General(
            guid=self.motor_guid,
            node=self.node_guid,
            name="FullMotor",
            s_L1=True,
            s_L2=False,
            s_L3=True,
            s_N=False,
            field_name="MotorField",
            phase=3,
            p_mechanic=75.0,
            istart_inom=10,
            ta=5,
            type="FullType",
            harmonics_type="HTypeFull",
            switch_on_frequency=50,
            creation_time=1234567890,
            mutation_date=123456789,
            revision_date=1234567890.0,
        )

        type_ = AsynchronousMotorLV.AsynchronousMotorType(
            single_phase=True,
            unom=400.0,
            pm_nom=100.0,
            r_x=0.1,
            istart_inom=12,
            poles=4,
            rpm_nom=1500.0,
            critical_torque=2.5,
            cos_nom=0.85,
            efficiency=0.95,
            p2=80.0,
            cos2=0.8,
            n2=1450.0,
            p3=60.0,
            cos3=0.75,
            n3=1400.0,
            p4=40.0,
            cos4=0.7,
            n4=1350.0,
            p5=20.0,
            cos5=0.65,
            n5=1300.0,
        )

        harmonics = HarmonicsType(
            h=[1.0, 2.0, 3.0] + [0.0] * 96, angle=[0.0, 90.0, 180.0] + [0.0] * 96
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

        motor = AsynchronousMotorLV(general, [presentation], type_, harmonics)
        motor.extras.append(Extra(text="foo=bar"))
        motor.notes.append(Note(text="Test note"))
        return motor

    def _verify_sections_present(self, serialized: str) -> None:
        """Verify all required sections are present in serialized output."""
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#AsynchronousMotorType", serialized)
        self.assertIn("#HarmonicsType", serialized)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

    def _verify_general_properties(self, serialized: str) -> None:
        """Verify general properties are serialized correctly."""
        self.assertIn("Name:'FullMotor'", serialized)
        self.assertIn("FieldName:'MotorField'", serialized)
        self.assertIn("s_L2:False", serialized)  # False values are explicitly shown
        self.assertIn("s_N:False", serialized)  # False values are explicitly shown
        self.assertNotIn("s_L1:true", serialized)
        self.assertNotIn("s_L3:true", serialized)
        self.assertIn("Phase:3", serialized)
        self.assertIn("Pmechanic:75.0", serialized)
        self.assertIn("Istart/Inom:10", serialized)
        self.assertIn("ta:5", serialized)
        self.assertIn("AsynchronousMotorType:'FullType'", serialized)
        self.assertIn("HarmonicsType:'HTypeFull'", serialized)
        self.assertIn("SwitchOnFrequency:50", serialized)
        self.assertIn("CreationTime:1234567890", serialized)
        self.assertIn("MutationDate:123456789", serialized)
        self.assertIn("RevisionDate:1234567890.0", serialized)

    def _verify_type_properties(self, serialized: str) -> None:
        """Verify type properties are serialized correctly."""
        self.assertIn("OnePhase:True", serialized)
        self.assertIn("Unom:400.0", serialized)
        self.assertIn("Pmnom:100.0", serialized)
        self.assertIn("R/X:0.1", serialized)
        self.assertIn("Istart/Inom:12", serialized)
        self.assertIn("Poles:4", serialized)
        self.assertIn("Rpm:1500.0", serialized)
        self.assertIn("CriticalTorque:2.5", serialized)
        self.assertIn("CosNom:0.85", serialized)
        self.assertIn("Efficiency:0.95", serialized)
        self.assertIn("p2:80.0", serialized)
        self.assertIn("cos2:0.8", serialized)
        self.assertIn("n2:1450.0", serialized)
        self.assertIn("p3:60.0", serialized)
        self.assertIn("cos3:0.75", serialized)
        self.assertIn("n3:1400.0", serialized)
        self.assertIn("p4:40.0", serialized)
        self.assertIn("cos4:0.7", serialized)
        self.assertIn("n4:1350.0", serialized)
        self.assertIn("p5:20.0", serialized)
        self.assertIn("cos5:0.65", serialized)
        self.assertIn("n5:1300.0", serialized)

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

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a motor with the same GUID overwrites the existing one."""
        general1 = AsynchronousMotorLV.General(
            guid=self.motor_guid,
            name="FirstMotor",
            node=self.node_guid,
            field_name="Field1",
            type="Type1",
            harmonics_type="HType1",
        )
        type1 = AsynchronousMotorLV.AsynchronousMotorType()
        motor1 = AsynchronousMotorLV(
            general1, [ElementPresentation(sheet=self.sheet_guid)], type1
        )
        motor1.register(self.network)

        general2 = AsynchronousMotorLV.General(
            guid=self.motor_guid,
            name="SecondMotor",
            node=self.node_guid,
            field_name="Field2",
            type="Type2",
            harmonics_type="HType2",
        )
        type2 = AsynchronousMotorLV.AsynchronousMotorType()
        motor2 = AsynchronousMotorLV(
            general2, [ElementPresentation(sheet=self.sheet_guid)], type2
        )
        motor2.register(self.network)

        # Should only have one motor
        self.assertEqual(len(self.network.async_motors), 1)
        # Should be the second motor
        self.assertEqual(
            self.network.async_motors[self.motor_guid].general.name, "SecondMotor"
        )

    def test_async_motor_with_profile_guid_serializes_correctly(self) -> None:
        """Test that async motors with profile GUID serialize correctly."""
        profile_guid = Guid(UUID("12345678-1234-5678-9abc-123456789abc"))

        general = AsynchronousMotorLV.General(
            guid=self.motor_guid,
            name="ProfileMotor",
            node=self.node_guid,
            field_name="ProfileField",
            type="ProfileType",
            harmonics_type="HTypeProfile",
            profile=profile_guid,
        )
        type_ = AsynchronousMotorLV.AsynchronousMotorType()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        motor = AsynchronousMotorLV(general, [presentation], type_)
        motor.register(self.network)

        serialized = motor.serialize()

        # Verify profile GUID is serialized
        self.assertIn(f"Profile:'{{{str(profile_guid).upper()}}}'", serialized)

    def test_minimal_async_motor_serialization(self) -> None:
        """Test that minimal async motors serialize correctly with only required fields."""
        general = AsynchronousMotorLV.General(
            guid=self.motor_guid,
            name="MinimalMotor",
            node=self.node_guid,
            field_name="MinimalField",
            type="MinimalType",
            harmonics_type="MinimalHType",
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        motor = AsynchronousMotorLV(
            general, [presentation], AsynchronousMotorLV.AsynchronousMotorType(), None
        )
        motor.register(self.network)

        serialized = motor.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalMotor'", serialized)
        self.assertIn("FieldName:'MinimalField'", serialized)
        self.assertIn("AsynchronousMotorType:'MinimalType'", serialized)
        self.assertIn("HarmonicsType:'MinimalHType'", serialized)
        self.assertNotIn("s_L1:true", serialized)
        self.assertNotIn("s_L2:true", serialized)
        self.assertNotIn("s_L3:true", serialized)
        self.assertNotIn("s_N:true", serialized)
        self.assertNotIn("Pmechanic:0", serialized)
        self.assertNotIn("Istart/Inom:0", serialized)
        self.assertNotIn("ta:0", serialized)
        self.assertNotIn("SwitchOnFrequency:0", serialized)

        # Should allow for empty #AsynchronousMotorType section
        self.assertIn("#AsynchronousMotorType", serialized)
        # Should not have optional sections
        self.assertNotIn("#Extra", serialized)
        self.assertNotIn("#Note", serialized)

    def test_multiple_presentations_serialize_correctly(self) -> None:
        """Test that async motors with multiple presentations serialize correctly."""
        general = AsynchronousMotorLV.General(
            guid=self.motor_guid,
            name="MultiPresMotor",
            node=self.node_guid,
            field_name="MultiField",
            type="MultiType",
            harmonics_type="MultiHType",
        )
        type_ = AsynchronousMotorLV.AsynchronousMotorType()

        pres1 = ElementPresentation(
            sheet=self.sheet_guid, x=100, y=100, color=DelphiColor("$FF0000")
        )
        pres2 = ElementPresentation(
            sheet=self.sheet_guid, x=200, y=200, color=DelphiColor("$00FF00")
        )

        motor = AsynchronousMotorLV(general, [pres1, pres2], type_)
        motor.register(self.network)

        serialized = motor.serialize()

        # Should have two presentations
        self.assertEqual(serialized.count("#Presentation"), 2)
        self.assertIn("Color:$FF0000", serialized)
        self.assertIn("Color:$00FF00", serialized)
        self.assertIn("X:100", serialized)
        self.assertIn("X:200", serialized)

    def test_async_motor_with_complex_harmonics_data_serializes_correctly(self) -> None:
        """Test that async motors with complex harmonics data serialize correctly."""
        general = AsynchronousMotorLV.General(
            guid=self.motor_guid,
            name="ComplexHarmonicsMotor",
            node=self.node_guid,
            field_name="ComplexField",
            type="ComplexType",
            harmonics_type="ComplexHType",
        )
        type_ = AsynchronousMotorLV.AsynchronousMotorType()

        harmonics = HarmonicsType(
            h=[i * 1.1 for i in range(1, 11)], angle=[i * 10.0 for i in range(1, 11)]
        )

        presentation = ElementPresentation(sheet=self.sheet_guid)

        motor = AsynchronousMotorLV(general, [presentation], type_, harmonics)
        motor.register(self.network)

        serialized = motor.serialize()

        # Verify harmonics section is present
        self.assertIn("#HarmonicsType", serialized)

        # Verify harmonics data is serialized (check for some key values)
        self.assertIn("h1:1.1", serialized)
        self.assertIn("h2:2.2", serialized)
        self.assertIn("h3:3.3000000000000003", serialized)
        self.assertIn("Angle1:10.0", serialized)
        self.assertIn("Angle2:20.0", serialized)
        self.assertIn("Angle3:30.0", serialized)


if __name__ == "__main__":
    unittest.main()
