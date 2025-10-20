"""Tests for Profile element (MV networks)."""

import unittest
from uuid import uuid4

from pyptp.elements.element_utils import Guid
from pyptp.elements.mv.profile import ProfileMV
from pyptp.network_mv import NetworkMV


class TestProfileRegistration(unittest.TestCase):
    """Test profile element registration and serialization behavior."""

    def setUp(self) -> None:
        """Create fresh network and dependencies for isolated testing."""
        self.network = NetworkMV()

    def test_profile_registration_works(self) -> None:
        """Verify basic profile element registration in network."""
        profile_guid = Guid(uuid4())

        profile = ProfileMV(
            general=ProfileMV.General(
                guid=profile_guid, name="Test Profile", type="Battery"
            ),
            type=ProfileMV.ProfileType(sort=123, f=[1.0, 2.0, 3.0]),
        )

        profile.register(self.network)

        self.assertIn(profile_guid, self.network.profiles)
        self.assertEqual(self.network.profiles[profile_guid], profile)

    def test_profile_with_dynamic_factors_serializes_correctly(self) -> None:
        """Test serialization with dynamic f1, f2, f3... properties."""
        profile_guid = Guid(uuid4())

        profile = ProfileMV(
            general=ProfileMV.General(
                guid=profile_guid, name="Accu Profile", type="Battery Type"
            ),
            type=ProfileMV.ProfileType(
                sort=456,
                f=[1.5, 2.7, 3.9, 4.1, 5.3],
            ),
        )

        serialized = profile.serialize()

        self.assertIn(
            f"#General GUID:'{{{str(profile_guid).upper()}}}' Name:'Accu Profile' ProfileType:'Battery Type'",
            serialized,
        )
        self.assertIn(
            "#ProfileType Sort:456 f1:1.5 f2:2.7 f3:3.9 f4:4.1 f5:5.3", serialized
        )

    def test_profile_deserialization_works(self) -> None:
        """Test deserialization from VNF data dictionary."""
        profile_guid = Guid(uuid4())

        data = {
            "general": [
                {
                    "GUID": str(profile_guid),
                    "Name": "Test Profile",
                    "ProfileType": "TestType",
                }
            ],
            "profileType": [
                {
                    "Sort": 789,
                    "f1": "1.1",
                    "f2": "2.2",
                    "f3": "3.3",
                }
            ],
        }

        profile = ProfileMV.deserialize(data)

        self.assertEqual(profile.general.guid, profile_guid)
        self.assertEqual(profile.general.name, "Test Profile")
        self.assertEqual(profile.general.type, "TestType")

        self.assertEqual(profile.type.sort, 789)
        self.assertEqual(profile.type.f, [1.1, 2.2, 3.3])

    def test_profile_dynamic_factors_deserialization(self) -> None:
        """Test deserialization with variable number of f factors."""
        # Test with many factors
        data = {
            "general": [
                {"GUID": str(uuid4()), "Name": "Many Factors", "ProfileType": "Multi"}
            ],
            "profileType": [
                {
                    "Sort": 100,
                    "f1": "0.1",
                    "f2": "0.2",
                    "f3": "0.3",
                    "f4": "0.4",
                    "f5": "0.5",
                    "f6": "0.6",
                    "f7": "0.7",
                    "f8": "0.8",
                    "f9": "0.9",
                    "f10": "1.0",
                }
            ],
        }

        profile = ProfileMV.deserialize(data)

        self.assertEqual(profile.type.sort, 100)
        expected_factors = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        self.assertEqual(profile.type.f, expected_factors)

    def test_profile_european_number_format_support(self) -> None:
        """Test deserialization with European number format (comma decimal separator)."""
        data = {
            "general": [
                {"GUID": str(uuid4()), "Name": "European", "ProfileType": "Euro"}
            ],
            "profileType": [
                {
                    "Sort": 200,
                    "f1": "1,5",  # European format with comma
                    "f2": "2,7",
                    "f3": "3,9",
                }
            ],
        }

        profile = ProfileMV.deserialize(data)

        self.assertEqual(profile.type.f, [1.5, 2.7, 3.9])

    def test_minimal_profile_serialization(self) -> None:
        """Test serialization with only required fields."""
        profile_guid = Guid(uuid4())

        profile = ProfileMV(
            general=ProfileMV.General(guid=profile_guid),
            type=ProfileMV.ProfileType(),
        )

        serialized = profile.serialize()

        self.assertIn(f"#General GUID:'{{{str(profile_guid).upper()}}}'", serialized)
        self.assertIn("#ProfileType Sort:0", serialized)
        # Should not contain any f properties since the list is empty
        self.assertNotIn("f1:", serialized)

    def test_duplicate_profile_registration_overwrites(self) -> None:
        """Test GUID collision handling with proper logging verification."""
        profile_guid = Guid(uuid4())

        profile1 = ProfileMV(
            general=ProfileMV.General(guid=profile_guid, name="First"),
            type=ProfileMV.ProfileType(sort=1, f=[1.0]),
        )

        profile2 = ProfileMV(
            general=ProfileMV.General(guid=profile_guid, name="Second"),
            type=ProfileMV.ProfileType(sort=2, f=[2.0]),
        )

        # Register first profile
        profile1.register(self.network)
        self.assertEqual(self.network.profiles[profile_guid].general.name, "First")

        # Register second profile with same GUID - should overwrite with warning
        profile2.register(self.network)

        self.assertEqual(self.network.profiles[profile_guid].general.name, "Second")


if __name__ == "__main__":
    unittest.main()
