"""Tests for TLoadSwitchLS class."""

from __future__ import annotations

import unittest
from uuid import uuid4

from pyptp.elements.element_utils import Guid, encode_guid
from pyptp.elements.lv.load_switch import LoadSwitchLV
from pyptp.elements.lv.presentations import BranchPresentation
from pyptp.elements.mixins import Extra, Note
from pyptp.network_lv import NetworkLV


class TestTLoadSwitchLS(unittest.TestCase):
    """Test TLoadSwitchLS registration and serialization behavior."""

    def setUp(self) -> None:
        """Create fresh network and dependencies for isolated testing."""
        self.network = NetworkLV()
        self.test_guid = Guid(uuid4())
        self.in_object_guid = Guid(uuid4())

    def test_load_switch_registration_works(self) -> None:
        """Verify basic load switch registration in network."""
        general = LoadSwitchLV.General(guid=self.test_guid, name="Test Load Switch")
        loadswitch_type = LoadSwitchLV.LoadSwitchType(
            short_name="LS-25A", unom=230.0, inom=25.0
        )
        load_switch = LoadSwitchLV(
            general=general, presentations=[], type=loadswitch_type
        )

        # Verify network starts empty
        self.assertEqual(len(self.network.load_switches), 0)

        # Register load switch
        load_switch.register(self.network)

        # Verify load switch was added
        self.assertEqual(len(self.network.load_switches), 1)
        self.assertEqual(self.network.load_switches[self.test_guid], load_switch)

    def test_load_switch_with_minimal_properties_serializes_correctly(self) -> None:
        """Test serialization with minimal properties."""
        general = LoadSwitchLV.General(guid=self.test_guid, name="Minimal Load Switch")
        loadswitch_type = LoadSwitchLV.LoadSwitchType(short_name="LS-16A")
        load_switch = LoadSwitchLV(
            general=general, presentations=[], type=loadswitch_type
        )

        result = load_switch.serialize()

        # Should contain general line
        self.assertIn("#General", result)
        self.assertIn(f"GUID:{encode_guid(self.test_guid)}", result)
        self.assertIn("Name:'Minimal Load Switch'", result)
        self.assertIn("CreationTime:0", result)
        self.assertIn("Side:1", result)
        self.assertIn("Standardizable:false", result)

        # Should contain loadswitch type section
        self.assertIn("#LoadSwitchType", result)
        self.assertIn("ShortName:'LS-16A'", result)
        self.assertIn("Unom:0.0", result)
        self.assertIn("Inom:0.0", result)

        # Should not contain optional fields that are default
        self.assertNotIn("MutationDate:", result)
        self.assertNotIn("RevisionDate:", result)
        self.assertNotIn("InObject:", result)

    def test_load_switch_with_full_properties_serializes_correctly(self) -> None:
        """Test serialization with all properties set."""
        general = LoadSwitchLV.General(
            guid=self.test_guid,
            creation_time=1234567890.5,
            mutation_date=20240101,
            name="Full Load Switch",
            revision_date=1234567891.0,
            in_object=self.in_object_guid,
            side=2,
            standardizable=True,
        )

        loadswitch_type = LoadSwitchLV.LoadSwitchType(
            short_name="LS-25A", unom=230.0, inom=25.0, ik_thermal=1000.0, t_thermal=1.0
        )

        presentation = BranchPresentation(
            sheet=self.test_guid,
            first_corners=[(10, 20), (30, 40)],
            second_corners=[(50, 60), (70, 80)],
            strings1_x=100,
            strings1_y=200,
        )

        load_switch = LoadSwitchLV(
            general=general, presentations=[presentation], type=loadswitch_type
        )

        # Add extras and notes
        load_switch.extras = [Extra(text="key1=value1"), Extra(text="key2=value2")]
        load_switch.notes = [Note(text="Test note 1"), Note(text="Test note 2")]

        result = load_switch.serialize()

        # Verify general section
        self.assertIn("#General", result)
        self.assertIn(f"GUID:{encode_guid(self.test_guid)}", result)
        self.assertIn("CreationTime:1234567890.5", result)
        self.assertIn("MutationDate:20240101", result)
        self.assertIn("Name:'Full Load Switch'", result)
        self.assertIn("RevisionDate:1234567891.0", result)
        self.assertIn(f"InObject:{encode_guid(self.in_object_guid)}", result)
        self.assertIn("Side:2", result)
        self.assertIn("Standardizable:true", result)

        # Verify loadswitch type section
        self.assertIn("#LoadSwitchType", result)
        self.assertIn("ShortName:'LS-25A'", result)
        self.assertIn("Unom:230.0", result)
        self.assertIn("Inom:25.0", result)
        self.assertIn("IkThermal:1000.0", result)
        self.assertIn("TThermal:1.0", result)

        # Verify presentation section
        self.assertIn("#Presentation", result)
        self.assertIn(f"Sheet:{encode_guid(self.test_guid)}", result)
        self.assertIn("Strings1X:100", result)
        self.assertIn("Strings1Y:200", result)
        self.assertIn("FirstCorners:'{(10 20) (30 40) }'", result)
        self.assertIn("SecondCorners:'{(50 60) (70 80) }'", result)

        # Verify extras and notes
        self.assertIn("#Extra Text:key1=value1", result)
        self.assertIn("#Extra Text:key2=value2", result)
        self.assertIn("#Note Text:Test note 1", result)
        self.assertIn("#Note Text:Test note 2", result)

    def test_load_switch_deserialization_works(self) -> None:
        """Test deserialization from GNF format data."""
        data = {
            "general": [
                {
                    "GUID": str(self.test_guid),
                    "Name": "Deserialized Load Switch",
                    "CreationTime": 1234567890.0,
                    "Side": 2,
                    "Standardizable": True,
                }
            ],
            "loadswitch": [
                {
                    "ShortName": "LS-25A",
                    "Unom": 230.0,
                    "Inom": 25.0,
                    "IkThermal": 1000.0,
                    "TThermal": 1.0,
                }
            ],
            "presentations": [
                {
                    "Sheet": str(self.test_guid),
                    "FirstCorners": [(10, 20), (30, 40)],
                    "SecondCorners": [(50, 60), (70, 80)],
                    "Strings1X": 100,
                    "Strings1Y": 200,
                }
            ],
        }

        load_switch = LoadSwitchLV.deserialize(data)

        # Verify general properties
        self.assertEqual(load_switch.general.guid, self.test_guid)
        self.assertEqual(load_switch.general.name, "Deserialized Load Switch")
        self.assertEqual(load_switch.general.creation_time, 1234567890.0)
        self.assertEqual(load_switch.general.side, 2)
        self.assertEqual(load_switch.general.standardizable, True)

        # Verify loadswitch type
        self.assertIsNotNone(load_switch.type)
        self.assertEqual(load_switch.type.short_name, "LS-25A")
        self.assertEqual(load_switch.type.unom, 230.0)
        self.assertEqual(load_switch.type.inom, 25.0)
        self.assertEqual(load_switch.type.ik_thermal, 1000.0)
        self.assertEqual(load_switch.type.t_thermal, 1.0)

        # Verify presentations
        self.assertEqual(len(load_switch.presentations), 1)
        self.assertEqual(load_switch.presentations[0].sheet, self.test_guid)
        self.assertEqual(
            load_switch.presentations[0].first_corners, [(10, 20), (30, 40)]
        )
        self.assertEqual(
            load_switch.presentations[0].second_corners, [(50, 60), (70, 80)]
        )
        self.assertEqual(load_switch.presentations[0].strings1_x, 100)
        self.assertEqual(load_switch.presentations[0].strings1_y, 200)

    def test_load_switch_deserialization_with_empty_data(self) -> None:
        """Test deserialization with empty data."""
        data = {}

        load_switch = LoadSwitchLV.deserialize(data)

        # Should have default general properties
        self.assertIsNotNone(load_switch.general)
        self.assertEqual(load_switch.general.name, "")
        self.assertEqual(load_switch.general.creation_time, 0)
        self.assertEqual(load_switch.general.side, 1)
        self.assertEqual(load_switch.general.standardizable, False)

        # Should have default loadswitch type
        self.assertIsNotNone(load_switch.type)
        self.assertEqual(load_switch.type.short_name, "")
        self.assertEqual(load_switch.type.unom, 0.0)
        self.assertEqual(load_switch.type.inom, 0.0)
        self.assertEqual(load_switch.type.ik_thermal, 0.0)
        self.assertEqual(load_switch.type.t_thermal, 0.0)

        # Should have empty presentations
        self.assertEqual(len(load_switch.presentations), 0)

    def test_duplicate_load_switch_registration_overwrites(self) -> None:
        """Test GUID collision handling with proper logging verification."""
        general1 = LoadSwitchLV.General(guid=self.test_guid, name="Load Switch 1")
        general2 = LoadSwitchLV.General(guid=self.test_guid, name="Load Switch 2")

        loadswitch_type1 = LoadSwitchLV.LoadSwitchType(short_name="LS-16A")
        loadswitch_type2 = LoadSwitchLV.LoadSwitchType(short_name="LS-25A")

        load_switch1 = LoadSwitchLV(
            general=general1, presentations=[], type=loadswitch_type1
        )
        load_switch2 = LoadSwitchLV(
            general=general2, presentations=[], type=loadswitch_type2
        )

        # Register first load switch
        load_switch1.register(self.network)
        self.assertEqual(
            self.network.load_switches[self.test_guid].general.name, "Load Switch 1"
        )

        # Register second load switch with same GUID should overwrite
        load_switch2.register(self.network)
        # Verify load switch was overwritten
        self.assertEqual(
            self.network.load_switches[self.test_guid].general.name, "Load Switch 2"
        )

    def test_load_switch_general_serialize_with_defaults(self) -> None:
        """Test General class serialization with default values."""
        general = LoadSwitchLV.General(guid=self.test_guid, name="Test Load Switch")

        result = general.serialize()

        # Should include required fields
        self.assertIn(f"GUID:{encode_guid(self.test_guid)}", result)
        self.assertIn("Name:'Test Load Switch'", result)
        self.assertIn("CreationTime:0", result)
        self.assertIn("Side:1", result)
        self.assertIn("Standardizable:false", result)

        # Should skip default values
        self.assertNotIn("MutationDate:", result)
        self.assertNotIn("RevisionDate:", result)
        self.assertNotIn("InObject:", result)  # NIL_GUID should be skipped

    def test_load_switch_general_serialize_with_in_object(self) -> None:
        """Test General class serialization with InObject set."""
        general = LoadSwitchLV.General(
            guid=self.test_guid, name="Test Load Switch", in_object=self.in_object_guid
        )

        result = general.serialize()

        # Should include InObject when not NIL_GUID
        self.assertIn(f"InObject:{encode_guid(self.in_object_guid)}", result)

    def test_load_switch_type_serialize_with_defaults(self) -> None:
        """Test LoadSwitchType class serialization with default values."""
        loadswitch_type = LoadSwitchLV.LoadSwitchType(short_name="LS-16A")

        result = loadswitch_type.serialize()

        # Should include all fields even if default
        self.assertIn("ShortName:'LS-16A'", result)
        self.assertIn("Unom:0.0", result)
        self.assertIn("Inom:0.0", result)
        self.assertIn("IkThermal:0.0", result)
        self.assertIn("TThermal:0.0", result)

    def test_load_switch_type_serialize_with_values(self) -> None:
        """Test LoadSwitchType class serialization with values."""
        loadswitch_type = LoadSwitchLV.LoadSwitchType(
            short_name="LS-25A", unom=230.0, inom=25.0, ik_thermal=1000.0, t_thermal=1.0
        )

        result = loadswitch_type.serialize()

        self.assertIn("ShortName:'LS-25A'", result)
        self.assertIn("Unom:230.0", result)
        self.assertIn("Inom:25.0", result)
        self.assertIn("IkThermal:1000.0", result)
        self.assertIn("TThermal:1.0", result)

    def test_load_switch_round_trip_serialization(self) -> None:
        """Test that serialization and deserialization are consistent."""
        original_general = LoadSwitchLV.General(
            guid=self.test_guid,
            name="Round Trip Load Switch",
            creation_time=1234567890.0,
            side=2,
        )

        original_loadswitch_type = LoadSwitchLV.LoadSwitchType(
            short_name="LS-25A", unom=230.0, inom=25.0, ik_thermal=1000.0, t_thermal=1.0
        )

        original_load_switch = LoadSwitchLV(
            general=original_general,
            presentations=[
                BranchPresentation(first_corners=[(10, 20)], second_corners=[(30, 40)])
            ],
            type=original_loadswitch_type,
        )

        original_load_switch.serialize()

        # Simulate parsing back from GNF format
        data = {
            "general": [
                {
                    "GUID": str(self.test_guid),
                    "Name": "Round Trip Load Switch",
                    "CreationTime": 1234567890.0,
                    "Side": 2,
                }
            ],
            "loadswitch": [
                {
                    "ShortName": "LS-25A",
                    "Unom": 230.0,
                    "Inom": 25.0,
                    "IkThermal": 1000.0,
                    "TThermal": 1.0,
                }
            ],
            "presentations": [
                {"FirstCorners": [(10, 20)], "SecondCorners": [(30, 40)]}
            ],
        }

        deserialized = LoadSwitchLV.deserialize(data)

        # Verify key properties match
        self.assertEqual(deserialized.general.guid, original_load_switch.general.guid)
        self.assertEqual(deserialized.general.name, original_load_switch.general.name)
        self.assertEqual(
            deserialized.general.creation_time,
            original_load_switch.general.creation_time,
        )
        self.assertEqual(deserialized.general.side, original_load_switch.general.side)

        # Verify loadswitch type properties
        self.assertEqual(
            deserialized.type.short_name,
            original_load_switch.type.short_name,
        )
        self.assertEqual(deserialized.type.unom, original_load_switch.type.unom)
        self.assertEqual(deserialized.type.inom, original_load_switch.type.inom)
        self.assertEqual(
            deserialized.type.ik_thermal,
            original_load_switch.type.ik_thermal,
        )
        self.assertEqual(
            deserialized.type.t_thermal, original_load_switch.type.t_thermal
        )

        # Verify presentations
        self.assertEqual(
            len(deserialized.presentations), len(original_load_switch.presentations)
        )
        self.assertEqual(
            deserialized.presentations[0].first_corners,
            original_load_switch.presentations[0].first_corners,
        )
        self.assertEqual(
            deserialized.presentations[0].second_corners,
            original_load_switch.presentations[0].second_corners,
        )


if __name__ == "__main__":
    unittest.main()
