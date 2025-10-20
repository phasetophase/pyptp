"""Handler for parsing VNF Indicator sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.mv.indicator import IndicatorMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType


class IndicatorHandler(DeclarativeHandler[TNetworkMSType]):
    """Parses VNF Indicator components using a declarative recipe."""

    COMPONENT_CLS = IndicatorMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Indicator-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.mv.presentations import SecondaryPresentation

            return SecondaryPresentation
        return None
