"""Handler for parsing GNF Earthing Transformer sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.lv.earthing_transformer import EarthingTransformerLV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_lv import NetworkLV


class EarthingTransformerHandler(DeclarativeHandler[NetworkLV]):
    """Parses GNF Earthing Transformer components using a declarative recipe."""

    COMPONENT_CLS = EarthingTransformerLV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation ", required=True),
        SectionConfig("type", "#EarthingTransformerType "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for EarthingTransformer-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.lv.presentations import ElementPresentation

            return ElementPresentation
        if kwarg_name == "type":
            from pyptp.elements.lv.earthing_transformer import EarthingTransformerLV

            return EarthingTransformerLV.EarthingTransformerType
        return None
