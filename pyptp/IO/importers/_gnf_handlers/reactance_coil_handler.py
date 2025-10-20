"""Handler for parsing GNF Reactance Coil sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.lv.reactance_coil import ReactanceCoilLV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_lv import NetworkLV


class ReactanceCoilHandler(DeclarativeHandler[NetworkLV]):
    """Parses GNF Reactance Coil components using a declarative recipe."""

    COMPONENT_CLS = ReactanceCoilLV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation ", required=True),
        SectionConfig("type", "#ReactanceCoilType "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for ReactanceCoil-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.lv.presentations import BranchPresentation

            return BranchPresentation
        if kwarg_name == "type":
            from pyptp.elements.lv.reactance_coil import ReactanceCoilLV

            return ReactanceCoilLV.ReactanceCoilType
        return None
