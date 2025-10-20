"""Handler for parsing VNF Mutual sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.mv.mutual import MutualMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType


class MutualHandler(DeclarativeHandler[TNetworkMSType]):
    """Parses VNF Mutual components using a declarative recipe."""

    COMPONENT_CLS = MutualMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("type", "#MutualType "),
        SectionConfig("presentations", "#Presentation "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Mutual-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.mv.presentations import (
                SecondaryPresentation,  # TODO: mutual is not a secondary presentation
            )

            return SecondaryPresentation
        if kwarg_name == "type":
            return MutualMV.MutualType
        return None
