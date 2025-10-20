"""Handler for parsing GNF Asynchronous Motor sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.lv.async_motor import AsynchronousMotorLV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_lv import NetworkLV


class AsyncMotorHandler(DeclarativeHandler[NetworkLV]):
    """Parses GNF Asynchronous Motor components using a declarative recipe."""

    COMPONENT_CLS = AsynchronousMotorLV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation "),
        SectionConfig("type", "#AsynchronousMotorType "),
        SectionConfig("harmonics", "#HarmonicsType "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for AsyncMotor-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.lv.presentations import ElementPresentation

            return ElementPresentation
        if kwarg_name == "type":
            from pyptp.elements.lv.async_motor import AsynchronousMotorLV

            return AsynchronousMotorLV.AsynchronousMotorType
        if kwarg_name == "harmonics":
            from pyptp.elements.lv.shared import HarmonicsType

            return HarmonicsType
        return None
