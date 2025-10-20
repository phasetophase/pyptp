"""Tests for TCircuitBreakerLS behavior using the new registration system."""

import unittest
from uuid import UUID

from pyptp.elements.color_utils import DelphiColor
from pyptp.elements.element_utils import Guid
from pyptp.elements.lv.circuit_breaker import CircuitBreakerLV
from pyptp.elements.lv.presentations import SecundairPresentation
from pyptp.elements.lv.shared import Fields
from pyptp.elements.mixins import Extra, Note
from pyptp.network_lv import NetworkLV


class TestCircuitBreakerRegistration(unittest.TestCase):
    """Test circuit breaker registration and functionality."""

    def setUp(self) -> None:
        """Create a fresh network for testing."""
        self.network = NetworkLV()
        self.circuit_breaker_guid = Guid(UUID("6301d096-5f64-46f3-b50c-b6717a4ea14c"))
        self.in_object_guid = Guid(UUID("fec2228f-a78e-4f54-9ed2-0a7dbd48b3f5"))

    def test_circuit_breaker_registration_works(self) -> None:
        """Test that circuit breakers can register themselves with the network."""
        general = CircuitBreakerLV.General(
            guid=self.circuit_breaker_guid,
            name="TestCircuitBreaker",
            in_object=self.in_object_guid,
        )
        presentation = SecundairPresentation()

        circuit_breaker = CircuitBreakerLV(general, [presentation])
        circuit_breaker.register(self.network)

        # Verify circuit breaker is in network
        self.assertIn(self.circuit_breaker_guid, self.network.circuit_breakers)
        self.assertIs(
            self.network.circuit_breakers[self.circuit_breaker_guid], circuit_breaker
        )

    def test_circuit_breaker_with_full_properties_serializes_correctly(self) -> None:
        """Test that circuit breakers with all properties serialize correctly."""
        general = CircuitBreakerLV.General(
            guid=self.circuit_breaker_guid,
            creation_time=123.45,
            mutation_date=10,
            revision_date=20.5,
            name="FullCircuitBreaker",
            in_object=self.in_object_guid,
            side=2,
            standardizable=False,
            type="ThermalMagnetic",
            current_protection1_present=True,
            current_protection1_type="Thermal",
            voltage_protection_present=True,
            voltage_protection_type="Undervoltage",
            earth_fault_protection1_present=True,
        )

        presentation = SecundairPresentation(
            distance=50,
            otherside=True,
            color=DelphiColor("$00FF00"),
            size=2,
            width=3,
            text_color=DelphiColor("$FF0000"),
            text_size=12,
            font="Arial",
            text_style=1,
            no_text=True,
            upside_down_text=True,
            strings_x=10,
            strings_y=20,
            note_x=30,
            note_y=40,
        )

        circuit_breaker = CircuitBreakerLV(general, [presentation])
        circuit_breaker.fields = Fields(values=["A", "B", "C"])
        circuit_breaker.extras.append(Extra(text="foo=bar"))
        circuit_breaker.notes.append(Note(text="Test note"))
        circuit_breaker.register(self.network)

        # Test serialization
        serialized = circuit_breaker.serialize()

        # Verify all sections are present
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#Fields", serialized)
        self.assertGreaterEqual(serialized.count("#Presentation"), 1)
        self.assertGreaterEqual(serialized.count("#Extra"), 1)
        self.assertGreaterEqual(serialized.count("#Note"), 1)

        # Verify key general properties are serialized
        self.assertIn("Name:'FullCircuitBreaker'", serialized)
        self.assertIn(f"InObject:'{{{str(self.in_object_guid).upper()}}}'", serialized)
        self.assertIn("Side:2", serialized)
        self.assertNotIn("Standardizable:", serialized)  # False values are skipped
        self.assertIn("CircuitBreakerType:'ThermalMagnetic'", serialized)
        self.assertIn("CurrentProtection1Present:True", serialized)
        self.assertIn("CurrentProtection1Type:'Thermal'", serialized)
        self.assertIn("VoltageProtectionPresent:True", serialized)
        self.assertIn("VoltageProtectionType:'Undervoltage'", serialized)
        self.assertIn("EarthFaultProtection1Present:True", serialized)

        # Verify presentation properties
        self.assertIn("Distance:50", serialized)
        self.assertIn("Otherside:True", serialized)
        self.assertIn("Color:$00FF00", serialized)
        self.assertIn("TextColor:$FF0000", serialized)
        self.assertIn("StringsX:10", serialized)
        self.assertIn("StringsY:20", serialized)
        self.assertIn("NoteX:30", serialized)
        self.assertIn("NoteY:40", serialized)

        # Verify fields, extras, and notes
        self.assertIn("#Fields Name0:'A' Name1:'B' Name2:'C'", serialized)
        self.assertIn("#Extra Text:foo=bar", serialized)
        self.assertIn("#Note Text:Test note", serialized)

    def test_duplicate_registration_overwrites(self) -> None:
        """Test that registering a circuit breaker with the same GUID overwrites the existing one."""
        general1 = CircuitBreakerLV.General(
            guid=self.circuit_breaker_guid,
            name="FirstCircuitBreaker",
            in_object=self.in_object_guid,
        )
        circuit_breaker1 = CircuitBreakerLV(general1, [SecundairPresentation()])
        circuit_breaker1.register(self.network)

        general2 = CircuitBreakerLV.General(
            guid=self.circuit_breaker_guid,
            name="SecondCircuitBreaker",
            in_object=self.in_object_guid,
        )
        circuit_breaker2 = CircuitBreakerLV(general2, [SecundairPresentation()])
        circuit_breaker2.register(self.network)

        # Should only have one circuit breaker
        self.assertEqual(len(self.network.circuit_breakers), 1)
        # Should be the second circuit breaker
        self.assertEqual(
            self.network.circuit_breakers[self.circuit_breaker_guid].general.name,
            "SecondCircuitBreaker",
        )

    def test_circuit_breaker_without_in_object_serializes_correctly(self) -> None:
        """Test that circuit breakers without InObject serialize correctly."""
        general = CircuitBreakerLV.General(
            guid=self.circuit_breaker_guid, name="NoInObjectCircuitBreaker"
        )
        presentation = SecundairPresentation()

        circuit_breaker = CircuitBreakerLV(general, [presentation])
        circuit_breaker.register(self.network)

        serialized = circuit_breaker.serialize()

        # Should not have InObject in serialization
        self.assertNotIn("InObject:", serialized)

        # Should have other properties
        self.assertIn("Name:'NoInObjectCircuitBreaker'", serialized)
        self.assertIn("Side:1", serialized)  # Default value

    def test_minimal_circuit_breaker_serialization(self) -> None:
        """Test that minimal circuit breakers serialize correctly with only required fields."""
        general = CircuitBreakerLV.General(
            guid=self.circuit_breaker_guid, name="MinimalCircuitBreaker"
        )
        presentation = SecundairPresentation()

        circuit_breaker = CircuitBreakerLV(general, [presentation])
        circuit_breaker.register(self.network)

        serialized = circuit_breaker.serialize()

        # Should have basic sections
        self.assertEqual(serialized.count("#General"), 1)
        self.assertIn("#Presentation", serialized)

        # Should have basic properties
        self.assertIn("Name:'MinimalCircuitBreaker'", serialized)
        self.assertIn("Side:1", serialized)  # Default value

        # Should not have optional sections
        self.assertNotIn("#Fields", serialized)
        self.assertNotIn("#Extra", serialized)
        self.assertNotIn("#Note", serialized)

    def test_multiple_presentations_serialize_correctly(self) -> None:
        """Test that circuit breakers with multiple presentations serialize correctly."""
        general = CircuitBreakerLV.General(
            guid=self.circuit_breaker_guid,
            name="MultiPresCircuitBreaker",
            in_object=self.in_object_guid,
        )

        pres1 = SecundairPresentation(distance=10, color=DelphiColor("$FF0000"))
        pres2 = SecundairPresentation(distance=20, color=DelphiColor("$00FF00"))

        circuit_breaker = CircuitBreakerLV(general, [pres1, pres2])
        circuit_breaker.register(self.network)

        serialized = circuit_breaker.serialize()

        # Should have two presentations
        self.assertEqual(serialized.count("#Presentation"), 2)
        self.assertIn("Color:$FF0000", serialized)
        self.assertIn("Color:$00FF00", serialized)
        self.assertIn("Distance:10", serialized)
        self.assertIn("Distance:20", serialized)

    def test_circuit_breaker_with_protection_settings_serializes_correctly(
        self,
    ) -> None:
        """Test that circuit breakers with protection settings serialize correctly."""
        general = CircuitBreakerLV.General(
            guid=self.circuit_breaker_guid,
            name="ProtectionCircuitBreaker",
            in_object=self.in_object_guid,
            type="Electronic",
            current_protection1_present=True,
            current_protection1_type="Electronic",
            voltage_protection_present=True,
            voltage_protection_type="Overvoltage",
            earth_fault_protection1_present=True,
        )
        presentation = SecundairPresentation()

        circuit_breaker = CircuitBreakerLV(general, [presentation])
        circuit_breaker.register(self.network)

        serialized = circuit_breaker.serialize()

        # Verify protection properties are serialized
        self.assertIn("CircuitBreakerType:'Electronic'", serialized)
        self.assertIn("CurrentProtection1Present:True", serialized)
        self.assertIn("CurrentProtection1Type:'Electronic'", serialized)
        self.assertIn("VoltageProtectionPresent:True", serialized)
        self.assertIn("VoltageProtectionType:'Overvoltage'", serialized)
        self.assertIn("EarthFaultProtection1Present:True", serialized)


if __name__ == "__main__":
    unittest.main()
