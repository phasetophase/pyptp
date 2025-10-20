"""Handler for parsing VNF Asynchronous Motor sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.mv.async_motor import AsynchronousMotorMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV


class AsyncMotorHandler(DeclarativeHandler[NetworkMV]):
    """Parses VNF Asynchronous Motor components using a declarative recipe."""

    COMPONENT_CLS = AsynchronousMotorMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation "),
        SectionConfig("type", "#AsynchronousMotorType ", required=True),
        SectionConfig("harmonics", "#Harmonics "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for AsynchronousMotor-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.mv.presentations import ElementPresentation

            return ElementPresentation
        if kwarg_name == "type":
            from pyptp.elements.mv.async_motor import AsynchronousMotorMV

            return AsynchronousMotorMV.AsynchronousMotorType
        if kwarg_name == "harmonics":
            from pyptp.elements.lv.shared import HarmonicsType

            return HarmonicsType
        return None
