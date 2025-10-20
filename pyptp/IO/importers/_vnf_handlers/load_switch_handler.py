"""Handler for parsing VNF Load Switch sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.mv.load_switch import LoadSwitchMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType


class LoadSwitchHandler(DeclarativeHandler[TNetworkMSType]):
    """Parses VNF Load Switch components using a declarative recipe."""

    COMPONENT_CLS = LoadSwitchMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("type", "#LoadSwitchType ", required=False),
        SectionConfig("presentations", "#Presentation ", required=False),
        SectionConfig("extras", "#Extra Text:", required=False),
        SectionConfig("notes", "#Note Text:", required=False),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for LoadSwitch-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.mv.presentations import SecondaryPresentation

            return SecondaryPresentation
        if kwarg_name == "type":
            return LoadSwitchMV.LoadSwitchType
        return None
