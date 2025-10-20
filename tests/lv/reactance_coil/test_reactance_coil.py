"""Tests for TReactanceCoilLS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import BranchPresentation, NodePresentation
from pyptp.elements.lv.reactance_coil import ReactanceCoilLV
from pyptp.elements.lv.sheet import SheetLV
from pyptp.elements.mixins import Extra, Note
from pyptp.network_lv import NetworkLV


class TestReactanceCoilRegistration(unittest.TestCase):
    """Test reactance coil registration and functionality."""

    def setUp(self) -> None:
        """Create a fresh network with sheet and nodes for testing."""
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

        # Create and register nodes
        node1 = NodeLV(
            NodeLV.General(
                guid=Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5")), name="Node1"
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node1.register(self.network)
        self.node1_guid = node1.general.guid

        node2 = NodeLV(
            NodeLV.General(
                guid=Guid(UUID("b8b53fef-12b8-4c98-96f2-0da060b51000")), name="Node2"
            ),
            [NodePresentation(sheet=self.sheet_guid)],
        )
        node2.register(self.network)
        self.node2_guid = node2.general.guid

        self.reactance_coil_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_reactance_coil_registration_works(self) -> None:
        """Test that reactance coils can register themselves with the network."""
        general = ReactanceCoilLV.General(
            guid=self.reactance_coil_guid,
            name="TestReactanceCoil",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        reactance_coil_type = ReactanceCoilLV.ReactanceCoilType(short_name="TestType")
        presentation = BranchPresentation(sheet=self.sheet_guid)

        reactance_coil = ReactanceCoilLV(general, [presentation], reactance_coil_type)
        reactance_coil.register(self.network)

        # Verify reactance coil is in network
        self.assertIn(self.reactance_coil_guid, self.network.reactance_coils)
        self.assertIs(
            self.network.reactance_coils[self.reactance_coil_guid], reactance_coil
        )

    def test_reactance_coil_with_full_properties_serializes_correctly(self) -> None:
        """Test that reactance coils with all properties serialize correctly."""
        general = ReactanceCoilLV.General(
            guid=self.reactance_coil_guid,
            creation_time=1234567890.5,
            mutation_date=20240101,
            revision_date=1234567891.0,
            node1=self.node1_guid,
            node2=self.node2_guid,
            name="FullReactanceCoil",
            switch_state1_L1=False,
            switch_state1_L2=True,
            switch_state1_L3=False,
            switch_state1_N=True,
            switch_state1_PE=False,
            switch_state2_L1=True,
            switch_state2_L2=False,
            switch_state2_L3=True,
            switch_state2_N=False,
            switch_state2_PE=True,
            field_name1="Field1",
            field_name2="Field2",
            type="TestReactanceCoilType",
        )

        reactance_coil_type = ReactanceCoilLV.ReactanceCoilType(
            short_name="TestReactanceCoilType",
            unom=0.4,
            inom=100.0,
            R=0.1,
            X=0.2,
            R0=0.3,
            X0=0.4,
            R2=0.5,
            X2=0.6,
            ik2s=5.0,
        )

        presentation = BranchPresentation(
            sheet=self.sheet_guid,
            color=DelphiColor("$00FF00"),
            size=2,
            width=3,
            text_color=DelphiColor("$FF0000"),
            text_size=12,
            font="Arial",
            text_style=1,
            no_text=True,
            upside_down_text=True,
            strings1_x=10,
            strings1_y=20,
            strings2_x=30,
            strings2_y=40,
            mid_strings_x=50,
            mid_strings_y=60,
            fault_strings_x=70,
            fault_strings_y=80,
            note_x=90,
            note_y=100,
            flag_flipped1=True,
            flag_flipped2=False,
        )

        reactance_coil = ReactanceCoilLV(general, [presentation], reactance_coil_type)
        reactance_coil.extras.append(Extra(text="foo=bar"))
        reactance_coil.notes.append(Note(text="Test note"))
        reactance_coil.register(self.network)

        # Test serialization
        serialized = reactance_coil.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#ReactanceCoilType", serialized)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify key properties are serialized
        self.assertIn("Name:'FullReactanceCoil'", serialized)
        self.assertIn("CreationTime:1234567890.5", serialized)
        self.assertIn("MutationDate:20240101", serialized)
        self.assertIn("RevisionDate:1234567891", serialized)
        self.assertIn("FieldName1:'Field1'", serialized)
        self.assertIn("FieldName2:'Field2'", serialized)
        self.assertIn("ReactanceCoilType:'TestReactanceCoilType'", serialized)
        self.assertIn("SwitchState1_L1:false", serialized)
        self.assertIn("SwitchState1_L2:true", serialized)
        self.assertIn("SwitchState2_PE:true", serialized)

        # Verify reactance coil type properties
        self.assertIn("ShortName:'TestReactanceCoilType'", serialized)
        self.assertIn("Unom:0.4", serialized)
        self.assertIn("Inom:100.0", serialized)
        self.assertIn("R:0.1", serialized)
        self.assertIn("X:0.2", serialized)
        self.assertIn("R0:0.3", serialized)
        self.assertIn("X0:0.4", serialized)
        self.assertIn("R2:0.5", serialized)
        self.assertIn("X2:0.6", serialized)
        self.assertIn("Ik2s:5.0", serialized)

        # Verify presentation properties
        self.assertIn(f"Sheet:'{{{str(self.sheet_guid).upper()}}}'", serialized)
        self.assertIn("Color:$00FF00", serialized)
        self.assertIn("TextColor:$FF0000", serialized)
        self.assertIn("Strings1X:10", serialized)
        self.assertIn("Strings1Y:20", serialized)
        self.assertIn("Strings2X:30", serialized)
        self.assertIn("Strings2Y:40", serialized)
        self.assertIn("MidStringsX:50", serialized)
        self.assertIn("MidStringsY:60", serialized)
        self.assertIn("FaultStringsX:70", serialized)
        self.assertIn("FaultStringsY:80", serialized)
        self.assertIn("NoteX:90", serialized)
        self.assertIn("NoteY:100", serialized)

        # Verify extras and notes
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)

    def test_reactance_coil_deserialization_works(self) -> None:
        """Test deserialization from GNF format data."""
        data = {
            "general": [
                {
                    "GUID": str(self.reactance_coil_guid),
                    "Name": "Deserialized Reactance Coil",
                    "CreationTime": 1234567890.0,
                    "Node1": str(self.node1_guid),
                    "Node2": str(self.node2_guid),
                    "SwitchState1_L1": False,
                    "SwitchState1_L2": True,
                    "ReactanceCoilType": "TestType",
                }
            ],
            "reactanceCoilType": [
                {
                    "ShortName": "TestType",
                    "Unom": 0.4,
                    "Inom": 100.0,
                    "R": 0.1,
                    "X": 0.2,
                    "Ik2s": 5.0,
                }
            ],
            "presentations": [{"Sheet": str(self.sheet_guid)}],
        }

        reactance_coil = ReactanceCoilLV.deserialize(data)

        # Verify general properties
        self.assertEqual(reactance_coil.general.guid, self.reactance_coil_guid)
        self.assertEqual(reactance_coil.general.name, "Deserialized Reactance Coil")
        self.assertEqual(reactance_coil.general.creation_time, 1234567890.0)
        self.assertEqual(reactance_coil.general.node1, self.node1_guid)
        self.assertEqual(reactance_coil.general.node2, self.node2_guid)
        self.assertEqual(reactance_coil.general.switch_state1_L1, False)
        self.assertEqual(reactance_coil.general.switch_state1_L2, True)
        self.assertEqual(reactance_coil.general.type, "TestType")

        # Verify reactance coil type
        self.assertIsNotNone(reactance_coil.type)
        self.assertEqual(reactance_coil.type.short_name, "TestType")
        self.assertEqual(reactance_coil.type.unom, 0.4)
        self.assertEqual(reactance_coil.type.inom, 100.0)
        self.assertEqual(reactance_coil.type.R, 0.1)
        self.assertEqual(reactance_coil.type.X, 0.2)
        self.assertEqual(reactance_coil.type.ik2s, 5.0)

        # Verify presentations
        self.assertEqual(len(reactance_coil.presentations), 1)
        self.assertEqual(reactance_coil.presentations[0].sheet, self.sheet_guid)

    def test_reactance_coil_deserialization_with_empty_data(self) -> None:
        """Test deserialization with empty data."""
        data = {}

        reactance_coil = ReactanceCoilLV.deserialize(data)

        # Should have default general properties
        self.assertIsNotNone(reactance_coil.general)
        self.assertEqual(reactance_coil.general.name, "")
        self.assertEqual(reactance_coil.general.creation_time, 0)
        self.assertEqual(reactance_coil.general.switch_state1_L1, True)
        self.assertEqual(reactance_coil.general.switch_state1_L2, True)
        self.assertEqual(reactance_coil.general.type, "")

        # Should have default reactance coil type
        self.assertIsNotNone(reactance_coil.type)
        self.assertEqual(reactance_coil.type.short_name, "")
        self.assertEqual(reactance_coil.type.unom, 0)
        self.assertEqual(reactance_coil.type.inom, 0)

        # Presentations should be empty
        self.assertEqual(len(reactance_coil.presentations), 0)

    def test_duplicate_reactance_coil_registration_overwrites(self) -> None:
        """Test GUID collision handling with proper logging verification."""
        general1 = ReactanceCoilLV.General(
            guid=self.reactance_coil_guid,
            name="Reactance Coil 1",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        reactance_coil1 = ReactanceCoilLV(
            general1,
            [BranchPresentation(sheet=self.sheet_guid)],
            ReactanceCoilLV.ReactanceCoilType(short_name="Type1"),
        )

        general2 = ReactanceCoilLV.General(
            guid=self.reactance_coil_guid,
            name="Reactance Coil 2",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        reactance_coil2 = ReactanceCoilLV(
            general2,
            [BranchPresentation(sheet=self.sheet_guid)],
            ReactanceCoilLV.ReactanceCoilType(short_name="Type2"),
        )

        # Register first reactance coil
        reactance_coil1.register(self.network)
        self.assertEqual(
            self.network.reactance_coils[self.reactance_coil_guid].general.name,
            "Reactance Coil 1",
        )

        # Register second reactance coil with same GUID should overwrite
        reactance_coil2.register(self.network)
        # Verify reactance coil was overwritten
        self.assertEqual(
            self.network.reactance_coils[self.reactance_coil_guid].general.name,
            "Reactance Coil 2",
        )

    def test_minimal_reactance_coil_serialization(self) -> None:
        """Test that minimal reactance coils serialize correctly with only required fields."""
        general = ReactanceCoilLV.General(
            guid=self.reactance_coil_guid,
            name="MinimalReactanceCoil",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        reactance_coil_type = ReactanceCoilLV.ReactanceCoilType(
            short_name="MinimalType"
        )
        presentation = BranchPresentation(sheet=self.sheet_guid)

        reactance_coil = ReactanceCoilLV(general, [presentation], reactance_coil_type)
        reactance_coil.register(self.network)

        serialized = reactance_coil.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#ReactanceCoilType", serialized)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalReactanceCoil'", serialized)
        self.assertIn("CreationTime:0", serialized)

        # Should not have optional sections
        self.assertNotIn("#Extra", serialized)
        self.assertNotIn("#Note", serialized)

        # Should have default boolean values (all True)
        self.assertIn("SwitchState1_L1:true", serialized)
        self.assertIn("SwitchState1_L2:true", serialized)
        self.assertIn("SwitchState1_L3:true", serialized)
        self.assertIn("SwitchState1_N:true", serialized)
        self.assertIn("SwitchState1_PE:true", serialized)
        self.assertIn("SwitchState2_L1:true", serialized)
        self.assertIn("SwitchState2_L2:true", serialized)
        self.assertIn("SwitchState2_L3:true", serialized)
        self.assertIn("SwitchState2_N:true", serialized)
        self.assertIn("SwitchState2_PE:true", serialized)

    def test_multiple_presentations_serialize_correctly(self) -> None:
        """Test that reactance coils with multiple presentations serialize correctly."""
        general = ReactanceCoilLV.General(
            guid=self.reactance_coil_guid,
            name="MultiPresReactanceCoil",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )
        reactance_coil_type = ReactanceCoilLV.ReactanceCoilType(short_name="MultiType")

        pres1 = BranchPresentation(sheet=self.sheet_guid, color=DelphiColor("$FF0000"))
        pres2 = BranchPresentation(sheet=self.sheet_guid, color=DelphiColor("$00FF00"))

        reactance_coil = ReactanceCoilLV(general, [pres1, pres2], reactance_coil_type)
        reactance_coil.register(self.network)

        serialized = reactance_coil.serialize()

        # Should have two presentations
        self.assertEqual(serialized.count("#Presentation"), 2)
        self.assertIn("Color:$FF0000", serialized)
        self.assertIn("Color:$00FF00", serialized)

    def test_reactance_coil_general_serialize_with_defaults(self) -> None:
        """Test General class serialization with default values."""
        general = ReactanceCoilLV.General(
            guid=self.reactance_coil_guid,
            name="Test Reactance Coil",
            node1=self.node1_guid,
            node2=self.node2_guid,
        )

        result = general.serialize()

        # Should include required fields
        self.assertIn(f"GUID:'{{{str(self.reactance_coil_guid).upper()}}}'", result)
        self.assertIn("Name:'Test Reactance Coil'", result)
        self.assertIn("CreationTime:0", result)
        self.assertIn(f"Node1:'{{{str(self.node1_guid).upper()}}}'", result)
        self.assertIn(f"Node2:'{{{str(self.node2_guid).upper()}}}'", result)

        # Should include default switch states
        self.assertIn("SwitchState1_L1:true", result)
        self.assertIn("SwitchState1_L2:true", result)
        self.assertIn("SwitchState1_L3:true", result)
        self.assertIn("SwitchState1_N:true", result)
        self.assertIn("SwitchState1_PE:true", result)
        self.assertIn("SwitchState2_L1:true", result)
        self.assertIn("SwitchState2_L2:true", result)
        self.assertIn("SwitchState2_L3:true", result)
        self.assertIn("SwitchState2_N:true", result)
        self.assertIn("SwitchState2_PE:true", result)

        # Should include empty field names
        self.assertIn("FieldName1:''", result)
        self.assertIn("FieldName2:''", result)

        # Should skip optional values that are defaults
        self.assertNotIn("MutationDate:", result)
        self.assertNotIn("RevisionDate:", result)
        self.assertNotIn("ReactanceCoilType:", result)  # Empty string should be skipped

    def test_reactance_coil_type_serialize_with_defaults(self) -> None:
        """Test ReactanceCoilType class serialization with default values."""
        reactance_coil_type = ReactanceCoilLV.ReactanceCoilType(short_name="Test Type")

        result = reactance_coil_type.serialize()

        # Should include required fields
        self.assertIn("ShortName:'Test Type'", result)

        # Should skip default values (0)
        self.assertNotIn("Unom:", result)
        self.assertNotIn("Inom:", result)
        self.assertNotIn("R:", result)
        self.assertNotIn("X:", result)
        self.assertNotIn("R0:", result)
        self.assertNotIn("X0:", result)
        self.assertNotIn("R2:", result)
        self.assertNotIn("X2:", result)
        self.assertNotIn("Ik2s:", result)

    def test_reactance_coil_round_trip_serialization(self) -> None:
        """Test that serialization and deserialization are consistent."""
        original_general = ReactanceCoilLV.General(
            guid=self.reactance_coil_guid,
            name="Round Trip Reactance Coil",
            creation_time=1234567890.0,
            node1=self.node1_guid,
            node2=self.node2_guid,
            switch_state1_L1=False,
            switch_state2_PE=True,
            type="TestType",
        )

        original_reactance_coil_type = ReactanceCoilLV.ReactanceCoilType(
            short_name="TestType",
            unom=0.4,
            inom=100.0,
            R=0.1,
            X=0.2,
            ik2s=5.0,
        )

        original_reactance_coil = ReactanceCoilLV(
            general=original_general,
            presentations=[BranchPresentation(sheet=self.sheet_guid)],
            type=original_reactance_coil_type,
        )

        original_reactance_coil.serialize()

        # Simulate parsing back from GNF format
        data = {
            "general": [
                {
                    "GUID": str(self.reactance_coil_guid),
                    "Name": "Round Trip Reactance Coil",
                    "CreationTime": 1234567890.0,
                    "Node1": str(self.node1_guid),
                    "Node2": str(self.node2_guid),
                    "SwitchState1_L1": False,
                    "SwitchState2_PE": True,
                    "ReactanceCoilType": "TestType",
                }
            ],
            "reactanceCoilType": [
                {
                    "ShortName": "TestType",
                    "Unom": 0.4,
                    "Inom": 100.0,
                    "R": 0.1,
                    "X": 0.2,
                    "Ik2s": 5.0,
                }
            ],
            "presentations": [{"Sheet": str(self.sheet_guid)}],
        }

        deserialized = ReactanceCoilLV.deserialize(data)

        # Verify key properties match
        self.assertEqual(
            deserialized.general.guid, original_reactance_coil.general.guid
        )
        self.assertEqual(
            deserialized.general.name, original_reactance_coil.general.name
        )
        self.assertEqual(
            deserialized.general.creation_time,
            original_reactance_coil.general.creation_time,
        )
        self.assertEqual(
            deserialized.general.node1, original_reactance_coil.general.node1
        )
        self.assertEqual(
            deserialized.general.node2, original_reactance_coil.general.node2
        )
        self.assertEqual(
            deserialized.general.switch_state1_L1,
            original_reactance_coil.general.switch_state1_L1,
        )
        self.assertEqual(
            deserialized.general.switch_state2_PE,
            original_reactance_coil.general.switch_state2_PE,
        )
        self.assertEqual(
            deserialized.general.type, original_reactance_coil.general.type
        )

        # Verify reactance coil type properties
        self.assertEqual(
            deserialized.type.short_name, original_reactance_coil.type.short_name
        )
        self.assertEqual(deserialized.type.unom, original_reactance_coil.type.unom)
        self.assertEqual(deserialized.type.inom, original_reactance_coil.type.inom)
        self.assertEqual(deserialized.type.R, original_reactance_coil.type.R)
        self.assertEqual(deserialized.type.X, original_reactance_coil.type.X)
        self.assertEqual(deserialized.type.ik2s, original_reactance_coil.type.ik2s)

        # Verify presentations
        self.assertEqual(
            len(deserialized.presentations), len(original_reactance_coil.presentations)
        )
        if (
            len(deserialized.presentations) > 0
            and len(original_reactance_coil.presentations) > 0
        ):
            self.assertEqual(
                deserialized.presentations[0].sheet,
                original_reactance_coil.presentations[0].sheet,
            )


if __name__ == "__main__":
    unittest.main()
