"""Handler for parsing GNF Profile sections using a declarative recipe."""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.lv.profile import ProfileLV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_lv import NetworkLV


class ProfileHandler(DeclarativeHandler[NetworkLV]):
    """Parses GNF Profile components using a declarative recipe.

    Processes load profile definitions with time-based factor arrays
    for modeling time-varying load behavior in low-voltage networks.
    """

    COMPONENT_CLS = ProfileLV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("type", "#ProfileType ", required=True),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Profile-specific section parsing.

        Args:
            kwarg_name: Section identifier from COMPONENT_CONFIG.

        Returns:
            Target class for deserializing the section data, or None if
            the section uses the base element's deserialize method.

        """
        if kwarg_name == "type":
            return ProfileLV.ProfileType
        return None
