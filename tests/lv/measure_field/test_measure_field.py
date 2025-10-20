"""Tests for TMeasureFieldLS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid, encode_guid
from pyptp.elements.lv.measure_field import MeasureFieldLV
from pyptp.elements.lv.presentations import SecundairPresentation
from pyptp.elements.lv.sheet import SheetLV
from pyptp.elements.mixins import Extra, Note
from pyptp.network_lv import NetworkLV


class TestMeasureFieldRegistration(unittest.TestCase):
    """Test measure field registration and functionality."""

    def setUp(self) -> None:
        """Create a fresh network with sheet for testing."""
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

        self.mf_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_measure_field_registration_works(self) -> None:
        """Test that measure fields can register themselves with the network."""
        general = MeasureFieldLV.General(
            guid=self.mf_guid,
            name="TestMeasureField",
        )
        presentation = SecundairPresentation(sheet=self.sheet_guid)

        mf = MeasureFieldLV(general, [presentation])
        mf.register(self.network)

        # Verify measure field is in network
        self.assertIn(self.mf_guid, self.network.measure_fields)
        self.assertIs(self.network.measure_fields[self.mf_guid], mf)

    def test_measure_field_with_full_properties_serializes_correctly(self) -> None:
        """Test that measure fields with all properties serialize correctly."""
        mf = self._create_full_measure_field()
        mf.register(self.network)

        # Test serialization
        serialized = mf.serialize()

        # Verify all sections are present
        self._verify_sections_present(serialized)

        # Verify key general properties are serialized
        self._verify_general_properties(serialized)

        # Verify measurement file properties
        self._verify_measurement_file_properties(serialized)

        # Verify presentation properties
        self._verify_presentation_properties(serialized)

        # Verify extras and notes
        self._verify_extras_and_notes(serialized)

    def _create_full_measure_field(self) -> MeasureFieldLV:
        """Create a measure field with all properties set."""
        general = MeasureFieldLV.General(
            guid=self.mf_guid,
            name="FullMeasureField",
            in_object=self.mf_guid,
            side=2,
            standardizable=True,
            voltage_measure_transformer_present=True,
            voltage_measure_transformer_function="VMF",
            current_measure_transformer1_present=True,
            current_measure_transformer1_function="CMF1",
            current_measure_transformer2_present=True,
            current_measure_transformer2_function="CMF2",
            current_measure_transformer3_present=True,
            current_measure_transformer3_function="CMF3",
            creation_time=1234567890,
            mutation_date=123456789,
            revision_date=1234567890.0,
        )

        measurement_file = MeasureFieldLV.MeasurementsFile(
            file_name="measurements.csv", column="A"
        )

        presentation = SecundairPresentation(
            sheet=self.sheet_guid,
            color=DelphiColor("$00FF00"),
            size=2,
            width=3,
            text_color=DelphiColor("$FF0000"),
            text_size=10,
            font="Arial",
            text_style=1,
            no_text=True,
            upside_down_text=True,
        )

        mf = MeasureFieldLV(general, [presentation], measurement_file)
        mf.extras.append(Extra(text="foo=bar"))
        mf.notes.append(Note(text="Test note"))
        return mf

    def _verify_sections_present(self, serialized: str) -> None:
        """Verify all required sections are present in serialized output."""
        self.assertIn("#General", serialized)
        self.assertIn("#MeasurementFile", serialized)
        self.assertIn("#Presentation", serialized)
        self.assertIn("#Extra", serialized)
        self.assertIn("#Note", serialized)

    def _verify_general_properties(self, serialized: str) -> None:
        """Verify general properties are serialized correctly."""
        self.assertIn("Name:'FullMeasureField'", serialized)
        self.assertIn(f"InObject:'{{{str(self.mf_guid).upper()}}}'", serialized)
        self.assertIn("Side:2", serialized)
        self.assertIn("VoltageMeasureTransformerFunction:'VMF'", serialized)
        self.assertIn("CurrentMeasureTransformer1Function:'CMF1'", serialized)
        self.assertIn("CurrentMeasureTransformer2Function:'CMF2'", serialized)
        self.assertIn("CurrentMeasureTransformer3Function:'CMF3'", serialized)
        self.assertIn("CreationTime:1234567890", serialized)
        self.assertIn("MutationDate:123456789", serialized)
        self.assertIn("RevisionDate:1234567890.0", serialized)

    def _verify_measurement_file_properties(self, serialized: str) -> None:
        """Verify measurement file properties are serialized correctly."""
        self.assertIn("FileName:'measurements.csv'", serialized)
        self.assertIn("Column:'A'", serialized)

    def _verify_presentation_properties(self, serialized: str) -> None:
        """Verify presentation properties are serialized correctly."""
        self.assertIn(f"Sheet:{encode_guid(self.sheet_guid)}", serialized)
        self.assertIn("Size:2", serialized)
        self.assertIn("Width:3", serialized)
        self.assertIn("TextSize:10", serialized)
        self.assertIn("NoText:True", serialized)
        self.assertIn("UpsideDownText:True", serialized)

    def _verify_extras_and_notes(self, serialized: str) -> None:
        """Verify extras and notes are serialized correctly."""
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a measure field with the same GUID overwrites the existing one."""
        general1 = MeasureFieldLV.General(
            guid=self.mf_guid,
            name="FirstMF",
        )
        mf1 = MeasureFieldLV(general1, [SecundairPresentation(sheet=self.sheet_guid)])
        mf1.register(self.network)

        general2 = MeasureFieldLV.General(
            guid=self.mf_guid,
            name="SecondMF",
        )
        mf2 = MeasureFieldLV(general2, [SecundairPresentation(sheet=self.sheet_guid)])
        mf2.register(self.network)

        # Should only have one measure field
        self.assertEqual(len(self.network.measure_fields), 1)
        # Should be the second measure field
        self.assertEqual(
            self.network.measure_fields[self.mf_guid].general.name, "SecondMF"
        )

    def test_minimal_measure_field_serialization(self) -> None:
        """Test that minimal measure fields serialize correctly with only required fields."""
        general = MeasureFieldLV.General(
            guid=self.mf_guid,
            name="MinimalMF",
        )
        presentation = SecundairPresentation(sheet=self.sheet_guid)

        mf = MeasureFieldLV(general, [presentation])
        mf.register(self.network)

        serialized = mf.serialize()

        # Should have basic sections
        self.assertIn("#General", serialized)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalMF'", serialized)

        # Should not have optional sections
        self.assertNotIn("#MeasurementFile", serialized)
        self.assertNotIn("#Extra", serialized)
        self.assertNotIn("#Note", serialized)

    def test_measure_field_without_in_object_serializes_correctly(self) -> None:
        """Test that measure field without InObject serialize correctly."""
        general = MeasureFieldLV.General(
            guid=self.mf_guid, name="NoInObjectCircuitBreaker"
        )
        presentation = SecundairPresentation()

        measure_field = MeasureFieldLV(general, [presentation])
        measure_field.register(self.network)

        serialized = measure_field.serialize()

        # Should not have InObject in serialization
        self.assertNotIn("InObject:", serialized)

        # Should have other properties
        self.assertIn("Name:'NoInObjectCircuitBreaker'", serialized)
        self.assertIn("Side:1", serialized)  # Default value

    def test_multiple_presentations_serialize_correctly(self) -> None:
        """Test that measure fields with multiple presentations serialize correctly."""
        general = MeasureFieldLV.General(
            guid=self.mf_guid,
            name="MultiPresMF",
        )

        pres1 = SecundairPresentation(sheet=self.sheet_guid, size=2, width=3)
        pres2 = SecundairPresentation(sheet=self.sheet_guid, size=4, width=5)

        mf = MeasureFieldLV(general, [pres1, pres2])
        mf.register(self.network)

        serialized = mf.serialize()

        # Should have two presentations
        self.assertIn("#Presentation", serialized)
        self.assertIn("Size:2", serialized)
        self.assertIn("Size:4", serialized)
        self.assertIn("Width:3", serialized)
        self.assertIn("Width:5", serialized)


if __name__ == "__main__":
    unittest.main()
