"""Handler for the TEXT section of a GNF file."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.lv.text import TextLV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_lv import NetworkLV


class TextHandler(DeclarativeHandler[NetworkLV]):
    """Parses the TEXT section of a GNF file using the declarative recipe."""

    COMPONENT_CLS = TextLV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("lines", "#Line Text:", required=False),
        SectionConfig("presentations", "#Presentation ", required=False),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Text-specific fields."""
        if kwarg_name == "general":
            return TextLV.General
        if kwarg_name == "presentations":
            return TextLV.Presentation
        return None
