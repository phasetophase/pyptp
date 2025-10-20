"""Tests for TSynchronousMotorMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.element_utils import Guid
from pyptp.elements.mixins import Extra, Note
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import ElementPresentation, NodePresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.elements.mv.synchronous_motor import SynchronousMotorMV
from pyptp.network_mv import NetworkMV


class TestSynchronousMotorRegistration(unittest.TestCase):
    """Test synchronous motor registration and functionality."""

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

        # Create and register a node
        node = NodeMV(
            NodeMV.General(
                guid=Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5")), name="TestNode"
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node.register(self.network)
        self.node_guid = node.general.guid

        self.synchronous_motor_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_synchronous_motor_registration_works(self) -> None:
        """Test that synchronous motors can register themselves with the network."""
        general = SynchronousMotorMV.General(
            guid=self.synchronous_motor_guid,
            name="TestSynchronousMotor",
            node=self.node_guid,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        synchronous_motor = SynchronousMotorMV(
            general, [presentation], SynchronousMotorMV.SynchronousMotorType()
        )
        synchronous_motor.register(self.network)

        # Verify synchronous motor is in network
        self.assertIn(self.synchronous_motor_guid, self.network.synchronous_motors)
        self.assertIs(
            self.network.synchronous_motors[self.synchronous_motor_guid],
            synchronous_motor,
        )

    def test_synchronous_motor_with_basic_properties_serializes_correctly(self) -> None:
        """Test that synchronous motors with basic properties serialize correctly."""
        general = SynchronousMotorMV.General(
            guid=self.synchronous_motor_guid,
            name="BasicSynchronousMotor",
            node=self.node_guid,
            pref=100.0,
            cos_ref=0.9,
            creation_time=123.45,
            variant=True,
            switch_state=True,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        synchronous_motor = SynchronousMotorMV(
            general, [presentation], SynchronousMotorMV.SynchronousMotorType()
        )
        synchronous_motor.register(self.network)

        serialized = synchronous_motor.serialize()

        # Verify general properties
        self.assertIn("Name:'BasicSynchronousMotor'", serialized)
        self.assertIn("Pref:100", serialized)
        self.assertIn("CosRef:0.9", serialized)
        self.assertIn("CreationTime:123.45", serialized)
        self.assertIn("Variant:True", serialized)
        self.assertIn("SwitchState:1", serialized)

        # Verify node reference
        self.assertIn(f"Node:'{{{str(self.node_guid).upper()}}}'", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a synchronous motor with the same GUID overwrites the existing one."""
        general1 = SynchronousMotorMV.General(
            guid=self.synchronous_motor_guid,
            name="FirstSynchronousMotor",
            node=self.node_guid,
        )
        synchronous_motor1 = SynchronousMotorMV(
            general1,
            [ElementPresentation(sheet=self.sheet_guid)],
            SynchronousMotorMV.SynchronousMotorType(),
        )
        synchronous_motor1.register(self.network)

        general2 = SynchronousMotorMV.General(
            guid=self.synchronous_motor_guid,
            name="SecondSynchronousMotor",
            node=self.node_guid,
        )
        synchronous_motor2 = SynchronousMotorMV(
            general2,
            [ElementPresentation(sheet=self.sheet_guid)],
            SynchronousMotorMV.SynchronousMotorType(),
        )
        synchronous_motor2.register(self.network)

        # Should only have one synchronous motor
        self.assertEqual(len(self.network.synchronous_motors), 1)
        # Should be the second synchronous motor
        self.assertEqual(
            self.network.synchronous_motors[self.synchronous_motor_guid].general.name,
            "SecondSynchronousMotor",
        )

    def test_minimal_synchronous_motor_serialization(self) -> None:
        """Test that minimal synchronous motors serialize correctly with only required fields."""
        general = SynchronousMotorMV.General(
            guid=self.synchronous_motor_guid,
            name="MinimalSynchronousMotor",
            node=self.node_guid,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        synchronous_motor = SynchronousMotorMV(
            general, [presentation], SynchronousMotorMV.SynchronousMotorType()
        )
        synchronous_motor.register(self.network)

        serialized = synchronous_motor.serialize()

        # Should have basic properties and defaults
        self.assertIn("Name:'MinimalSynchronousMotor'", serialized)
        self.assertIn(f"Node:'{{{str(self.node_guid).upper()}}}'", serialized)
        self.assertIn("ControlSort:'C'", serialized)
        self.assertIn("CosRef:0.85", serialized)

    def test_synchronous_motor_with_extras_and_notes(self) -> None:
        """Test that synchronous motors can have extras and notes."""
        general = SynchronousMotorMV.General(
            guid=self.synchronous_motor_guid,
            name="ExtrasNotesSynchronousMotor",
            node=self.node_guid,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        synchronous_motor = SynchronousMotorMV(
            general, [presentation], SynchronousMotorMV.SynchronousMotorType()
        )
        synchronous_motor.extras.append(Extra(text="foo=bar"))
        synchronous_motor.notes.append(Note(text="Test note"))
        synchronous_motor.register(self.network)

        serialized = synchronous_motor.serialize()

        # Verify extras and notes
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)


if __name__ == "__main__":
    unittest.main()
