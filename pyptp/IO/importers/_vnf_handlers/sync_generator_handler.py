"""Handler for parsing VNF Synchronous Generator sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.mv.synchronous_generator import SynchronousGeneratorMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType


class SyncGeneratorHandler(DeclarativeHandler[TNetworkMSType]):
    """Parses VNF Synchronous Generator components using a declarative recipe."""

    COMPONENT_CLS = SynchronousGeneratorMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation "),
        SectionConfig("type", "#SynchronousGeneratorType ", required=True),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for SynchronousGenerator-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.mv.presentations import ElementPresentation

            return ElementPresentation
        if kwarg_name == "type":
            from pyptp.elements.mv.synchronous_generator import SynchronousGeneratorMV

            return SynchronousGeneratorMV.SynchronousGeneratorType
        return None
