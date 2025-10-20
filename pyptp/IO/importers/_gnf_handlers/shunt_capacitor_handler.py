"""Handler for parsing GNF Shunt Capacitor sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.lv.shunt_capacitor import ShuntCapacitorLV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_lv import NetworkLV


class ShuntCapacitorHandler(DeclarativeHandler[NetworkLV]):
    """Parses GNF Shunt Capacitor components using a declarative recipe."""

    COMPONENT_CLS = ShuntCapacitorLV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation ", required=True),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for ShuntCapacitor-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.lv.presentations import ElementPresentation

            return ElementPresentation
        return None
