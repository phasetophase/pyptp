"""Tests for TLoadSwitchMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid
from pyptp.elements.mixins import Extra, Note
from pyptp.elements.mv.load_switch import LoadSwitchMV
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import NodePresentation, SecondaryPresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.network_mv import NetworkMV


class TestLoadSwitchRegistration(unittest.TestCase):
    """Test load switch registration and functionality."""

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

        # Create and register a node for the load switch
        node = NodeMV(
            NodeMV.General(
                guid=Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5")), name="TestNode"
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node.register(self.network)
        self.node_guid = node.general.guid

        self.load_switch_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))
        self.in_object_guid = Guid(UUID("aec2228f-a78e-4f54-9ed2-0a7dbd48b3f6"))

    def test_load_switch_registration_works(self) -> None:
        """Test that load switches can register themselves with the network."""
        general = LoadSwitchMV.General(
            guid=self.load_switch_guid, name="TestLoadSwitch"
        )
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        load_switch = LoadSwitchMV(general, None, [presentation])
        load_switch.register(self.network)

        # Verify load switch is in network
        self.assertIn(self.load_switch_guid, self.network.load_switches)
        self.assertIs(self.network.load_switches[self.load_switch_guid], load_switch)

    def test_load_switch_with_full_properties_serializes_correctly(self) -> None:
        """Test that load switches with all properties serialize correctly."""
        general = LoadSwitchMV.General(
            guid=self.load_switch_guid,
            creation_time=123.45,
            mutation_date=10,
            revision_date=20.5,
            variant=True,
            name="FullLoadSwitch",
            in_object=self.in_object_guid,
            side=2,
            node=self.node_guid,
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

        load_switch_type = LoadSwitchMV.LoadSwitchType(
            short_name="TestType",
            unom=400.0,
            inom=100.0,
            switch_time=0.1,
            ik_make=1000.0,
            ik_break=800.0,
            ik_dynamic=1200.0,
            ik_thermal=1000.0,
            t_thermal=1.0,
        )

        load_switch = LoadSwitchMV(general, load_switch_type, [presentation])
        load_switch.extras.append(Extra(text="foo=bar"))
        load_switch.notes.append(Note(text="Test note"))
        load_switch.register(self.network)

        # Test serialization
        serialized = load_switch.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertEqual(serialized.count("#LoadSwitchType"), 1)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify general properties
        self.assertIn("Name:'FullLoadSwitch'", serialized)
        self.assertIn("CreationTime:123.45", serialized)
        self.assertIn("MutationDate:10", serialized)
        self.assertIn("RevisionDate:20.5", serialized)
        self.assertIn("Variant:True", serialized)
        self.assertIn(f"InObject:'{{{str(self.in_object_guid).upper()}}}'", serialized)
        self.assertIn("Side:2", serialized)
        self.assertIn(f"Node:'{{{str(self.node_guid).upper()}}}'", serialized)

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

        # Verify load switch type properties
        self.assertIn("ShortName:'TestType'", serialized)
        self.assertIn("Unom:400", serialized)
        self.assertIn("Inom:100", serialized)
        self.assertIn("SwitchTime:0.1", serialized)
        self.assertIn("IkMake:1000", serialized)
        self.assertIn("IkBreak:800", serialized)
        self.assertIn("IkDynamic:1200", serialized)
        self.assertIn("IkThermal:1000", serialized)
        self.assertIn("TThermal:1", serialized)

        # Verify extras and notes
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a load switch with the same GUID overwrites the existing one."""
        general1 = LoadSwitchMV.General(
            guid=self.load_switch_guid, name="FirstLoadSwitch"
        )
        load_switch1 = LoadSwitchMV(
            general1, None, [SecondaryPresentation(sheet=self.sheet_guid)]
        )
        load_switch1.register(self.network)

        general2 = LoadSwitchMV.General(
            guid=self.load_switch_guid, name="SecondLoadSwitch"
        )
        load_switch2 = LoadSwitchMV(
            general2, None, [SecondaryPresentation(sheet=self.sheet_guid)]
        )
        load_switch2.register(self.network)

        # Should only have one load switch
        self.assertEqual(len(self.network.load_switches), 1)
        # Should be the second load switch
        self.assertEqual(
            self.network.load_switches[self.load_switch_guid].general.name,
            "SecondLoadSwitch",
        )

    def test_minimal_load_switch_serialization(self) -> None:
        """Test that minimal load switches serialize correctly with only required fields."""
        general = LoadSwitchMV.General(
            guid=self.load_switch_guid, name="MinimalLoadSwitch"
        )
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        load_switch = LoadSwitchMV(general, None, [presentation])
        load_switch.register(self.network)

        serialized = load_switch.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalLoadSwitch'", serialized)
        self.assertIn("Side:1", serialized)  # Default value

        # Should not have optional properties with default values
        self.assertNotIn("MutationDate", serialized)
        self.assertNotIn("RevisionDate", serialized)
        self.assertNotIn("Variant:True", serialized)
        self.assertNotIn("InObject", serialized)
        self.assertNotIn("Node", serialized)

    def test_load_switch_with_in_object_serializes_correctly(self) -> None:
        """Test that load switches with in-object reference serialize correctly."""
        general = LoadSwitchMV.General(
            guid=self.load_switch_guid,
            name="InObjectLoadSwitch",
            in_object=self.in_object_guid,
            side=2,
        )
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        load_switch = LoadSwitchMV(general, None, [presentation])
        load_switch.register(self.network)

        serialized = load_switch.serialize()
        self.assertIn(f"InObject:'{{{str(self.in_object_guid).upper()}}}'", serialized)
        self.assertIn("Side:2", serialized)

    def test_load_switch_with_node_serializes_correctly(self) -> None:
        """Test that load switches with node reference serialize correctly."""
        general = LoadSwitchMV.General(
            guid=self.load_switch_guid,
            name="NodeLoadSwitch",
            node=self.node_guid,
        )
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        load_switch = LoadSwitchMV(general, None, [presentation])
        load_switch.register(self.network)

        serialized = load_switch.serialize()
        self.assertIn(f"Node:'{{{str(self.node_guid).upper()}}}'", serialized)

    def test_load_switch_with_variant_serializes_correctly(self) -> None:
        """Test that load switches with variant flag serialize correctly."""
        general = LoadSwitchMV.General(
            guid=self.load_switch_guid,
            name="VariantLoadSwitch",
            variant=True,
        )
        presentation = SecondaryPresentation(sheet=self.sheet_guid)

        load_switch = LoadSwitchMV(general, None, [presentation])
        load_switch.register(self.network)

        serialized = load_switch.serialize()
        self.assertIn("Variant:True", serialized)


if __name__ == "__main__":
    unittest.main()
