"""Handler for parsing GNF Node sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.lv.node import NodeLV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_lv import NetworkLV as TNetworkLSType


class NodeHandler(DeclarativeHandler[TNetworkLSType]):
    """Declarative handler for parsing GNF Node sections into TNodeLS elements.

    Processes electrical nodes (connection points) in low-voltage networks
    with support for asymmetrical modeling and multiple presentation formats.
    """

    COMPONENT_CLS = NodeLV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation ", required=True),
        SectionConfig("fields", "#Fields "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Node-specific section parsing.

        Args:
            kwarg_name: Section identifier from COMPONENT_CONFIG.

        Returns:
            Target class for deserializing the section data, or None if
            the section uses the base element's deserialize method.

        """
        if kwarg_name == "presentations":
            from pyptp.elements.lv.presentations import NodePresentation

            return NodePresentation
        if kwarg_name == "fields":
            from pyptp.elements.lv.shared import Fields

            return Fields
        return None
