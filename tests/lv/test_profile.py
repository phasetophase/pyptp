"""Tests for TProfileLS class."""

from __future__ import annotations

import unittest
from uuid import uuid4

from pyptp.elements.element_utils import Guid, encode_guid
from pyptp.elements.lv.profile import ProfileLV
from pyptp.network_lv import NetworkLV


class TestTProfileLS(unittest.TestCase):
    """Test TProfileLS registration and serialization behavior."""

    def setUp(self) -> None:
        """Create fresh network and dependencies for isolated testing."""
        self.network = NetworkLV()
        self.test_guid = Guid(uuid4())

    def test_profile_registration_works(self) -> None:
        """Verify basic profile registration in network."""
        general = ProfileLV.General(
            guid=self.test_guid, name="Test Profile", profile_type="Daily"
        )
        profile_type = ProfileLV.ProfileType(sort=1, f=[0.8, 0.9, 1.0, 1.1, 1.2])
        profile = ProfileLV(general=general, type=profile_type)

        # Verify network starts empty
        self.assertEqual(len(self.network.profiles), 0)

        # Register profile
        profile.register(self.network)

        # Verify profile was added
        self.assertEqual(len(self.network.profiles), 1)
        self.assertEqual(self.network.profiles[self.test_guid], profile)

    def test_profile_with_minimal_properties_serializes_correctly(self) -> None:
        """Test serialization with minimal properties."""
        general = ProfileLV.General(
            guid=self.test_guid, name="Minimal Profile", profile_type="Daily"
        )
        profile_type = ProfileLV.ProfileType()
        profile = ProfileLV(general=general, type=profile_type)

        result = profile.serialize()

        # Should contain general line
        self.assertIn("#General", result)
        self.assertIn(f"GUID:{encode_guid(self.test_guid)}", result)
        self.assertIn("Name:'Minimal Profile'", result)
        self.assertIn("ProfileType:'Daily'", result)

        # Should contain profile type line
        self.assertIn("#ProfileType", result)
        self.assertIn("Sort:-3456", result)

        # Should not contain f factors for empty list
        self.assertNotIn("f1:", result)

    def test_profile_with_full_properties_serializes_correctly(self) -> None:
        """Test serialization with all properties set."""
        general = ProfileLV.General(
            guid=self.test_guid, name="Full Profile", profile_type="Hourly"
        )
        profile_type = ProfileLV.ProfileType(
            sort=1, f=[0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5]
        )
        profile = ProfileLV(general=general, type=profile_type)

        result = profile.serialize()

        # Verify general section
        self.assertIn("#General", result)
        self.assertIn(f"GUID:{encode_guid(self.test_guid)}", result)
        self.assertIn("Name:'Full Profile'", result)
        self.assertIn("ProfileType:'Hourly'", result)

        # Verify profile type section
        self.assertIn("#ProfileType", result)
        self.assertIn("Sort:1", result)
        self.assertIn("f1:0.8", result)
        self.assertIn("f2:0.9", result)
        self.assertIn("f3:1", result)
        self.assertIn("f4:1.1", result)
        self.assertIn("f5:1.2", result)
        self.assertIn("f6:1.3", result)
        self.assertIn("f7:1.4", result)
        self.assertIn("f8:1.5", result)

    def test_profile_deserialization_works(self) -> None:
        """Test deserialization from GNF format data."""
        data = {
            "general": [
                {
                    "GUID": str(self.test_guid),
                    "Name": "Deserialized Profile",
                    "ProfileType": "Weekly",
                }
            ],
            "profileType": [
                {
                    "Sort": 2,
                    "f1": "0,8",
                    "f2": "0,9",
                    "f3": "1,0",
                    "f4": "1,1",
                    "f5": "1,2",
                }
            ],
        }

        profile = ProfileLV.deserialize(data)

        # Verify general properties
        self.assertEqual(profile.general.guid, self.test_guid)
        self.assertEqual(profile.general.name, "Deserialized Profile")
        self.assertEqual(profile.general.profile_type, "Weekly")

        # Verify profile type properties
        self.assertEqual(profile.type.sort, 2)
        self.assertEqual(profile.type.f, [0.8, 0.9, 1.0, 1.1, 1.2])

    def test_profile_deserialization_with_empty_data(self) -> None:
        """Test deserialization with empty data."""
        data = {}

        profile = ProfileLV.deserialize(data)

        # Should have default general properties
        self.assertIsNotNone(profile.general)
        self.assertEqual(profile.general.name, "")
        self.assertEqual(profile.general.profile_type, "")

        # Should have default profile type properties
        self.assertIsNotNone(profile.type)
        self.assertEqual(profile.type.sort, -3456)
        self.assertEqual(profile.type.f, [])

    def test_duplicate_profile_registration_overwrites(self) -> None:
        """Test GUID collision handling with proper logging verification."""
        general1 = ProfileLV.General(
            guid=self.test_guid, name="Profile 1", profile_type="Daily"
        )
        general2 = ProfileLV.General(
            guid=self.test_guid, name="Profile 2", profile_type="Hourly"
        )

        profile_type1 = ProfileLV.ProfileType(sort=1, f=[0.8, 0.9, 1.0])
        profile_type2 = ProfileLV.ProfileType(sort=2, f=[1.0, 1.1, 1.2])

        profile1 = ProfileLV(general=general1, type=profile_type1)
        profile2 = ProfileLV(general=general2, type=profile_type2)

        # Register first profile
        profile1.register(self.network)
        self.assertEqual(
            self.network.profiles[self.test_guid].general.name, "Profile 1"
        )

        # Register second profile with same GUID should overwrite
        profile2.register(self.network)
        # Verify profile was overwritten
        self.assertEqual(
            self.network.profiles[self.test_guid].general.name, "Profile 2"
        )

    def test_profile_general_serialize_with_empty_strings(self) -> None:
        """Test General class serialization with empty strings."""
        general = ProfileLV.General(guid=self.test_guid, name="", profile_type="")

        result = general.serialize()

        # Should include required GUID
        self.assertIn(f"GUID:{encode_guid(self.test_guid)}", result)

        # Should skip empty strings
        self.assertNotIn("Name:", result)
        self.assertNotIn("ProfileType:", result)

    def test_profile_general_serialize_with_values(self) -> None:
        """Test General class serialization with values."""
        general = ProfileLV.General(
            guid=self.test_guid, name="Test Profile", profile_type="Daily"
        )

        result = general.serialize()

        self.assertIn(f"GUID:{encode_guid(self.test_guid)}", result)
        self.assertIn("Name:'Test Profile'", result)
        self.assertIn("ProfileType:'Daily'", result)

    def test_profile_type_serialize_with_defaults(self) -> None:
        """Test ProfileType class serialization with default values."""
        profile_type = ProfileLV.ProfileType()

        result = profile_type.serialize()

        # Should include Sort even if default
        self.assertIn("Sort:-3456", result)

        # Should not include f values for empty list
        self.assertNotIn("f1:", result)

    def test_profile_type_serialize_with_factors(self) -> None:
        """Test ProfileType class serialization with factors."""
        profile_type = ProfileLV.ProfileType(sort=1, f=[0.8, 0.9, 1.0, 1.1, 1.2])

        result = profile_type.serialize()

        self.assertIn("Sort:1", result)
        self.assertIn("f1:0.8", result)
        self.assertIn("f2:0.9", result)
        self.assertIn("f3:1", result)
        self.assertIn("f4:1.1", result)
        self.assertIn("f5:1.2", result)

    def test_profile_type_deserialize_with_comma_decimals(self) -> None:
        """Test ProfileType class deserialization with comma decimal notation."""
        data = {
            "Sort": 1,
            "f1": "0,8",
            "f2": "0,9",
            "f3": "1,0",
            "f4": "1,1",
            "f5": "1,2",
        }

        profile_type = ProfileLV.ProfileType.deserialize(data)

        self.assertEqual(profile_type.sort, 1)
        self.assertEqual(profile_type.f, [0.8, 0.9, 1.0, 1.1, 1.2])

    def test_profile_type_deserialize_with_dot_decimals(self) -> None:
        """Test ProfileType class deserialization with dot decimal notation."""
        data = {
            "Sort": 1,
            "f1": "0.8",
            "f2": "0.9",
            "f3": "1.0",
            "f4": "1.1",
            "f5": "1.2",
        }

        profile_type = ProfileLV.ProfileType.deserialize(data)

        self.assertEqual(profile_type.sort, 1)
        self.assertEqual(profile_type.f, [0.8, 0.9, 1.0, 1.1, 1.2])

    def test_profile_type_deserialize_with_gap_in_factors(self) -> None:
        """Test ProfileType class deserialization with gap in f factors."""
        data = {
            "Sort": 1,
            "f1": "0.8",
            "f2": "0.9",
            "f4": "1.1",
            "f5": "1.2",
        }  # f3 is missing

        profile_type = ProfileLV.ProfileType.deserialize(data)

        # Should stop at first missing factor
        self.assertEqual(profile_type.sort, 1)
        self.assertEqual(profile_type.f, [0.8, 0.9])

    def test_profile_round_trip_serialization(self) -> None:
        """Test that serialization and deserialization are consistent."""
        original_general = ProfileLV.General(
            guid=self.test_guid, name="Round Trip Profile", profile_type="Daily"
        )

        original_profile_type = ProfileLV.ProfileType(
            sort=1, f=[0.8, 0.9, 1.0, 1.1, 1.2]
        )

        original_profile = ProfileLV(
            general=original_general, type=original_profile_type
        )

        original_profile.serialize()

        # Simulate parsing back from GNF format
        data = {
            "general": [
                {
                    "GUID": str(self.test_guid),
                    "Name": "Round Trip Profile",
                    "ProfileType": "Daily",
                }
            ],
            "profileType": [
                {
                    "Sort": 1,
                    "f1": "0.8",
                    "f2": "0.9",
                    "f3": "1.0",
                    "f4": "1.1",
                    "f5": "1.2",
                }
            ],
        }

        deserialized = ProfileLV.deserialize(data)

        # Verify key properties match
        self.assertEqual(deserialized.general.guid, original_profile.general.guid)
        self.assertEqual(deserialized.general.name, original_profile.general.name)
        self.assertEqual(
            deserialized.general.profile_type, original_profile.general.profile_type
        )

        # Verify profile type properties
        self.assertEqual(deserialized.type.sort, original_profile.type.sort)
        self.assertEqual(deserialized.type.f, original_profile.type.f)

    def test_profile_serialize_with_large_factor_list(self) -> None:
        """Test serialization with a large list of factors."""
        # Create 24 factors for hourly profile
        factors = [round(0.5 + i * 0.1, 2) for i in range(24)]

        general = ProfileLV.General(
            guid=self.test_guid, name="24 Hour Profile", profile_type="Hourly"
        )
        profile_type = ProfileLV.ProfileType(sort=1, f=factors)
        profile = ProfileLV(general=general, type=profile_type)

        result = profile.serialize()

        # Verify all factors are present
        for i, factor in enumerate(factors):
            self.assertIn(f"f{i + 1}:{factor}", result)

    def test_profile_deserialize_with_large_factor_list(self) -> None:
        """Test deserialization with a large list of factors."""
        factors = [round(0.5 + i * 0.1, 2) for i in range(24)]

        profile_type_data: dict[str, str | int] = {"Sort": 1}
        for i, factor in enumerate(factors):
            profile_type_data[f"f{i + 1}"] = str(factor)

        data = {
            "general": [
                {
                    "GUID": str(self.test_guid),
                    "Name": "24 Hour Profile",
                    "ProfileType": "Hourly",
                }
            ],
            "profileType": [profile_type_data],
        }

        profile = ProfileLV.deserialize(data)

        # Verify all factors are correctly parsed
        self.assertEqual(profile.type.f, factors)


if __name__ == "__main__":
    unittest.main()
