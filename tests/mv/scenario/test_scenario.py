"""Tests for TScenarioMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.element_utils import Guid
from pyptp.elements.mv.scenario import ScenarioMV
from pyptp.network_mv import NetworkMV


class TestScenarioRegistration(unittest.TestCase):
    """Test scenario registration and functionality."""

    def setUp(self) -> None:
        """Create a fresh network for testing."""
        self.network = NetworkMV()
        self.scenario_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_scenario_registration_works(self) -> None:
        """Test that scenarios can register themselves with the network."""
        general = ScenarioMV.General(Name="TestScenario")

        scenario = ScenarioMV(general)
        scenario.register(self.network)

        # Verify scenario is in network
        self.assertIn("TestScenario", self.network.scenarios)
        self.assertIs(self.network.scenarios["TestScenario"], scenario)

    def test_scenario_with_full_properties_serializes_correctly(self) -> None:
        """Test that scenarios with all properties serialize correctly."""
        general = ScenarioMV.General(
            Name="FullScenario",
        )

        scenario = ScenarioMV(general)
        scenario.register(self.network)

        # Test serialization
        serialized = scenario.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)

        # Verify general properties
        self.assertIn("Name:'FullScenario'", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a scenario with the same name overwrites the existing one."""
        general1 = ScenarioMV.General(Name="TestScenario")
        scenario1 = ScenarioMV(general1)
        scenario1.register(self.network)

        general2 = ScenarioMV.General(Name="TestScenario")
        scenario2 = ScenarioMV(general2)
        scenario2.register(self.network)

        # Should only have one scenario
        self.assertEqual(len(self.network.scenarios), 1)
        # Should be the second scenario
        self.assertEqual(
            self.network.scenarios["TestScenario"].general.Name, "TestScenario"
        )

    def test_minimal_scenario_serialization(self) -> None:
        """Test that minimal scenarios serialize correctly with only required fields."""
        general = ScenarioMV.General(Name="MinimalScenario")
        scenario = ScenarioMV(general)
        scenario.register(self.network)

        serialized = scenario.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)

        # Should have basic properties
        self.assertIn("Name:'MinimalScenario'", serialized)

        # Empty strings should be included since using no_skip

    def test_scenario_with_description_serializes_correctly(self) -> None:
        """Test that scenarios serialize correctly with only Name."""
        general = ScenarioMV.General(
            Name="DescriptionScenario",
        )
        scenario = ScenarioMV(general)
        scenario.register(self.network)

        serialized = scenario.serialize()
        self.assertIn("Name:'DescriptionScenario'", serialized)

    def test_scenario_with_message_serializes_correctly(self) -> None:
        """Test that scenarios serialize correctly with only Name."""
        general = ScenarioMV.General(
            Name="MessageScenario",
        )
        scenario = ScenarioMV(general)
        scenario.register(self.network)

        serialized = scenario.serialize()
        self.assertIn("Name:'MessageScenario'", serialized)

    def test_scenario_with_related_variants_serializes_correctly(self) -> None:
        """Test that scenarios serialize correctly with only Name."""
        general = ScenarioMV.General(
            Name="VariantScenario",
        )
        scenario = ScenarioMV(general)
        scenario.register(self.network)

        serialized = scenario.serialize()
        self.assertIn("Name:'VariantScenario'", serialized)

    def test_scenario_with_empty_name_serializes_correctly(self) -> None:
        """Test that scenarios with empty name serialize correctly."""
        general = ScenarioMV.General(Name="")
        scenario = ScenarioMV(general)
        scenario.register(self.network)

        serialized = scenario.serialize()
        self.assertIn("Name:''", serialized)

    def test_scenario_deserialization_works(self) -> None:
        """Test that scenarios can be deserialized correctly."""
        data = {
            "general": [
                {
                    "Name": "TestScenario",
                }
            ],
        }

        scenario = ScenarioMV.deserialize(data)

        self.assertEqual(scenario.general.Name, "TestScenario")

    def test_scenario_deserialization_with_missing_data_works(self) -> None:
        """Test that scenario deserialization works with missing data."""
        data = {}

        scenario = ScenarioMV.deserialize(data)

        self.assertEqual(scenario.general.Name, "")

    def test_scenario_general_serialization_works(self) -> None:
        """Test that scenario general serialization works correctly."""
        general = ScenarioMV.General(
            Name="TestScenario",
        )
        serialized = general.serialize()

        self.assertIn("Name:'TestScenario'", serialized)

    def test_scenario_item_serialization_works(self) -> None:
        """Test that scenario item serialization works correctly."""
        vision_object_guid = Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5"))
        item = ScenarioMV.ScenarioItem(
            date=20231201,
            vision_object=vision_object_guid,
            attribute=1,
            value=100.5,
            comment="Test comment",
        )

        serialized = item.serialize()

        self.assertIn("Date:20231201", serialized)
        self.assertIn(
            f"VisionObject:'{{{str(vision_object_guid).upper()}}}'", serialized
        )
        self.assertIn("Attribute:1", serialized)
        self.assertIn("Value:100.5", serialized)
        self.assertIn("Comment:'Test comment'", serialized)

    def test_scenario_item_serialization_with_no_vision_object_works(self) -> None:
        """Test that scenario item serialization works without vision object."""
        item = ScenarioMV.ScenarioItem(
            date=20231201,
            vision_object=None,
            attribute=1,
            value=100.5,
            comment="Test comment",
        )

        serialized = item.serialize()

        self.assertIn("Date:20231201", serialized)
        self.assertNotIn("VisionObject:", serialized)
        self.assertIn("Attribute:1", serialized)
        self.assertIn("Value:100.5", serialized)
        self.assertIn("Comment:'Test comment'", serialized)

    def test_scenario_item_deserialization_works(self) -> None:
        """Test that scenario item deserialization works correctly."""
        vision_object_guid = Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5"))
        data = {
            "Date": 20231201,
            "VisionObject": str(vision_object_guid),
            "Attribute": 1,
            "Value": 100.5,
            "Comment": "Test comment",
        }

        item = ScenarioMV.ScenarioItem.deserialize(data)

        self.assertEqual(item.date, 20231201)
        self.assertEqual(item.vision_object, vision_object_guid)
        self.assertEqual(item.attribute, 1)
        self.assertEqual(item.value, 100.5)
        self.assertEqual(item.comment, "Test comment")

    def test_scenario_item_deserialization_with_no_vision_object_works(self) -> None:
        """Test that scenario item deserialization works without vision object."""
        data = {
            "Date": 20231201,
            "VisionObject": None,
            "Attribute": 1,
            "Value": 100.5,
            "Comment": "Test comment",
        }

        item = ScenarioMV.ScenarioItem.deserialize(data)

        self.assertEqual(item.date, 20231201)
        self.assertIsNone(item.vision_object)
        self.assertEqual(item.attribute, 1)
        self.assertEqual(item.value, 100.5)
        self.assertEqual(item.comment, "Test comment")


if __name__ == "__main__":
    unittest.main()
