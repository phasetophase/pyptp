"""Tests for TEarthingTransformerLS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid, encode_guid
from pyptp.elements.lv.earthing_transformer import EarthingTransformerLV
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import ElementPresentation, NodePresentation
from pyptp.elements.lv.sheet import SheetLV
from pyptp.elements.mixins import Extra, Note
from pyptp.network_lv import NetworkLV


class TestEarthingTransformerRegistration(unittest.TestCase):
    """Test earthing transformer registration and functionality."""

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

        self.et_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_earthing_transformer_registration_works(self) -> None:
        """Test that earthing transformers can register themselves with the network."""
        general = EarthingTransformerLV.General(
            guid=self.et_guid,
            name="TestEarthingTransformer",
            node=self.node_guid,
            field_name="ETField",
            earthing_transformer_type="Type1",
        )
        type_ = EarthingTransformerLV.EarthingTransformerType()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        et = EarthingTransformerLV(general, [presentation], type_)
        et.register(self.network)

        # Verify earthing transformer is in network
        self.assertIn(self.et_guid, self.network.earthing_transformers)
        self.assertIs(self.network.earthing_transformers[self.et_guid], et)

    def test_earthing_transformer_with_full_properties_serializes_correctly(
        self,
    ) -> None:
        """Test that earthing transformers with all properties serialize correctly."""
        et = self._create_full_et()
        et.register(self.network)

        # Test serialization
        serialized = et.serialize()

        # Verify all sections are present
        self._verify_sections_present(serialized)

        # Verify key general properties are serialized
        self._verify_general_properties(serialized)

        # Verify type properties
        self._verify_type_properties(serialized)

        # Verify presentation properties
        self._verify_presentation_properties(serialized)

        # Verify extras and notes
        self._verify_extras_and_notes(serialized)

    def _create_full_et(self) -> EarthingTransformerLV:
        """Create an earthing transformer with all properties set."""
        general = EarthingTransformerLV.General(
            guid=self.et_guid,
            node=self.node_guid,
            name="FullEarthingTransformer",
            s_L2=False,
            s_N=False,
            field_name="ETField",
            earthing_transformer_type="FullType",
            creation_time=1234567890,
            mutation_date=123456789,
            revision_date=1234567890.0,
        )

        type_ = EarthingTransformerLV.EarthingTransformerType(
            R0=0.1,
            X0=0.2,
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

        et = EarthingTransformerLV(general, [presentation], type_)
        et.extras.append(Extra(text="foo=bar"))
        et.notes.append(Note(text="Test note"))
        return et

    def _verify_sections_present(self, serialized: str) -> None:
        """Verify all required sections are present in serialized output."""
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#EarthingTransformerType", serialized)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

    def _verify_general_properties(self, serialized: str) -> None:
        """Verify general properties are serialized correctly."""
        self.assertIn("Name:'FullEarthingTransformer'", serialized)
        self.assertIn("FieldName:'ETField'", serialized)
        self.assertNotIn("s_L2:", serialized)  # False values are skipped
        self.assertNotIn("s_N:", serialized)  # False values are skipped
        self.assertIn("EarthingTransformerType:'FullType'", serialized)
        self.assertIn("CreationTime:1234567890", serialized)
        self.assertIn("MutationDate:123456789", serialized)
        self.assertIn("RevisionDate:1234567890.0", serialized)

    def _verify_type_properties(self, serialized: str) -> None:
        """Verify type properties are serialized correctly."""
        self.assertIn("R0:0.1", serialized)
        self.assertIn("X0:0.2", serialized)

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
        """Test that registering an earthing transformer with the same GUID overwrites the existing one."""
        general1 = EarthingTransformerLV.General(
            guid=self.et_guid,
            name="FirstET",
            node=self.node_guid,
            field_name="Field1",
            earthing_transformer_type="Type1",
        )
        type1 = EarthingTransformerLV.EarthingTransformerType()
        et1 = EarthingTransformerLV(
            general1, [ElementPresentation(sheet=self.sheet_guid)], type1
        )
        et1.register(self.network)

        general2 = EarthingTransformerLV.General(
            guid=self.et_guid,
            name="SecondET",
            node=self.node_guid,
            field_name="Field2",
            earthing_transformer_type="Type2",
        )
        type2 = EarthingTransformerLV.EarthingTransformerType()
        et2 = EarthingTransformerLV(
            general2, [ElementPresentation(sheet=self.sheet_guid)], type2
        )
        et2.register(self.network)

        # Should only have one earthing transformer
        self.assertEqual(len(self.network.earthing_transformers), 1)
        # Should be the second earthing transformer
        self.assertEqual(
            self.network.earthing_transformers[self.et_guid].general.name, "SecondET"
        )

    def test_minimal_earthing_transformer_serialization(self) -> None:
        """Test that minimal earthing transformers serialize correctly with only required fields."""
        general = EarthingTransformerLV.General(
            guid=self.et_guid,
            name="MinimalET",
            node=self.node_guid,
            field_name="MinimalField",
            earthing_transformer_type="MinimalType",
        )
        type_ = EarthingTransformerLV.EarthingTransformerType()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        et = EarthingTransformerLV(general, [presentation], type_)
        et.register(self.network)

        serialized = et.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#EarthingTransformerType", serialized)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalET'", serialized)
        self.assertIn("FieldName:'MinimalField'", serialized)
        self.assertIn("EarthingTransformerType:'MinimalType'", serialized)
        # self.assertIn("s_N:True", serialized)  # Default value, should not be checked

        # Should not have optional sections
        self.assertNotIn("#Extra", serialized)
        self.assertNotIn("#Note", serialized)

    def test_multiple_presentations_serialize_correctly(self) -> None:
        """Test that earthing transformers with multiple presentations serialize correctly."""
        general = EarthingTransformerLV.General(
            guid=self.et_guid,
            name="MultiPresET",
            node=self.node_guid,
            field_name="MultiField",
            earthing_transformer_type="MultiType",
        )
        type_ = EarthingTransformerLV.EarthingTransformerType()

        pres1 = ElementPresentation(
            sheet=self.sheet_guid, x=100, y=100, color=DelphiColor("$FF0000")
        )
        pres2 = ElementPresentation(
            sheet=self.sheet_guid, x=200, y=200, color=DelphiColor("$00FF00")
        )

        et = EarthingTransformerLV(general, [pres1, pres2], type_)
        et.register(self.network)

        serialized = et.serialize()

        # Should have two presentations
        self.assertEqual(serialized.count("#Presentation"), 2)
        self.assertIn("Color:$FF0000", serialized)
        self.assertIn("Color:$00FF00", serialized)
        self.assertIn("X:100", serialized)
        self.assertIn("X:200", serialized)


if __name__ == "__main__":
    unittest.main()
