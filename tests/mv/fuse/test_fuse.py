"""Tests for TFuseMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid
from pyptp.elements.mixins import Extra, Note
from pyptp.elements.mv.fuse import FuseMV
from pyptp.elements.mv.presentations import SecondaryPresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.network_mv import NetworkMV


class TestFuseRegistration(unittest.TestCase):
    """Test fuse registration and functionality."""

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

        self.fuse_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))
        self.in_object_guid = Guid(UUID("12345678-9abc-def0-1234-56789abcdef0"))

    def test_fuse_registration_works(self) -> None:
        """Test that fuses can register themselves with the network."""
        general = FuseMV.General(guid=self.fuse_guid, name="TestFuse")
        fuse_type = FuseMV.FuseType()
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        fuse = FuseMV(general, fuse_type, [presentation])
        fuse.register(self.network)

        # Verify fuse is in network
        self.assertIn(self.fuse_guid, self.network.fuses)
        self.assertIs(self.network.fuses[self.fuse_guid], fuse)

    def test_fuse_with_full_properties_serializes_correctly(self) -> None:
        """Test that fuses with all properties serialize correctly."""
        general = FuseMV.General(
            guid=self.fuse_guid,
            creation_time=123.45,
            mutation_date=10,
            revision_date=20,
            variant=True,
            name="FullFuse",
            in_object=self.in_object_guid,
            side=2,
            type="TestFuseType",
        )

        fuse_type = FuseMV.FuseType(
            short_name="TestFuseShort",
            unom=20.0,
            inom=100.0,
            three_phase=False,
            I1=0.5,
            T1=0.1,
            I2=1.0,
            T2=0.2,
            I3=1.5,
            T3=0.3,
            I4=2.0,
            T4=0.4,
            I5=2.5,
            T5=0.5,
            I6=3.0,
            T6=0.6,
            I7=3.5,
            T7=0.7,
            I8=4.0,
            T8=0.8,
            I9=4.5,
            T9=0.9,
            I10=5.0,
            T10=1.0,
            I11=5.5,
            T11=1.1,
            I12=6.0,
            T12=1.2,
            I13=6.5,
            T13=1.3,
            I14=7.0,
            T14=1.4,
            I15=7.5,
            T15=1.5,
            I16=8.0,
            T16=1.6,
        )

        presentation = SecondaryPresentation(
            sheet=self.sheet_guid,
            distance=100,
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

        fuse = FuseMV(general, fuse_type, [presentation])
        fuse.extras.append(Extra(text="foo=bar"))
        fuse.notes.append(Note(text="Test note"))
        fuse.register(self.network)

        # Test serialization
        serialized = fuse.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertEqual(serialized.count("#FuseType"), 1)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify general properties
        self.assertIn("Name:'FullFuse'", serialized)
        self.assertIn("Variant:True", serialized)
        self.assertIn("Side:2", serialized)
        self.assertIn("FuseType:'TestFuseType'", serialized)

        # Verify InObject reference
        self.assertIn(f"InObject:'{{{str(self.in_object_guid).upper()}}}'", serialized)

        # Verify fuse type properties
        self.assertIn("ShortName:'TestFuseShort'", serialized)
        self.assertIn("Unom:20", serialized)
        self.assertIn("Inom:100", serialized)
        # ThreePhase:False is skipped in serialization (False is the default skip value)
        self.assertIn("I1:0.5", serialized)
        self.assertIn("T1:0.1", serialized)
        self.assertIn("I2:1", serialized)
        self.assertIn("T2:0.2", serialized)
        self.assertIn("I3:1.5", serialized)
        self.assertIn("T3:0.3", serialized)
        self.assertIn("I16:8", serialized)
        self.assertIn("T16:1.6", serialized)

        # Verify presentation properties
        self.assertIn(f"Sheet:'{{{str(self.sheet_guid).upper()}}}'", serialized)
        self.assertIn("Distance:100", serialized)
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
        """Test that registering a fuse with the same GUID overwrites the existing one."""
        general1 = FuseMV.General(guid=self.fuse_guid, name="FirstFuse")
        fuse_type1 = FuseMV.FuseType(inom=50.0)
        fuse1 = FuseMV(
            general1, fuse_type1, [SecondaryPresentation(sheet=self.sheet_guid)]
        )
        fuse1.register(self.network)

        general2 = FuseMV.General(guid=self.fuse_guid, name="SecondFuse")
        fuse_type2 = FuseMV.FuseType(inom=100.0)
        fuse2 = FuseMV(
            general2, fuse_type2, [SecondaryPresentation(sheet=self.sheet_guid)]
        )
        fuse2.register(self.network)

        # Should only have one fuse
        self.assertEqual(len(self.network.fuses), 1)
        # Should be the second fuse
        self.assertEqual(self.network.fuses[self.fuse_guid].general.name, "SecondFuse")

    def test_minimal_fuse_serialization(self) -> None:
        """Test that minimal fuses serialize correctly with only required fields."""
        general = FuseMV.General(guid=self.fuse_guid, name="MinimalFuse")
        fuse_type = FuseMV.FuseType()
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        fuse = FuseMV(general, fuse_type, [presentation])
        fuse.register(self.network)

        serialized = fuse.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertEqual(serialized.count("#FuseType"), 1)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalFuse'", serialized)
        self.assertIn("Side:1", serialized)  # Default value

    def test_fuse_with_in_object_serializes_correctly(self) -> None:
        """Test that fuses with InObject serialize correctly."""
        general = FuseMV.General(
            guid=self.fuse_guid,
            name="InObjectFuse",
            in_object=self.in_object_guid,
        )
        fuse_type = FuseMV.FuseType()
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        fuse = FuseMV(general, fuse_type, [presentation])
        fuse.register(self.network)

        serialized = fuse.serialize()
        self.assertIn(f"InObject:'{{{str(self.in_object_guid).upper()}}}'", serialized)

    def test_fuse_with_side_serializes_correctly(self) -> None:
        """Test that fuses with side setting serialize correctly."""
        general = FuseMV.General(
            guid=self.fuse_guid,
            name="SideFuse",
            side=3,
        )
        fuse_type = FuseMV.FuseType()
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        fuse = FuseMV(general, fuse_type, [presentation])
        fuse.register(self.network)

        serialized = fuse.serialize()
        self.assertIn("Side:3", serialized)

    def test_fuse_with_variant_serializes_correctly(self) -> None:
        """Test that fuses with variant flag serialize correctly."""
        general = FuseMV.General(
            guid=self.fuse_guid,
            name="VariantFuse",
            variant=True,
        )
        fuse_type = FuseMV.FuseType()
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        fuse = FuseMV(general, fuse_type, [presentation])
        fuse.register(self.network)

        serialized = fuse.serialize()
        self.assertIn("Variant:True", serialized)

    def test_fuse_with_fuse_type_string_serializes_correctly(self) -> None:
        """Test that fuses with fuse type string serialize correctly."""
        general = FuseMV.General(
            guid=self.fuse_guid,
            name="FuseTypeFuse",
            type="TestFuseType",
        )
        fuse_type = FuseMV.FuseType()
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        fuse = FuseMV(general, fuse_type, [presentation])
        fuse.register(self.network)

        serialized = fuse.serialize()
        self.assertIn("FuseType:'TestFuseType'", serialized)

    def test_fuse_with_three_phase_false_serializes_correctly(self) -> None:
        """Test that fuses with three phase false serialize correctly."""
        general = FuseMV.General(guid=self.fuse_guid, name="SinglePhaseFuse")
        fuse_type = FuseMV.FuseType(three_phase=False)
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        fuse = FuseMV(general, fuse_type, [presentation])
        fuse.register(self.network)

        serialized = fuse.serialize()
        # ThreePhase:False is skipped in serialization (False is the default skip value)
        self.assertNotIn("ThreePhase:", serialized)

    def test_fuse_with_nominal_values_serializes_correctly(self) -> None:
        """Test that fuses with nominal values serialize correctly."""
        general = FuseMV.General(guid=self.fuse_guid, name="NominalFuse")
        fuse_type = FuseMV.FuseType(
            short_name="NominalFuseShort",
            unom=20.0,
            inom=100.0,
        )
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        fuse = FuseMV(general, fuse_type, [presentation])
        fuse.register(self.network)

        serialized = fuse.serialize()
        self.assertIn("ShortName:'NominalFuseShort'", serialized)
        self.assertIn("Unom:20", serialized)
        self.assertIn("Inom:100", serialized)

    def test_fuse_with_time_current_characteristics_serializes_correctly(self) -> None:
        """Test that fuses with time-current characteristics serialize correctly."""
        general = FuseMV.General(guid=self.fuse_guid, name="TimeCurrentFuse")
        fuse_type = FuseMV.FuseType(
            I1=1.0,
            T1=0.1,
            I2=2.0,
            T2=0.2,
            I3=3.0,
            T3=0.3,
        )
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        fuse = FuseMV(general, fuse_type, [presentation])
        fuse.register(self.network)

        serialized = fuse.serialize()
        self.assertIn("I1:1", serialized)
        self.assertIn("T1:0.1", serialized)
        self.assertIn("I2:2", serialized)
        self.assertIn("T2:0.2", serialized)
        self.assertIn("I3:3", serialized)
        self.assertIn("T3:0.3", serialized)

    def test_fuse_without_in_object_serializes_correctly(self) -> None:
        """Test that fuses without InObject serialize correctly."""
        general = FuseMV.General(
            guid=self.fuse_guid,
            name="NoInObjectFuse",
            in_object=None,
        )
        fuse_type = FuseMV.FuseType()
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        fuse = FuseMV(general, fuse_type, [presentation])
        fuse.register(self.network)

        serialized = fuse.serialize()
        self.assertNotIn("InObject:", serialized)


if __name__ == "__main__":
    unittest.main()
