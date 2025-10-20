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
        SectionConfig("fields", "#Fields "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for CircuitBreaker-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.lv.presentations import ElementPresentation

            return ElementPresentation
        if kwarg_name == "fields":
            from pyptp.elements.lv.shared import Fields

            return Fields
        return None
