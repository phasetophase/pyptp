"""Handler for parsing VNF Special Transformer sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.mv.special_transformer import SpecialTransformerMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType


class SpecialTransformerHandler(DeclarativeHandler[TNetworkMSType]):
    """Parses VNF Special Transformer components using a declarative recipe."""

    COMPONENT_CLS = SpecialTransformerMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation "),
        SectionConfig("type", "#SpecialTransformerType ", required=True),
        SectionConfig("voltage_control", "#VoltageControl "),
        SectionConfig("p_control", "#PControl "),
        SectionConfig("tap_special", "#TapSpecial "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for SpecialTransformer-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.mv.presentations import BranchPresentation

            return BranchPresentation
        if kwarg_name == "type":
            from pyptp.elements.mv.special_transformer import SpecialTransformerMV

            return SpecialTransformerMV.SpecialTransformerType
        if kwarg_name == "voltage_control":
            from pyptp.elements.mv.special_transformer import SpecialTransformerMV

            return SpecialTransformerMV.VoltageControl
        if kwarg_name == "p_control":
            from pyptp.elements.mv.special_transformer import SpecialTransformerMV

            return SpecialTransformerMV.PControl
        if kwarg_name == "tap_special":
            from pyptp.elements.mv.special_transformer import SpecialTransformerMV

            return SpecialTransformerMV.TapSpecial
        return None
