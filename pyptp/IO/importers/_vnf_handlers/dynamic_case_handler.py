"""Handler for parsing VNF Dynamic Case sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.mv.dynamic_case import DynamicCaseMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType


class DynamicCaseHandler(DeclarativeHandler[TNetworkMSType]):
    """Parses VNF Dynamic Case components using a declarative recipe."""

    COMPONENT_CLS = DynamicCaseMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("dynamic_events", "#DynamicEvent "),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for DynamicCase-specific section parsing."""
        if kwarg_name == "dynamic_events":
            return DynamicCaseMV.DynamicEvent
        return None
