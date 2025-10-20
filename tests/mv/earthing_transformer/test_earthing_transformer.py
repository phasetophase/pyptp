"""Tests for TEarthingTransformerMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid
from pyptp.elements.mixins import Extra, Note
from pyptp.elements.mv.earthing_transformer import EarthingTransformerMV
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import ElementPresentation, NodePresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.network_mv import NetworkMV


class TestEarthingTransformerRegistration(unittest.TestCase):
    """Test earthing transformer registration and functionality."""

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

        # Create and register a node for the transformer
        node = NodeMV(
            NodeMV.General(
                guid=Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5")), name="TestNode"
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node.register(self.network)
        self.node_guid = node.general.guid

        # Create and register an earthing node
        earthing_node = NodeMV(
            NodeMV.General(
                guid=Guid(UUID("12345678-9abc-def0-1234-56789abcdef0")),
                name="EarthingNode",
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        earthing_node.register(self.network)
        self.earthing_node_guid = earthing_node.general.guid

        self.transformer_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_earthing_transformer_registration_works(self) -> None:
        """Test that earthing transformers can register themselves with the network."""
        general = EarthingTransformerMV.General(
            guid=self.transformer_guid, name="TestTransformer", node=self.node_guid
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        transformer = EarthingTransformerMV(general, [presentation])
        transformer.register(self.network)

        # Verify transformer is in network
        self.assertIn(self.transformer_guid, self.network.earthing_transformers)
        self.assertIs(
            self.network.earthing_transformers[self.transformer_guid], transformer
        )

    def test_earthing_transformer_with_full_properties_serializes_correctly(
        self,
    ) -> None:
        """Test that earthing transformers with all properties serialize correctly."""
        general = EarthingTransformerMV.General(
            guid=self.transformer_guid,
            node=self.node_guid,
            creation_time=123.45,
            mutation_date=10,
            revision_date=20,
            variant=True,
            name="FullTransformer",
            switch_state=True,
            field_name="TestField",
            failure_frequency=0.01,
            repair_duration=2.5,
            maintenance_frequency=0.1,
            maintenance_duration=4.0,
            maintenance_cancel_duration=1.0,
            not_preferred=True,
            pref=50.0,
            earthing=True,
            re=1.5,
            xe=2.0,
            earthing_node=self.earthing_node_guid,
            type="TestType",
        )

        transformer_type = EarthingTransformerMV.EarthingTransformerType(
            r0=0.1,
            x0=0.2,
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

        transformer = EarthingTransformerMV(general, [presentation], transformer_type)
        transformer.extras.append(Extra(text="foo=bar"))
        transformer.notes.append(Note(text="Test note"))
        transformer.register(self.network)

        # Test serialization
        serialized = transformer.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertEqual(serialized.count("#EarthingTransformerType"), 1)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify general properties
        self.assertIn("Name:'FullTransformer'", serialized)
        self.assertIn("Variant:True", serialized)
        self.assertIn("SwitchState:1", serialized)
        self.assertIn("FieldName:'TestField'", serialized)
        self.assertIn("NotPreferred:True", serialized)
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("RepairDuration:2.5", serialized)
        self.assertIn("MaintenanceFrequency:0.1", serialized)
        self.assertIn("MaintenanceDuration:4.0", serialized)
        self.assertIn("MaintenanceCancelDuration:1.0", serialized)
        self.assertIn("Pref:50", serialized)
        self.assertIn("Earthing:True", serialized)
        self.assertIn("Re:1.5", serialized)
        self.assertIn("Xe:2", serialized)
        self.assertIn("EarthingTransformerType:'TestType'", serialized)

        # Verify node references
        self.assertIn(f"Node:'{{{str(self.node_guid).upper()}}}'", serialized)
        self.assertIn(
            f"EarthingNode:'{{{str(self.earthing_node_guid).upper()}}}'", serialized
        )

        # Verify transformer type properties
        self.assertIn("R0:0.1", serialized)
        self.assertIn("X0:0.2", serialized)

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
        """Test that registering a transformer with the same GUID overwrites the existing one."""
        general1 = EarthingTransformerMV.General(
            guid=self.transformer_guid, name="FirstTransformer", node=self.node_guid
        )
        transformer1 = EarthingTransformerMV(
            general1, [ElementPresentation(sheet=self.sheet_guid)]
        )
        transformer1.register(self.network)

        general2 = EarthingTransformerMV.General(
            guid=self.transformer_guid, name="SecondTransformer", node=self.node_guid
        )
        transformer2 = EarthingTransformerMV(
            general2, [ElementPresentation(sheet=self.sheet_guid)]
        )
        transformer2.register(self.network)

        # Should only have one transformer
        self.assertEqual(len(self.network.earthing_transformers), 1)
        # Should be the second transformer
        self.assertEqual(
            self.network.earthing_transformers[self.transformer_guid].general.name,
            "SecondTransformer",
        )

    def test_minimal_earthing_transformer_serialization(self) -> None:
        """Test that minimal earthing transformers serialize correctly with only required fields."""
        general = EarthingTransformerMV.General(
            guid=self.transformer_guid, name="MinimalTransformer", node=self.node_guid
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        transformer = EarthingTransformerMV(general, [presentation])
        transformer.register(self.network)

        serialized = transformer.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalTransformer'", serialized)

        # Should not have optional sections
        self.assertNotIn("#EarthingTransformerType", serialized)

    def test_earthing_transformer_with_earthing_serializes_correctly(self) -> None:
        """Test that earthing transformers with earthing serialize correctly."""
        general = EarthingTransformerMV.General(
            guid=self.transformer_guid,
            name="EarthingTransformer",
            node=self.node_guid,
            earthing=True,
            re=1.5,
            xe=2.0,
            earthing_node=self.earthing_node_guid,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        transformer = EarthingTransformerMV(general, [presentation])
        transformer.register(self.network)

        serialized = transformer.serialize()
        self.assertIn("Earthing:True", serialized)
        self.assertIn("Re:1.5", serialized)
        self.assertIn("Xe:2", serialized)
        self.assertIn(
            f"EarthingNode:'{{{str(self.earthing_node_guid).upper()}}}'", serialized
        )

    def test_earthing_transformer_with_power_reference_serializes_correctly(
        self,
    ) -> None:
        """Test that earthing transformers with power reference serialize correctly."""
        general = EarthingTransformerMV.General(
            guid=self.transformer_guid,
            name="PowerRefTransformer",
            node=self.node_guid,
            pref=50.0,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        transformer = EarthingTransformerMV(general, [presentation])
        transformer.register(self.network)

        serialized = transformer.serialize()
        self.assertIn("Pref:50", serialized)

    def test_earthing_transformer_with_type_properties_serializes_correctly(
        self,
    ) -> None:
        """Test that earthing transformers with type properties serialize correctly."""
        general = EarthingTransformerMV.General(
            guid=self.transformer_guid, name="TypeTransformer", node=self.node_guid
        )
        transformer_type = EarthingTransformerMV.EarthingTransformerType(
            r0=0.1,
            x0=0.2,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        transformer = EarthingTransformerMV(general, [presentation], transformer_type)
        transformer.register(self.network)

        serialized = transformer.serialize()
        self.assertIn("R0:0.1", serialized)
        self.assertIn("X0:0.2", serialized)

    def test_earthing_transformer_with_maintenance_properties_serializes_correctly(
        self,
    ) -> None:
        """Test that earthing transformers with maintenance properties serialize correctly."""
        general = EarthingTransformerMV.General(
            guid=self.transformer_guid,
            name="MaintenanceTransformer",
            node=self.node_guid,
            failure_frequency=0.01,
            repair_duration=2.5,
            maintenance_frequency=0.1,
            maintenance_duration=4.0,
            maintenance_cancel_duration=1.0,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        transformer = EarthingTransformerMV(general, [presentation])
        transformer.register(self.network)

        serialized = transformer.serialize()
        self.assertIn("FailureFrequency:0.01", serialized)
        self.assertIn("RepairDuration:2.5", serialized)
        self.assertIn("MaintenanceFrequency:0.1", serialized)
        self.assertIn("MaintenanceDuration:4.0", serialized)
        self.assertIn("MaintenanceCancelDuration:1.0", serialized)

    def test_earthing_transformer_with_switch_state_serializes_correctly(self) -> None:
        """Test that earthing transformers with switch state serialize correctly."""
        general = EarthingTransformerMV.General(
            guid=self.transformer_guid,
            name="SwitchStateTransformer",
            node=self.node_guid,
            switch_state=True,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        transformer = EarthingTransformerMV(general, [presentation])
        transformer.register(self.network)

        serialized = transformer.serialize()
        self.assertIn("SwitchState:1", serialized)

    def test_earthing_transformer_with_field_name_serializes_correctly(self) -> None:
        """Test that earthing transformers with field name serialize correctly."""
        general = EarthingTransformerMV.General(
            guid=self.transformer_guid,
            name="FieldNameTransformer",
            node=self.node_guid,
            field_name="TestField",
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        transformer = EarthingTransformerMV(general, [presentation])
        transformer.register(self.network)

        serialized = transformer.serialize()
        self.assertIn("FieldName:'TestField'", serialized)

    def test_earthing_transformer_with_not_preferred_serializes_correctly(self) -> None:
        """Test that earthing transformers with not preferred flag serialize correctly."""
        general = EarthingTransformerMV.General(
            guid=self.transformer_guid,
            name="NotPreferredTransformer",
            node=self.node_guid,
            not_preferred=True,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        transformer = EarthingTransformerMV(general, [presentation])
        transformer.register(self.network)

        serialized = transformer.serialize()
        self.assertIn("NotPreferred:True", serialized)

    def test_earthing_transformer_with_transformer_type_serializes_correctly(
        self,
    ) -> None:
        """Test that earthing transformers with transformer type serialize correctly."""
        general = EarthingTransformerMV.General(
            guid=self.transformer_guid,
            name="TransformerTypeTransformer",
            node=self.node_guid,
            type="TestType",
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        transformer = EarthingTransformerMV(general, [presentation])
        transformer.register(self.network)

        serialized = transformer.serialize()
        self.assertIn("EarthingTransformerType:'TestType'", serialized)

    def test_earthing_transformer_without_earthing_node_serializes_correctly(
        self,
    ) -> None:
        """Test that earthing transformers without earthing node serialize correctly."""
        general = EarthingTransformerMV.General(
            guid=self.transformer_guid,
            name="NoEarthingNodeTransformer",
            node=self.node_guid,
            earthing_node=None,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        transformer = EarthingTransformerMV(general, [presentation])
        transformer.register(self.network)

        serialized = transformer.serialize()
        self.assertNotIn("EarthingNode:", serialized)


if __name__ == "__main__":
    unittest.main()
