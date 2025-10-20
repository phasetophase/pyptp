"""Handler for parsing VNF Fuse sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.mv.fuse import FuseMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV


class FuseHandler(DeclarativeHandler[NetworkMV]):
    """Parses VNF Fuse components using a declarative recipe."""

    COMPONENT_CLS = FuseMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation "),
        SectionConfig("type", "#FuseType "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Fuse-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.mv.presentations import SecondaryPresentation

            return SecondaryPresentation
        if kwarg_name == "type":
            return FuseMV.FuseType
        return None
