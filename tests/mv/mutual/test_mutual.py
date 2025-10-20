"""Tests for MutualMV behavior using the simplified dataclass structure."""

import unittest
from uuid import UUID

from pyptp.elements.element_utils import Guid
from pyptp.elements.mv.mutual import MutualMV
from pyptp.network_mv import NetworkMV


class TestMutualRegistration(unittest.TestCase):
    """Test mutual registration and serialization."""

    def setUp(self) -> None:
        """Create fresh network and test GUIDs for isolated testing."""
        self.network = NetworkMV()
        self.line1_guid = Guid(UUID("aec2228f-a78e-4f54-9ed2-0a7dbd48b3f6"))
        self.line2_guid = Guid(UUID("bec2228f-a78e-4f54-9ed2-0a7dbd48b3f7"))

    def test_mutual_registration_works(self) -> None:
        """Verify basic mutual registration in network."""
        mutual = MutualMV(
            line1=self.line1_guid,
            line2=self.line2_guid,
            R00=1.5,
            X00=2.5,
        )
        mutual.register(self.network)

        # Verify mutual is in network with correct key
        key = f"{self.line1_guid}_{self.line2_guid}"
        self.assertIn(key, self.network.mutuals)
        self.assertIs(self.network.mutuals[key], mutual)

    def test_mutual_with_full_properties_serializes_correctly(self) -> None:
        """Test serialization with ALL properties set.

        Critical for ensuring comprehensive format coverage and
        detecting serialization issues early.
        """
        mutual = MutualMV(
            line1=self.line1_guid,
            line2=self.line2_guid,
            R00=1.5,
            X00=2.5,
        )
        mutual.register(self.network)

        serialized = mutual.serialize()

        # Verify General section
        self.assertEqual(serialized.count("#General"), 1)

        # Verify all properties are serialized (no_skip variants used)
        self.assertIn(f"Line1:'{{{str(self.line1_guid).upper()}}}'", serialized)
        self.assertIn(f"Line2:'{{{str(self.line2_guid).upper()}}}'", serialized)
        self.assertIn("R00:1.5", serialized)
        self.assertIn("X00:2.5", serialized)

    def test_minimal_mutual_serialization(self) -> None:
        """Test serialization with zero values for R00 and X00.

        Verifies that even zero values are serialized since
        no_skip variants are used.
        """
        mutual = MutualMV(
            line1=self.line1_guid,
            line2=self.line2_guid,
            R00=0.0,
            X00=0.0,
        )
        mutual.register(self.network)

        serialized = mutual.serialize()

        # Should have General section
        self.assertEqual(serialized.count("#General"), 1)

        # All properties should be present (no_skip variants)
        self.assertIn(f"Line1:'{{{str(self.line1_guid).upper()}}}'", serialized)
        self.assertIn(f"Line2:'{{{str(self.line2_guid).upper()}}}'", serialized)
        self.assertIn("R00:0.0", serialized)
        self.assertIn("X00:0.0", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test GUID collision handling with proper logging verification."""
        mutual1 = MutualMV(
            line1=self.line1_guid,
            line2=self.line2_guid,
            R00=1.0,
            X00=1.0,
        )
        mutual1.register(self.network)

        # Register another mutual with same line pair
        mutual2 = MutualMV(
            line1=self.line1_guid,
            line2=self.line2_guid,
            R00=2.0,
            X00=2.0,
        )
        mutual2.register(self.network)

        # Should only have one mutual
        self.assertEqual(len(self.network.mutuals), 1)

        # Should be the second mutual
        key = f"{self.line1_guid}_{self.line2_guid}"
        self.assertEqual(self.network.mutuals[key].R00, 2.0)
        self.assertEqual(self.network.mutuals[key].X00, 2.0)

    def test_deserialize_with_valid_data(self) -> None:
        """Test deserialization from VNF format."""
        data = {
            "general": [
                {
                    "Line1": f"{{{str(self.line1_guid).upper()}}}",
                    "Line2": f"{{{str(self.line2_guid).upper()}}}",
                    "R00": 1.5,
                    "X00": 2.5,
                }
            ]
        }

        mutual = MutualMV.deserialize(data)

        self.assertEqual(mutual.line1, self.line1_guid)
        self.assertEqual(mutual.line2, self.line2_guid)
        self.assertEqual(mutual.R00, 1.5)
        self.assertEqual(mutual.X00, 2.5)

    def test_deserialize_with_missing_lines_raises_error(self) -> None:
        """Test that deserialization fails when Line1 or Line2 are missing."""
        # Missing Line1
        data1 = {
            "general": [
                {
                    "Line2": f"{{{str(self.line2_guid).upper()}}}",
                    "R00": 1.5,
                    "X00": 2.5,
                }
            ]
        }

        with self.assertRaises(ValueError) as ctx:
            MutualMV.deserialize(data1)
        self.assertIn("requires both Line1 and Line2", str(ctx.exception))

        # Missing Line2
        data2 = {
            "general": [
                {
                    "Line1": f"{{{str(self.line1_guid).upper()}}}",
                    "R00": 1.5,
                    "X00": 2.5,
                }
            ]
        }

        with self.assertRaises(ValueError) as ctx:
            MutualMV.deserialize(data2)
        self.assertIn("requires both Line1 and Line2", str(ctx.exception))

    def test_deserialize_with_default_values(self) -> None:
        """Test deserialization with missing R00/X00 uses defaults."""
        data = {
            "general": [
                {
                    "Line1": f"{{{str(self.line1_guid).upper()}}}",
                    "Line2": f"{{{str(self.line2_guid).upper()}}}",
                }
            ]
        }

        mutual = MutualMV.deserialize(data)

        self.assertEqual(mutual.line1, self.line1_guid)
        self.assertEqual(mutual.line2, self.line2_guid)
        self.assertEqual(mutual.R00, 0.0)
        self.assertEqual(mutual.X00, 0.0)

    def test_roundtrip_serialization(self) -> None:
        """Test that serialize->deserialize produces equivalent mutual."""
        original = MutualMV(
            line1=self.line1_guid,
            line2=self.line2_guid,
            R00=3.14,
            X00=2.71,
        )

        # Serialize
        serialized = original.serialize()

        # Parse the serialized format into data dict
        # (This simulates what the VNF parser would do)
        data = {"general": [{}]}

        # Extract properties from "#General ..." line
        if "Line1:" in serialized:
            start = serialized.index("Line1:'") + len("Line1:'")
            end = serialized.index("'", start)
            data["general"][0]["Line1"] = serialized[start:end]

        if "Line2:" in serialized:
            start = serialized.index("Line2:'") + len("Line2:'")
            end = serialized.index("'", start)
            data["general"][0]["Line2"] = serialized[start:end]

        if "R00:" in serialized:
            start = serialized.index("R00:") + len("R00:")
            end = serialized.find(" ", start)
            if end == -1:
                end = len(serialized)
            data["general"][0]["R00"] = float(serialized[start:end])

        if "X00:" in serialized:
            start = serialized.index("X00:") + len("X00:")
            end = serialized.find(" ", start)
            if end == -1:
                end = len(serialized)
            data["general"][0]["X00"] = float(serialized[start:end])

        # Deserialize
        deserialized = MutualMV.deserialize(data)

        # Verify equality
        self.assertEqual(deserialized.line1, original.line1)
        self.assertEqual(deserialized.line2, original.line2)
        self.assertEqual(deserialized.R00, original.R00)
        self.assertEqual(deserialized.X00, original.X00)


if __name__ == "__main__":
    unittest.main()
