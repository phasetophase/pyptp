"""Tests for TSpecialTransformerMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.element_utils import Guid
from pyptp.elements.mixins import Extra, Note
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import BranchPresentation, NodePresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.elements.mv.special_transformer import SpecialTransformerMV
from pyptp.network_mv import NetworkMV


class TestSpecialTransformerRegistration(unittest.TestCase):
    """Test special transformer registration and functionality."""

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

        self.special_transformer_guid = Guid(
            UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c")
        )

    def test_special_transformer_registration_works(self) -> None:
        """Test that special transformers can register themselves with the network."""
        general = SpecialTransformerMV.General(
            guid=self.special_transformer_guid,
            name="TestSpecialTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        presentation = BranchPresentation(sheet=self.sheet_guid)

        special_transformer_type = SpecialTransformerMV.SpecialTransformerType()
        special_transformer = SpecialTransformerMV(
            general, [presentation], special_transformer_type
        )
        special_transformer.register(self.network)

        # Verify special transformer is in network
        self.assertIn(self.special_transformer_guid, self.network.special_transformers)
        self.assertIs(
            self.network.special_transformers[self.special_transformer_guid],
            special_transformer,
        )

    def test_special_transformer_with_basic_properties_serializes_correctly(
        self,
    ) -> None:
        """Test that special transformers with basic properties serialize correctly."""
        general = SpecialTransformerMV.General(
            guid=self.special_transformer_guid,
            name="BasicSpecialTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
            snom=100.0,
            type="TestType",
            creation_time=123.45,
            variant=True,
            switch_state1=True,
            switch_state2=True,
        )
        presentation = BranchPresentation(sheet=self.sheet_guid)

        special_transformer_type = SpecialTransformerMV.SpecialTransformerType()
        special_transformer = SpecialTransformerMV(
            general, [presentation], special_transformer_type
        )
        special_transformer.register(self.network)

        serialized = special_transformer.serialize()

        # Verify general properties
        self.assertIn("Name:'BasicSpecialTransformer'", serialized)
        self.assertIn("Snom:100", serialized)
        self.assertIn("SpecialTransformerType:'TestType'", serialized)
        self.assertIn("CreationTime:123.45", serialized)
        self.assertIn("Variant:True", serialized)
        self.assertIn("SwitchState1:1", serialized)
        self.assertIn("SwitchState2:1", serialized)

        # Verify node references
        self.assertIn(f"Node1:'{{{str(self.node1_guid).upper()}}}'", serialized)
        self.assertIn(f"Node2:'{{{str(self.node2_guid).upper()}}}'", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a special transformer with the same GUID overwrites the existing one."""
        general1 = SpecialTransformerMV.General(
            guid=self.special_transformer_guid,
            name="FirstSpecialTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        special_transformer1 = SpecialTransformerMV(
            general1,
            [BranchPresentation(sheet=self.sheet_guid)],
            SpecialTransformerMV.SpecialTransformerType(),
        )
        special_transformer1.register(self.network)

        general2 = SpecialTransformerMV.General(
            guid=self.special_transformer_guid,
            name="SecondSpecialTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        special_transformer2 = SpecialTransformerMV(
            general2,
            [BranchPresentation(sheet=self.sheet_guid)],
            SpecialTransformerMV.SpecialTransformerType(),
        )
        special_transformer2.register(self.network)

        # Should only have one special transformer
        self.assertEqual(len(self.network.special_transformers), 1)
        # Should be the second special transformer
        self.assertEqual(
            self.network.special_transformers[
                self.special_transformer_guid
            ].general.name,
            "SecondSpecialTransformer",
        )

    def test_minimal_special_transformer_serialization(self) -> None:
        """Test that minimal special transformers serialize correctly with only required fields."""
        general = SpecialTransformerMV.General(
            guid=self.special_transformer_guid,
            name="MinimalSpecialTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        presentation = BranchPresentation(sheet=self.sheet_guid)

        special_transformer_type = SpecialTransformerMV.SpecialTransformerType()
        special_transformer = SpecialTransformerMV(
            general, [presentation], special_transformer_type
        )
        special_transformer.register(self.network)

        serialized = special_transformer.serialize()

        # Should have basic properties
        self.assertIn("Name:'MinimalSpecialTransformer'", serialized)
        self.assertIn(f"Node1:'{{{str(self.node1_guid).upper()}}}'", serialized)
        self.assertIn(f"Node2:'{{{str(self.node2_guid).upper()}}}'", serialized)

    def test_special_transformer_with_extras_and_notes(self) -> None:
        """Test that special transformers can have extras and notes."""
        general = SpecialTransformerMV.General(
            guid=self.special_transformer_guid,
            name="ExtrasNotesSpecialTransformer",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        presentation = BranchPresentation(sheet=self.sheet_guid)

        special_transformer = SpecialTransformerMV(
            general, [presentation], SpecialTransformerMV.SpecialTransformerType()
        )
        special_transformer.extras.append(Extra(text="foo=bar"))
        special_transformer.notes.append(Note(text="Test note"))
        special_transformer.register(self.network)

        serialized = special_transformer.serialize()

        # Verify extras and notes
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)


if __name__ == "__main__":
    unittest.main()
