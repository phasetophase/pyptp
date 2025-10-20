"""Handler for parsing GNF Fuse sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.lv.fuse import FuseLV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_lv import NetworkLV


class FuseHandler(DeclarativeHandler[NetworkLV]):
    """Parses GNF Fuse components using a declarative recipe."""

    COMPONENT_CLS = FuseLV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation ", required=True),
        SectionConfig("type", "#FuseType "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Fuse-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.lv.presentations import SecundairPresentation

            return SecundairPresentation
        if kwarg_name == "type":
            from pyptp.elements.lv.shared import FuseType

            return FuseType
        return None
