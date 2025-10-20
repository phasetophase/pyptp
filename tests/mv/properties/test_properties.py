"""Tests for TPropertiesMS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.element_utils import Guid
from pyptp.elements.mixins import Extra, Note
from pyptp.elements.mv.properties import PropertiesMV
from pyptp.network_mv import NetworkMV


class TestPropertiesRegistration(unittest.TestCase):
    """Test properties registration and functionality."""

    def setUp(self) -> None:
        """Create a fresh network for testing."""
        self.network = NetworkMV()

    def test_properties_registration_works(self) -> None:
        """Test that properties can register themselves with the network."""
        system = PropertiesMV.System()
        network = PropertiesMV.Network()
        general = PropertiesMV.General()
        invisible = PropertiesMV.Invisible()
        history = PropertiesMV.History()

        properties = PropertiesMV(system, network, general, invisible, history)
        properties.register(self.network)

        # Verify properties is in network
        self.assertIs(self.network.properties, properties)

    def test_properties_with_full_properties_serializes_correctly(self) -> None:
        """Test that properties with all properties serialize correctly."""
        system = PropertiesMV.System(currency="USD")

        network_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))
        state_guid = Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5"))
        previous_state_guid = Guid(UUID("aec2228f-a78e-4f54-9ed2-0a7dbd48b3f6"))

        network = PropertiesMV.Network(
            guid=network_guid,
            state=state_guid,
            previous_state=previous_state_guid,
            last_saved_datetime=1234567890.0,
        )

        general = PropertiesMV.General(
            customer="TestCustomer",
            place="TestPlace",
            region="TestRegion",
            country="TestCountry",
            date=1234567890.0,
            project="TestProject",
            description="Test Description",
            version="1.0.0",
            state="Active",
            by="TestUser",
        )

        invisible = PropertiesMV.Invisible(property=["prop1", "prop2"])
        history = PropertiesMV.History(ask=True, always=True)

        properties = PropertiesMV(system, network, general, invisible, history)
        properties.extras.append(Extra(text="foo=bar"))
        properties.notes.append(Note(text="Test note"))
        properties.register(self.network)

        # Test serialization
        serialized = properties.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#System"), 1)
        self.assertEqual(serialized.count("#Network"), 1)
        self.assertEqual(serialized.count("#General"), 1)
        self.assertEqual(serialized.count("#Invisible"), 1)
        self.assertEqual(serialized.count("#History "), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify system properties
        self.assertIn("Currency:'USD'", serialized)

        # Verify network properties
        self.assertIn(f"GUID:'{{{str(network_guid).upper()}}}'", serialized)
        self.assertIn(f"State:'{{{str(state_guid).upper()}}}'", serialized)
        self.assertIn(
            f"PreviousState:'{{{str(previous_state_guid).upper()}}}'", serialized
        )
        self.assertIn("SaveDateTime:1234567890", serialized)

        # Verify general properties
        self.assertIn("Customer:'TestCustomer'", serialized)
        self.assertIn("Place:'TestPlace'", serialized)
        self.assertIn("Region:'TestRegion'", serialized)
        self.assertIn("Country:'TestCountry'", serialized)
        self.assertIn("Date:1234567890", serialized)
        self.assertIn("Project:'TestProject'", serialized)
        self.assertIn("Description:'Test Description'", serialized)
        self.assertIn("Version:'1.0.0'", serialized)
        self.assertIn("State:'Active'", serialized)
        self.assertIn("By:'TestUser'", serialized)

        # Verify invisible properties
        self.assertIn("Property0:'prop1'", serialized)
        self.assertIn("Property1:'prop2'", serialized)

        # Verify history properties
        self.assertIn("Ask:True", serialized)
        self.assertIn("Always:True", serialized)

        # Verify extras and notes
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering properties overwrites the existing one."""
        system1 = PropertiesMV.System(currency="USD")
        network1 = PropertiesMV.Network()
        general1 = PropertiesMV.General(customer="First")
        invisible1 = PropertiesMV.Invisible()
        history1 = PropertiesMV.History()

        properties1 = PropertiesMV(system1, network1, general1, invisible1, history1)
        properties1.register(self.network)

        system2 = PropertiesMV.System(currency="EUR")
        network2 = PropertiesMV.Network()
        general2 = PropertiesMV.General(customer="Second")
        invisible2 = PropertiesMV.Invisible()
        history2 = PropertiesMV.History()

        properties2 = PropertiesMV(system2, network2, general2, invisible2, history2)
        properties2.register(self.network)

        # Should be the second properties
        if self.network.properties.general:
            self.assertEqual(self.network.properties.general.customer, "Second")
        self.assertEqual(self.network.properties.system.currency, "EUR")

    def test_minimal_properties_serialization(self) -> None:
        """Test that minimal properties serialize correctly with only required fields."""
        system = PropertiesMV.System()
        network = PropertiesMV.Network()
        general = PropertiesMV.General()
        invisible = PropertiesMV.Invisible()
        history = PropertiesMV.History()

        properties = PropertiesMV(system, network, general, invisible, history)
        properties.register(self.network)

        serialized = properties.serialize()

        # Should have all sections
        self.assertEqual(serialized.count("#System"), 1)
        self.assertEqual(serialized.count("#Network"), 1)
        self.assertEqual(serialized.count("#General"), 1)
        self.assertEqual(serialized.count("#Invisible"), 1)
        self.assertEqual(serialized.count("#History "), 1)

        # Should have default values
        self.assertIn("Currency:'EUR'", serialized)
        self.assertIn("SaveDateTime:0", serialized)
        self.assertNotIn("Date:", serialized)  # 0.0 values are skipped
        self.assertNotIn("By:", serialized)  # 'PyPtP' is default and skipped
        self.assertNotIn("Ask:", serialized)  # False values are skipped
        self.assertNotIn("Always:", serialized)  # False values are skipped

    def test_properties_with_system_currency_serializes_correctly(self) -> None:
        """Test that properties with system currency serialize correctly."""
        system = PropertiesMV.System(currency="USD")
        network = PropertiesMV.Network()
        general = PropertiesMV.General()
        invisible = PropertiesMV.Invisible()
        history = PropertiesMV.History()

        properties = PropertiesMV(system, network, general, invisible, history)
        properties.register(self.network)

        serialized = properties.serialize()
        self.assertIn("Currency:'USD'", serialized)

    def test_properties_with_network_guids_serializes_correctly(self) -> None:
        """Test that properties with network GUIDs serialize correctly."""
        system = PropertiesMV.System()

        network_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))
        state_guid = Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5"))
        previous_state_guid = Guid(UUID("aec2228f-a78e-4f54-9ed2-0a7dbd48b3f6"))

        network = PropertiesMV.Network(
            guid=network_guid,
            state=state_guid,
            previous_state=previous_state_guid,
            last_saved_datetime=1234567890.0,
        )

        general = PropertiesMV.General()
        invisible = PropertiesMV.Invisible()
        history = PropertiesMV.History()

        properties = PropertiesMV(system, network, general, invisible, history)
        properties.register(self.network)

        serialized = properties.serialize()
        self.assertIn(f"GUID:'{{{str(network_guid).upper()}}}'", serialized)
        self.assertIn(f"State:'{{{str(state_guid).upper()}}}'", serialized)
        self.assertIn(
            f"PreviousState:'{{{str(previous_state_guid).upper()}}}'", serialized
        )
        self.assertIn("SaveDateTime:1234567890", serialized)

    def test_properties_with_general_info_serializes_correctly(self) -> None:
        """Test that properties with general info serialize correctly."""
        system = PropertiesMV.System()
        network = PropertiesMV.Network()

        general = PropertiesMV.General(
            customer="TestCustomer",
            place="TestPlace",
            region="TestRegion",
            country="TestCountry",
            date=1234567890.0,
            project="TestProject",
            description="Test Description",
            version="1.0.0",
            state="Active",
            by="TestUser",
        )

        invisible = PropertiesMV.Invisible()
        history = PropertiesMV.History()

        properties = PropertiesMV(system, network, general, invisible, history)
        properties.register(self.network)

        serialized = properties.serialize()
        self.assertIn("Customer:'TestCustomer'", serialized)
        self.assertIn("Place:'TestPlace'", serialized)
        self.assertIn("Region:'TestRegion'", serialized)
        self.assertIn("Country:'TestCountry'", serialized)
        self.assertIn("Date:1234567890", serialized)
        self.assertIn("Project:'TestProject'", serialized)
        self.assertIn("Description:'Test Description'", serialized)
        self.assertIn("Version:'1.0.0'", serialized)
        self.assertIn("State:'Active'", serialized)
        self.assertIn("By:'TestUser'", serialized)

    def test_properties_with_invisible_properties_serializes_correctly(self) -> None:
        """Test that properties with invisible properties serialize correctly."""
        system = PropertiesMV.System()
        network = PropertiesMV.Network()
        general = PropertiesMV.General()
        invisible = PropertiesMV.Invisible(property=["prop1", "prop2", "prop3"])
        history = PropertiesMV.History()

        properties = PropertiesMV(system, network, general, invisible, history)
        properties.register(self.network)

        serialized = properties.serialize()
        self.assertIn("Property0:'prop1'", serialized)
        self.assertIn("Property1:'prop2'", serialized)
        self.assertIn("Property2:'prop3'", serialized)

    def test_properties_with_history_flags_serializes_correctly(self) -> None:
        """Test that properties with history flags serialize correctly."""
        system = PropertiesMV.System()
        network = PropertiesMV.Network()
        general = PropertiesMV.General()
        invisible = PropertiesMV.Invisible()
        history = PropertiesMV.History(ask=True, always=True)

        properties = PropertiesMV(system, network, general, invisible, history)
        properties.register(self.network)

        serialized = properties.serialize()
        self.assertIn("Ask:True", serialized)
        self.assertIn("Always:True", serialized)


if __name__ == "__main__":
    unittest.main()
