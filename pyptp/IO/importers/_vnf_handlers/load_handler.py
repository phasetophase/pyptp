"""Handler for parsing VNF Load sections for medium-voltage network modeling.

Provides declarative configuration for parsing electrical loads in Vision Network Files,
supporting symmetrical three-phase modeling with advanced control systems.
"""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.mv.load import LoadMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV


class LoadHandler(DeclarativeHandler[NetworkMV]):
    """Handler for VNF Load elements in medium-voltage networks.

    Parses electrical load components from Vision Network Files using the declarative
    handler pattern. Supports complex load modeling with multiple control types
    including P(U), Q, P(I) controls and CERES integration for MV networks.
    """

    COMPONENT_CLS = LoadMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation "),
        SectionConfig("p_control", "#P(U)Control "),
        SectionConfig("q_control", "#QControl "),
        SectionConfig("pi_control", "#P(I)Control "),
        SectionConfig("ceres", "#CERES "),
        SectionConfig("restrictions", "#Restriction "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Load-specific field deserialization.

        Args:
            kwarg_name: Name of the field requiring class resolution.

        Returns:
            Target class for the specified field, or None if no special handling needed.

        """
        if kwarg_name == "presentations":
            from pyptp.elements.mv.presentations import ElementPresentation

            return ElementPresentation
        if kwarg_name == "p_control":
            from pyptp.elements.mv.shared import PControl

            return PControl
        if kwarg_name == "q_control":
            from pyptp.elements.mv.shared import QControl

            return QControl
        if kwarg_name == "pi_control":
            return LoadMV.PIControl
        if kwarg_name == "restrictions":
            return LoadMV.Capacity
        # Note: ceres is handled as a dict in the element class
        return None
