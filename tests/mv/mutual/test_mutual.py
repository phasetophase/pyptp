"""Tests for TMutualMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.element_utils import Guid
from pyptp.elements.mixins import Extra, Note
from pyptp.elements.mv.mutual import MutualMV
from pyptp.network_mv import NetworkMV


class TestMutualRegistration(unittest.TestCase):
    """Test mutual registration and functionality."""

    def setUp(self) -> None:
        """Create a fresh network for testing."""
        self.network = NetworkMV()
        self.mutual_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))
        self.in_object_guid = Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5"))
        self.line1_guid = Guid(UUID("aec2228f-a78e-4f54-9ed2-0a7dbd48b3f6"))
        self.line2_guid = Guid(UUID("bec2228f-a78e-4f54-9ed2-0a7dbd48b3f7"))

    def test_mutual_registration_works(self) -> None:
        """Test that mutuals can register themselves with the network."""
        general = MutualMV.General(guid=self.mutual_guid, name="TestMutual")

        mutual = MutualMV(general)
        mutual.register(self.network)

        # Verify mutual is in network (registered with key "None_None")
        key = f"{general.line1}_{general.line2}"
        self.assertIn(key, self.network.mutuals)
        self.assertIs(self.network.mutuals[key], mutual)

    def test_mutual_with_full_properties_serializes_correctly(self) -> None:
        """Test that mutuals with all properties serialize correctly."""
        general = MutualMV.General(
            guid=self.mutual_guid,
            creation_time=123.45,
            mutation_date=10,
            revision_date=20.5,
            variant=True,
            name="FullMutual",
            line1=self.line1_guid,
            line2=self.line2_guid,
            R00=1.5,
            X00=2.5,
        )

        mutual = MutualMV(general)
        mutual.extras.append(Extra(text="foo=bar"))
        mutual.notes.append(Note(text="Test note"))
        mutual.register(self.network)

        # Test serialization
        serialized = mutual.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify only Line1, Line2, R00, X00 are serialized (MUTUAL doesn't have other properties)
        self.assertIn(f"Line1:'{{{str(self.line1_guid).upper()}}}'", serialized)
        self.assertIn(f"Line2:'{{{str(self.line2_guid).upper()}}}'", serialized)
        self.assertIn("R00:1.5", serialized)
        self.assertIn("X00:2.5", serialized)

        # MUTUAL doesn't serialize these properties
        self.assertNotIn("Name:", serialized)
        self.assertNotIn("CreationTime:", serialized)
        self.assertNotIn("MutationDate:", serialized)
        self.assertNotIn("RevisionDate:", serialized)
        self.assertNotIn("Variant:", serialized)
        self.assertNotIn("GUID:", serialized)

        # Verify extras and notes
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a mutual with the same GUID overwrites the existing one."""
        general1 = MutualMV.General(guid=self.mutual_guid, name="FirstMutual")
        mutual1 = MutualMV(general1)
        mutual1.register(self.network)

        general2 = MutualMV.General(guid=self.mutual_guid, name="SecondMutual")
        mutual2 = MutualMV(general2)
        mutual2.register(self.network)

        # Should only have one mutual
        self.assertEqual(len(self.network.mutuals), 1)
        # Should be the second mutual
        key = f"{general2.line1}_{general2.line2}"
        self.assertEqual(self.network.mutuals[key].general.name, "SecondMutual")

    def test_minimal_mutual_serialization(self) -> None:
        """Test that minimal mutuals serialize correctly with only required fields."""
        general = MutualMV.General(
            guid=self.mutual_guid
        )  # GUID is for internal tracking only

        mutual = MutualMV(general)
        mutual.register(self.network)

        serialized = mutual.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)

        # MUTUAL only serializes Line1, Line2, R00, X00
        # With default values (None, None, 0, 0), all are skipped
        self.assertNotIn("Line1", serialized)  # None values are skipped
        self.assertNotIn("Line2", serialized)  # None values are skipped
        self.assertNotIn("R00", serialized)  # 0 values are skipped
        self.assertNotIn("X00", serialized)  # 0 values are skipped

        # MUTUAL never serializes these properties
        self.assertNotIn("GUID", serialized)
        self.assertNotIn("Name", serialized)
        self.assertNotIn("CreationTime", serialized)
        self.assertNotIn("MutationDate", serialized)
        self.assertNotIn("RevisionDate", serialized)
        self.assertNotIn("Variant", serialized)

    def test_mutual_with_element_references_serializes_correctly(self) -> None:
        """Test that mutuals with element references serialize correctly."""
        general = MutualMV.General(
            guid=self.mutual_guid,
            name="ElementReferencesMutual",
            line1=self.line1_guid,
            line2=self.line2_guid,
            R00=1.5,
            X00=2.5,
        )

        mutual = MutualMV(general)
        mutual.register(self.network)

        serialized = mutual.serialize()
        self.assertIn(f"Line1:'{{{str(self.line1_guid).upper()}}}'", serialized)
        self.assertIn(f"Line2:'{{{str(self.line2_guid).upper()}}}'", serialized)
        self.assertIn("R00:1.5", serialized)
        self.assertIn("X00:2.5", serialized)


if __name__ == "__main__":
    unittest.main()
