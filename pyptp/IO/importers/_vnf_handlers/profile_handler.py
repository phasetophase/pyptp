"""Handler for parsing VNF Profile sections using a declarative recipe."""

from __future__ import annotations

from typing import Any, ClassVar

from pyptp.elements.mv.profile import ProfileMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType


class ProfileHandler(DeclarativeHandler[TNetworkMSType]):
    """Parses VNF Profile components using a declarative recipe.

    Handles load profiles with dynamic factor properties (f1, f2, f3, ...)
    whose count depends on the Sort value in the ProfileType section.
    """

    COMPONENT_CLS = ProfileMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("type", "#ProfileType ", required=True),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type[Any] | None:
        """Resolve target class for Profile-specific fields.

        Args:
            kwarg_name: Name of the field requiring class resolution.

        Returns:
            Target class for deserialization, or None if not found.

        """
        if kwarg_name == "type":
            return ProfileMV.ProfileType
        return None
