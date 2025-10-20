"""Tests for TGrowthMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.element_utils import Guid
from pyptp.elements.mv.growth import GrowthMV
from pyptp.network_mv import NetworkMV


class TestGrowthRegistration(unittest.TestCase):
    """Test growth registration and functionality."""

    def setUp(self) -> None:
        """Create a fresh network for testing."""
        self.network = NetworkMV()
        self.growth_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_growth_registration_works(self) -> None:
        """Test that growth can register themselves with the network."""
        general = GrowthMV.General(guid=self.growth_guid, name="TestGrowth")

        growth = GrowthMV(general)
        growth.register(self.network)

        # Verify growth is in network
        self.assertIn(self.growth_guid, self.network.growths)
        self.assertIs(self.network.growths[self.growth_guid], growth)

    def test_growth_with_full_properties_serializes_correctly(self) -> None:
        """Test that growth with all properties serialize correctly."""
        scale_values = [0.1, 0.2, 0.3, 0.4, 0.5] + [0.0] * 25
        growth_values = [1.1, 1.2, 1.3, 1.4] + [1.0] * 25

        general = GrowthMV.General(
            guid=self.growth_guid,
            name="FullGrowth",
            scale=scale_values,
            growth=growth_values,
        )

        growth = GrowthMV(general)
        growth.register(self.network)

        # Test serialization
        serialized = growth.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)

        # Verify general properties
        self.assertIn("Name:'FullGrowth'", serialized)
        self.assertIn(f"GUID:'{{{str(self.growth_guid).upper()}}}'", serialized)

        # Verify scale array properties
        self.assertIn("Scale0:0.1", serialized)
        self.assertIn("Scale1:0.2", serialized)
        self.assertIn("Scale2:0.3", serialized)
        self.assertIn("Scale3:0.4", serialized)
        self.assertIn("Scale4:0.5", serialized)

        # Verify growth array properties
        self.assertIn("Growth1:1.1", serialized)
        self.assertIn("Growth2:1.2", serialized)
        self.assertIn("Growth3:1.3", serialized)
        self.assertIn("Growth4:1.4", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a growth with the same GUID overwrites the existing one."""
        general1 = GrowthMV.General(guid=self.growth_guid, name="FirstGrowth")
        growth1 = GrowthMV(general1)
        growth1.register(self.network)

        general2 = GrowthMV.General(guid=self.growth_guid, name="SecondGrowth")
        growth2 = GrowthMV(general2)
        growth2.register(self.network)

        # Should only have one growth
        self.assertEqual(len(self.network.growths), 1)
        # Should be the second growth
        self.assertEqual(
            self.network.growths[self.growth_guid].general.name, "SecondGrowth"
        )

    def test_minimal_growth_serialization(self) -> None:
        """Test that minimal growth serialize correctly with only required fields."""
        general = GrowthMV.General(guid=self.growth_guid, name="MinimalGrowth")

        growth = GrowthMV(general)
        growth.register(self.network)

        serialized = growth.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)

        # Should have basic properties
        self.assertIn("Name:'MinimalGrowth'", serialized)
        self.assertIn(f"GUID:'{{{str(self.growth_guid).upper()}}}'", serialized)

        # Should have default growth values (29 ones) - Scale values are 0.0 and get skipped
        self.assertIn("Growth1:1", serialized)
        self.assertIn("Growth29:1", serialized)

        # Should not have scale values since they're 0.0 and get skipped
        self.assertNotIn("Scale1:0", serialized)

    def test_growth_with_custom_scale_serializes_correctly(self) -> None:
        """Test that growth with custom scale values serialize correctly."""
        scale_values = [0.5, 0.6, 0.7] + [0.0] * 27

        general = GrowthMV.General(
            guid=self.growth_guid,
            name="CustomScaleGrowth",
            scale=scale_values,
        )

        growth = GrowthMV(general)
        growth.register(self.network)

        serialized = growth.serialize()
        self.assertIn("Scale0:0.5", serialized)
        self.assertIn("Scale1:0.6", serialized)
        self.assertIn("Scale2:0.7", serialized)

    def test_growth_with_custom_growth_serializes_correctly(self) -> None:
        """Test that growth with custom growth values serialize correctly."""
        growth_values = [2.0, 2.5, 3.0] + [1.0] * 26

        general = GrowthMV.General(
            guid=self.growth_guid,
            name="CustomGrowthGrowth",
            growth=growth_values,
        )

        growth = GrowthMV(general)
        growth.register(self.network)

        serialized = growth.serialize()
        self.assertIn("Growth1:2", serialized)
        self.assertIn("Growth2:2.5", serialized)
        self.assertIn("Growth3:3", serialized)

    def test_growth_with_empty_arrays_serializes_correctly(self) -> None:
        """Test that growth with empty arrays serialize correctly."""
        general = GrowthMV.General(
            guid=self.growth_guid,
            name="EmptyArraysGrowth",
            scale=[],
            growth=[],
        )

        growth = GrowthMV(general)
        growth.register(self.network)

        serialized = growth.serialize()
        self.assertIn("Name:'EmptyArraysGrowth'", serialized)
        self.assertIn(f"GUID:'{{{str(self.growth_guid).upper()}}}'", serialized)

        # Should not have any Scale or Growth values
        self.assertNotIn("Scale1", serialized)
        self.assertNotIn("Growth1", serialized)


if __name__ == "__main__":
    unittest.main()
