"""Handler for parsing VNF Asynchronous Generator sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.mv.async_generator import AsynchronousGeneratorMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV


class AsyncGeneratorHandler(DeclarativeHandler[NetworkMV]):
    """Parses VNF Asynchronous Generator components using a declarative recipe."""

    COMPONENT_CLS = AsynchronousGeneratorMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation "),
        SectionConfig("type", "#AsynchronousGeneratorType ", required=True),
        SectionConfig("restriction", "#Restriction "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for AsynchronousGenerator-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.mv.presentations import ElementPresentation

            return ElementPresentation
        if kwarg_name == "type":
            from pyptp.elements.mv.async_generator import AsynchronousGeneratorMV

            return AsynchronousGeneratorMV.ASynchronousGeneratorType
        if kwarg_name == "restriction":
            from pyptp.elements.mv.async_generator import AsynchronousGeneratorMV

            return AsynchronousGeneratorMV.Restriction
        return None
