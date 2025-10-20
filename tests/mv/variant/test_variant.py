"""Tests for TVariantMS behavior using the new registration system."""

import unittest

from pyptp.elements.mv.variant import VariantMV
from pyptp.network_mv import NetworkMV


class TestVariantRegistration(unittest.TestCase):
    """Test variant registration and functionality."""

    def setUp(self) -> None:
        """Create a fresh network for testing."""
        self.network = NetworkMV()

    def test_variant_registration_works(self) -> None:
        """Test that variants can register themselves with the network."""
        general = VariantMV.General(name="TestVariant")

        variant = VariantMV(general)
        variant.register(self.network)

        # Verify variant is in network
        self.assertIn("TestVariant", self.network.variants)
        self.assertIs(self.network.variants["TestVariant"], variant)

    def test_variant_with_full_properties_serializes_correctly(self) -> None:
        """Test that variants with all properties serialize correctly."""
        general = VariantMV.General(
            name="FullVariant",
            description="Full variant description",
            message="Full variant message",
            related_scenarios="scenario1,scenario2",
        )

        variant = VariantMV(general)
        variant.register(self.network)

        # Test serialization
        serialized = variant.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)

        # Verify general properties
        self.assertIn("Name:'FullVariant'", serialized)
        self.assertIn("Description:'Full variant description'", serialized)
        self.assertIn("Message:'Full variant message'", serialized)
        self.assertIn("RelatedScenarios:'scenario1,scenario2'", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a variant with the same name overwrites the existing one."""
        general1 = VariantMV.General(name="TestVariant", description="First")
        variant1 = VariantMV(general1)
        variant1.register(self.network)

        general2 = VariantMV.General(name="TestVariant", description="Second")
        variant2 = VariantMV(general2)
        variant2.register(self.network)

        # Should only have one variant
        self.assertEqual(len(self.network.variants), 1)
        # Should be the second variant
        self.assertEqual(
            self.network.variants["TestVariant"].general.description, "Second"
        )

    def test_minimal_variant_serialization(self) -> None:
        """Test that minimal variants serialize correctly with only required fields."""
        general = VariantMV.General(name="MinimalVariant")
        variant = VariantMV(general)
        variant.register(self.network)

        serialized = variant.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)

        # Should have basic properties
        self.assertIn("Name:'MinimalVariant'", serialized)

        # Empty strings should be included since using no_skip
        self.assertIn("Description:''", serialized)
        self.assertIn("Message:''", serialized)
        self.assertIn("RelatedScenarios:''", serialized)

    def test_variant_with_description_serializes_correctly(self) -> None:
        """Test that variants with description serialize correctly."""
        general = VariantMV.General(
            name="DescriptionVariant",
            description="Test description",
        )
        variant = VariantMV(general)
        variant.register(self.network)

        serialized = variant.serialize()
        self.assertIn("Description:'Test description'", serialized)

    def test_variant_with_message_serializes_correctly(self) -> None:
        """Test that variants with message serialize correctly."""
        general = VariantMV.General(
            name="MessageVariant",
            message="Test message",
        )
        variant = VariantMV(general)
        variant.register(self.network)

        serialized = variant.serialize()
        self.assertIn("Message:'Test message'", serialized)

    def test_variant_with_related_scenarios_serializes_correctly(self) -> None:
        """Test that variants with related scenarios serialize correctly."""
        general = VariantMV.General(
            name="ScenarioVariant",
            related_scenarios="scenario1,scenario2,scenario3",
        )
        variant = VariantMV(general)
        variant.register(self.network)

        serialized = variant.serialize()
        self.assertIn("RelatedScenarios:'scenario1,scenario2,scenario3'", serialized)

    def test_variant_with_empty_name_serializes_correctly(self) -> None:
        """Test that variants with empty name serialize correctly."""
        general = VariantMV.General(name="")
        variant = VariantMV(general)
        variant.register(self.network)

        serialized = variant.serialize()
        self.assertIn("Name:''", serialized)

    def test_variant_deserialization_works(self) -> None:
        """Test that variants can be deserialized correctly."""
        data = {
            "general": [
                {
                    "Name": "TestVariant",
                    "Description": "Test description",
                    "Message": "Test message",
                    "RelatedScenarios": "scenario1,scenario2",
                }
            ],
        }

        variant = VariantMV.deserialize(data)

        self.assertEqual(variant.general.name, "TestVariant")
        self.assertEqual(variant.general.description, "Test description")
        self.assertEqual(variant.general.message, "Test message")
        self.assertEqual(variant.general.related_scenarios, "scenario1,scenario2")

    def test_variant_deserialization_with_missing_data_works(self) -> None:
        """Test that variant deserialization works with missing data."""
        data = {}

        variant = VariantMV.deserialize(data)

        self.assertEqual(variant.general.name, "")
        self.assertEqual(variant.general.description, "")
        self.assertEqual(variant.general.message, "")
        self.assertEqual(variant.general.related_scenarios, "")

    def test_variant_general_serialization_works(self) -> None:
        """Test that variant general serialization works correctly."""
        general = VariantMV.General(
            name="TestVariant",
            description="Test description",
            message="Test message",
            related_scenarios="scenario1,scenario2",
        )
        serialized = general.serialize()

        self.assertIn("Name:'TestVariant'", serialized)
        self.assertIn("Description:'Test description'", serialized)
        self.assertIn("Message:'Test message'", serialized)
        self.assertIn("RelatedScenarios:'scenario1,scenario2'", serialized)


if __name__ == "__main__":
    unittest.main()
