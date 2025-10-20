"""Handler for parsing VNF Sheet sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.mv.sheet import SheetMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType


class SheetHandler(DeclarativeHandler[TNetworkMSType]):
    """Parses VNF Sheet components using a declarative recipe."""

    COMPONENT_CLS = SheetMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("comment", "#Comment "),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Sheet-specific fields."""
        if kwarg_name == "comment":
            from pyptp.elements.mv.shared import Comment

            return Comment
        return None
