"""Tests for TSynGeneratorLS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid, encode_guid
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import ElementPresentation, NodePresentation
from pyptp.elements.lv.sheet import SheetLV
from pyptp.elements.lv.syn_generator import SynchronousGeneratorLV
from pyptp.elements.mixins import Extra, Note
from pyptp.network_lv import NetworkLV


class TestSynGeneratorRegistration(unittest.TestCase):
    """Test synchronous generator registration and functionality."""

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

        self.syn_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_syn_generator_registration_works(self) -> None:
        """Test that synchronous generators can register themselves with the network."""
        general = SynchronousGeneratorLV.General(
            guid=self.syn_guid,
            name="TestSynGenerator",
            node=self.node_guid,
            field_name="SynField",
            type="Type1",
        )
        type_ = SynchronousGeneratorLV.SynchronousGeneratorType()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        syn = SynchronousGeneratorLV(general, [presentation], type_)
        syn.register(self.network)

        # Verify synchronous generator is in network
        self.assertIn(self.syn_guid, self.network.syn_generators)
        self.assertIs(self.network.syn_generators[self.syn_guid], syn)

    def test_syn_generator_with_full_properties_serializes_correctly(self) -> None:
        """Test that synchronous generators with all properties serialize correctly."""
        syn = self._create_full_syn()
        syn.register(self.network)

        # Test serialization
        serialized = syn.serialize()

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

    def _create_full_syn(self) -> SynchronousGeneratorLV:
        """Create a synchronous generator with all properties set."""
        general = SynchronousGeneratorLV.General(
            guid=self.syn_guid,
            node=self.node_guid,
            name="FullSynGenerator",
            s_L1=True,
            s_L2=False,
            s_L3=True,
            s_N=False,
            field_name="SynField",
            pref=100.0,
            control_sort="Auto",
            cos_ref=0.99,
            uref=400.0,
            type="FullType",
            creation_time=1234567890,
            mutation_date=123456789,
            revision_date=1234567890.0,
        )

        type_ = SynchronousGeneratorLV.SynchronousGeneratorType(
            unom=400.0,
            snom=200.0,
            cos_nom=0.98,
            q_min=-50.0,
            q_max=50.0,
            rg=0.1,
            xd2sat=0.2,
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

        syn = SynchronousGeneratorLV(general, [presentation], type_)
        syn.extras.append(Extra(text="foo=bar"))
        syn.notes.append(Note(text="Test note"))
        return syn

    def _verify_sections_present(self, serialized: str) -> None:
        """Verify all required sections are present in serialized output."""
        self.assertIn("#General", serialized)
        self.assertIn("#SynchronousGeneratorType", serialized)
        self.assertIn("#Presentation", serialized)
        self.assertIn("#Extra", serialized)
        self.assertIn("#Note", serialized)

    def _verify_general_properties(self, serialized: str) -> None:
        """Verify general properties are serialized correctly."""
        self.assertIn("Name:'FullSynGenerator'", serialized)
        self.assertIn("FieldName:'SynField'", serialized)
        self.assertNotIn("s_L2:", serialized)  # False values are skipped
        self.assertIn("Pref:100.0", serialized)
        self.assertIn("ControlSort:'Auto'", serialized)
        self.assertIn("CosRef:0.99", serialized)
        self.assertIn("Uref:400.0", serialized)
        self.assertIn("SynchronousGeneratorType:'FullType'", serialized)
        self.assertIn("CreationTime:1234567890", serialized)
        self.assertIn("MutationDate:123456789", serialized)
        self.assertIn("RevisionDate:1234567890.0", serialized)

    def _verify_type_properties(self, serialized: str) -> None:
        """Verify type properties are serialized correctly."""
        self.assertIn("Unom:400.0", serialized)
        self.assertIn("Snom:200.0", serialized)
        self.assertIn("CosNom:0.98", serialized)
        self.assertIn("Qmin:-50.0", serialized)
        self.assertIn("Qmax:50.0", serialized)
        self.assertIn("Rg:0.1", serialized)
        self.assertIn("Xd2sat:0.2", serialized)

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
        """Test that registering a synchronous generator with the same GUID overwrites the existing one."""
        general1 = SynchronousGeneratorLV.General(
            guid=self.syn_guid,
            name="FirstSyn",
            node=self.node_guid,
            field_name="Field1",
            type="Type1",
        )
        type1 = SynchronousGeneratorLV.SynchronousGeneratorType()
        syn1 = SynchronousGeneratorLV(
            general1, [ElementPresentation(sheet=self.sheet_guid)], type1
        )
        syn1.register(self.network)

        general2 = SynchronousGeneratorLV.General(
            guid=self.syn_guid,
            name="SecondSyn",
            node=self.node_guid,
            field_name="Field2",
            type="Type2",
        )
        type2 = SynchronousGeneratorLV.SynchronousGeneratorType()
        syn2 = SynchronousGeneratorLV(
            general2, [ElementPresentation(sheet=self.sheet_guid)], type2
        )
        syn2.register(self.network)

        # Should only have one synchronous generator
        self.assertEqual(len(self.network.syn_generators), 1)
        # Should be the second synchronous generator
        self.assertEqual(
            self.network.syn_generators[self.syn_guid].general.name, "SecondSyn"
        )

    def test_minimal_syn_generator_serialization(self) -> None:
        """Test that minimal synchronous generators serialize correctly with only required fields."""
        general = SynchronousGeneratorLV.General(
            guid=self.syn_guid,
            name="MinimalSyn",
            node=self.node_guid,
            field_name="MinimalField",
            type="MinimalType",
        )
        type_ = SynchronousGeneratorLV.SynchronousGeneratorType()
        presentation = ElementPresentation(sheet=self.sheet_guid)

        syn = SynchronousGeneratorLV(general, [presentation], type_)
        syn.register(self.network)

        serialized = syn.serialize()

        # Should have basic sections
        self.assertIn("#General", serialized)
        self.assertIn("#SynchronousGeneratorType", serialized)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalSyn'", serialized)
        self.assertIn("FieldName:'MinimalField'", serialized)
        self.assertIn("SynchronousGeneratorType:'MinimalType'", serialized)

        # Should not have optional sections
        self.assertNotIn("#Extra", serialized)
        self.assertNotIn("#Note", serialized)

    def test_multiple_presentations_serialize_correctly(self) -> None:
        """Test that synchronous generators with multiple presentations serialize correctly."""
        general = SynchronousGeneratorLV.General(
            guid=self.syn_guid,
            name="MultiPresSyn",
            node=self.node_guid,
            field_name="MultiField",
            type="MultiType",
        )
        type_ = SynchronousGeneratorLV.SynchronousGeneratorType()

        pres1 = ElementPresentation(
            sheet=self.sheet_guid, x=100, y=100, color=DelphiColor("$FF0000")
        )
        pres2 = ElementPresentation(
            sheet=self.sheet_guid, x=200, y=200, color=DelphiColor("$00FF00")
        )

        syn = SynchronousGeneratorLV(general, [pres1, pres2], type_)
        syn.register(self.network)

        serialized = syn.serialize()

        # Should have two presentations
        self.assertIn("#Presentation", serialized)
        self.assertIn("Color:$FF0000", serialized)
        self.assertIn("Color:$00FF00", serialized)
        self.assertIn("X:100", serialized)
        self.assertIn("X:200", serialized)


if __name__ == "__main__":
    unittest.main()
