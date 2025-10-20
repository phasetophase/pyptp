"""Handler for parsing GNF Link sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.lv.link import LinkLV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_lv import NetworkLV


class LinkHandler(DeclarativeHandler[NetworkLV]):
    """Parses GNF Link components using a declarative recipe."""

    COMPONENT_CLS = LinkLV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation ", required=True),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
        SectionConfig("fuse1_h1", "#FuseType1_h1 "),
        SectionConfig("fuse1_h2", "#FuseType1_h2 "),
        SectionConfig("fuse1_h3", "#FuseType1_h3 "),
        SectionConfig("fuse1_h4", "#FuseType1_h4 "),
        SectionConfig("fuse2_h1", "#FuseType2_h1 "),
        SectionConfig("fuse2_h2", "#FuseType2_h2 "),
        SectionConfig("fuse2_h3", "#FuseType2_h3 "),
        SectionConfig("fuse2_h4", "#FuseType2_h4 "),
        SectionConfig("current_protection1_h1", "#CurrentType1_h1 "),
        SectionConfig("current_protection1_h2", "#CurrentType1_h2 "),
        SectionConfig("current_protection1_h3", "#CurrentType1_h3 "),
        SectionConfig("current_protection1_h4", "#CurrentType1_h4 "),
        SectionConfig("current_protection2_h1", "#CurrentType2_h1 "),
        SectionConfig("current_protection2_h2", "#CurrentType2_h2 "),
        SectionConfig("current_protection2_h3", "#CurrentType2_h3 "),
        SectionConfig("current_protection2_h4", "#CurrentType2_h4 "),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Link-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.lv.presentations import BranchPresentation

            return BranchPresentation
        if kwarg_name.startswith("fuse"):
            from pyptp.elements.lv.shared import FuseType

            return FuseType
        if kwarg_name.startswith("current_protection"):
            from pyptp.elements.lv.shared import CurrentType

            return CurrentType
        return None
