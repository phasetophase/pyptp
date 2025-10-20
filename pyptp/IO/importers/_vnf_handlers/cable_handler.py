"""Handler for parsing VNF Cable sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.mv.cable import CableMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV


class CableHandler(DeclarativeHandler[NetworkMV]):
    """Parses VNF Cable components using a declarative recipe."""

    COMPONENT_CLS = CableMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation "),
        SectionConfig("cable_parts", "#CablePart "),
        SectionConfig("cable_types", "#CableType "),
        SectionConfig("geo_cable_parts", "#GeoCablePart "),
        SectionConfig("joints", "#Joint "),
        SectionConfig("geo", "#Geo "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Cable-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.mv.presentations import BranchPresentation

            return BranchPresentation
        if kwarg_name == "cable_parts":
            return CableMV.CablePart
        if kwarg_name == "cable_types":
            from pyptp.elements.mv.shared import CableType

            return CableType
        if kwarg_name == "geo_cable_parts":
            from pyptp.elements.mv.shared import GeoCablePart

            return GeoCablePart
        if kwarg_name == "joints":
            return CableMV.Joint
        if kwarg_name == "geo":
            return CableMV.Geo
        return None
