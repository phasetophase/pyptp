"""Handler for parsing GNF Asynchronous Generator sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.lv.async_generator import AsynchronousGeneratorLV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_lv import NetworkLV


class AsyncGeneratorHandler(DeclarativeHandler[NetworkLV]):
    """Parses GNF Asynchronous Generator components using a declarative recipe."""

    COMPONENT_CLS = AsynchronousGeneratorLV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation "),
        SectionConfig("type", "#AsynchronousGeneratorType "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for AsyncGenerator-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.lv.presentations import ElementPresentation

            return ElementPresentation
        if kwarg_name == "type":
            from pyptp.elements.lv.async_generator import AsynchronousGeneratorLV

            return AsynchronousGeneratorLV.AsynchronousGeneratorType
        return None
