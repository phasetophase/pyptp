"""Tests for TLoadLS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid
from pyptp.elements.lv.load import LoadLV
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import ElementPresentation, NodePresentation
from pyptp.elements.lv.shared import HarmonicsType
from pyptp.elements.lv.sheet import SheetLV
from pyptp.elements.mixins import Extra, Note
from pyptp.network_lv import NetworkLV


class TestLoadRegistration(unittest.TestCase):
    """Test load registration and functionality."""

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

        self.load_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_load_registration_works(self) -> None:
        """Test that loads can register themselves with the network."""
        general = LoadLV.General(
            guid=self.load_guid, name="TestLoad", node=self.node_guid
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        load = LoadLV(general, [presentation])
        load.register(self.network)

        # Verify load is in network
        self.assertIn(self.load_guid, self.network.loads)
        self.assertIs(self.network.loads[self.load_guid], load)

    def test_load_with_full_properties_serializes_correctly(self) -> None:
        """Test that loads with all properties serialize correctly."""
        general = LoadLV.General(
            guid=self.load_guid,
            creation_time=123.45,
            mutation_date=10,
            revision_date=20.5,
            node=self.node_guid,
            name="FullLoad",
            s_L1=True,
            s_L2=False,
            s_L3=True,
            s_N=False,
            field_name="LoadField",
            pa=10.5,
            qa=5.2,
            pb=15.0,
            qb=7.8,
            pc=20.0,
            qc=10.0,
            pab=25.0,
            qab=12.5,
            pac=30.0,
            qac=15.0,
            pbc=35.0,
            qbc=17.5,
            behaviour_sort="Residential",
            switch_on_frequency=0.8,
            harmonics_type="Type1",
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

        harmonics = HarmonicsType(
            h=[1.0, 2.0, 3.0] + [0.0] * 96, angle=[0.0, 90.0, 180.0] + [0.0] * 96
        )

        load = LoadLV(general, [presentation], harmonics)
        load.extras.append(Extra(text="foo=bar"))
        load.notes.append(Note(text="Test note"))
        load.register(self.network)

        # Test serialization
        serialized = load.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#HarmonicsType", serialized)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify key properties are serialized
        self.assertIn("Name:'FullLoad'", serialized)
        self.assertIn("FieldName:'LoadField'", serialized)
        self.assertIn("s_L1:True", serialized)
        self.assertIn("s_L2:False", serialized)
        self.assertIn("s_L3:True", serialized)
        self.assertIn("s_N:False", serialized)
        self.assertIn("Pa:10.5", serialized)
        self.assertIn("Qa:5.2", serialized)
        self.assertIn("Pb:15.0", serialized)
        self.assertIn("Qb:7.8", serialized)
        self.assertIn("Pc:20.0", serialized)
        self.assertIn("Qc:10.0", serialized)
        self.assertIn("Pab:25.0", serialized)
        self.assertIn("Qab:12.5", serialized)
        self.assertIn("Pac:30.0", serialized)
        self.assertIn("Qac:15.0", serialized)
        self.assertIn("Pbc:35.0", serialized)
        self.assertIn("Qbc:17.5", serialized)
        self.assertIn("BehaviourSort:'Residential'", serialized)
        self.assertIn("SwitchOnFrequency:0.8", serialized)
        self.assertIn("HarmonicsType:'Type1'", serialized)

        # Verify presentation properties
        self.assertIn(f"Sheet:'{{{str(self.sheet_guid).upper()}}}'", serialized)
        self.assertIn("X:100", serialized)
        self.assertIn("Y:200", serialized)
        self.assertIn("Color:$00FF00", serialized)
        self.assertIn("TextColor:$FF0000", serialized)

        # Verify harmonics properties
        self.assertIn("h1:1.0", serialized)
        self.assertIn("h2:2.0", serialized)
        self.assertIn("h3:3.0", serialized)
        self.assertIn("Angle2:90.0", serialized)
        self.assertIn("Angle3:180.0", serialized)

        # Verify extras and notes
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a load with the same GUID overwrites the existing one."""
        general1 = LoadLV.General(
            guid=self.load_guid, name="FirstLoad", node=self.node_guid
        )
        load1 = LoadLV(general1, [ElementPresentation(sheet=self.sheet_guid)])
        load1.register(self.network)

        general2 = LoadLV.General(
            guid=self.load_guid, name="SecondLoad", node=self.node_guid
        )
        load2 = LoadLV(general2, [ElementPresentation(sheet=self.sheet_guid)])
        load2.register(self.network)

        # Should only have one load
        self.assertEqual(len(self.network.loads), 1)
        # Should be the second load
        self.assertEqual(self.network.loads[self.load_guid].general.name, "SecondLoad")

    def test_load_with_complex_harmonics_serializes_correctly(self) -> None:
        """Test that loads with complex harmonics data serialize correctly."""
        general = LoadLV.General(
            guid=self.load_guid, name="HarmonicLoad", node=self.node_guid
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        # Create harmonics with more complex data
        harmonics_data = [0.1 * i for i in range(1, 100)]
        angle_data = [i * 10.0 for i in range(99)]

        harmonics = HarmonicsType(h=harmonics_data, angle=angle_data)

        load = LoadLV(general, [presentation], harmonics)
        load.register(self.network)

        serialized = load.serialize()

        # Verify harmonics section is present
        self.assertIn("#HarmonicsType", serialized)

        # Verify harmonics data is serialized (check for some key values)
        self.assertIn("h1:0.1", serialized)
        self.assertIn("h2:0.2", serialized)
        self.assertIn("h3:0.3", serialized)
        self.assertIn("Angle2:10.0", serialized)
        self.assertIn("Angle3:20.0", serialized)

        # Verify the full harmonics data is included
        self.assertIn("9.8", serialized)  # Last harmonic value
        self.assertIn("980.0", serialized)  # Last angle value

    def test_minimal_load_serialization(self) -> None:
        """Test that minimal loads serialize correctly with only required fields."""
        general = LoadLV.General(
            guid=self.load_guid, name="MinimalLoad", node=self.node_guid
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        load = LoadLV(general, [presentation])
        load.register(self.network)

        serialized = load.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalLoad'", serialized)
        self.assertIn("s_L1:True", serialized)  # Default values
        self.assertIn("s_L2:True", serialized)
        self.assertIn("s_L3:True", serialized)
        self.assertIn("s_N:True", serialized)
        # Pa and Qa are optional_field(0), so they're excluded when 0

        # Should not have harmonics section
        self.assertNotIn("#HarmonicsType", serialized)

        # Should not have optional sections
        self.assertNotIn("#Extra", serialized)
        self.assertNotIn("#Note", serialized)

    def test_multiple_presentations_serialize_correctly(self) -> None:
        """Test that loads with multiple presentations serialize correctly."""
        general = LoadLV.General(
            guid=self.load_guid, name="MultiPresLoad", node=self.node_guid
        )

        pres1 = ElementPresentation(
            sheet=self.sheet_guid, x=100, y=100, color=DelphiColor("$FF0000")
        )
        pres2 = ElementPresentation(
            sheet=self.sheet_guid, x=200, y=200, color=DelphiColor("$00FF00")
        )

        load = LoadLV(general, [pres1, pres2])
        load.register(self.network)

        serialized = load.serialize()

        # Should have two presentations
        self.assertEqual(serialized.count("#Presentation"), 2)
        self.assertIn("Color:$FF0000", serialized)
        self.assertIn("Color:$00FF00", serialized)
        self.assertIn("X:100", serialized)
        self.assertIn("X:200", serialized)

    def test_load_with_profile_guid_serializes_correctly(self) -> None:
        """Test that loads with profile GUID serialize correctly."""
        profile_guid = Guid(UUID("12345678-1234-5678-9abc-123456789abc"))

        general = LoadLV.General(
            guid=self.load_guid,
            name="ProfileLoad",
            node=self.node_guid,
            profile=profile_guid,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        load = LoadLV(general, [presentation])
        load.register(self.network)

        serialized = load.serialize()

        # Verify profile GUID is serialized
        self.assertIn(f"Profile:'{{{str(profile_guid).upper()}}}'", serialized)


if __name__ == "__main__":
    unittest.main()
