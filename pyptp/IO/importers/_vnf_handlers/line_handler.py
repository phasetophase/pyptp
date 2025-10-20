"""Handler for parsing VNF Line sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.mv.line import LineMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType


class LineHandler(DeclarativeHandler[TNetworkMSType]):
    """Parses VNF Line components using a declarative recipe."""

    COMPONENT_CLS = LineMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation "),
        SectionConfig("lineparts", "#LinePart "),
        SectionConfig("joints", "#Joint "),
        SectionConfig("geo", "#Geo "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Line-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.mv.presentations import BranchPresentation

            return BranchPresentation
        if kwarg_name == "lineparts":
            return LineMV.LinePart
        if kwarg_name == "joints":
            return LineMV.Joint
        if kwarg_name == "geo":
            return LineMV.Geo
        return None
