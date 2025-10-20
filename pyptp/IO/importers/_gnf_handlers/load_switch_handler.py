"""Handler for parsing GNF Load Switch sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.lv.load_switch import LoadSwitchLV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_lv import NetworkLV


class LoadSwitchHandler(DeclarativeHandler[NetworkLV]):
    """Parses GNF Load Switch components using a declarative recipe."""

    COMPONENT_CLS = LoadSwitchLV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation ", required=True),
        SectionConfig("type", "#LoadSwitchType "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Load Switch-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.lv.presentations import SecundairPresentation

            return SecundairPresentation
        if kwarg_name == "type":
            from pyptp.elements.lv.load_switch import LoadSwitchLV

            return LoadSwitchLV.LoadSwitchType
        return None
