"""Handler for parsing VNF Transformer sections for medium-voltage network modeling.

Provides declarative configuration for parsing power transformers in Vision Network Files,
supporting symmetrical three-phase modeling with voltage control capabilities.
"""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.mv.transformer import TransformerMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType


class TransformerHandler(DeclarativeHandler[TNetworkMSType]):
    """Handler for VNF Transformer elements in medium-voltage networks."""

    COMPONENT_CLS = TransformerMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation "),
        SectionConfig("type", "#TransformerType "),
        SectionConfig("dynamics", "#Dynamics "),
        SectionConfig("voltage_control", "#VoltageControl "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Transformer-specific field deserialization.

        Args:
            kwarg_name: Name of the field requiring class resolution.

        Returns:
            Target class for the specified field, or None if no special handling needed.

        """
        if kwarg_name == "presentations":
            from pyptp.elements.mv.presentations import BranchPresentation

            return BranchPresentation
        if kwarg_name == "type":
            return TransformerMV.TransformerType
        if kwarg_name == "dynamics":
            return TransformerMV.Dynamics
        if kwarg_name == "voltage_control":
            return TransformerMV.VoltageControl
        return None
