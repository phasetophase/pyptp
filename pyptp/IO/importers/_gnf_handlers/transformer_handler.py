"""Handler for parsing GNF Transformer sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.lv.transformer import TransformerLV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_lv import NetworkLV


class TransformerHandler(DeclarativeHandler[NetworkLV]):
    """Declarative handler for parsing GNF Transformer sections into TTransformerLS elements.

    Processes electrical transformers with support for complex impedance modeling,
    multiple winding configurations, and voltage control systems for accurate
    unbalanced load flow analysis in low-voltage networks.
    """

    COMPONENT_CLS = TransformerLV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation ", required=True),
        SectionConfig("type", "#TransformerType "),
        SectionConfig("voltage_control", "#VoltageControl "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Transformer-specific section parsing.

        Args:
            kwarg_name: Section identifier from COMPONENT_CONFIG.

        Returns:
            Target class for deserializing the section data, or None if
            the section uses the base element's deserialize method.

        """
        if kwarg_name == "presentations":
            from pyptp.elements.lv.presentations import BranchPresentation

            return BranchPresentation
        if kwarg_name == "type":
            return TransformerLV.TransformerType
        if kwarg_name == "voltage_control":
            return TransformerLV.VoltageControl
        return None
