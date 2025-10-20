"""Handler for parsing VNF Three Winding Transformer sections using a declarative recipe."""

from __future__ import annotations

from typing import Any, ClassVar

from pyptp.elements.mv.threewinding_transformer import ThreewindingTransformerMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType


class ThreewindingTransformerHandler(DeclarativeHandler[TNetworkMSType]):
    """Parses VNF Three Winding Transformer components using a declarative recipe."""

    COMPONENT_CLS = ThreewindingTransformerMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("type", "#ThreewindingsTransformerType ", required=True),
        SectionConfig("presentations", "#Presentation "),
        SectionConfig("voltage_control", "#VoltageControl "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type[Any] | None:
        """Resolve target class for ThreewindingTransformer-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.mv.presentations import DWPresentation

            return DWPresentation
        if kwarg_name == "type":
            from pyptp.elements.mv.threewinding_transformer import ThreewindingTransformerMV

            return ThreewindingTransformerMV.ThreewindingTransformerType
        if kwarg_name == "voltage_control":
            from pyptp.elements.mv.threewinding_transformer import ThreewindingTransformerMV

            return ThreewindingTransformerMV.VoltageControl
        return None
