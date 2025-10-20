"""Tests for TRailsystemMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.element_utils import Guid
from pyptp.elements.mv.rails import RailSystemMV
from pyptp.network_mv import NetworkMV


class TestRailsRegistration(unittest.TestCase):
    """Test rails registration and functionality."""

    def setUp(self) -> None:
        """Create a fresh network for testing."""
        self.network = NetworkMV()
        self.rails_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))
        self.node_guid = Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5"))

    def test_rails_registration_works(self) -> None:
        """Test that rails can register themselves with the network."""
        general = RailSystemMV.General(guid=self.rails_guid, name="TestRails")
        node = RailSystemMV.Node(guid=self.node_guid)

        rails = RailSystemMV(general, [node])
        rails.register(self.network)

        # Verify rails is in network
        self.assertIn(self.rails_guid, self.network.rail_systems)
        self.assertIs(self.network.rail_systems[self.rails_guid], rails)

    def test_rails_with_full_properties_serializes_correctly(self) -> None:
        """Test that rails with all properties serialize correctly."""
        general = RailSystemMV.General(
            guid=self.rails_guid,
            name="FullRails",
        )

        node1 = RailSystemMV.Node(guid=self.node_guid)
        node2 = RailSystemMV.Node(
            guid=Guid(UUID("8b7d4c3e-2f1a-4e5d-9c8b-7a6f5e4d3c2b"))
        )

        rails = RailSystemMV(general, [node1, node2])
        rails.register(self.network)

        # Test serialization
        serialized = rails.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertEqual(serialized.count("#Node"), 2)

        # Verify general properties
        self.assertIn("Name:'FullRails'", serialized)
        self.assertIn(f"GUID:'{{{str(self.rails_guid).upper()}}}'", serialized)

        # Verify node properties
        self.assertIn(f"GUID:'{{{str(self.node_guid).upper()}}}'", serialized)
        self.assertIn("GUID:'{8B7D4C3E-2F1A-4E5D-9C8B-7A6F5E4D3C2B}'", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering rails with the same GUID overwrites the existing one."""
        general1 = RailSystemMV.General(guid=self.rails_guid, name="FirstRails")
        rails1 = RailSystemMV(general1, [])
        rails1.register(self.network)

        general2 = RailSystemMV.General(guid=self.rails_guid, name="SecondRails")
        rails2 = RailSystemMV(general2, [])
        rails2.register(self.network)

        # Should only have one rails
        self.assertEqual(len(self.network.rail_systems), 1)
        # Should be the second rails
        self.assertEqual(
            self.network.rail_systems[self.rails_guid].general.name, "SecondRails"
        )

    def test_minimal_rails_serialization(self) -> None:
        """Test that minimal rails serialize correctly with only required fields."""
        general = RailSystemMV.General(guid=self.rails_guid, name="MinimalRails")
        rails = RailSystemMV(general, [])
        rails.register(self.network)

        serialized = rails.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertEqual(serialized.count("#Node"), 0)

        # Should have basic properties
        self.assertIn("Name:'MinimalRails'", serialized)
        self.assertIn(f"GUID:'{{{str(self.rails_guid).upper()}}}'", serialized)

    def test_rails_with_multiple_nodes_serializes_correctly(self) -> None:
        """Test that rails with multiple nodes serialize correctly."""
        general = RailSystemMV.General(guid=self.rails_guid, name="MultiNodeRails")

        node1 = RailSystemMV.Node(guid=self.node_guid)
        node2 = RailSystemMV.Node(
            guid=Guid(UUID("8b7d4c3e-2f1a-4e5d-9c8b-7a6f5e4d3c2b"))
        )
        node3 = RailSystemMV.Node(
            guid=Guid(UUID("1a2b3c4d-5e6f-7890-abcd-ef1234567890"))
        )

        rails = RailSystemMV(general, [node1, node2, node3])
        rails.register(self.network)

        serialized = rails.serialize()

        # Should have all nodes
        self.assertEqual(serialized.count("#Node"), 3)
        self.assertIn(f"GUID:'{{{str(self.node_guid).upper()}}}'", serialized)
        self.assertIn("GUID:'{8B7D4C3E-2F1A-4E5D-9C8B-7A6F5E4D3C2B}'", serialized)
        self.assertIn("GUID:'{1A2B3C4D-5E6F-7890-ABCD-EF1234567890}'", serialized)

    def test_rails_with_empty_name_serializes_correctly(self) -> None:
        """Test that rails with empty name serialize correctly."""
        general = RailSystemMV.General(guid=self.rails_guid, name="")
        rails = RailSystemMV(general, [])
        rails.register(self.network)

        serialized = rails.serialize()
        # Empty name should be skipped
        self.assertIsNotNone(serialized)
        self.assertNotIn("Name:''", serialized)  # Empty name should not appear

    def test_rails_deserialization_works(self) -> None:
        """Test that rails can be deserialized correctly."""
        data = {
            "general": [
                {
                    "Name": "TestRails",
                    "GUID": str(self.rails_guid),
                }
            ],
            "nodes": [
                {"GUID": str(self.node_guid)},
                {"GUID": str(Guid(UUID("8b7d4c3e-2f1a-4e5d-9c8b-7a6f5e4d3c2b")))},
            ],
        }

        rails = RailSystemMV.deserialize(data)

        self.assertEqual(rails.general.name, "TestRails")
        self.assertEqual(rails.general.guid, self.rails_guid)
        self.assertEqual(len(rails.nodes), 2)
        self.assertEqual(rails.nodes[0].guid, self.node_guid)
        self.assertEqual(
            rails.nodes[1].guid, Guid(UUID("8b7d4c3e-2f1a-4e5d-9c8b-7a6f5e4d3c2b"))
        )

    def test_rails_deserialization_with_missing_data_works(self) -> None:
        """Test that rails deserialization works with missing data."""
        data = {}

        rails = RailSystemMV.deserialize(data)

        self.assertEqual(rails.general.name, "")
        self.assertEqual(len(rails.nodes), 0)

    def test_rails_node_serialization_works(self) -> None:
        """Test that rails node serialization works correctly."""
        node = RailSystemMV.Node(guid=self.node_guid)
        serialized = node.serialize()

        self.assertEqual(serialized, f"GUID:'{{{str(self.node_guid).upper()}}}'")

    def test_rails_general_serialization_works(self) -> None:
        """Test that rails general serialization works correctly."""
        general = RailSystemMV.General(guid=self.rails_guid, name="TestRails")
        serialized = general.serialize()

        self.assertIn("Name:'TestRails'", serialized)
        self.assertIn(f"GUID:'{{{str(self.rails_guid).upper()}}}'", serialized)


if __name__ == "__main__":
    unittest.main()
