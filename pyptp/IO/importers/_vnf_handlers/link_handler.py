"""Handler for parsing VNF Link sections for medium-voltage network modeling.

Provides declarative configuration for parsing electrical links in Vision Network Files,
supporting symmetrical three-phase modeling used in MV distribution networks.
"""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.mv.link import LinkMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV


class LinkHandler(DeclarativeHandler[NetworkMV]):
    """Handler for VNF Link elements in medium-voltage networks."""

    COMPONENT_CLS = LinkMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Link-specific field deserialization.

        Args:
            kwarg_name: Name of the field requiring class resolution.

        Returns:
            Target class for the specified field, or None if no special handling needed.

        """
        if kwarg_name == "presentations":
            from pyptp.elements.mv.presentations import BranchPresentation

            return BranchPresentation
        return None
