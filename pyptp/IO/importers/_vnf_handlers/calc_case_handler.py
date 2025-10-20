"""Handler for parsing VNF Case sections using a declarative recipe."""

from __future__ import annotations

from typing import Any, ClassVar

from pyptp.elements.mv.calc_case import CalculationCaseMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType


class CalcCaseHandler(DeclarativeHandler[TNetworkMSType]):
    """Parses VNF Case components using a declarative recipe.

    Handles calculation cases with general properties and content strings
    for network analysis scenarios.
    """

    COMPONENT_CLS = CalculationCaseMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("content_strings", "#Content ", required=False),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type[Any] | None:
        """Resolve target class for CalcCase-specific fields.

        Args:
            kwarg_name: Name of the field requiring class resolution.

        Returns:
            Target class for deserialization, or None if not found.

        """
        if kwarg_name == "general":
            return CalculationCaseMV.General
        # content_strings are plain strings, no class
        return None

    def post_process_element(self, element: CalculationCaseMV, network: TNetworkMSType) -> None:
        """Post-process the calc case element after parsing.

        Calc cases are stored in the network calc_cases list rather than a GUID-indexed dict.

        Args:
            element: The parsed calc case element.
            network: The target network to register the element with.

        """
        network.calc_cases.append(element)
