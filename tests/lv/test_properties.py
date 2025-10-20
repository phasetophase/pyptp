"""Tests for TPropertiesLS class."""

from __future__ import annotations

import unittest
from uuid import uuid4

from pyptp.elements.element_utils import Guid, encode_guid
from pyptp.elements.lv.properties import PropertiesLV
from pyptp.network_lv import NetworkLV


class TestTPropertiesLS(unittest.TestCase):
    """Test TPropertiesLS registration and serialization behavior."""

    def setUp(self) -> None:
        """Create fresh network and dependencies for isolated testing."""
        self.network = NetworkLV()
        self.test_guid = Guid(uuid4())
        self.test_state_guid = Guid(uuid4())
        self.test_previous_state_guid = Guid(uuid4())

    def test_properties_registration_works(self) -> None:
        """Verify basic properties registration in network."""
        system = PropertiesLV.System(currency="USD")
        properties = PropertiesLV(system=system)

        # Verify network starts with default properties
        self.assertIsNotNone(self.network.properties)
        original_properties = self.network.properties

        # Register new properties
        properties.register(self.network)

        # Verify properties were replaced
        self.assertEqual(self.network.properties, properties)
        self.assertNotEqual(self.network.properties, original_properties)

    def test_properties_with_minimal_properties_serializes_correctly(self) -> None:
        """Test serialization with minimal properties."""
        system = PropertiesLV.System()
        properties = PropertiesLV(system=system)

        result = properties.serialize()

        # Should contain system line with default currency
        self.assertIn("#System", result)
        self.assertIn("Currency:'EUR'", result)

        # Should not contain optional sections
        self.assertNotIn("#Network", result)
        self.assertNotIn("#General", result)
        self.assertNotIn("#History", result)
        self.assertNotIn("#HistoryItems", result)
        self.assertNotIn("#Users", result)

    def test_properties_with_full_properties_serializes_correctly(self) -> None:
        """Test serialization with all properties set."""
        system = PropertiesLV.System(currency="USD")
        network = PropertiesLV.Network(
            guid=self.test_guid,
            state=self.test_state_guid,
            previous_state=self.test_previous_state_guid,
            save_datetime=1234567890.5,
        )
        general = PropertiesLV.General(
            customer="Test Customer",
            place="Test Place",
            region="Test Region",
            country="Test Country",
            date=20240101.0,
            project="Test Project",
            description="Test Description",
            version="1.0.0",
            state="Development",
            by="Test User",
        )
        history = PropertiesLV.History(ask=True, always=False)
        history_items = PropertiesLV.HistoryItems(Text=["Item 1", "Item 2", "Item 3"])
        users = PropertiesLV.Users(User=["User1", "User2", "User3"])

        properties = PropertiesLV(
            system=system,
            network=network,
            general=general,
            history=history,
            history_items=history_items,
            users=users,
        )

        result = properties.serialize()

        # Verify system section
        self.assertIn("#System", result)
        self.assertIn("Currency:'USD'", result)

        # Verify network section
        self.assertIn("#Network", result)
        self.assertIn(f"GUID:{encode_guid(self.test_guid)}", result)
        self.assertIn(f"State:{encode_guid(self.test_state_guid)}", result)
        self.assertIn(
            f"PreviousState:{encode_guid(self.test_previous_state_guid)}", result
        )
        self.assertIn("SaveDateTime:1234567890.5", result)

        # Verify general section
        self.assertIn("#General", result)
        self.assertIn("Customer:'Test Customer'", result)
        self.assertIn("Place:'Test Place'", result)
        self.assertIn("Region:'Test Region'", result)
        self.assertIn("Country:'Test Country'", result)
        self.assertIn("Date:20240101", result)
        self.assertIn("Project:'Test Project'", result)
        self.assertIn("Description:'Test Description'", result)
        self.assertIn("Version:'1.0.0'", result)
        self.assertIn("State:'Development'", result)
        self.assertIn("By:'Test User'", result)

        # Verify history section
        self.assertIn("#History", result)
        self.assertIn("Ask:True", result)
        # Always:False is skipped when False

        # Verify history items section
        self.assertIn("#HistoryItems", result)
        self.assertIn("Text0:'Item 1'", result)
        self.assertIn("Text1:'Item 2'", result)
        self.assertIn("Text2:'Item 3'", result)

        # Verify users section
        self.assertIn("#Users", result)
        self.assertIn("User0:'User1'", result)
        self.assertIn("User1:'User2'", result)
        self.assertIn("User2:'User3'", result)

    def test_properties_deserialization_works(self) -> None:
        """Test deserialization from GNF format data."""
        data = {
            "system": [{"Currency": "GBP"}],
            "network": [
                {
                    "GUID": str(self.test_guid),
                    "State": str(self.test_state_guid),
                    "PreviousState": str(self.test_previous_state_guid),
                    "SaveDateTime": 1234567890.0,
                }
            ],
            "general": [
                {
                    "Customer": "Deserialized Customer",
                    "Place": "Deserialized Place",
                    "Region": "Deserialized Region",
                    "Country": "Deserialized Country",
                    "Date": 20240201.0,
                    "Project": "Deserialized Project",
                    "Description": "Deserialized Description",
                    "Version": "2.0.0",
                    "State": "Production",
                    "By": "Deserialized User",
                }
            ],
            "history": [{"Ask": True, "Always": True}],
            "historyItems": [{"Text0": "History Item 1", "Text1": "History Item 2"}],
            "users": [{"User0": "TestUser1", "User1": "TestUser2"}],
        }

        properties = PropertiesLV.deserialize(data)

        # Verify system properties
        self.assertIsNotNone(properties.system)
        self.assertEqual(properties.system.currency, "GBP")

        # Verify network properties
        self.assertIsNotNone(properties.network)
        if properties.network:
            self.assertEqual(properties.network.guid, self.test_guid)
            self.assertEqual(properties.network.state, self.test_state_guid)
            self.assertEqual(
                properties.network.previous_state, self.test_previous_state_guid
            )
            self.assertEqual(properties.network.save_datetime, 1234567890.0)

        # Verify general properties
        self.assertIsNotNone(properties.general)
        if properties.general:
            self.assertEqual(properties.general.customer, "Deserialized Customer")
            self.assertEqual(properties.general.place, "Deserialized Place")
            self.assertEqual(properties.general.region, "Deserialized Region")
            self.assertEqual(properties.general.country, "Deserialized Country")
            self.assertEqual(properties.general.date, 20240201.0)
            self.assertEqual(properties.general.project, "Deserialized Project")
            self.assertEqual(properties.general.description, "Deserialized Description")
            self.assertEqual(properties.general.version, "2.0.0")
            self.assertEqual(properties.general.state, "Production")
            self.assertEqual(properties.general.by, "Deserialized User")

        # Verify history properties
        self.assertIsNotNone(properties.history)
        if properties.history:
            self.assertEqual(properties.history.ask, True)
            self.assertEqual(properties.history.always, True)

        # Verify history items
        self.assertIsNotNone(properties.history_items)
        if properties.history_items:
            self.assertEqual(
                properties.history_items.Text, ["History Item 1", "History Item 2"]
            )

        # Verify users
        self.assertIsNotNone(properties.users)
        if properties.users:
            self.assertEqual(properties.users.User, ["TestUser1", "TestUser2"])

    def test_properties_deserialization_with_empty_data(self) -> None:
        """Test deserialization with empty data."""
        data = {}

        properties = PropertiesLV.deserialize(data)

        # Should have default system properties
        self.assertIsNotNone(properties.system)
        self.assertEqual(properties.system.currency, "EUR")

        # Should have None for optional sections
        self.assertIsNone(properties.network)
        self.assertIsNone(properties.general)
        self.assertIsNone(properties.history)
        self.assertIsNone(properties.history_items)
        self.assertIsNone(properties.users)

    def test_system_serialize_with_default_currency(self) -> None:
        """Test System class serialization with default currency."""
        system = PropertiesLV.System()

        result = system.serialize()

        self.assertIn("Currency:'EUR'", result)

    def test_system_serialize_with_custom_currency(self) -> None:
        """Test System class serialization with custom currency."""
        system = PropertiesLV.System(currency="USD")

        result = system.serialize()

        self.assertIn("Currency:'USD'", result)

    def test_network_serialize_with_defaults(self) -> None:
        """Test Network class serialization with default values."""
        network = PropertiesLV.Network(guid=self.test_guid, state=self.test_state_guid)

        result = network.serialize()

        # Should include required fields
        self.assertIn(f"GUID:{encode_guid(self.test_guid)}", result)
        self.assertIn(f"State:{encode_guid(self.test_state_guid)}", result)

        # Should skip default values
        self.assertNotIn("PreviousState:", result)  # None should be skipped
        self.assertNotIn("SaveDateTime:", result)  # 0 should be skipped

    def test_network_serialize_with_previous_state(self) -> None:
        """Test Network class serialization with PreviousState set."""
        network = PropertiesLV.Network(
            guid=self.test_guid,
            state=self.test_state_guid,
            previous_state=self.test_previous_state_guid,
            save_datetime=1234567890.5,
        )

        result = network.serialize()

        # Should include all fields
        self.assertIn(f"GUID:{encode_guid(self.test_guid)}", result)
        self.assertIn(
            f"PreviousState:{encode_guid(self.test_previous_state_guid)}", result
        )
        self.assertIn(f"State:{encode_guid(self.test_state_guid)}", result)
        self.assertIn("SaveDateTime:1234567890.5", result)

    def test_general_serialize_with_empty_strings(self) -> None:
        """Test General class serialization with empty strings."""
        general = PropertiesLV.General()

        result = general.serialize()

        # Should skip empty strings
        self.assertNotIn("Customer:", result)
        self.assertNotIn("Place:", result)
        self.assertNotIn("Region:", result)
        self.assertNotIn("Country:", result)
        self.assertNotIn("Date:", result)  # 0 should be skipped
        self.assertNotIn("Project:", result)
        self.assertNotIn("Description:", result)
        self.assertNotIn("Version:", result)
        self.assertNotIn("State:", result)
        self.assertNotIn("By:", result)

    def test_general_serialize_with_values(self) -> None:
        """Test General class serialization with values."""
        general = PropertiesLV.General(
            customer="Test Customer",
            place="Test Place",
            region="Test Region",
            country="Test Country",
            date=20240101.0,
            project="Test Project",
            description="Test Description",
            version="1.0.0",
            state="Development",
            by="Test User",
        )

        result = general.serialize()

        self.assertIn("Customer:'Test Customer'", result)
        self.assertIn("Place:'Test Place'", result)
        self.assertIn("Region:'Test Region'", result)
        self.assertIn("Country:'Test Country'", result)
        self.assertIn("Date:20240101", result)
        self.assertIn("Project:'Test Project'", result)
        self.assertIn("Description:'Test Description'", result)
        self.assertIn("Version:'1.0.0'", result)
        self.assertIn("State:'Development'", result)
        self.assertIn("By:'Test User'", result)

    def test_invisible_serialize_with_empty_list(self) -> None:
        """Test Invisible class serialization with empty list."""
        invisible = PropertiesLV.Invisible()

        result = invisible.serialize()

        # Should be empty string for empty list
        self.assertEqual(result, "")

    def test_invisible_serialize_with_properties(self) -> None:
        """Test Invisible class serialization with properties."""
        invisible = PropertiesLV.Invisible(Property=["Prop1", "Prop2", "Prop3"])

        result = invisible.serialize()

        self.assertIn("Property0:'Prop1'", result)
        self.assertIn("Property1:'Prop2'", result)
        self.assertIn("Property2:'Prop3'", result)

    def test_invisible_deserialize_with_properties(self) -> None:
        """Test Invisible class deserialization with properties."""
        data = {"Property0": "Prop1", "Property1": "Prop2", "Property2": "Prop3"}

        invisible = PropertiesLV.Invisible.deserialize(data)

        self.assertEqual(invisible.Property, ["Prop1", "Prop2", "Prop3"])

    def test_invisible_deserialize_with_gap_in_properties(self) -> None:
        """Test Invisible class deserialization with gap in properties."""
        data = {
            "Property0": "Prop1",
            "Property1": "Prop2",
            "Property3": "Prop4",
        }  # Property2 is missing

        invisible = PropertiesLV.Invisible.deserialize(data)

        # Should stop at first missing property
        self.assertEqual(invisible.Property, ["Prop1", "Prop2"])

    def test_history_serialize_with_defaults(self) -> None:
        """Test History class serialization with default values."""
        history = PropertiesLV.History()

        result = history.serialize()

        # Default False values are skipped, resulting in empty string
        self.assertEqual(result, "")

    def test_history_serialize_with_values(self) -> None:
        """Test History class serialization with values."""
        history = PropertiesLV.History(ask=True, always=True)

        result = history.serialize()

        self.assertIn("Ask:True", result)
        self.assertIn("Always:True", result)

    def test_history_serialize_with_mixed_values(self) -> None:
        """Test History class serialization with mixed boolean values."""
        # Test Ask=True, Always=False
        history = PropertiesLV.History(ask=True, always=False)
        result = history.serialize()
        self.assertIn("Ask:True", result)
        self.assertNotIn("Always:", result)  # False is skipped

        # Test Ask=False, Always=True
        history = PropertiesLV.History(ask=False, always=True)
        result = history.serialize()
        self.assertNotIn("Ask:", result)  # False is skipped
        self.assertIn("Always:True", result)

    def test_history_items_serialize_with_empty_list(self) -> None:
        """Test HistoryItems class serialization with empty list."""
        history_items = PropertiesLV.HistoryItems()

        result = history_items.serialize()

        # Should be empty string for empty list
        self.assertEqual(result, "")

    def test_history_items_serialize_with_texts(self) -> None:
        """Test HistoryItems class serialization with texts."""
        history_items = PropertiesLV.HistoryItems(Text=["Text1", "Text2", "Text3"])

        result = history_items.serialize()

        self.assertIn("Text0:'Text1'", result)
        self.assertIn("Text1:'Text2'", result)
        self.assertIn("Text2:'Text3'", result)

    def test_history_items_deserialize_with_texts(self) -> None:
        """Test HistoryItems class deserialization with texts."""
        data = {"Text0": "Text1", "Text1": "Text2", "Text2": "Text3"}

        history_items = PropertiesLV.HistoryItems.deserialize(data)

        self.assertEqual(history_items.Text, ["Text1", "Text2", "Text3"])

    def test_users_serialize_with_empty_list(self) -> None:
        """Test Users class serialization with empty list."""
        users = PropertiesLV.Users()

        result = users.serialize()

        # Should be empty string for empty list
        self.assertEqual(result, "")

    def test_users_serialize_with_users(self) -> None:
        """Test Users class serialization with users."""
        users = PropertiesLV.Users(User=["User1", "User2", "User3"])

        result = users.serialize()

        self.assertIn("User0:'User1'", result)
        self.assertIn("User1:'User2'", result)
        self.assertIn("User2:'User3'", result)

    def test_users_deserialize_with_users(self) -> None:
        """Test Users class deserialization with users."""
        data = {"User0": "User1", "User1": "User2", "User2": "User3"}

        users = PropertiesLV.Users.deserialize(data)

        self.assertEqual(users.User, ["User1", "User2", "User3"])

    def test_properties_round_trip_serialization(self) -> None:
        """Test that serialization and deserialization are consistent."""
        original_system = PropertiesLV.System(currency="USD")
        original_network = PropertiesLV.Network(
            guid=self.test_guid,
            state=self.test_state_guid,
            previous_state=self.test_previous_state_guid,
            save_datetime=1234567890.0,
        )
        original_general = PropertiesLV.General(
            customer="Round Trip Customer",
            place="Round Trip Place",
            region="Round Trip Region",
            country="Round Trip Country",
            date=20240101.0,
            project="Round Trip Project",
            description="Round Trip Description",
            version="1.0.0",
            state="Development",
            by="Round Trip User",
        )
        original_history = PropertiesLV.History(ask=True, always=False)
        original_history_items = PropertiesLV.HistoryItems(Text=["Item 1", "Item 2"])
        original_users = PropertiesLV.Users(User=["User1", "User2"])

        original_properties = PropertiesLV(
            system=original_system,
            network=original_network,
            general=original_general,
            history=original_history,
            history_items=original_history_items,
            users=original_users,
        )

        original_properties.serialize()

        # Simulate parsing back from GNF format
        data = {
            "system": [{"Currency": "USD"}],
            "network": [
                {
                    "GUID": str(self.test_guid),
                    "State": str(self.test_state_guid),
                    "PreviousState": str(self.test_previous_state_guid),
                    "SaveDateTime": 1234567890.0,
                }
            ],
            "general": [
                {
                    "Customer": "Round Trip Customer",
                    "Place": "Round Trip Place",
                    "Region": "Round Trip Region",
                    "Country": "Round Trip Country",
                    "Date": 20240101.0,
                    "Project": "Round Trip Project",
                    "Description": "Round Trip Description",
                    "Version": "1.0.0",
                    "State": "Development",
                    "By": "Round Trip User",
                }
            ],
            "history": [{"Ask": True, "Always": False}],
            "historyItems": [{"Text0": "Item 1", "Text1": "Item 2"}],
            "users": [{"User0": "User1", "User1": "User2"}],
        }

        deserialized = PropertiesLV.deserialize(data)

        # Verify key properties match
        self.assertEqual(
            deserialized.system.currency, original_properties.system.currency
        )
        if deserialized.network and original_properties.network:
            self.assertEqual(
                deserialized.network.guid, original_properties.network.guid
            )
            self.assertEqual(
                deserialized.network.state, original_properties.network.state
            )
            self.assertEqual(
                deserialized.network.previous_state,
                original_properties.network.previous_state,
            )
            self.assertEqual(
                deserialized.network.save_datetime,
                original_properties.network.save_datetime,
            )

        # Verify general properties
        if deserialized.general and original_properties.general:
            self.assertEqual(
                deserialized.general.customer, original_properties.general.customer
            )
            self.assertEqual(
                deserialized.general.place, original_properties.general.place
            )
            self.assertEqual(
                deserialized.general.region, original_properties.general.region
            )
            self.assertEqual(
                deserialized.general.country, original_properties.general.country
            )
            self.assertEqual(
                deserialized.general.date, original_properties.general.date
            )
            self.assertEqual(
                deserialized.general.project, original_properties.general.project
            )
            self.assertEqual(
                deserialized.general.description,
                original_properties.general.description,
            )
            self.assertEqual(
                deserialized.general.version, original_properties.general.version
            )
            self.assertEqual(
                deserialized.general.state, original_properties.general.state
            )
            self.assertEqual(deserialized.general.by, original_properties.general.by)

        # Verify other sections
        if (
            deserialized.history
            and original_properties.history
            and deserialized.history_items
            and original_properties.history_items
            and deserialized.users
            and original_properties.users
        ):
            self.assertEqual(deserialized.history.ask, original_properties.history.ask)
            self.assertEqual(
                deserialized.history.always, original_properties.history.always
            )
            self.assertEqual(
                deserialized.history_items.Text, original_properties.history_items.Text
            )
            self.assertEqual(deserialized.users.User, original_properties.users.User)


if __name__ == "__main__":
    unittest.main()
