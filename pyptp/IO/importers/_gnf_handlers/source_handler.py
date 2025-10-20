"""Handler for parsing GNF Source sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.lv.source import SourceLV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_lv import NetworkLV


class SourceHandler(DeclarativeHandler[NetworkLV]):
    """Declarative handler for parsing GNF Source sections into TSourceLS elements.

    Processes electrical sources (supply points) with support for asymmetrical
    modeling and complex voltage/impedance characteristics in low-voltage networks.
    """

    COMPONENT_CLS = SourceLV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation ", required=True),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Source-specific section parsing.

        Args:
            kwarg_name: Section identifier from COMPONENT_CONFIG.

        Returns:
            Target class for deserializing the section data, or None if
            the section uses the base element's deserialize method.

        """
        if kwarg_name == "presentations":
            from pyptp.elements.lv.presentations import ElementPresentation

            return ElementPresentation
        return None
