"""Handler for parsing VNF Rails sections using a declarative recipe."""

from __future__ import annotations

from typing import Any, ClassVar

from pyptp.elements.mv.rails import RailSystemMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType


class RailsHandler(DeclarativeHandler[TNetworkMSType]):
    """Parses VNF Rails components using a declarative recipe.

    Handles rail system components with general properties and multiple nodes
    for electrical network modeling and analysis.
    """

    COMPONENT_CLS = RailSystemMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("nodes", "#Node "),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type[Any] | None:
        """Resolve target class for Rails-specific fields.

        Args:
            kwarg_name: Name of the field requiring class resolution.

        Returns:
            Target class for deserialization, or None if not found.

        """
        if kwarg_name == "nodes":
            return RailSystemMV.Node
        return None
