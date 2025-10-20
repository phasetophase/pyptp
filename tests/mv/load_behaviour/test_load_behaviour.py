"""Tests for TLoadBehaviourMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.element_utils import Guid
from pyptp.elements.mv.load_behaviour import LoadBehaviourMV
from pyptp.network_mv import NetworkMV


class TestLoadBehaviourRegistration(unittest.TestCase):
    """Test load behaviour registration and functionality."""

    def setUp(self) -> None:
        """Create a fresh network for testing."""
        self.network = NetworkMV()
        self.load_behaviour_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))

    def test_load_behaviour_registration_works(self) -> None:
        """Test that load behaviours can register themselves with the network."""
        general = LoadBehaviourMV.General(
            guid=self.load_behaviour_guid, name="TestLoadBehaviour"
        )

        load_behaviour = LoadBehaviourMV(general)
        load_behaviour.register(self.network)

        # Verify load behaviour is in network
        self.assertIn(self.load_behaviour_guid, self.network.load_behaviours)
        self.assertIs(
            self.network.load_behaviours[self.load_behaviour_guid], load_behaviour
        )

    def test_load_behaviour_with_full_properties_serializes_correctly(self) -> None:
        """Test that load behaviours with all properties serialize correctly."""
        general = LoadBehaviourMV.General(
            guid=self.load_behaviour_guid,
            name="FullLoadBehaviour",
            constant_p=1,
            constant_q=1,
        )

        load_behaviour = LoadBehaviourMV(general)
        load_behaviour.register(self.network)

        # Test serialization
        serialized = load_behaviour.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)

        # Verify general properties
        self.assertIn("Name:'FullLoadBehaviour'", serialized)
        self.assertIn(f"GUID:'{{{str(self.load_behaviour_guid).upper()}}}'", serialized)
        self.assertIn("ConstantP:1", serialized)
        self.assertIn("ConstantQ:1", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a load behaviour with the same GUID overwrites the existing one."""
        general1 = LoadBehaviourMV.General(
            guid=self.load_behaviour_guid, name="FirstLoadBehaviour"
        )
        load_behaviour1 = LoadBehaviourMV(general1)
        load_behaviour1.register(self.network)

        general2 = LoadBehaviourMV.General(
            guid=self.load_behaviour_guid, name="SecondLoadBehaviour"
        )
        load_behaviour2 = LoadBehaviourMV(general2)
        load_behaviour2.register(self.network)

        # Should only have one load behaviour
        self.assertEqual(len(self.network.load_behaviours), 1)
        # Should be the second load behaviour
        self.assertEqual(
            self.network.load_behaviours[self.load_behaviour_guid].general.name,
            "SecondLoadBehaviour",
        )

    def test_minimal_load_behaviour_serialization(self) -> None:
        """Test that minimal load behaviours serialize correctly with only required fields."""
        general = LoadBehaviourMV.General(
            guid=self.load_behaviour_guid, name="MinimalLoadBehaviour"
        )

        load_behaviour = LoadBehaviourMV(general)
        load_behaviour.register(self.network)

        serialized = load_behaviour.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)

        # Should have basic properties
        self.assertIn("Name:'MinimalLoadBehaviour'", serialized)
        self.assertIn(f"GUID:'{{{str(self.load_behaviour_guid).upper()}}}'", serialized)

        # ConstantP and ConstantQ are 0, which is the default skip value, so they won't appear
        self.assertNotIn("ConstantP:0", serialized)
        self.assertNotIn("ConstantQ:0", serialized)

    def test_load_behaviour_with_constant_p_serializes_correctly(self) -> None:
        """Test that load behaviours with constant P serialize correctly."""
        general = LoadBehaviourMV.General(
            guid=self.load_behaviour_guid,
            name="ConstantPLoadBehaviour",
            constant_p=1,
        )

        load_behaviour = LoadBehaviourMV(general)
        load_behaviour.register(self.network)

        serialized = load_behaviour.serialize()
        self.assertIn("ConstantP:1", serialized)

    def test_load_behaviour_with_constant_q_serializes_correctly(self) -> None:
        """Test that load behaviours with constant Q serialize correctly."""
        general = LoadBehaviourMV.General(
            guid=self.load_behaviour_guid,
            name="ConstantQLoadBehaviour",
            constant_q=1,
        )

        load_behaviour = LoadBehaviourMV(general)
        load_behaviour.register(self.network)

        serialized = load_behaviour.serialize()
        self.assertIn("ConstantQ:1", serialized)


if __name__ == "__main__":
    unittest.main()
