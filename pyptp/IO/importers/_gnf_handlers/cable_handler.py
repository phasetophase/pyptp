"""Handler for parsing GNF Cable sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.lv.cable import CableLV
from pyptp.elements.lv.presentations import BranchPresentation
from pyptp.elements.lv.shared import CableType, CurrentType, Fields, FuseType, GeoCablePart
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_lv import NetworkLV


class CableHandler(DeclarativeHandler[NetworkLV]):
    """Declarative handler for parsing GNF Cable sections into TCableLS elements.

    Processes electrical cables with support for complex impedance modeling,
    multiple conductor configurations (up to 9 conductors), and extensive
    protection device configuration (fuses and current limiters).
    """

    COMPONENT_CLS = CableLV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("cable_part", "#CablePart "),
        SectionConfig("cable_type", "#CableType "),
        SectionConfig("cablepart_geography", "#GeoCablePart "),
        SectionConfig("presentations", "#Presentation ", required=True),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
        SectionConfig("fields", "#Fields "),
        SectionConfig("fuse1_h1", "#FuseType1_h1 "),
        SectionConfig("fuse1_h2", "#FuseType1_h2 "),
        SectionConfig("fuse1_h3", "#FuseType1_h3 "),
        SectionConfig("fuse1_h4", "#FuseType1_h4 "),
        SectionConfig("fuse2_h1", "#FuseType2_h1 "),
        SectionConfig("fuse2_h2", "#FuseType2_h2 "),
        SectionConfig("fuse2_h3", "#FuseType2_h3 "),
        SectionConfig("fuse2_h4", "#FuseType2_h4 "),
        SectionConfig("current1_h1", "#CurrentType1_h1 "),
        SectionConfig("current1_h2", "#CurrentType1_h2 "),
        SectionConfig("current1_h3", "#CurrentType1_h3 "),
        SectionConfig("current1_h4", "#CurrentType1_h4 "),
        SectionConfig("current2_h1", "#CurrentType2_h1 "),
        SectionConfig("current2_h2", "#CurrentType2_h2 "),
        SectionConfig("current2_h3", "#CurrentType2_h3 "),
        SectionConfig("current2_h4", "#CurrentType2_h4 "),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Cable-specific section parsing.

        Args:
            kwarg_name: Section identifier from COMPONENT_CONFIG.

        Returns:
            Target class for deserializing the section data, or None if
            the section uses the base element's deserialize method.

        """
        if kwarg_name == "cable_part":
            return CableLV.CablePart
        if kwarg_name == "presentations":
            return BranchPresentation
        if kwarg_name == "cable_type":
            return CableType
        if kwarg_name == "cablepart_geography":
            return GeoCablePart
        if kwarg_name == "fields":
            return Fields
        if kwarg_name.startswith("fuse"):
            return FuseType
        if kwarg_name.startswith("current"):
            return CurrentType
        return None
