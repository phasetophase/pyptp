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
        date_values = [20230101, 20240101, 20250101]
        scale_values = [0.1, 0.2, 0.3]

        general = GrowthMV.General(
            guid=self.growth_guid,
            name="FullGrowth",
            dates=date_values,
            scale=scale_values,
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

        # Verify date array properties
        self.assertIn("Date0:20230101", serialized)
        self.assertIn("Date1:20240101", serialized)
        self.assertIn("Date2:20250101", serialized)

        # Verify scale array properties
        self.assertIn("Scale0:0.1", serialized)
        self.assertIn("Scale1:0.2", serialized)
        self.assertIn("Scale2:0.3", serialized)

        # Verify old fields are not present
        self.assertNotIn("Growth1", serialized)
        self.assertNotIn("GrowthSort", serialized)

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

        # Should not have any Date or Scale values with empty defaults
        self.assertNotIn("Date", serialized)
        self.assertNotIn("Scale", serialized)

    def test_growth_with_custom_dates_and_scale_serializes_correctly(self) -> None:
        """Test that growth with custom date and scale values serialize correctly."""
        general = GrowthMV.General(
            guid=self.growth_guid,
            name="CustomGrowth",
            dates=[20200101, 20210101],
            scale=[0.5, 0.6],
        )

        growth = GrowthMV(general)
        growth.register(self.network)

        serialized = growth.serialize()
        self.assertIn("Date0:20200101", serialized)
        self.assertIn("Date1:20210101", serialized)
        self.assertIn("Scale0:0.5", serialized)
        self.assertIn("Scale1:0.6", serialized)

    def test_growth_with_empty_arrays_serializes_correctly(self) -> None:
        """Test that growth with empty arrays serialize correctly."""
        general = GrowthMV.General(
            guid=self.growth_guid,
            name="EmptyArraysGrowth",
            dates=[],
            scale=[],
        )

        growth = GrowthMV(general)
        growth.register(self.network)

        serialized = growth.serialize()
        self.assertIn("Name:'EmptyArraysGrowth'", serialized)
        self.assertIn(f"GUID:'{{{str(self.growth_guid).upper()}}}'", serialized)

        # Should not have any Date or Scale values
        self.assertNotIn("Date", serialized)
        self.assertNotIn("Scale", serialized)


if __name__ == "__main__":
    unittest.main()
