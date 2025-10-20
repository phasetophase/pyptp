"""Handler for parsing VNF Shunt Coil sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.mv.shunt_coil import ShuntCoilMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType


class ShuntCoilHandler(DeclarativeHandler[TNetworkMSType]):
    """Parses VNF Shunt Coil components using a declarative recipe."""

    COMPONENT_CLS = ShuntCoilMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation ", required=False),
        SectionConfig("extras", "#Extra Text:", required=False),
        SectionConfig("notes", "#Note Text:", required=False),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for ShuntCoil-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.mv.presentations import ElementPresentation

            return ElementPresentation
        return None
