"""Handler for parsing VNF Wind Turbine sections for medium-voltage network modeling.

Provides declarative configuration for parsing wind turbine generators in Vision Network Files,
supporting symmetrical three-phase modeling with advanced power control systems.
"""

from __future__ import annotations

from typing import ClassVar

from pyptp.elements.mv.windturbine import WindTurbineMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType


class WindTurbineHandler(DeclarativeHandler[TNetworkMSType]):
    """Handler for VNF Wind Turbine elements in medium-voltage networks."""

    COMPONENT_CLS = WindTurbineMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("presentations", "#Presentation "),
        SectionConfig("type", "#WindTurbineType "),
        SectionConfig("q_control", "#QControl "),
        SectionConfig("pu_control", "#P(U)Control "),
        SectionConfig("pf_control", "#P(f)Control "),
        SectionConfig("pi_control", "#P(I)Control "),
        SectionConfig("restriction", "#Restriction "),
        SectionConfig("extras", "#Extra Text:"),
        SectionConfig("notes", "#Note Text:"),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for WindTurbine-specific field deserialization.

        Args:
            kwarg_name: Name of the field requiring class resolution.

        Returns:
            Target class for the specified field, or None if no special handling needed.

        """
        if kwarg_name == "presentations":
            from pyptp.elements.mv.presentations import ElementPresentation

            return ElementPresentation
        if kwarg_name == "type":
            return WindTurbineMV.WindTurbineType
        if kwarg_name == "q_control":
            return WindTurbineMV.QControl
        if kwarg_name == "pu_control":
            return WindTurbineMV.PUControl
        if kwarg_name == "pf_control":
            return WindTurbineMV.PfControl
        if kwarg_name == "pi_control":
            return WindTurbineMV.PIControl
        if kwarg_name == "restriction":
            return WindTurbineMV.Restriction
        return None
