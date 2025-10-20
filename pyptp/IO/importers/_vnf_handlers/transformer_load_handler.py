"""Handler for parsing VNF Transformer Load sections using a declarative recipe."""

from __future__ import annotations

from typing import Any, ClassVar

from pyptp.elements.mv.transformer_load import TransformerLoadMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType


class TransformerLoadHandler(DeclarativeHandler[TNetworkMSType]):
    """Parses VNF Transformer Load components using a declarative recipe."""

    COMPONENT_CLS = TransformerLoadMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("type", "#TransformerType ", required=True),
        SectionConfig("presentations", "#Presentation "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type[Any] | None:
        """Resolve target class for TransformerLoad-specific fields."""
        if kwarg_name == "presentations":
            from pyptp.elements.mv.presentations import ElementPresentation

            return ElementPresentation
        if kwarg_name == "type":
            from pyptp.elements.mv.transformer_load import TransformerLoadMV

            return TransformerLoadMV.TransformerLoadType
        return None
