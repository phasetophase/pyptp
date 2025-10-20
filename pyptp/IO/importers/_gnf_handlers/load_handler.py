"""Handler for parsing GNF Load sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.lv.load import LoadLV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_lv import NetworkLV


class LoadHandler(DeclarativeHandler[NetworkLV]):
    """Declarative handler for parsing GNF Load sections into TLoadLS elements.

    Processes electrical loads (consumers) with support for asymmetrical modeling,
    complex power characteristics, and harmonic analysis in low-voltage networks.
    """

    COMPONENT_CLS = LoadLV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation ", required=True),
        SectionConfig("harmonics", "#HarmonicsType "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Load-specific section parsing.

        Args:
            kwarg_name: Section identifier from COMPONENT_CONFIG.

        Returns:
            Target class for deserializing the section data, or None if
            the section uses the base element's deserialize method.

        """
        if kwarg_name == "presentations":
            from pyptp.elements.lv.presentations import ElementPresentation

            return ElementPresentation
        if kwarg_name == "harmonics":
            from pyptp.elements.lv.shared import HarmonicsType

            return HarmonicsType
        return None
