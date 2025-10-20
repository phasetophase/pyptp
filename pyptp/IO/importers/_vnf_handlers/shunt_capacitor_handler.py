"""Handler for parsing VNF Shunt Capacitor sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.mv.shunt_capacitor import ShuntCapacitorMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType


class ShuntCapacitorHandler(DeclarativeHandler[TNetworkMSType]):
    """Parses VNF Shunt Capacitor components using a declarative recipe."""

    COMPONENT_CLS = ShuntCapacitorMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("active_filter", "#ActiveFilter ", required=False),
        SectionConfig("presentations", "#Presentation ", required=False),
        SectionConfig("extras", "#Extra Text:", required=False),
        SectionConfig("notes", "#Note Text:", required=False),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for ShuntCapacitor-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.mv.presentations import ElementPresentation

            return ElementPresentation
        if kwarg_name == "active_filter":
            return ShuntCapacitorMV.ActiveFilter
        return None
