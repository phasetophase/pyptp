"""Tests for TIndicatorMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid
from pyptp.elements.mixins import Extra, Note
from pyptp.elements.mv.indicator import IndicatorMV
from pyptp.elements.mv.presentations import SecondaryPresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.network_mv import NetworkMV


class TestIndicatorRegistration(unittest.TestCase):
    """Test indicator registration and functionality."""

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

        self.indicator_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))
        self.in_object_guid = Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5"))

    def test_indicator_registration_works(self) -> None:
        """Test that indicators can register themselves with the network."""
        general = IndicatorMV.General(guid=self.indicator_guid, name="TestIndicator")
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        indicator = IndicatorMV(general, [presentation])
        indicator.register(self.network)

        # Verify indicator is in network
        self.assertIn(self.indicator_guid, self.network.indicators)
        self.assertIs(self.network.indicators[self.indicator_guid], indicator)

    def test_indicator_with_full_properties_serializes_correctly(self) -> None:
        """Test that indicators with all properties serialize correctly."""
        general = IndicatorMV.General(
            guid=self.indicator_guid,
            creation_time=123.45,
            mutation_date=10,
            revision_date=20,
            variant=True,
            name="FullIndicator",
            in_object=self.in_object_guid,
            side=2,
            phase_current=100.0,
            phase_direction_sensitive=True,
            phase_response_time=0.5,
            earth_current=50.0,
            earth_voltage=400.0,
            earth_response_time=0.2,
            auto_reset=True,
            remote_signaling=True,
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

        indicator = IndicatorMV(general, [presentation])
        indicator.extras.append(Extra(text="foo=bar"))
        indicator.notes.append(Note(text="Test note"))
        indicator.register(self.network)

        # Test serialization
        serialized = indicator.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify general properties
        self.assertIn("Name:'FullIndicator'", serialized)
        self.assertIn("CreationTime:123.45", serialized)
        self.assertIn("MutationDate:10", serialized)
        self.assertIn("RevisionDate:20", serialized)
        self.assertIn("Variant:True", serialized)
        self.assertIn(f"InObject:'{{{str(self.in_object_guid).upper()}}}'", serialized)
        self.assertIn("Side:2", serialized)
        self.assertIn("PhaseCurrent:100", serialized)
        self.assertIn("PhaseDirectionSensitive:True", serialized)
        self.assertIn("PhaseResponseTime:0.5", serialized)
        self.assertIn("EarthCurrent:50", serialized)
        self.assertIn("EarthVoltage:400", serialized)
        self.assertIn("EarthResponseTime:0.2", serialized)
        self.assertIn("AutoReset:True", serialized)
        self.assertIn("RemoteSignaling:True", serialized)

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
        """Test that registering an indicator with the same GUID overwrites the existing one."""
        general1 = IndicatorMV.General(guid=self.indicator_guid, name="FirstIndicator")
        indicator1 = IndicatorMV(
            general1, [SecondaryPresentation(sheet=self.sheet_guid)]
        )
        indicator1.register(self.network)

        general2 = IndicatorMV.General(guid=self.indicator_guid, name="SecondIndicator")
        indicator2 = IndicatorMV(
            general2, [SecondaryPresentation(sheet=self.sheet_guid)]
        )
        indicator2.register(self.network)

        # Should only have one indicator
        self.assertEqual(len(self.network.indicators), 1)
        # Should be the second indicator
        self.assertEqual(
            self.network.indicators[self.indicator_guid].general.name, "SecondIndicator"
        )

    def test_minimal_indicator_serialization(self) -> None:
        """Test that minimal indicators serialize correctly with only required fields."""
        general = IndicatorMV.General(guid=self.indicator_guid, name="MinimalIndicator")
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        indicator = IndicatorMV(general, [presentation])
        indicator.register(self.network)

        serialized = indicator.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalIndicator'", serialized)
        self.assertIn("Side:1", serialized)  # Default value

        # Should not have optional properties with default values
        self.assertNotIn("MutationDate", serialized)
        self.assertNotIn("RevisionDate", serialized)
        self.assertNotIn("Variant:True", serialized)
        self.assertNotIn("InObject", serialized)
        self.assertNotIn("PhaseCurrent", serialized)
        self.assertNotIn("PhaseDirectionSensitive:True", serialized)
        self.assertNotIn("PhaseResponseTime", serialized)
        self.assertNotIn("EarthCurrent", serialized)
        self.assertNotIn("EarthVoltage", serialized)
        self.assertNotIn("EarthResponseTime", serialized)
        self.assertNotIn("AutoReset:True", serialized)
        self.assertNotIn("RemoteSignaling:True", serialized)

    def test_indicator_with_phase_current_serializes_correctly(self) -> None:
        """Test that indicators with phase current serialize correctly."""
        general = IndicatorMV.General(
            guid=self.indicator_guid,
            name="PhaseCurrentIndicator",
            phase_current=150.0,
            phase_direction_sensitive=True,
            phase_response_time=1.0,
        )
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        indicator = IndicatorMV(general, [presentation])
        indicator.register(self.network)

        serialized = indicator.serialize()
        self.assertIn("PhaseCurrent:150", serialized)
        self.assertIn("PhaseDirectionSensitive:True", serialized)
        self.assertIn("PhaseResponseTime:1", serialized)

    def test_indicator_with_earth_protection_serializes_correctly(self) -> None:
        """Test that indicators with earth protection serialize correctly."""
        general = IndicatorMV.General(
            guid=self.indicator_guid,
            name="EarthProtectionIndicator",
            earth_current=25.0,
            earth_voltage=230.0,
            earth_response_time=0.1,
        )
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        indicator = IndicatorMV(general, [presentation])
        indicator.register(self.network)

        serialized = indicator.serialize()
        self.assertIn("EarthCurrent:25", serialized)
        self.assertIn("EarthVoltage:230", serialized)
        self.assertIn("EarthResponseTime:0.1", serialized)

    def test_indicator_with_auto_reset_serializes_correctly(self) -> None:
        """Test that indicators with auto reset serialize correctly."""
        general = IndicatorMV.General(
            guid=self.indicator_guid,
            name="AutoResetIndicator",
            auto_reset=True,
        )
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        indicator = IndicatorMV(general, [presentation])
        indicator.register(self.network)

        serialized = indicator.serialize()
        self.assertIn("AutoReset:True", serialized)

    def test_indicator_with_remote_signaling_serializes_correctly(self) -> None:
        """Test that indicators with remote signaling serialize correctly."""
        general = IndicatorMV.General(
            guid=self.indicator_guid,
            name="RemoteSignalingIndicator",
            remote_signaling=True,
        )
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        indicator = IndicatorMV(general, [presentation])
        indicator.register(self.network)

        serialized = indicator.serialize()
        self.assertIn("RemoteSignaling:True", serialized)

    def test_indicator_with_in_object_serializes_correctly(self) -> None:
        """Test that indicators with in-object reference serialize correctly."""
        general = IndicatorMV.General(
            guid=self.indicator_guid,
            name="InObjectIndicator",
            in_object=self.in_object_guid,
            side=2,
        )
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        indicator = IndicatorMV(general, [presentation])
        indicator.register(self.network)

        serialized = indicator.serialize()
        self.assertIn(f"InObject:'{{{str(self.in_object_guid).upper()}}}'", serialized)
        self.assertIn("Side:2", serialized)

    def test_indicator_with_variant_serializes_correctly(self) -> None:
        """Test that indicators with variant flag serialize correctly."""
        general = IndicatorMV.General(
            guid=self.indicator_guid,
            name="VariantIndicator",
            variant=True,
        )
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        indicator = IndicatorMV(general, [presentation])
        indicator.register(self.network)

        serialized = indicator.serialize()
        self.assertIn("Variant:True", serialized)


if __name__ == "__main__":
    unittest.main()
