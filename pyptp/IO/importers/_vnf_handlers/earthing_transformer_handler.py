"""Handler for parsing VNF Earthing Transformer sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.mv.earthing_transformer import EarthingTransformerMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV


class EarthingTransformerHandler(DeclarativeHandler[NetworkMV]):
    """Parses VNF Earthing Transformer components using a declarative recipe."""

    COMPONENT_CLS = EarthingTransformerMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation "),
        SectionConfig("type", "#EarthingTransformerType "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for EarthingTransformer-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.mv.presentations import ElementPresentation

            return ElementPresentation
        if kwarg_name == "type":
            return EarthingTransformerMV.EarthingTransformerType
        return None
