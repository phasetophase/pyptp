"""Handler for parsing VNF Text sections using a declarative recipe."""

from __future__ import annotations

from typing import Any, ClassVar

from pyptp.elements.mv.text import TextMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType


class TextHandler(DeclarativeHandler[TNetworkMSType]):
    """Parses VNF Text components using a declarative recipe."""

    COMPONENT_CLS = TextMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("lines", "#Line ", required=False),
        SectionConfig("presentations", "#Presentation ", required=False),
        SectionConfig("extras", "#Extra Text:", required=False),
        SectionConfig("notes", "#Note Text:", required=False),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type[Any] | None:
        """Resolve target class for Text-specific fields.

        Args:
            kwarg_name: Name of the field requiring class resolution.

        Returns:
            Target class for deserialization, or None if not found.

        """
        if kwarg_name == "lines":
            return TextMV.Line
        if kwarg_name == "presentations":
            return TextMV.Presentation
        return None
