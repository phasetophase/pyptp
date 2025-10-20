"""Tests for TSynchronousGeneratorMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.element_utils import Guid
from pyptp.elements.mixins import Extra, Note
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import ElementPresentation, NodePresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.elements.mv.synchronous_generator import SynchronousGeneratorMV
from pyptp.network_mv import NetworkMV


class TestSynchronousGeneratorRegistration(unittest.TestCase):
    """Test synchronous generator registration and functionality."""

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

        self.synchronous_generator_guid = Guid(
            UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c")
        )

    def test_synchronous_generator_registration_works(self) -> None:
        """Test that synchronous generators can register themselves with the network."""
        general = SynchronousGeneratorMV.General(
            guid=self.synchronous_generator_guid,
            name="TestSynchronousGenerator",
            node=self.node_guid,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        synchronous_generator = SynchronousGeneratorMV(
            general, [presentation], SynchronousGeneratorMV.SynchronousGeneratorType()
        )
        synchronous_generator.register(self.network)

        # Verify synchronous generator is in network
        self.assertIn(
            self.synchronous_generator_guid, self.network.synchronous_generators
        )
        self.assertIs(
            self.network.synchronous_generators[self.synchronous_generator_guid],
            synchronous_generator,
        )

    def test_synchronous_generator_with_basic_properties_serializes_correctly(
        self,
    ) -> None:
        """Test that synchronous generators with basic properties serialize correctly."""
        general = SynchronousGeneratorMV.General(
            guid=self.synchronous_generator_guid,
            name="BasicSynchronousGenerator",
            node=self.node_guid,
            pnom=100.0,
            cos_ref=0.9,
            creation_time=123.45,
            variant=True,
            switch_state=True,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        synchronous_generator = SynchronousGeneratorMV(
            general, [presentation], SynchronousGeneratorMV.SynchronousGeneratorType()
        )
        synchronous_generator.register(self.network)

        serialized = synchronous_generator.serialize()

        # Verify general properties
        self.assertIn("Name:'BasicSynchronousGenerator'", serialized)
        self.assertIn("Pnom:100", serialized)
        self.assertIn("CosRef:0.9", serialized)
        self.assertIn("CreationTime:123.45", serialized)
        self.assertIn("Variant:True", serialized)
        self.assertIn("SwitchState:1", serialized)

        # Verify node reference
        self.assertIn(f"Node:'{{{str(self.node_guid).upper()}}}'", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a synchronous generator with the same GUID overwrites the existing one."""
        general1 = SynchronousGeneratorMV.General(
            guid=self.synchronous_generator_guid,
            name="FirstSynchronousGenerator",
            node=self.node_guid,
        )
        synchronous_generator1 = SynchronousGeneratorMV(
            general1,
            [ElementPresentation(sheet=self.sheet_guid)],
            SynchronousGeneratorMV.SynchronousGeneratorType(),
        )
        synchronous_generator1.register(self.network)

        general2 = SynchronousGeneratorMV.General(
            guid=self.synchronous_generator_guid,
            name="SecondSynchronousGenerator",
            node=self.node_guid,
        )
        synchronous_generator2 = SynchronousGeneratorMV(
            general2,
            [ElementPresentation(sheet=self.sheet_guid)],
            SynchronousGeneratorMV.SynchronousGeneratorType(),
        )
        synchronous_generator2.register(self.network)

        # Should only have one synchronous generator
        self.assertEqual(len(self.network.synchronous_generators), 1)
        # Should be the second synchronous generator
        self.assertEqual(
            self.network.synchronous_generators[
                self.synchronous_generator_guid
            ].general.name,
            "SecondSynchronousGenerator",
        )

    def test_minimal_synchronous_generator_serialization(self) -> None:
        """Test that minimal synchronous generators serialize correctly with only required fields."""
        general = SynchronousGeneratorMV.General(
            guid=self.synchronous_generator_guid,
            name="MinimalSynchronousGenerator",
            node=self.node_guid,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        synchronous_generator = SynchronousGeneratorMV(
            general, [presentation], SynchronousGeneratorMV.SynchronousGeneratorType()
        )
        synchronous_generator.register(self.network)

        serialized = synchronous_generator.serialize()

        # Should have basic properties and defaults
        self.assertIn("Name:'MinimalSynchronousGenerator'", serialized)
        self.assertIn(f"Node:'{{{str(self.node_guid).upper()}}}'", serialized)
        self.assertIn("ControlSort:'C'", serialized)
        self.assertIn("CosRef:0.95", serialized)
        self.assertIn("Uref:1", serialized)

    def test_synchronous_generator_with_extras_and_notes(self) -> None:
        """Test that synchronous generators can have extras and notes."""
        general = SynchronousGeneratorMV.General(
            guid=self.synchronous_generator_guid,
            name="ExtrasNotesSynchronousGenerator",
            node=self.node_guid,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        synchronous_generator = SynchronousGeneratorMV(
            general, [presentation], SynchronousGeneratorMV.SynchronousGeneratorType()
        )
        synchronous_generator.extras.append(Extra(text="foo=bar"))
        synchronous_generator.notes.append(Note(text="Test note"))
        synchronous_generator.register(self.network)

        serialized = synchronous_generator.serialize()

        # Verify extras and notes
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)


if __name__ == "__main__":
    unittest.main()
