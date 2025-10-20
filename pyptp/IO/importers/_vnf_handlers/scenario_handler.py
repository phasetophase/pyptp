"""Handler for parsing VNF Scenario sections using a declarative recipe."""

from __future__ import annotations

from typing import Any, ClassVar

from pyptp.elements.mv.scenario import ScenarioMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType


class ScenarioHandler(DeclarativeHandler[TNetworkMSType]):
    """Parses VNF Scenario components using a declarative recipe."""

    COMPONENT_CLS = ScenarioMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("scenario_items", "#ScenarioItem ", required=False),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type[Any] | None:
        """Resolve target class for Scenario-specific fields.

        Args:
            kwarg_name: Name of the field requiring class resolution.

        Returns:
            Target class for deserialization, or None if not found.

        """
        if kwarg_name == "general":
            return ScenarioMV.General
        if kwarg_name == "scenario_items":
            return ScenarioMV.ScenarioItem
        return None
