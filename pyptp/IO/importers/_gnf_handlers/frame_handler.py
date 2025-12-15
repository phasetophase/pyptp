"""Handler for parsing GNF Frame sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.lv.frame import FrameLV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_lv import NetworkLV


class FrameHandler(DeclarativeHandler[NetworkLV]):
    COMPONENT_CLS = FrameLV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation "),
        SectionConfig("lines", "#Line Text:"),
        SectionConfig("geo", "#Geo "),
        SectionConfig("extras", "#Extra Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Frame-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.lv.presentations import BranchPresentation

            return BranchPresentation
        return None
