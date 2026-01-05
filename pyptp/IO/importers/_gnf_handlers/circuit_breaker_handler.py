"""Handler for parsing GNF Circuit Breaker sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.lv.circuit_breaker import CircuitBreakerLV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_lv import NetworkLV


class CircuitBreakerHandler(DeclarativeHandler[NetworkLV]):
    """Parses GNF Circuit Breaker components using a declarative recipe."""

    COMPONENT_CLS = CircuitBreakerLV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation ", required=True),
        SectionConfig("circuit_breaker_type", "#CircuitBreakerType "),
        SectionConfig("current_protection_type", "#CurrentProtectionType "),
        SectionConfig("earth_fault_protection_type", "#EarthFaultProtectionType "),
        SectionConfig("voltage_protection_type", "#VoltageProtectionType "),
        SectionConfig("fields", "#Fields "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for CircuitBreaker-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.lv.presentations import SecundairPresentation

            return SecundairPresentation
        if kwarg_name == "fields":
            from pyptp.elements.lv.shared import Fields

            return Fields
        if kwarg_name == "circuit_breaker_type":
            from pyptp.elements.lv.circuit_breaker import CircuitBreakerLV

            return CircuitBreakerLV.CircuitBreakerType
        if kwarg_name == "current_protection_type":
            from pyptp.elements.lv.circuit_breaker import CircuitBreakerLV

            return CircuitBreakerLV.CurrentProtectionType
        if kwarg_name == "earth_fault_protection_type":
            from pyptp.elements.lv.circuit_breaker import CircuitBreakerLV

            return CircuitBreakerLV.CurrentProtectionType
        if kwarg_name == "voltage_protection_type":
            from pyptp.elements.lv.circuit_breaker import CircuitBreakerLV

            return CircuitBreakerLV.VoltageProtectionType

        return None
