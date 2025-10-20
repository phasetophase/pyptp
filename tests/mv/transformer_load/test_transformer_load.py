"""Tests for TTransformerLoadMS behavior using the new registration system."""

import unittest
from uuid import UUID, uuid4

from pyptp.elements.element_utils import Guid
from pyptp.elements.lv.shared import HarmonicsType
from pyptp.elements.mixins import Extra, Note
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import ElementPresentation, NodePresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.elements.mv.transformer_load import TransformerLoadMV
from pyptp.network_mv import NetworkMV


class TestTransformerLoadRegistration(unittest.TestCase):
    """Test transformer load registration and functionality."""

    def setUp(self) -> None:
        """Create a fresh network with sheet and nodes for testing."""
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

        # Create and register nodes
        node1 = NodeMV(
            NodeMV.General(
                guid=Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5")),
                name="TestNode1",
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node1.register(self.network)
        self.node1_guid = node1.general.guid

        node2 = NodeMV(
            NodeMV.General(
                guid=Guid(UUID("8b7d4c3e-2f1a-4e5d-9c8b-7a6f5e4d3c2b")),
                name="TestNode2",
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node2.register(self.network)
        self.node2_guid = node2.general.guid

        self.transformer_load_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_transformer_load_registration_works(self) -> None:
        """Test that transformer loads can register themselves with the network."""
        general = TransformerLoadMV.General(
            guid=self.transformer_load_guid,
            name="TestTransformerLoad",
            node=self.node1_guid,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        transformer_load = TransformerLoadMV(
            general, TransformerLoadMV.TransformerLoadType(), [presentation]
        )
        transformer_load.register(self.network)

        # Verify transformer load is in network
        self.assertIn(self.transformer_load_guid, self.network.transformer_loads)
        self.assertIs(
            self.network.transformer_loads[self.transformer_load_guid], transformer_load
        )

    def test_transformer_load_with_basic_properties_serializes_correctly(self) -> None:
        """Test that transformer loads with basic properties serialize correctly."""
        general = TransformerLoadMV.General(
            guid=self.transformer_load_guid,
            name="BasicTransformerLoad",
            node=self.node1_guid,
            creation_time=123.45,
            variant=True,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        transformer_type = TransformerLoadMV.TransformerLoadType(
            snom=100.0,
            unom1=20.0,
            unom2=0.4,
        )
        transformer_load = TransformerLoadMV(general, transformer_type, [presentation])
        transformer_load.register(self.network)

        serialized = transformer_load.serialize()

        # Verify general properties
        self.assertIn("Name:'BasicTransformerLoad'", serialized)
        self.assertIn("Snom:100", serialized)
        self.assertIn("Unom1:20", serialized)
        self.assertIn("Unom2:0.4", serialized)
        self.assertIn("CreationTime:123.45", serialized)
        self.assertIn("Variant:True", serialized)

        # Verify node references
        self.assertIn(f"Node:'{{{str(self.node1_guid).upper()}}}'", serialized)

    def test_transformer_load_with_guid_references_serializes_correctly(self) -> None:
        """Test that transformer loads with GUID references serialize correctly."""
        profile_guid = Guid(uuid4())
        load_behaviour_guid = Guid(uuid4())
        load_growth_guid = Guid(uuid4())

        general = TransformerLoadMV.General(
            guid=self.transformer_load_guid,
            name="GuidRefTransformerLoad",
            node=self.node1_guid,
            sub_number=42,
            profile=profile_guid,
            load_behaviour=load_behaviour_guid,
            load_growth=load_growth_guid,
            load_p=100.5,
            load_q=50.2,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        transformer_load = TransformerLoadMV(
            general, TransformerLoadMV.TransformerLoadType(), [presentation]
        )
        transformer_load.register(self.network)

        serialized = transformer_load.serialize()

        # Verify GUID references are included
        self.assertIn(f"Profile:'{{{str(profile_guid).upper()}}}'", serialized)
        self.assertIn(
            f"LoadBehaviour:'{{{str(load_behaviour_guid).upper()}}}'", serialized
        )
        self.assertIn(f"LoadGrowth:'{{{str(load_growth_guid).upper()}}}'", serialized)
        self.assertIn("SubNumber:42", serialized)
        self.assertIn("LoadP:100.5", serialized)
        self.assertIn("LoadQ:50.2", serialized)

    def test_transformer_load_with_generation_properties_serializes_correctly(
        self,
    ) -> None:
        """Test that transformer loads with generation properties serialize correctly."""
        generation_growth_guid = Guid(uuid4())
        generation_profile_guid = Guid(uuid4())
        pv_growth_guid = Guid(uuid4())
        pv_profile_guid = Guid(uuid4())

        general = TransformerLoadMV.General(
            guid=self.transformer_load_guid,
            name="GenerationTransformerLoad",
            node=self.node1_guid,
            generation_p=75.0,
            generation_q=25.0,
            generation_growth=generation_growth_guid,
            generation_profile=generation_profile_guid,
            pv_pnom=150.0,
            pv_growth=pv_growth_guid,
            pv_profile=pv_profile_guid,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        transformer_load = TransformerLoadMV(
            general, TransformerLoadMV.TransformerLoadType(), [presentation]
        )
        transformer_load.register(self.network)

        serialized = transformer_load.serialize()

        # Verify generation properties
        self.assertIn("GenerationP:75.0", serialized)
        self.assertIn("GenerationQ:25.0", serialized)
        self.assertIn(
            f"GenerationGrowth:'{{{str(generation_growth_guid).upper()}}}'", serialized
        )
        self.assertIn(
            f"GenerationProfile:'{{{str(generation_profile_guid).upper()}}}'",
            serialized,
        )
        self.assertIn("PVPnom:150.0", serialized)
        self.assertIn(f"PvGrowth:'{{{str(pv_growth_guid).upper()}}}'", serialized)
        self.assertIn(f"PvProfile:'{{{str(pv_profile_guid).upper()}}}'", serialized)

    def test_transformer_load_with_harmonics_type_serializes_correctly(self) -> None:
        """Test that transformer loads with HarmonicsType serialize correctly."""
        general = TransformerLoadMV.General(
            guid=self.transformer_load_guid,
            name="HarmonicsTransformerLoad",
            node=self.node1_guid,
            harmonics_type="TestHarmonics",
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        # Create harmonics with some test data
        harmonics = HarmonicsType(
            h=[1.0, 2.0, 3.0] + [0.0] * 96, angle=[0.0, 90.0, 180.0] + [0.0] * 96
        )

        transformer_load = TransformerLoadMV(
            general,
            TransformerLoadMV.TransformerLoadType(),
            [presentation],
            harmonics_type=harmonics,
        )
        transformer_load.register(self.network)

        serialized = transformer_load.serialize()

        # Verify harmonics type name in general section
        self.assertIn("HarmonicsType:'TestHarmonics'", serialized)

        # Verify separate HarmonicsType section
        self.assertIn("#HarmonicsType", serialized)
        self.assertIn("h1:1.0", serialized)
        self.assertIn("h2:2.0", serialized)
        self.assertIn("h3:3.0", serialized)
        self.assertIn("Angle2:90.0", serialized)
        self.assertIn("Angle3:180.0", serialized)

    def test_transformer_load_with_ceres_serializes_correctly(self) -> None:
        """Test that transformer loads with CERES data serialize correctly."""
        general = TransformerLoadMV.General(
            guid=self.transformer_load_guid,
            name="CeresTransformerLoad",
            node=self.node1_guid,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        ceres_data = {
            "CERES0": "test_value_0",
            "CERES1": "test_value_1",
            "CERES10": "test_value_10",
        }

        transformer_load = TransformerLoadMV(
            general,
            TransformerLoadMV.TransformerLoadType(),
            [presentation],
            ceres=ceres_data,
        )
        transformer_load.register(self.network)

        serialized = transformer_load.serialize()

        # Verify CERES section
        self.assertIn("#CERES", serialized)
        self.assertIn("CERES0:test_value_0", serialized)
        self.assertIn("CERES1:test_value_1", serialized)
        self.assertIn("CERES10:test_value_10", serialized)

    def test_transformer_load_deserialization_with_new_properties(self) -> None:
        """Test that transformer loads deserialize correctly with new properties."""
        profile_guid = Guid(uuid4())
        load_behaviour_guid = Guid(uuid4())

        data = {
            "general": [
                {
                    "GUID": str(self.transformer_load_guid),
                    "Name": "DeserializeTest",
                    "Node": str(self.node1_guid),
                    "SubNumber": 123,
                    "Profile": str(profile_guid),
                    "LoadBehaviour": str(load_behaviour_guid),
                    "LoadP": 200.0,
                    "LoadQ": 100.0,
                    "HarmonicsType": "TestType",
                }
            ],
            "transformerType": [
                {
                    "ShortName": "TestTransformer",
                    "Snom": 500.0,
                    "Unom1": 10.0,
                    "Unom2": 0.4,
                }
            ],
            "harmonicsType": [{"h1": 1.5, "h2": 2.5, "Angle1": 45.0, "Angle2": 135.0}],
            "ceres": [{"CERES0": "deserialized_value"}],
        }

        transformer_load = TransformerLoadMV.deserialize(data)

        # Verify general properties
        self.assertEqual(transformer_load.general.guid, self.transformer_load_guid)
        self.assertEqual(transformer_load.general.name, "DeserializeTest")
        self.assertEqual(transformer_load.general.sub_number, 123)
        self.assertEqual(transformer_load.general.profile, profile_guid)
        self.assertEqual(transformer_load.general.load_behaviour, load_behaviour_guid)
        self.assertEqual(transformer_load.general.load_p, 200.0)
        self.assertEqual(transformer_load.general.load_q, 100.0)
        self.assertEqual(transformer_load.general.harmonics_type, "TestType")

        # Verify transformer type
        self.assertEqual(transformer_load.type.short_name, "TestTransformer")
        self.assertEqual(transformer_load.type.snom, 500.0)

        # Verify harmonics
        self.assertIsNotNone(transformer_load.harmonics_type)
        if (
            transformer_load.harmonics_type
            and transformer_load.harmonics_type.h
            and transformer_load.harmonics_type.angle
        ):
            self.assertEqual(transformer_load.harmonics_type.h[0], 1.5)
            self.assertEqual(transformer_load.harmonics_type.h[1], 2.5)
            self.assertEqual(transformer_load.harmonics_type.angle[0], 45.0)
            self.assertEqual(transformer_load.harmonics_type.angle[1], 135.0)

        # Verify CERES
        self.assertIsNotNone(transformer_load.ceres)
        if transformer_load.ceres:
            self.assertEqual(transformer_load.ceres["CERES0"], "deserialized_value")

    def test_transformer_load_nil_guids_not_serialized(self) -> None:
        """Test that NIL GUIDs are not serialized in output."""
        general = TransformerLoadMV.General(
            guid=self.transformer_load_guid,
            name="NilGuidTest",
            node=self.node1_guid,
            # All GUID references default to NIL_GUID
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        transformer_load = TransformerLoadMV(
            general, TransformerLoadMV.TransformerLoadType(), [presentation]
        )
        transformer_load.register(self.network)

        serialized = transformer_load.serialize()

        # Verify NIL GUIDs are not included in serialization
        self.assertNotIn("Profile:", serialized)
        self.assertNotIn("LoadBehaviour:", serialized)
        self.assertNotIn("LoadGrowth:", serialized)
        self.assertNotIn("GenerationGrowth:", serialized)
        self.assertNotIn("GenerationProfile:", serialized)
        self.assertNotIn("PvGrowth:", serialized)
        self.assertNotIn("PvProfile:", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a transformer load with the same GUID overwrites the existing one."""
        general1 = TransformerLoadMV.General(
            guid=self.transformer_load_guid,
            name="FirstTransformerLoad",
            node=self.node1_guid,
        )
        transformer_load1 = TransformerLoadMV(
            general1,
            TransformerLoadMV.TransformerLoadType(),
            [ElementPresentation(sheet=self.sheet_guid)],
        )
        transformer_load1.register(self.network)

        general2 = TransformerLoadMV.General(
            guid=self.transformer_load_guid,
            name="SecondTransformerLoad",
            node=self.node1_guid,
        )
        transformer_load2 = TransformerLoadMV(
            general2,
            TransformerLoadMV.TransformerLoadType(),
            [ElementPresentation(sheet=self.sheet_guid)],
        )
        transformer_load2.register(self.network)

        # Should only have one transformer load
        self.assertEqual(len(self.network.transformer_loads), 1)
        # Should be the second transformer load
        self.assertEqual(
            self.network.transformer_loads[self.transformer_load_guid].general.name,
            "SecondTransformerLoad",
        )

    def test_minimal_transformer_load_serialization(self) -> None:
        """Test that minimal transformer loads serialize correctly with only required fields."""
        general = TransformerLoadMV.General(
            guid=self.transformer_load_guid,
            name="MinimalTransformerLoad",
            node=self.node1_guid,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        transformer_load = TransformerLoadMV(
            general, TransformerLoadMV.TransformerLoadType(), [presentation]
        )
        transformer_load.register(self.network)

        serialized = transformer_load.serialize()

        # Should have basic properties
        self.assertIn("Name:'MinimalTransformerLoad'", serialized)
        self.assertIn(f"Node:'{{{str(self.node1_guid).upper()}}}'", serialized)

    def test_transformer_load_without_harmonics_or_ceres(self) -> None:
        """Test that transformer loads without harmonics or CERES don't include those sections."""
        general = TransformerLoadMV.General(
            guid=self.transformer_load_guid,
            name="NoHarmonicsNoCeres",
            node=self.node1_guid,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        transformer_load = TransformerLoadMV(
            general, TransformerLoadMV.TransformerLoadType(), [presentation]
        )
        transformer_load.register(self.network)

        serialized = transformer_load.serialize()

        # Should not have HarmonicsType or CERES sections
        self.assertNotIn("#HarmonicsType", serialized)
        self.assertNotIn("#CERES", serialized)

    def test_transformer_load_with_extras_and_notes(self) -> None:
        """Test that transformer loads can have extras and notes."""
        general = TransformerLoadMV.General(
            guid=self.transformer_load_guid,
            name="ExtrasNotesTransformerLoad",
            node=self.node1_guid,
        )
        presentation = ElementPresentation(sheet=self.sheet_guid)

        transformer_load = TransformerLoadMV(
            general, TransformerLoadMV.TransformerLoadType(), [presentation]
        )
        transformer_load.extras.append(Extra(text="foo=bar"))
        transformer_load.notes.append(Note(text="Test note"))
        transformer_load.register(self.network)

        serialized = transformer_load.serialize()

        # Verify extras and notes
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)


if __name__ == "__main__":
    unittest.main()
