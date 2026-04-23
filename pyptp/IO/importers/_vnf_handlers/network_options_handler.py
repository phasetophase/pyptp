"""Handler for parsing VNF NETWORKOPTIONS sections."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.mv.network_options import NetworkOptionsMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV


class NetworkOptionsHandler(DeclarativeHandler[NetworkMV]):
    """Handler for VNF NETWORKOPTIONS sections."""

    COMPONENT_CLS = NetworkOptionsMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Network Options."""
        if kwarg_name == "general":
            return NetworkOptionsMV.General
        return None
