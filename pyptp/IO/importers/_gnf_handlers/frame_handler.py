"""Handler for parsing GNF Frame sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.lv.frame import FrameLV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_lv import NetworkLV


class FrameHandler(DeclarativeHandler[NetworkLV]):
    """Parses GNF Frame components using a declarative recipe."""

    COMPONENT_CLS = FrameLV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("lines", "#Line Text:", required=False),
        SectionConfig("geo_series", "#Geo ", required=False),
        SectionConfig("presentations", "#Presentation ", required=False),
        SectionConfig("extras", "#Extra Text:", required=False),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Frame-specific fields."""
        if kwarg_name == "general":
            return FrameLV.General
        if kwarg_name == "presentations":
            return FrameLV.FramePresentation
        return None
