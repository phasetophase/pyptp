"""Handler for parsing VNF Reactance Coil sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.mv.reactance_coil import ReactanceCoilMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType


class ReactanceCoilHandler(DeclarativeHandler[TNetworkMSType]):
    """Parses VNF Reactance Coil components using a declarative recipe."""

    COMPONENT_CLS = ReactanceCoilMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation ", required=False),
        SectionConfig("type", "#ReactanceCoilType ", required=True),
        SectionConfig("extras", "#Extra Text:", required=False),
        SectionConfig("notes", "#Note Text:", required=False),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for required fields."""
        if kwarg_name == "general":
            return ReactanceCoilMV.General
        if kwarg_name == "presentations":
            from pyptp.elements.mv.presentations import BranchPresentation

            return BranchPresentation
        if kwarg_name == "type":
            return ReactanceCoilMV.ReactanceCoilType
        if kwarg_name == "extras":
            from pyptp.elements.mixins import Extra

            return Extra
        if kwarg_name == "notes":
            from pyptp.elements.mixins import Note

            return Note
        return None
