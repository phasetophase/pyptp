"""Tests for TMeasureFieldMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid
from pyptp.elements.mixins import Extra, Note
from pyptp.elements.mv.measure_field import MeasureFieldMV
from pyptp.elements.mv.presentations import SecondaryPresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.network_mv import NetworkMV


class TestMeasureFieldRegistration(unittest.TestCase):
    """Test measure field registration and functionality."""

    def setUp(self) -> None:
        """Create a fresh network with sheet for testing."""
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

        self.measure_field_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))
        self.vision_object_guid = Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5"))

    def test_measure_field_registration_works(self) -> None:
        """Test that measure fields can register themselves with the network."""
        general = MeasureFieldMV.General(
            guid=self.measure_field_guid, name="TestMeasureField"
        )
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        measure_field = MeasureFieldMV(general, [presentation])
        measure_field.register(self.network)

        # Verify measure field is in network
        self.assertIn(self.measure_field_guid, self.network.measure_fields)
        self.assertIs(
            self.network.measure_fields[self.measure_field_guid], measure_field
        )

    def test_measure_field_with_full_properties_serializes_correctly(self) -> None:
        """Test that measure fields with all properties serialize correctly."""
        general = MeasureFieldMV.General(
            guid=self.measure_field_guid,
            creation_time=123.45,
            mutation_date=10,
            revision_date=20,
            variant=True,
            name="FullMeasureField",
            in_object=self.vision_object_guid,
            side=2,
            is_voltage_measure_transformer_present=True,
            voltage_measure_transformer_function="Protection",
            voltage_measure_transformer_type="VT1",
            is_current_measure_transformer1_present=True,
            current_measure_transformer1_function="Protection",
            current_measure_transformer1_type="CT1",
            is_current_measure_transformer2_present=True,
            current_measure_transformer2_function="Measurement",
            current_measure_transformer2_type="CT2",
            is_current_measure_transformer3_present=True,
            current_measure_transformer3_function="Backup",
            current_measure_transformer3_type="CT3",
        )

        presentation = SecondaryPresentation(
            sheet=self.sheet_guid,
            distance=10,
            otherside=True,
            color=DelphiColor("$FF0000"),
            size=2,
            width=3,
            text_color=DelphiColor("$00FF00"),
            text_size=12,
            font="Arial",
            text_style=1,
            no_text=True,
            upside_down_text=True,
            strings_x=10,
            strings_y=20,
            note_x=50,
            note_y=60,
        )

        measure_field = MeasureFieldMV(general, [presentation])
        measure_field.extras.append(Extra(text="foo=bar"))
        measure_field.notes.append(Note(text="Test note"))
        measure_field.register(self.network)

        # Test serialization
        serialized = measure_field.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify general properties
        self.assertIn("Name:'FullMeasureField'", serialized)
        self.assertIn("CreationTime:123.45", serialized)
        self.assertIn("MutationDate:10", serialized)
        self.assertIn("RevisionDate:20", serialized)
        self.assertIn("Variant:True", serialized)
        self.assertIn(
            f"InObject:'{{{str(self.vision_object_guid).upper()}}}'", serialized
        )
        self.assertIn("Side:2", serialized)
        self.assertIn("VoltageMeasureTransformerPresent:True", serialized)
        self.assertIn("VoltageMeasureTransformerFunction:'Protection'", serialized)
        self.assertIn("VoltageMeasureTransformerType:'VT1'", serialized)
        self.assertIn("CurrentMeasureTransformer1Present:True", serialized)
        self.assertIn("CurrentMeasureTransformer1Function:'Protection'", serialized)
        self.assertIn("CurrentMeasureTransformer1Type:'CT1'", serialized)
        self.assertIn("CurrentMeasureTransformer2Present:True", serialized)
        self.assertIn("CurrentMeasureTransformer2Function:'Measurement'", serialized)
        self.assertIn("CurrentMeasureTransformer2Type:'CT2'", serialized)
        self.assertIn("CurrentMeasureTransformer3Present:True", serialized)
        self.assertIn("CurrentMeasureTransformer3Function:'Backup'", serialized)
        self.assertIn("CurrentMeasureTransformer3Type:'CT3'", serialized)

        # Verify presentation properties
        self.assertIn(f"Sheet:'{{{str(self.sheet_guid).upper()}}}'", serialized)
        self.assertIn("Distance:10", serialized)
        self.assertIn("Otherside:True", serialized)
        self.assertIn("Color:$FF0000", serialized)
        self.assertIn("Size:2", serialized)
        self.assertIn("Width:3", serialized)
        self.assertIn("TextColor:$00FF00", serialized)
        self.assertIn("TextSize:12", serialized)
        self.assertIn("NoText:True", serialized)
        self.assertIn("UpsideDownText:True", serialized)
        self.assertIn("StringsX:10", serialized)
        self.assertIn("StringsY:20", serialized)
        self.assertIn("NoteX:50", serialized)
        self.assertIn("NoteY:60", serialized)

        # Verify extras and notes
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a measure field with the same GUID overwrites the existing one."""
        general1 = MeasureFieldMV.General(
            guid=self.measure_field_guid, name="FirstMeasureField"
        )
        measure_field1 = MeasureFieldMV(
            general1, [SecondaryPresentation(sheet=self.sheet_guid)]
        )
        measure_field1.register(self.network)

        general2 = MeasureFieldMV.General(
            guid=self.measure_field_guid, name="SecondMeasureField"
        )
        measure_field2 = MeasureFieldMV(
            general2, [SecondaryPresentation(sheet=self.sheet_guid)]
        )
        measure_field2.register(self.network)

        # Should only have one measure field
        self.assertEqual(len(self.network.measure_fields), 1)
        # Should be the second measure field
        self.assertEqual(
            self.network.measure_fields[self.measure_field_guid].general.name,
            "SecondMeasureField",
        )

    def test_minimal_measure_field_serialization(self) -> None:
        """Test that minimal measure fields serialize correctly with only required fields."""
        general = MeasureFieldMV.General(
            guid=self.measure_field_guid, name="MinimalMeasureField"
        )
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        measure_field = MeasureFieldMV(general, [presentation])
        measure_field.register(self.network)

        serialized = measure_field.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties (all properties are serialized with no_skip)
        self.assertIn("Name:'MinimalMeasureField'", serialized)
        self.assertIn("CreationTime:0", serialized)
        self.assertIn("Side:1", serialized)

        # Should not have optional properties with default values that are skipped
        self.assertNotIn("Variant:", serialized)  # False values are skipped
        self.assertNotIn("VoltageMeasureTransformerPresent:False", serialized)
        self.assertNotIn("VoltageMeasureTransformerFunction:''", serialized)
        self.assertNotIn("VoltageMeasureTransformerType:''", serialized)
        self.assertNotIn("CurrentMeasureTransformer1Present:False", serialized)
        self.assertNotIn("CurrentMeasureTransformer1Function:''", serialized)
        self.assertNotIn("CurrentMeasureTransformer1Type:''", serialized)
        self.assertNotIn("CurrentMeasureTransformer2Present:False", serialized)
        self.assertNotIn("CurrentMeasureTransformer2Function:''", serialized)
        self.assertNotIn("CurrentMeasureTransformer2Type:''", serialized)
        self.assertNotIn("CurrentMeasureTransformer3Present:False", serialized)
        self.assertNotIn("CurrentMeasureTransformer3Function:''", serialized)
        self.assertNotIn("CurrentMeasureTransformer3Type:''", serialized)
        self.assertNotIn("MutationDate", serialized)
        self.assertNotIn("RevisionDate", serialized)
        self.assertNotIn("VisionObject", serialized)

    def test_measure_field_with_voltage_transformer_serializes_correctly(self) -> None:
        """Test that measure fields with voltage transformer serialize correctly."""
        general = MeasureFieldMV.General(
            guid=self.measure_field_guid,
            name="VoltageTransformerMeasureField",
            is_voltage_measure_transformer_present=True,
            voltage_measure_transformer_function="Protection",
            voltage_measure_transformer_type="VT1",
        )
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        measure_field = MeasureFieldMV(general, [presentation])
        measure_field.register(self.network)

        serialized = measure_field.serialize()
        self.assertIn("VoltageMeasureTransformerPresent:True", serialized)
        self.assertIn("VoltageMeasureTransformerFunction:'Protection'", serialized)
        self.assertIn("VoltageMeasureTransformerType:'VT1'", serialized)

    def test_measure_field_with_current_transformer_1_serializes_correctly(
        self,
    ) -> None:
        """Test that measure fields with current transformer 1 serialize correctly."""
        general = MeasureFieldMV.General(
            guid=self.measure_field_guid,
            name="CurrentTransformer1MeasureField",
            is_current_measure_transformer1_present=True,
            current_measure_transformer1_function="Protection",
            current_measure_transformer1_type="CT1",
        )
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        measure_field = MeasureFieldMV(general, [presentation])
        measure_field.register(self.network)

        serialized = measure_field.serialize()
        self.assertIn("CurrentMeasureTransformer1Present:True", serialized)
        self.assertIn("CurrentMeasureTransformer1Function:'Protection'", serialized)
        self.assertIn("CurrentMeasureTransformer1Type:'CT1'", serialized)

    def test_measure_field_with_current_transformer_2_serializes_correctly(
        self,
    ) -> None:
        """Test that measure fields with current transformer 2 serialize correctly."""
        general = MeasureFieldMV.General(
            guid=self.measure_field_guid,
            name="CurrentTransformer2MeasureField",
            is_current_measure_transformer2_present=True,
            current_measure_transformer2_function="Measurement",
            current_measure_transformer2_type="CT2",
        )
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        measure_field = MeasureFieldMV(general, [presentation])
        measure_field.register(self.network)

        serialized = measure_field.serialize()
        self.assertIn("CurrentMeasureTransformer2Present:True", serialized)
        self.assertIn("CurrentMeasureTransformer2Function:'Measurement'", serialized)
        self.assertIn("CurrentMeasureTransformer2Type:'CT2'", serialized)

    def test_measure_field_with_current_transformer_3_serializes_correctly(
        self,
    ) -> None:
        """Test that measure fields with current transformer 3 serialize correctly."""
        general = MeasureFieldMV.General(
            guid=self.measure_field_guid,
            name="CurrentTransformer3MeasureField",
            is_current_measure_transformer3_present=True,
            current_measure_transformer3_function="Backup",
            current_measure_transformer3_type="CT3",
        )
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        measure_field = MeasureFieldMV(general, [presentation])
        measure_field.register(self.network)

        serialized = measure_field.serialize()
        self.assertIn("CurrentMeasureTransformer3Present:True", serialized)
        self.assertIn("CurrentMeasureTransformer3Function:'Backup'", serialized)
        self.assertIn("CurrentMeasureTransformer3Type:'CT3'", serialized)

    def test_measure_field_with_in_object_serializes_correctly(self) -> None:
        """Test that measure fields with vision object reference serialize correctly."""
        general = MeasureFieldMV.General(
            guid=self.measure_field_guid,
            name="VisionObjectMeasureField",
            in_object=self.vision_object_guid,
            side=2,
        )
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        measure_field = MeasureFieldMV(general, [presentation])
        measure_field.register(self.network)

        serialized = measure_field.serialize()
        self.assertIn(
            f"InObject:'{{{str(self.vision_object_guid).upper()}}}'", serialized
        )
        self.assertIn("Side:2", serialized)

    def test_measure_field_with_variant_serializes_correctly(self) -> None:
        """Test that measure fields with variant flag serialize correctly."""
        general = MeasureFieldMV.General(
            guid=self.measure_field_guid,
            name="VariantMeasureField",
            variant=True,
        )
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        measure_field = MeasureFieldMV(general, [presentation])
        measure_field.register(self.network)

        serialized = measure_field.serialize()
        self.assertIn("Variant:True", serialized)


if __name__ == "__main__":
    unittest.main()
