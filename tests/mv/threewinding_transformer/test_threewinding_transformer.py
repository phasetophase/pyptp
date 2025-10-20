"""Tests for TThreewindingTransformerMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.element_utils import Guid
from pyptp.elements.mixins import Extra, Note
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import DWPresentation, NodePresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.elements.mv.threewinding_transformer import ThreewindingTransformerMV
from pyptp.network_mv import NetworkMV


class TestThreewindingTransformerRegistration(unittest.TestCase):
    """Test threewinding transformer registration and functionality."""

    def setUp(self) -> None:
        """Create a fresh network with sheet and nodes for testing."""
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

        # Create and register nodes
        node1 = NodeMV(
            NodeMV.General(
                guid=Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5")),
                name="TestNode1",
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node1.register(self.network)
        self.node1_guid = node1.general.guid

        node2 = NodeMV(
            NodeMV.General(
                guid=Guid(UUID("8b7d4c3e-2f1a-4e5d-9c8b-7a6f5e4d3c2b")),
                name="TestNode2",
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node2.register(self.network)
        self.node2_guid = node2.general.guid

        node3 = NodeMV(
            NodeMV.General(
                guid=Guid(UUID("1a2b3c4d-5e6f-7890-abcd-ef1234567890")),
                name="TestNode3",
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node3.register(self.network)
        self.node3_guid = node3.general.guid

        self.threewinding_transformer_guid = Guid(
            UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c")
        )

    def test_threewinding_transformer_registration_works(self) -> None:
        """Test that threewinding transformers can register themselves with the network."""
        general = ThreewindingTransformerMV.General(
            guid=self.threewinding_transformer_guid,
            name="TestThreewindingTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
            node3=self.node3_guid,
        )
        presentation = DWPresentation(sheet=self.sheet_guid)

        threewinding_transformer = ThreewindingTransformerMV(
            general,
            ThreewindingTransformerMV.ThreewindingTransformerType(),
            [presentation],
        )
        threewinding_transformer.register(self.network)

        # Verify threewinding transformer is in network
        self.assertIn(
            self.threewinding_transformer_guid, self.network.threewinding_transformers
        )
        self.assertIs(
            self.network.threewinding_transformers[self.threewinding_transformer_guid],
            threewinding_transformer,
        )

    def test_threewinding_transformer_with_basic_properties_serializes_correctly(
        self,
    ) -> None:
        """Test that threewinding transformers with basic properties serialize correctly."""
        general = ThreewindingTransformerMV.General(
            guid=self.threewinding_transformer_guid,
            name="BasicThreewindingTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
            node3=self.node3_guid,
            snom1=100.0,
            snom2=90.0,
            snom3=80.0,
            creation_time=123.45,
            variant=True,
        )
        presentation = DWPresentation(sheet=self.sheet_guid)

        threewinding_transformer = ThreewindingTransformerMV(
            general,
            ThreewindingTransformerMV.ThreewindingTransformerType(),
            [presentation],
        )
        threewinding_transformer.register(self.network)

        serialized = threewinding_transformer.serialize()

        # Verify general properties
        self.assertIn("Name:'BasicThreewindingTransformer'", serialized)
        self.assertIn("Snom1:100", serialized)
        self.assertIn("Snom2:90", serialized)
        self.assertIn("Snom3:80", serialized)
        self.assertIn("CreationTime:123.45", serialized)
        self.assertIn("Variant:True", serialized)

        # Verify node references
        self.assertIn(f"Node1:'{{{str(self.node1_guid).upper()}}}'", serialized)
        self.assertIn(f"Node2:'{{{str(self.node2_guid).upper()}}}'", serialized)
        self.assertIn(f"Node3:'{{{str(self.node3_guid).upper()}}}'", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a threewinding transformer with the same GUID overwrites the existing one."""
        general1 = ThreewindingTransformerMV.General(
            guid=self.threewinding_transformer_guid,
            name="FirstThreewindingTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
            node3=self.node3_guid,
        )
        threewinding_transformer1 = ThreewindingTransformerMV(
            general1,
            ThreewindingTransformerMV.ThreewindingTransformerType(),
            [DWPresentation(sheet=self.sheet_guid)],
        )
        threewinding_transformer1.register(self.network)

        general2 = ThreewindingTransformerMV.General(
            guid=self.threewinding_transformer_guid,
            name="SecondThreewindingTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
            node3=self.node3_guid,
        )
        threewinding_transformer2 = ThreewindingTransformerMV(
            general2,
            ThreewindingTransformerMV.ThreewindingTransformerType(),
            [DWPresentation(sheet=self.sheet_guid)],
        )
        threewinding_transformer2.register(self.network)

        # Should only have one threewinding transformer
        self.assertEqual(len(self.network.threewinding_transformers), 1)
        # Should be the second threewinding transformer
        self.assertEqual(
            self.network.threewinding_transformers[
                self.threewinding_transformer_guid
            ].general.name,
            "SecondThreewindingTransformer",
        )

    def test_minimal_threewinding_transformer_serialization(self) -> None:
        """Test that minimal threewinding transformers serialize correctly with only required fields."""
        general = ThreewindingTransformerMV.General(
            guid=self.threewinding_transformer_guid,
            name="MinimalThreewindingTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
            node3=self.node3_guid,
        )
        presentation = DWPresentation(sheet=self.sheet_guid)

        threewinding_transformer = ThreewindingTransformerMV(
            general,
            ThreewindingTransformerMV.ThreewindingTransformerType(),
            [presentation],
        )
        threewinding_transformer.register(self.network)

        serialized = threewinding_transformer.serialize()

        # Should have basic properties
        self.assertIn("Name:'MinimalThreewindingTransformer'", serialized)
        self.assertIn(f"Node1:'{{{str(self.node1_guid).upper()}}}'", serialized)
        self.assertIn(f"Node2:'{{{str(self.node2_guid).upper()}}}'", serialized)
        self.assertIn(f"Node3:'{{{str(self.node3_guid).upper()}}}'", serialized)

    def test_threewinding_transformer_with_extras_and_notes(self) -> None:
        """Test that threewinding transformers can have extras and notes."""
        general = ThreewindingTransformerMV.General(
            guid=self.threewinding_transformer_guid,
            name="ExtrasNotesThreewindingTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
            node3=self.node3_guid,
        )
        presentation = DWPresentation(sheet=self.sheet_guid)

        threewinding_transformer = ThreewindingTransformerMV(
            general,
            ThreewindingTransformerMV.ThreewindingTransformerType(),
            [presentation],
        )
        threewinding_transformer.extras.append(Extra(text="foo=bar"))
        threewinding_transformer.notes.append(Note(text="Test note"))
        threewinding_transformer.register(self.network)

        serialized = threewinding_transformer.serialize()

        # Verify extras and notes
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)


if __name__ == "__main__":
    unittest.main()
