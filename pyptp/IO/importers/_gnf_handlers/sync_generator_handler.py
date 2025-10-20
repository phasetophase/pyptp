"""Handler for parsing GNF Synchronous Generator sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.lv.syn_generator import SynchronousGeneratorLV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_lv import NetworkLV


class SyncGeneratorHandler(DeclarativeHandler[NetworkLV]):
    """Parses GNF Synchronous Generator components using a declarative recipe."""

    COMPONENT_CLS = SynchronousGeneratorLV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation "),
        SectionConfig("type", "#SynchronousGeneratorType "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for SyncGenerator-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.lv.presentations import ElementPresentation

            return ElementPresentation
        if kwarg_name == "type":
            from pyptp.elements.lv.syn_generator import SynchronousGeneratorLV

            return SynchronousGeneratorLV.SynchronousGeneratorType
        return None
