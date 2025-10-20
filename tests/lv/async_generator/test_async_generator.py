"""Tests for TASynGeneratorLS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid, encode_guid
from pyptp.elements.lv.async_generator import AsynchronousGeneratorLV
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import ElementPresentation, NodePresentation
from pyptp.elements.lv.sheet import SheetLV
from pyptp.elements.mixins import Extra, Note
from pyptp.network_lv import NetworkLV


class TestAsyncGeneratorRegistration(unittest.TestCase):
    """Test async generator registration and functionality."""

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

        self.generator_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_async_generator_registration_works(self) -> None:
        """Test that async generators can register themselves with the network."""
        general = AsynchronousGeneratorLV.General(
            guid=self.generator_guid,
            name="TestGenerator",
            node=self.node_guid,
            field_name="GeneratorField",
            type="Type1",
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        generator = AsynchronousGeneratorLV(general, [presentation])
        generator.register(self.network)

        # Verify generator is in network
        self.assertIn(self.generator_guid, self.network.async_generators)
        self.assertIs(self.network.async_generators[self.generator_guid], generator)

    def test_async_generator_with_full_properties_serializes_correctly(self) -> None:
        """Test that async generators with all properties serialize correctly."""
        generator = self._create_full_generator()
        generator.register(self.network)

        # Test serialization
        serialized = generator.serialize()

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

    def _create_full_generator(self) -> AsynchronousGeneratorLV:
        """Create an async generator with all properties set."""
        general = AsynchronousGeneratorLV.General(
            guid=self.generator_guid,
            node=self.node_guid,
            name="FullGenerator",
            s_L1=True,
            s_L2=False,
            s_L3=True,
            s_N=False,
            field_name="GeneratorField",
            pref=50.0,
            creation_time=1234567890,
            mutation_date=123456789,
            revision_date=1234567890.0,
            type="FullType",
        )

        async_type = AsynchronousGeneratorLV.AsynchronousGeneratorType(
            unom=400.0,
            pnom=100.0,
            r_x=0.1,
            istart_inom=5.0,
            poles=4,
            rpm_nom=1500.0,
            critical_torque=2.5,
            cos_nom=0.85,
            p2=80.0,
            cos2=0.8,
            p3=60.0,
            cos3=0.75,
            p4=40.0,
            cos4=0.7,
            p5=20.0,
            cos5=0.65,
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

        generator = AsynchronousGeneratorLV(general, [presentation], async_type)
        generator.extras.append(Extra(text="foo=bar"))
        generator.notes.append(Note(text="Test note"))
        return generator

    def _verify_sections_present(self, serialized: str) -> None:
        """Verify all required sections are present in serialized output."""
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#AsynchronousGeneratorType", serialized)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

    def _verify_general_properties(self, serialized: str) -> None:
        """Verify general properties are serialized correctly."""
        self.assertIn("Name:'FullGenerator'", serialized)
        self.assertIn("FieldName:'GeneratorField'", serialized)
        self.assertIn("s_L2:False", serialized)  # False values are explicitly shown
        self.assertIn("s_N:False", serialized)  # False values are explicitly shown
        self.assertNotIn("s_L1:true", serialized)
        self.assertNotIn("s_L3:true", serialized)
        self.assertIn("Pref:50.0", serialized)
        self.assertIn("CreationTime:1234567890", serialized)
        self.assertIn("MutationDate:123456789", serialized)
        self.assertIn("RevisionDate:1234567890.0", serialized)
        self.assertIn("AsynchronousGeneratorType:'FullType'", serialized)

    def _verify_type_properties(self, serialized: str) -> None:
        """Verify type properties are serialized correctly."""
        self.assertIn("Unom:400.0", serialized)
        self.assertIn("Pnom:100.0", serialized)
        self.assertIn("R/X:0.1", serialized)
        self.assertIn("Istart/Inom:5.0", serialized)
        self.assertIn("Poles:4", serialized)
        self.assertIn("Rpm:1500.0", serialized)
        self.assertIn("CriticalTorque:2.5", serialized)
        self.assertIn("CosNom:0.85", serialized)
        self.assertIn("p2:80.0", serialized)
        self.assertIn("cos2:0.8", serialized)
        self.assertIn("p3:60.0", serialized)
        self.assertIn("cos3:0.75", serialized)
        self.assertIn("p4:40.0", serialized)
        self.assertIn("cos4:0.7", serialized)
        self.assertIn("p5:20.0", serialized)
        self.assertIn("cos5:0.65", serialized)

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
        """Test that registering a generator with the same GUID overwrites the existing one."""
        general1 = AsynchronousGeneratorLV.General(
            guid=self.generator_guid,
            name="FirstGenerator",
            node=self.node_guid,
            field_name="Field1",
            type="Type1",
        )
        generator1 = AsynchronousGeneratorLV(
            general1, [ElementPresentation(sheet=self.sheet_guid)]
        )
        generator1.register(self.network)

        general2 = AsynchronousGeneratorLV.General(
            guid=self.generator_guid,
            name="SecondGenerator",
            node=self.node_guid,
            field_name="Field2",
            type="Type2",
        )
        generator2 = AsynchronousGeneratorLV(
            general2, [ElementPresentation(sheet=self.sheet_guid)]
        )
        generator2.register(self.network)

        # Should only have one generator
        self.assertEqual(len(self.network.async_generators), 1)
        # Should be the second generator
        self.assertEqual(
            self.network.async_generators[self.generator_guid].general.name,
            "SecondGenerator",
        )

    def test_async_generator_with_profile_guid_serializes_correctly(self) -> None:
        """Test that async generators with profile GUID serialize correctly."""
        profile_guid = Guid(UUID("12345678-1234-5678-9abc-123456789abc"))

        general = AsynchronousGeneratorLV.General(
            guid=self.generator_guid,
            name="ProfileGenerator",
            node=self.node_guid,
            field_name="ProfileField",
            type="ProfileType",
            profile=profile_guid,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        generator = AsynchronousGeneratorLV(general, [presentation])
        generator.register(self.network)

        serialized = generator.serialize()

        # Verify profile GUID is serialized
        self.assertIn(f"Profile:'{{{str(profile_guid).upper()}}}'", serialized)

    def test_minimal_async_generator_serialization(self) -> None:
        """Test that minimal async generators serialize correctly with only required fields."""
        general = AsynchronousGeneratorLV.General(
            guid=self.generator_guid,
            name="MinimalGenerator",
            node=self.node_guid,
            field_name="MinimalField",
            type="MinimalType",
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        generator = AsynchronousGeneratorLV(general, [presentation])
        generator.register(self.network)

        serialized = generator.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalGenerator'", serialized)
        self.assertIn("FieldName:'MinimalField'", serialized)
        self.assertIn("AsynchronousGeneratorType:'MinimalType'", serialized)
        # s_L1, s_L2, s_L3, s_N are not serialized if True (default)
        self.assertNotIn("s_L1:true", serialized)
        self.assertNotIn("s_L2:true", serialized)
        self.assertNotIn("s_L3:true", serialized)
        self.assertNotIn("s_N:true", serialized)
        # Pref is not serialized if 0 (default)
        self.assertNotIn("Pref:0", serialized)

        # Should not have optional sections
        self.assertNotIn("#AsynchronousGeneratorType", serialized)
        self.assertNotIn("#Extra", serialized)
        self.assertNotIn("#Note", serialized)

    def test_multiple_presentations_serialize_correctly(self) -> None:
        """Test that async generators with multiple presentations serialize correctly."""
        general = AsynchronousGeneratorLV.General(
            guid=self.generator_guid,
            name="MultiPresGenerator",
            node=self.node_guid,
            field_name="MultiField",
            type="MultiType",
        )

        pres1 = ElementPresentation(
            sheet=self.sheet_guid, x=100, y=100, color=DelphiColor("$FF0000")
        )
        pres2 = ElementPresentation(
            sheet=self.sheet_guid, x=200, y=200, color=DelphiColor("$00FF00")
        )

        generator = AsynchronousGeneratorLV(general, [pres1, pres2])
        generator.register(self.network)

        serialized = generator.serialize()

        # Should have two presentations
        self.assertEqual(serialized.count("#Presentation"), 2)
        self.assertIn("Color:$FF0000", serialized)
        self.assertIn("Color:$00FF00", serialized)
        self.assertIn("X:100", serialized)
        self.assertIn("X:200", serialized)

    def test_async_generator_with_complex_type_data_serializes_correctly(self) -> None:
        """Test that async generators with complex type data serialize correctly."""
        general = AsynchronousGeneratorLV.General(
            guid=self.generator_guid,
            name="ComplexTypeGenerator",
            node=self.node_guid,
            field_name="ComplexField",
            type="ComplexType",
        )

        # Create type data with more complex values
        async_type = AsynchronousGeneratorLV.AsynchronousGeneratorType(
            unom=690.0,
            pnom=500.0,
            r_x=0.15,
            istart_inom=7.2,
            poles=6,
            rpm_nom=1000.0,
            critical_torque=3.8,
            cos_nom=0.92,
            p2=90.0,
            cos2=0.88,
            p3=70.0,
            cos3=0.82,
            p4=50.0,
            cos4=0.76,
            p5=30.0,
            cos5=0.70,
        )

        presentation = ElementPresentation(sheet=self.sheet_guid)

        generator = AsynchronousGeneratorLV(general, [presentation], async_type)
        generator.register(self.network)

        serialized = generator.serialize()

        # Verify type section is present
        self.assertIn("#AsynchronousGeneratorType", serialized)

        # Verify type data is serialized
        self.assertIn("Unom:690.0", serialized)
        self.assertIn("Pnom:500.0", serialized)
        self.assertIn("R/X:0.15", serialized)
        self.assertIn("Istart/Inom:7.2", serialized)
        self.assertIn("Poles:6", serialized)
        self.assertIn("Rpm:1000.0", serialized)
        self.assertIn("CriticalTorque:3.8", serialized)
        self.assertIn("CosNom:0.92", serialized)
        self.assertIn("p2:90.0", serialized)
        self.assertIn("cos2:0.88", serialized)
        self.assertIn("p3:70.0", serialized)
        self.assertIn("cos3:0.82", serialized)
        self.assertIn("p4:50.0", serialized)
        self.assertIn("cos4:0.76", serialized)
        self.assertIn("p5:30.0", serialized)
        self.assertIn("cos5:0.7", serialized)


if __name__ == "__main__":
    unittest.main()
